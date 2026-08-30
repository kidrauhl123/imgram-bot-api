# Compatibility matrix

imGram v1 deliberately implements a useful Telegram-style subset. A matching method name does not imply support for every Telegram parameter or response field.

## Methods

| Telegram-style method | imGram v1 | Important differences |
|---|---:|---|
| `getMe` | Yes | Core User fields only. |
| `sendMessage` | Partial | Text, replies, automatic `@mentions`, `HTML`/`MarkdownV2`/`Markdown` parse modes, explicit entities, and a tolerant CommonMark fallback for Agent output; no link-preview options or `reply_markup`. |
| `sendPhoto` | Partial | Multipart upload up to 50 MiB, caption formatting, and replies; no URL or `file_id` upload input. |
| `sendDocument` | Partial | Multipart upload up to 50 MiB, filename/MIME type, caption formatting, and replies; no URL or `file_id` upload input. |
| `sendVideo` | Partial | Multipart upload, caption formatting, replies, dimensions/duration, and streaming flag; no URL or `file_id` upload input. |
| `sendVoice` | Partial | Multipart upload, caption formatting, replies, and duration; no URL or `file_id` upload input. |
| `sendAudio` | Partial | Multipart upload, caption formatting, replies, duration, title, and performer; no URL or `file_id` upload input. |
| `sendChatAction` | Yes | Telegram action names are accepted and rendered by imGram clients. |
| `setMessageReaction` | Partial | One of the 73 standard emoji listed in [BOT_API.md](BOT_API.md#setmessagereaction) per bot is supported; pass an empty array to clear it. Custom emoji and multiple simultaneous reactions are not supported. |
| `editMessageText` | Partial | Text and the same parse modes/entities as `sendMessage`; Bot streaming edits hide the client “edited” marker; no inline-message editing or `reply_markup`. |
| `deleteMessage` | Partial | `message_id` is used; `chat_id` is not currently required or read. |
| `pinChatMessage` | Partial | Silent pin; advanced notification/business parameters are absent. |
| `unpinChatMessage` | Partial | Basic form only. |
| `getUpdates` | Partial | `offset`, `limit`, and `timeout`; no `allowed_updates`. |
| `setWebhook` | Partial | `url` and `secret_token`; no certificates, IP address, connection limits, or update filters. |
| `deleteWebhook` | Partial | No `drop_pending_updates`. |
| `getWebhookInfo` | Partial | Core status fields only. |
| `sendChecklist` | Yes | imGram extension for native checklists. |
| `sendRichMessage`, `sendArticle` | Yes | imGram native article from structural Markdown blocks. |
| `toggleChecklist` | Yes | imGram extension for changing task state. |
| `appendChecklist` | Yes | imGram extension for adding tasks. |
| `getFile` | Yes | Returns an authenticated `file_path`; download it through `/file/bot<TOKEN>/<file_path>`. |
| `setMyCommands`, `deleteMyCommands`, `getMyCommands` | Partial | Default scope is supported and rendered by imGram clients; language-specific and chat-specific scopes are not yet supported. |
| `answerCallbackQuery` | No | Inline keyboards and callback queries are not exposed yet. |

## Chat and update coverage

| Capability | imGram v1 |
|---|---:|
| Private chats | Yes |
| Basic groups | Yes |
| Channels / supergroups | No |
| Incoming text messages | Yes |
| Incoming text entities | Yes |
| Incoming checklist messages | Yes |
| Checklist completion changes | Yes, as `edited_message` |
| Incoming photo/video/video-note/animation/voice/audio/document metadata | Yes |
| Bot file download | Yes; Telegram-style `getFile` plus authenticated file download |
| Long polling | Yes |
| HTTPS webhook | Yes |

## Connector readiness

| Connector | Can a user paste only an imGram token today? | Status |
|---|---:|---|
| Raw HTTP client | Yes | Supported; follow [CONNECT.md](CONNECT.md). |
| OpenClaw Telegram channel | Not reliably | Experimental: custom `apiRoot` exists, but optional runtime methods can still exceed the imGram subset. |
| CC Connect Telegram platform | No | Its Telegram adapter currently targets Telegram's API root and can use unsupported callbacks and additional media methods. An imGram adapter is required. |
| Hermes Agent Telegram gateway | No | Its public configuration documents a Telegram token but no custom Bot API root. An endpoint option or imGram adapter is required. |
| nanobot imGram channel | Yes | Versioned v0.3.0 overlay inherits the official Telegram runtime, isolates the API/file roots, and adds typed pin/checklist/article actions. |

Compatibility is based on the currently published integrations, not on their project names. Recheck this table when either side changes. The product goal is 100% compatibility with the Telegram capabilities actually used by the official imGram adapters for OpenClaw, CC Connect, Hermes, and nanobot—not an untested claim that every Telegram Bot API method already exists.

When implementing one of these connectors, method compatibility is only half
of the work. Follow [ADAPTER_GUIDE.md](ADAPTER_GUIDE.md) to keep typing,
one-message streaming, final formatting, media routing, and cleanup in the
adapter rather than relying on the language model.
