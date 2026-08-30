# Hermes Agent

Status: **a custom endpoint option or imGram adapter is required**.

Hermes Agent's public Telegram gateway configuration documents a Telegram bot token and user access controls, but does not currently document a custom Telegram Bot API root. An imGram token alone therefore is not enough to route Hermes to imGram.

Do not place an imGram token in `TELEGRAM_BOT_TOKEN` unless the installed Hermes version has first been modified and verified to send all requests only to `https://bot.premsir.com`.

## Adapter contract

A minimal imGram gateway for Hermes should:

1. read `IMGRAM_BOT_TOKEN` and an optional `IMGRAM_API_ROOT`;
2. verify the bot with `getMe`;
3. receive `message` and `edited_message` using `getUpdates` or a webhook;
4. send plain replies using `sendMessage`;
5. store the polling offset and enforce an imGram user allowlist;
6. expose checklist operations only when the Hermes tool layer requests them.

The gateway should also implement [imGram's adapter UX contract](../ADAPTER_GUIDE.md)
in code, including typing refresh, coalesced streamed edits, final cleanup, and
supported media routing.

The proposed environment-variable names above describe an imGram adapter; they are not upstream Hermes variables today.

Hermes reference: [environment variables](https://github.com/NousResearch/hermes-agent/blob/main/website/docs/reference/environment-variables.md).
