# nanobot

Status: **the Telegram channel is a strong base, but it needs a small first-class
imGram adapter**.

The current nanobot Telegram runtime already implements most of the experience
imGram wants: a four-second typing loop, one-message streaming with
`editMessageText`, final HTML rendering, automatic command registration,
incoming media download, and temporary reactions. Its current configuration
does not expose a custom Bot API root, so pasting an imGram token into the stock
Telegram channel would still send it to Telegram.

## Required transport patch

Add an `api_root` setting to a dedicated `imgram` channel and configure both
URLs used by `python-telegram-bot`:

```python
api_root = self.config.api_root.rstrip("/")
builder = (
    Application.builder()
    .token(self.config.token)
    .base_url(f"{api_root}/bot")
    .base_file_url(f"{api_root}/file/bot")
    .request(api_request)
    .get_updates_request(poll_request)
)
```

For production imGram, `api_root` is `https://bot.premsir.com`. The library
appends the token to both configured prefixes; do not include the token in the
setting itself.

Keep nanobot's existing deterministic behavior:

- register `BOT_COMMANDS` with `setMyCommands` during startup;
- download incoming photos/documents through `getFile` and the configured file
  base URL before forwarding their bytes/path to the Agent;
- refresh `sendChatAction(typing)` every four seconds;
- use the existing coalesced `editMessageText` streaming buffer;
- use the default `👀` acknowledgement reaction and clear it in final cleanup.

Keep `inline_keyboards` and `rich_messages` disabled until the corresponding
imGram methods are listed as supported. Route generated photos and ordinary
files through `sendPhoto` and `sendDocument`; do not silently call unsupported
video, voice, or audio methods.

## Pinning is a separate Agent capability

nanobot's streaming channel behavior does not by itself give the model a real
pin tool. Add a typed `pin_message(chat_id, message_id)` operation that calls
`pinChatMessage` and returns success only after receiving
`{"ok":true,"result":true}`. Apply the same rule to unpinning. Do not teach the
model to claim success through prompt text.

After the transport patch, run the complete checklist in
[ADAPTER_GUIDE.md](../ADAPTER_GUIDE.md), especially command-menu visibility,
image bytes reaching multimodal input, and a response-level pin test.

References: [nanobot Telegram runtime](https://github.com/HKUDS/nanobot/blob/main/nanobot/channels/telegram/runtime.py), [nanobot Telegram guide](https://github.com/HKUDS/nanobot/blob/main/docs/guides/telegram-ai-agent.md), and [`python-telegram-bot` custom base URLs](https://docs.python-telegram-bot.org/en/v22.6/telegram.ext.applicationbuilder.html#telegram.ext.ApplicationBuilder.base_url).
