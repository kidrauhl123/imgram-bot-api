# Connect an AI agent to imGram

This page is the canonical starting point for humans and AI coding agents.

## Connection contract

You need two values:

```text
API root: https://bot.premsir.com
Bot token: supplied by the imGram user
```

Construct method URLs as:

```text
<API root>/bot<token>/<method>
```

The API root must not include `/bot<TOKEN>`. Never send an imGram token to Telegram or any unrelated host.

## Instructions for an AI agent

When a user asks you to connect their imGram bot:

1. Treat the token as a secret. Do not quote it back, commit it, print it in logs, or put it in a public command example.
2. Read [COMPATIBILITY.md](COMPATIBILITY.md) before choosing a Telegram SDK or an existing connector.
3. If you are adding or modifying a framework adapter, read and implement [ADAPTER_GUIDE.md](ADAPTER_GUIDE.md). Typing refresh, streamed message editing, cleanup, retries, and media routing belong in adapter code rather than the model prompt.
4. Verify credentials with `getMe` against the imGram API root.
5. Prefer raw HTTP for v1 unless the selected connector supports both a custom API root and the methods imGram implements.
6. Choose exactly one update transport: `getUpdates` or webhook.
7. Persist the last successfully processed `update_id`; acknowledge it by using `offset=update_id+1` on the next poll.
8. Make handlers idempotent because an update can be delivered more than once around failures.

Do not silently fall back to `api.telegram.org`. A failure against imGram should remain visible to the user.

## Minimal polling loop

This example proves connectivity and update delivery. It is not a complete
user-experience adapter. Production adapters should additionally implement the
deterministic lifecycle in [ADAPTER_GUIDE.md](ADAPTER_GUIDE.md).

The following Python example uses only the standard library:

```python
import json
import os
import urllib.parse
import urllib.request

root = os.environ.get("IMGRAM_API_ROOT", "https://bot.premsir.com").rstrip("/")
token = os.environ["IMGRAM_BOT_TOKEN"]
base = f"{root}/bot{token}"
offset = 0

def call(method, params=None):
    body = urllib.parse.urlencode(params or {}).encode()
    request = urllib.request.Request(f"{base}/{method}", data=body, method="POST")
    with urllib.request.urlopen(request, timeout=35) as response:
        payload = json.load(response)
    if not payload.get("ok"):
        raise RuntimeError(payload.get("description", "imGram API error"))
    return payload["result"]

print(call("getMe"))

while True:
    for update in call("getUpdates", {"offset": offset, "timeout": 30}):
        message = update.get("message") or update.get("edited_message")
        if message and message.get("text"):
            call("sendMessage", {
                "chat_id": message["chat"]["id"],
                "text": f"<b>You said:</b> {message['text']}",
                "parse_mode": "HTML",
            })
        offset = update["update_id"] + 1
```

For production, persist `offset` outside process memory, add exponential backoff, handle HTTP errors, and shut down cleanly.

`sendMessage` and `editMessageText` accept `parse_mode` (`HTML`, `MarkdownV2`, or `Markdown`) or explicit Telegram-style `entities`. Incoming messages expose their `entities` as well. Prefer HTML for simple Agent output and escape untrusted text before inserting it into HTML. When a framework omits `parse_mode`, imGram also recognizes a conservative CommonMark subset so ordinary Agent output such as `**bold**` and inline code does not leak formatting markers.

For a slow response, the adapter should call `sendChatAction` with `action=typing` immediately and refresh it every four seconds until the answer is finalized. It should coalesce text deltas into one message using `editMessageText`, not ask the model to make those calls. Use `setMessageReaction` for lightweight acknowledgement before or after a response; imGram accepts one standard emoji and an empty array clears it. Send generated photos or files with Telegram-compatible multipart `sendPhoto` and `sendDocument` requests. Download user-sent media by calling `getFile(file_id)` and fetching the returned authenticated path, then pass the bytes to the Agent's real attachment or multimodal input. Uploads are limited to 50 MiB; URL and reusable `file_id` upload inputs are not part of v1 yet.

## Existing agent frameworks

- [OpenClaw](integrations/openclaw.md): closest path because it exposes a custom Telegram API root, but currently experimental with imGram.
- [CC Connect](integrations/cc-connect.md): requires a dedicated imGram adapter or an upstream endpoint option.
- [Hermes Agent](integrations/hermes.md): requires a custom endpoint option or adapter.
- [nanobot](integrations/nanobot.md): a maintained imGram channel inherits its official Telegram runtime and adds verified native imGram actions.

These short guides document connector-specific facts. The Bot API reference remains the source of truth; a separate guide is not needed for every agent framework that can make ordinary HTTP requests.
