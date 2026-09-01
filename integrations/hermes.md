# Hermes Agent

Status: **supported for the Telegram-compatible imGram path; no Hermes fork is needed.**

Recent Hermes releases already expose the two `python-telegram-bot` transport
settings that matter here: `extra.base_url` and `extra.base_file_url`. Its
maintained Telegram adapter therefore keeps ownership of long polling, command
registration, group mention routing, typing refresh, one-message streaming
edits, final formatting, retries, and photo/video/voice/audio/document
routing. Do not replace it with a small hand-written polling loop.

## Configuration

Use the existing `telegram` platform, but point both API roots at imGram. The
two trailing `/bot` path segments are intentional: the Telegram SDK appends
the token itself.

```yaml
# ~/.hermes/config.yaml
gateway:
  platforms:
    telegram:
      enabled: true
      token: "YOUR_IMGRAM_BOT_TOKEN"
      typing_indicator: true
      extra:
        base_url: "https://bot.premsir.com/bot"
        base_file_url: "https://bot.premsir.com/file/bot"
        # imGram v1 does not expose inline keyboards/callback queries.
        # Keep normal replies as messages; use an explicit native article
        # operation only when a user actually asks for an article.
        rich_messages: false
        rich_drafts: false
```

If your Hermes installation reads the token from the environment, use one
secret source:

```bash
export TELEGRAM_BOT_TOKEN="$IMGRAM_BOT_TOKEN"
```

Never set either root to `api.telegram.org`. Startup `getMe` must succeed
against `bot.premsir.com`; Hermes' normal `setMyCommands` call then powers
imGram's command menu and `/` suggestions.

## What this preserves

| Behaviour | Hermes through the configuration above |
|---|---:|
| Text, HTML/Markdown, replies and mentions | Yes |
| Long polling and webhook cleanup | Yes |
| `正在输入` refresh and one-bubble streaming edits | Yes |
| Command menu (`setMyCommands`) | Yes |
| Photos, documents, video, voice and audio | Yes, through the maintained adapter |
| Incoming file download (`getFile`) | Yes, through `base_file_url` |
| Standard emoji reactions | Yes when Hermes enables its reaction path |
| Inline keyboards / callback queries | No — imGram v1 does not expose them |

## imGram-native actions

Normal replies remain `sendMessage`/`editMessageText`. For a pin, checklist,
checklist change, article, or explicit reaction, Hermes needs a typed tool
instead of asking the model to claim it performed an action. Install the
companion [`hermes-imgram-actions`](hermes-imgram-actions/) plugin into
`~/.hermes/plugins/imgram-actions/`, then enable its `imgram` toolset. It acts
only in the current chat, reads real chat/message IDs from Hermes session
context, and reports the Bot API result to the Agent.

The bundled Telegram adapter may ignore imGram-only incoming checklist fields
until its `python-telegram-bot` dependency adds the corresponding Bot API
types. The action plugin can send and change native checklists now; for an
Agent that must react to every human checklist completion, use nanobot's
versioned imGram channel until Hermes upstream exposes those update fields.

## Verification

1. A slow prompt shows `正在输入` and a final answer grows in one message.
2. A photo and document reach Hermes as downloaded media, not only metadata.
3. The bot menu or `/` shows commands registered by Hermes.
4. After enabling the `imgram` toolset, pin the current message and create a
   checklist; verify the native client UI operation.

References: [Hermes Telegram adapter](https://github.com/NousResearch/hermes-agent/tree/main/plugins/platforms/telegram) and [Hermes platform-plugin guide](https://github.com/NousResearch/hermes-agent/blob/main/website/docs/developer-guide/adding-platform-adapters.md).
