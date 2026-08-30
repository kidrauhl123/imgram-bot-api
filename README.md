# Imgram Bot API

Imgram Bot API lets bots and AI agents participate in Imgram private chats and groups through a small, Telegram-style HTTP API.

> Status: experimental v1. This is a compatible subset, not a drop-in implementation of the complete Telegram Bot API.

Imgram is an independent service. Imgram accounts, chats, and bot tokens do not belong to Telegram and cannot be used at `api.telegram.org`.

## Quick start

Create a bot in Imgram by opening **BotFather**, sending `/newbot`, and following the prompts. Then test the token without placing it directly in your command history:

```bash
export IMGRAM_BOT_TOKEN='replace-with-your-token'
export IMGRAM_API_ROOT='https://bot.premsir.com'

curl "$IMGRAM_API_ROOT/bot$IMGRAM_BOT_TOKEN/getMe"
```

Send a message:

```bash
curl -X POST "$IMGRAM_API_ROOT/bot$IMGRAM_BOT_TOKEN/sendMessage" \
  --data-urlencode 'chat_id=123456' \
  --data-urlencode 'text=Hello from an Imgram bot'
```

The same endpoint style supports typing indicators (`sendChatAction`), message reactions (`setMessageReaction`), and multipart photo/file uploads (`sendPhoto`, `sendDocument`).

Consume incoming messages with [`getUpdates`](BOT_API.md#getupdates) or a [webhook](BOT_API.md#webhooks).

## Documentation

- [Bot API reference](BOT_API.md)
- [Compatibility matrix](COMPATIBILITY.md)
- [Connection guide for AI agents](CONNECT.md)
- [Adapter implementation and UX contract](ADAPTER_GUIDE.md)
- [OpenAPI 3.1 document](openapi.json)
- Integration notes: [CC Connect](integrations/cc-connect.md), [OpenClaw](integrations/openclaw.md), [Hermes Agent](integrations/hermes.md)
- [Machine-readable documentation index](llms.txt)

## 中文说明

Imgram Bot API 让机器人和 Agent 通过 HTTP 参与 Imgram 私聊、群聊和原生核对清单。接口沿用 Telegram Bot API 熟悉的 URL、方法名与 JSON 外形，但当前只实现了明确列出的子集。

给 AI 的最短说明是：

```text
这是 Imgram Bot，不是 Telegram Bot。
API Root: https://bot.premsir.com
Token: <IMGRAM_BOT_TOKEN>
连接前先阅读：https://github.com/kidrauhl123/imgram-bot-api/blob/main/CONNECT.md
不要把 Token 发送到 api.telegram.org。
```

如果 AI 正在给现有 Agent 框架编写 Imgram 适配器，还必须阅读
[适配器体验规范](ADAPTER_GUIDE.md)。`正在输入`、流式编辑、重试、附件路由和
结束清理应该一次性写进适配器；不要依赖上层模型每次自己记得调用。

API 域名目前使用 `bot.premsir.com`，产品名是 **Imgram**；域名不代表产品名。

## Security

Treat a bot token as a password. Keep it out of source code, screenshots, issue reports, analytics, and logs. If a token is exposed, stop using it, create a replacement bot, and ask the Imgram service operator to invalidate the exposed token. Self-service token revocation is not part of v1 yet.
