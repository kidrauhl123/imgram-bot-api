# Compatibility matrix

Imgram v1 deliberately implements a useful Telegram-style subset. A matching method name does not imply support for every Telegram parameter or response field.

## Methods

| Telegram-style method | Imgram v1 | Important differences |
|---|---:|---|
| `getMe` | Yes | Core User fields only. |
| `sendMessage` | Partial | Text, replies, `HTML`/`MarkdownV2`/`Markdown` parse modes, and explicit entities; no link-preview options or `reply_markup`. |
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
| `sendPhoto`, `sendDocument`, `sendAudio`, `sendVoice` | No | User-to-user media exists in the app; Bot API media methods do not yet exist. |
| `getFile` | No | Bot file download is not exposed yet. |
| `sendChatAction` | No | Typing/upload status is not exposed yet. |
| `setMyCommands`, `deleteMyCommands`, `getMyCommands` | No | Command menus are not exposed yet. |
| `answerCallbackQuery` | No | Inline keyboards and callback queries are not exposed yet. |
| `setMessageReaction` | No | Bot reactions are not exposed yet. |

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
| Incoming media metadata and files | No public Bot API contract yet |
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
