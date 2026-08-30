# CC Connect

Status: **an imGram adapter is required**.

The current CC Connect Telegram platform cannot be made imGram-compatible by changing only the bot token. Its Telegram implementation targets Telegram's API root, and its normal feature set still includes methods that imGram v1 does not yet expose, including callback queries and additional media types. imGram now supports bot-side file downloads and default command setup.

Do not configure an imGram token under an unchanged `type = "telegram"` integration: that risks sending the token to the wrong service and will not produce a working connection.

## Recommended implementation

Add a first-class `imgram` platform to CC Connect that:

- accepts `token` and `api_base`, defaulting `api_base` to `https://bot.premsir.com`;
- uses only methods marked supported in [COMPATIBILITY.md](../COMPATIBILITY.md);
- maps incoming `message` and `edited_message` updates;
- uses `getFile` for incoming media and `setMyCommands` for its stable command list;
- degrades unsupported callbacks, inline buttons, and additional media methods explicitly;
- exposes imGram checklists as a native capability instead of flattening them to text.

Its channel runtime should implement the deterministic typing, streaming,
cleanup, retry, and media rules in [ADAPTER_GUIDE.md](../ADAPTER_GUIDE.md),
instead of adding those instructions to the connected Agent's prompt.

A future configuration could look like this; it is a design target, not valid upstream configuration today:

```toml
[[projects.platforms]]
type = "imgram"

[projects.platforms.options]
token = "${IMGRAM_BOT_TOKEN}"
api_base = "https://bot.premsir.com"
```

CC Connect reference: [project](https://github.com/chenhg5/cc-connect) and [Telegram guide](https://github.com/chenhg5/cc-connect/blob/main/docs/telegram.md).
