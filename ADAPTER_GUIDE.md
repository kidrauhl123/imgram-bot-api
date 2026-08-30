# Build an AI-friendly imGram adapter

This guide is for the human or coding agent implementing imGram support in an
Agent framework. Read [CONNECT.md](CONNECT.md) and
[COMPATIBILITY.md](COMPATIBILITY.md) first.

The central rule is:

> Put deterministic chat behavior in the adapter once. Do not rely on the
> language model to remember when to type, stream, edit, retry, upload, or
> clean up.

"Put it in the adapter" does **not** mean hard-code credentials or user data.
The token must remain secret and configurable. The API root must remain
configurable, with `https://bot.premsir.com` as the default.

## Responsibility boundary

| Agent or tool layer decides | imGram adapter enforces |
|---|---|
| What the answer says | Where every HTTP request is sent |
| Whether a user-requested message should be pinned, deleted, or reacted to | Typing lifecycle and refresh timing |
| Whether to send a checklist or attach a generated artifact | One-message streaming through `editMessageText` |
| Which structured capability to invoke | Formatting conversion, chunking, retries, and cleanup |

Do not add prompt text such as "remember to call typing every four seconds".
The model can forget it, call it too late, or leave it running after an error.
Implement that behavior in transport code.

Bot-authored `editMessageText` calls automatically hide the client “edited”
marker. Adapters do not need a separate flag for streaming-message edits;
human-authored edits remain visibly marked.

Expose explicit structured operations to the Agent core when the framework
supports tools or typed outbound events:

- `send_text`, `send_photo`, and `send_document`;
- `edit_message` and `delete_message`;
- `pin_message` and `unpin_message`;
- `set_reaction` and `clear_reaction`;
- `send_checklist`, `toggle_checklist`, and `append_checklist`.

Avoid magic strings in model output such as `PIN_MESSAGE:42`. Translate typed
operations into Bot API calls inside the adapter.

## Required configuration

Recommended adapter-owned settings:

```text
token: secret, required
api_root: https://bot.premsir.com
update_transport: polling | webhook
streaming: true
typing_refresh_seconds: 4
stream_edit_interval_ms: 800
parse_mode: HTML
ack_reaction: optional; one documented standard reaction, such as 🤔
```

Construct every method URL as:

```text
<api_root>/bot<token>/<method>
```

The adapter MUST NOT fall back to `api.telegram.org`. Prefer a first-class
channel name such as `imgram` instead of placing an imGram token in an
unchanged `telegram` channel. Verify the token with `getMe` at startup. Also
register the adapter's stable command list with `setMyCommands`; imGram uses it
for the command-menu button and `/` autocomplete.

## Default response lifecycle

For every accepted incoming user message, the adapter SHOULD perform this
sequence automatically:

1. Serialize work per chat so two response streams cannot edit the same
   message state.
2. Start a background `sendChatAction(action=typing)` loop immediately.
3. Refresh `typing` every four seconds until the response is finalized,
   cancelled, or fails.
4. Optionally add a small, best-effort acknowledgement reaction to the user's
   message. `🤔` is a suitable processing reaction in the current catalog.
5. On the first non-whitespace text delta, call `sendMessage` and retain the
   returned `message_id`.
6. Accumulate later deltas and edit that same message no more often than once
   every 800 milliseconds.
7. On stream end, force one final edit with fully rendered formatting, even if
   the normal edit interval has not elapsed.
8. In a `finally` block, cancel the typing task and remove any temporary
   acknowledgement reaction. There is no explicit "stop typing" method; stop
   refreshing it and let the transient action expire.

The timing values are defaults, not protocol constants. They should be
configuration options, while the lifecycle itself should remain adapter code.

### Framework-neutral pseudocode

