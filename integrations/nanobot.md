# nanobot

Status: **the Telegram channel is a strong base, but it needs a small first-class
imGram adapter**.

The current nanobot Telegram runtime already implements most of the experience
imGram wants: a four-second typing loop, one-message streaming with
`editMessageText`, final HTML rendering, automatic command registration,
incoming media download, and temporary reactions. Its current configuration
does not expose a custom Bot API root, so pasting an imGram token into the stock
Telegram channel would still send it to Telegram.

## Apply the ready transport patch

Use the stock Telegram channel and apply
[`nanobot-imgram.patch`](nanobot-imgram.patch) to the nanobot checkout. Do not
replace its runtime with a minimal hand-written channel: doing so drops the
command registration and media-download behavior that make the official
channel useful.

Existing installations that already use the earlier dedicated `imgram`
channel can apply
[`nanobot-imgram-runtime-fixes.patch`](nanobot-imgram-runtime-fixes.patch).
That repair registers the real nanobot command list at startup, downloads
incoming photo/document bytes into nanobot's media directory, and forwards the
path through `InboundMessage.media` instead of sending attachment metadata only.

```bash
git -C /path/to/nanobot apply /path/to/imgram-bot-api/integrations/nanobot-imgram.patch
```

Then add `apiRoot` to nanobot's existing Telegram channel configuration:

```json
{
  "channels": {
    "telegram": {
      "enabled": true,
      "token": "YOUR_IMGRAM_BOT_TOKEN",
      "apiRoot": "https://bot.premsir.com"
    }
  }
}
```

Restart the nanobot gateway after changing the runtime or configuration. On
startup, the unchanged official runtime calls `setMyCommands`; for incoming
photos it calls `getFile`, downloads the bytes through `base_file_url`, and
passes the local media path to the Agent.

## What the patch changes

The patch adds an `api_root` setting to the existing Telegram channel and
configures both URLs used by `python-telegram-bot`:

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
