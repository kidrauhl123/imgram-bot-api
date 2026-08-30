# OpenClaw

Status: **experimental; not yet a paste-token-and-run integration**.

OpenClaw's Telegram channel supports a custom `apiRoot`, so it can direct requests to imGram instead of Telegram:

```js
{
  channels: {
    telegram: {
      enabled: true,
      botToken: process.env.IMGRAM_BOT_TOKEN,
      apiRoot: "https://bot.premsir.com"
    }
  }
}
```

The API root must be the host root only. Do not append `/bot<TOKEN>`.

This routing feature is necessary but not sufficient. imGram now supports bot-command setup, chat actions, photo/document upload, and incoming file download. OpenClaw releases may still call unsupported callback, inline-button, or additional media methods; a release that treats those optional failures as fatal may fail during startup or at runtime.

Before using this in production:

1. Compare the OpenClaw release's required Telegram methods with [imGram's compatibility matrix](../COMPATIBILITY.md).
2. Disable optional Telegram features that require unsupported methods, where the installed OpenClaw version documents such settings.
3. Verify `getMe`, incoming text through `getUpdates`, and `sendMessage` in a test bot.
4. Never allow fallback to `api.telegram.org`.

If a dedicated imGram channel is added, implement the lifecycle in
[ADAPTER_GUIDE.md](../ADAPTER_GUIDE.md) in channel code rather than relying on
an Agent prompt to remember typing, streaming edits, or cleanup.

OpenClaw reference: [Telegram channel documentation](https://github.com/openclaw/openclaw/blob/main/docs/channels/telegram.md).