```text
on_incoming_message(update):
    reject_or_ignore_unauthorized_sender(update)
    deduplicate(update.update_id)
    state = begin_serial_chat_run(update.message.chat.id)
    sendChatAction(update.message.chat.id, "typing")
    state.typing_task = repeat_every(4s,
        sendChatAction(update.message.chat.id, "typing"))
    best_effort(setMessageReaction(
        update.message.chat.id, update.message.message_id, "🤔"))

    try:
        for event in agent.run(update):
            if event is text_delta:
                state.text += event.text
                if state.text is blank:
                    continue
                if state.message_id is missing:
                    sent = sendMessage(
                        update.message.chat.id, plain_preview(state.text))
                    state.message_id = sent.message_id
                else if 800ms elapsed and preview changed:
                    editMessageText(
                        update.message.chat.id, state.message_id,
                        plain_preview(state.text))

            if event is structured_message_operation:
                dispatch_to_supported_imgram_method(event)

        final_text = render_safe_html(state.text)
        if state.message_id exists:
            editMessageText(
                update.message.chat.id, state.message_id, final_text,
                parse_mode="HTML")
        else if final_text is not blank:
            sendMessage(
                update.message.chat.id, final_text, parse_mode="HTML")

        send_queued_media_and_structured_outputs()
    finally:
        cancel(state.typing_task)
        best_effort(clear_reaction(
            update.message.chat.id, update.message.message_id))
        end_serial_chat_run(state)
```

Keep a separate stream state for each chat. If the framework deliberately
supports concurrent turns in one chat, key it by `(chat_id, stream_id)` and
make typing cancellation reference-counted.

## Streaming and formatting rules

- Do not send one new message for every token or progress event.
- Do not edit on every token. Coalesce deltas and use the configured interval.
- Do not parse incomplete Markdown during intermediate edits. Strip unstable
  markers or send a safe plain-text preview.
- Render final output once, preferably as escaped HTML, and use
  `parse_mode=HTML` for the final send or edit.
- Treat a "message is not modified" response as success.
- Only retry a final edit as plain text when the server rejected formatting.
  Do not turn a timeout or network error into a second plain-text request.
- Reuse the framework's Telegram-compatible message chunker. A conservative
  ceiling of 4,000 characters per chunk leaves room below Telegram-style
  limits. Preserve code blocks and entity boundaries when splitting.
- If a stream exceeds one message, finalize the current chunk, send the next
  chunk once, and continue editing only the newest message.
- On cancellation or failure, never leave a background typing loop running.
  Either finalize the useful partial text, replace it with a short failure
  notice, or delete the preview according to the host framework's policy.

Progress events such as tool names, internal reasoning, and file-edit traces
should not create a flood of ordinary chat messages. Render them only when the
product explicitly exposes such progress, and keep them separate from the
single user-facing answer stream.

## Media behavior

imGram v1 exposes Telegram-style `sendPhoto`, `sendDocument`, and `getFile`.

The adapter SHOULD:

- choose `sendPhoto` for supported image output and `sendDocument` for every
  other generated file;
- upload with `multipart/form-data` and keep each file below 50 MiB;
- use `upload_photo` or `upload_document` chat actions while preparing a slow
  upload;
- download an HTTPS source into a validated temporary file before uploading
  when the Agent produces a remote URL;
- enforce the framework's workspace/path and SSRF safety policy;
- report an unsupported or failed attachment visibly instead of silently
  dropping it.
- for an incoming photo, select the largest useful `photo` entry, call
  `getFile(file_id)`, download `/file/bot<TOKEN>/<file_path>`, and pass the
  bytes and MIME type into the Agent's actual image/multimodal input;
- download incoming documents the same way and expose them through the host
  framework's safe attachment/workspace mechanism.

Do not pass remote URLs or Telegram `file_id` values to imGram v1. Do not call
`sendVideo`, `sendVoice`, or `sendAudio`; they are not implemented. A `file_id`
from an incoming update is valid as input to `getFile`, but is not yet valid as
the upload argument to `sendPhoto` or `sendDocument`.

## Reactions, edits, pins, and checklists

Temporary acknowledgement reactions belong to the adapter lifecycle. A
reaction explicitly requested by the user or Agent is a structured operation
and should not be automatically removed.

Use only the documented reaction set and treat decorative acknowledgement
failures as non-fatal. User-requested operations such as `pinChatMessage`,
`unpinChatMessage`, `editMessageText`, and checklist changes should return a
visible error to the Agent if they fail.

