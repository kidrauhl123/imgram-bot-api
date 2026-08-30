# Compatibility matrix

Imgram v1 deliberately implements a useful Telegram-style subset. A matching method name does not imply support for every Telegram parameter or response field.

## Methods

| Telegram-style method | Imgram v1 | Important differences |
|---|---:|---|
| `getMe` | Yes | Core User fields only. |
| `sendMessage` | Partial | Text, replies, automatic `@mentions`, `HTML`/`MarkdownV2`/`Markdown` parse modes, explicit entities, and a tolerant CommonMark fallback for Agent output; no link-preview options or `reply_markup`. |
| `sendPhoto` | Partial | Multipart upload up to 50 MiB, caption formatting, and replies; no URL or `file_id` upload input. |
| `sendDocument` | Partial | Multipart upload up to 50 MiB, filename/MIME type, caption formatting, and replies; no URL or `file_id` upload input. |
| `sendChatAction` | Yes | Telegram action names are accepted and rendered by Imgram clients. |
| `setMessageReaction` | Partial | One of `👍 👎 ❤ 🔥 😁 🤔 👏 🤯 😱 😭 🤩 🤮 👌 🥴 🥱 🤡 🐳 🎉 🥰 🤣` per bot is supported; pass an empty array to clear it. Custom emoji and multiple simultaneous reactions are not supported. |
| `editMessageText` | Partial | Text and the same parse modes/entities as `sendMessage`; no inline-message editing or `reply_markup`. |
| `deleteMessage` | Partial | `message_id` is used; `chat_id` is not currently required or read. |
| `pinChatMessage` | Partial | Silent pin; advanced notification/business parameters are absent. |
| `unpinChatMessage` | Partial | Basic form only. |
| `getUpdates` | Partial | `offset`, `limit`, and `timeout`; no `allowed_updates`. |
| `setWebhook` | Partial | `url` and `secret_token`; no certificates, IP address, connection limits, or update filters. |
| `deleteWebhook` | Partial | No `drop_pending_updates`. |
| `getWebhookInfo` | Partial | Core status fields only. |
| `sendChecklist` | Yes | Imgram extension for native checklists. |
| `toggleChecklist` | Yes | Imgram extension for changing task state. |
| `appendChecklist` | Yes | Imgram extension for adding tasks. |
| `sendAudio`, `sendVoice` | No | Dedicated Bot API audio/voice methods are not exposed yet. |
| `getFile` | No | Bot file download is not exposed yet. |
| `setMyCommands`, `deleteMyCommands`, `getMyCommands` | No | Command menus are not exposed yet. |
| `answerCallbackQuery` | No | Inline keyboards and callback queries are not exposed yet. |

## Chat and update coverage

| Capability | Imgram v1 |
|---|---:|
| Private chats | Yes |
| Basic groups | Yes |
| Channels / supergroups | No |
| Incoming text messages | Yes |
| Incoming text entities | Yes |
| Incoming checklist messages | Yes |
| Checklist completion changes | Yes, as `edited_message` |
| Incoming photo/document metadata | Yes |
| Bot file download | No; `getFile` is not exposed yet |
| Long polling | Yes |
| HTTPS webhook | Yes |

## Connector readiness

| Connector | Can a user paste only an Imgram token today? | Status |
|---|---:|---|
| Raw HTTP client | Yes | Supported; follow [CONNECT.md](CONNECT.md). |
| OpenClaw Telegram channel | Not reliably | Experimental: custom `apiRoot` exists, but startup/runtime methods exceed the Imgram subset. |
| CC Connect Telegram platform | No | Its Telegram adapter currently targets Telegram's API root and uses unsupported media/action/command methods. An Imgram adapter is required. |
| Hermes Agent Telegram gateway | No | Its public configuration documents a Telegram token but no custom Bot API root. An endpoint option or Imgram adapter is required. |

Compatibility is based on the currently published integrations, not on their project names. Recheck this table when either side changes.

When implementing one of these connectors, method compatibility is only half
of the work. Follow [ADAPTER_GUIDE.md](ADAPTER_GUIDE.md) to keep typing,
one-message streaming, final formatting, media routing, and cleanup in the
adapter rather than relying on the language model.
