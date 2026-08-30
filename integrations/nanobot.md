# nanobot

imGram ships a first-class nanobot channel overlay based on the official
nanobot v0.3.0 Telegram runtime. It does not reimplement the chat lifecycle.
`ImgramChannel` subclasses `TelegramChannel`, so command registration, ordered
ingress, group mentions, reply context, albums, media download, typing refresh,
temporary reactions, streaming edits, formatting, chunking, retries, polling,
and webhooks continue to use nanobot's official code.

The maintained source is in
[`nanobot_channel/`](nanobot_channel/). The only transport differences are:

- channel/session identity is `imgram` / `imgram:<chat_id>`;
- API calls use `apiRoot`, defaulting to `https://bot.premsir.com`;
- files use the matching `<apiRoot>/file/bot` endpoint;
- downloaded media is isolated in nanobot's `imgram` media directory;
- the API root validator refuses Telegram hosts, so an imGram token cannot be
  leaked through an accidental fallback.

## Configuration

Install the overlay into the same environment as nanobot, then configure a
dedicated `imgram` channel:

```json
{
  "channels": {
    "imgram": {
      "enabled": true,
      "token": "YOUR_IMGRAM_BOT_TOKEN",
      "apiRoot": "https://bot.premsir.com",
      "streaming": true,
      "groupPolicy": "mention",
      "replyToMessage": false,
      "inlineKeyboards": false,
      "richMessages": false
    }
  }
}
```

Do not put an imGram token in nanobot's ordinary `telegram` channel. Restart
the nanobot gateway after installation or configuration changes. Startup calls
`getMe` and `setMyCommands`; the latter powers imGram's command-menu button and
`/` autocomplete.

## Native imGram actions

The overlay also installs the typed `imgram_action` Agent tool. The tool uses
the current request's real `chat_id` and `message_id`, calls the Bot API, and
returns success only after an `ok=true` response. Supported actions are:

- pin, unpin, react, edit, and delete;
- send, toggle, and append a native checklist;
- send a native imGram article from Markdown.

This is deliberately separate from the transport's ordinary response path.
The model decides whether the requested action is appropriate; deterministic
typing, streaming, media transfer, and cleanup remain official adapter code.

`richMessages` stays disabled by default because enabling it makes every normal
nanobot answer a native article. Use `imgram_action(action="send_article", ...)`
when the user explicitly requests an article.

## Media behavior

The inherited official runtime sends local output through `sendPhoto`,
`sendVideo`, `sendVoice`, `sendAudio`, or `sendDocument` according to file type.
Incoming photo, video, video note, animation, voice, audio, and document updates
are downloaded through `getFile` and forwarded to nanobot as actual local media
paths. Voice and audio continue through nanobot's official transcription path.

## Version contract

The overlay is pinned to nanobot v0.3.0 because it inherits private helper
methods from that exact runtime. Its regression test asserts that `send`,
`send_delta`, and `_process_message_update` are still inherited rather than
forked. Re-audit those seams before supporting a later nanobot release.

References: [nanobot v0.3.0 Telegram runtime](https://github.com/HKUDS/nanobot/blob/v0.3.0/nanobot/channels/telegram/runtime.py), [nanobot Telegram guide](https://github.com/HKUDS/nanobot/blob/v0.3.0/docs/guides/telegram-ai-agent.md), and [`python-telegram-bot` custom base URLs](https://docs.python-telegram-bot.org/en/v22.6/telegram.ext.applicationbuilder.html#telegram.ext.ApplicationBuilder.base_url).
