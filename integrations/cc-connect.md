# CC Connect

Status: **an Imgram adapter is required**.

The current CC Connect Telegram platform cannot be made Imgram-compatible by changing only the bot token. Its Telegram implementation targets Telegram's API root, and its normal feature set includes methods that Imgram v1 does not yet expose, including bot-side file downloads, command setup, and callback queries.

Do not configure an Imgram token under an unchanged `type = "telegram"` integration: that risks sending the token to the wrong service and will not produce a working connection.

## Recommended implementation

Add a first-class `imgram` platform to CC Connect that:

- accepts `token` and `api_base`, defaulting `api_base` to `https://bot.premsir.com`;
- uses only methods marked supported in [COMPATIBILITY.md](../COMPATIBILITY.md);
- maps incoming `message` and `edited_message` updates;
- degrades unsupported bot-side downloads, commands, and buttons explicitly;
- exposes Imgram checklists as a native capability instead of flattening them to text.

A future configuration could look like this; it is a design target, not valid upstream configuration today:

```toml
[[projects.platforms]]
type = "imgram"

[projects.platforms.options]
token = "${IMGRAM_BOT_TOKEN}"
api_base = "https://bot.premsir.com"
```

CC Connect reference: [project](https://github.com/chenhg5/cc-connect) and [Telegram guide](https://github.com/chenhg5/cc-connect/blob/main/docs/telegram.md).