`pin_message(chat_id, message_id)` must be a real structured tool or outbound
event. Its implementation calls `pinChatMessage` and returns success only for
an HTTP success containing `{"ok":true,"result":true}`. If the framework
cannot expose that tool, tell the user pinning is unavailable; never let the
model claim it pinned a message after producing text alone. Add a request-level
test that fails unless invoking the tool emits exactly one `pinChatMessage`
request with the retained `chat_id` and `message_id`.

Retain `chat_id` and `message_id` in the framework's inbound metadata so later
tools can target the correct message. Do not ask the model to infer IDs from
displayed text.

## Update delivery and retries

- Choose exactly one transport: long polling or webhook.
- Persist the last successfully processed `update_id` and poll next with
  `offset=update_id+1`.
- Make inbound handlers idempotent because delivery around failures can repeat.
- Process updates in stable order per chat.
- Ignore the bot's own output if the host framework can receive it back.
- Treat typing and temporary reactions as best-effort; they must never prevent
  the final answer.
- Bound retries and use exponential backoff for transient failures.
- Do not retry authentication, invalid-parameter, or unknown-method errors.
- Be careful retrying message-creation requests after an ambiguous timeout:
  imGram v1 has no public idempotency key, so a blind retry can duplicate a
  message.

For webhooks, validate `X-Telegram-Bot-Api-Secret-Token` before accepting an
update. The header name is Telegram-compatible even though the service is
imGram.

## Adapting an existing Telegram channel

Do not assume that changing the base URL is the entire port. Audit the channel
and make these changes explicitly:

1. Add an imGram-specific configuration type with a configurable API root.
2. Prove through a request test that an imGram token is never sent to any other
   host.
3. Keep Telegram-style command registration, but disable unsupported startup
   calls, inline keyboards, callback queries, channels, and supergroups.
4. Map outbound video/audio/voice artifacts to `sendDocument`, or expose a
   clear unsupported result.
5. Implement the response lifecycle above in channel code.
6. Expose supported message operations as typed capabilities to the Agent.
7. Keep unsupported capabilities visible in logs and user-facing errors.

This is the same architectural pattern used by mature Agent chat channels:
progress streaming, typing refresh, reaction acknowledgement, retry policy,
and media routing live in channel code rather than in the model prompt.

## Acceptance checklist

The adapter is not complete until a user can verify all applicable items:

- [ ] `getMe` succeeds against the configured imGram API root.
- [ ] Network inspection shows no imGram token sent to `api.telegram.org` or
      another host.
- [ ] Polling restarts without replaying already completed turns.
- [ ] `setMyCommands` produces a visible command menu and `/` autocomplete in
      the bot chat.
- [ ] A deliberately slow answer shows `正在输入` promptly and keeps it alive.
- [ ] A streamed answer grows inside one message instead of producing many
      bubbles.
- [ ] The final edit contains correct rich text and no leaked Markdown markers.
- [ ] Cancelling or failing a turn stops typing and cleans temporary reaction
      state.
- [ ] Photo and document uploads render in the imGram client.
- [ ] A user-sent photo is downloaded through `getFile` and reaches the
      Agent's image input as bytes, not merely as metadata.
- [ ] Reaction add/clear, message edit, pin, and unpin work through structured
      adapter operations.
- [ ] A failed pin request is reported as a failure; the Agent never claims it
      succeeded without `ok=true` and `result=true`.
- [ ] Private chats and groups keep independent stream state.
- [ ] Unsupported methods fail explicitly and do not prevent basic startup.

## Prompt for the coding agent doing the first port

Give the coding agent the repository and this instruction:

```text
Implement a first-class imGram adapter. Read CONNECT.md, ADAPTER_GUIDE.md,
COMPATIBILITY.md, and BOT_API.md before editing. Hard-code the deterministic
chat UX lifecycle into the adapter: typing refresh, coalesced one-message
streaming, final formatting, cleanup, bounded retries, media routing, and
structured message operations. Keep token and API root configurable. Never
send an imGram token to api.telegram.org, never silently fall back to Telegram,
and do not call methods outside imGram's documented compatibility subset.
Download incoming media with getFile and pass the bytes to the Agent's real
attachment or multimodal input. Implement pin/unpin as typed tools and never
report success unless the Bot API returned ok=true and result=true.
Add tests for the lifecycle and host routing, then report any missing server
capability instead of faking it in the model prompt.
```
