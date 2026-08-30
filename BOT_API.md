# Imgram Bot API v1

Updated: 2026-08-30

The Imgram Bot API is an experimental, Telegram-style compatible subset for Imgram bots. Only the methods and fields documented here are supported.

## Making requests

The production endpoint is:

```text
https://bot.premsir.com/bot<TOKEN>/<METHOD>
```

Method names are case-insensitive. Read-only calls may use `GET`; all calls may use `POST`. POST parameters may be sent as JSON or `application/x-www-form-urlencoded` data. Media uploads use `multipart/form-data`. JSON request bodies are limited to 2 MiB; uploaded files are limited to 50 MiB.

Do not send an Imgram token to `api.telegram.org`. Imgram and Telegram tokens are not interchangeable.

Successful response:

```json
{
  "ok": true,
  "result": {}
}
```

Error response:

```json
{
  "ok": false,
  "error_code": 400,
  "description": "Bad Request: ..."
}
```

The HTTP status code matches `error_code` for public API errors. Common codes are `400` for invalid parameters, `401` for an invalid token, `404` for an unknown method, and `409` for polling while a webhook is active.

## Core types

### User

| Field | Type | Description |
|---|---|---|
| `id` | Integer | Imgram user ID. |
| `is_bot` | Boolean | Whether this user is a bot. |
| `first_name` | String | Display name. |
| `last_name` | String | Last name; may be empty. |
| `username` | String | Username; may be empty for users. |

### Chat

| Field | Type | Description |
|---|---|---|
| `id` | Integer | Positive for a private chat and negative for a basic group. |
| `type` | String | `private` or `group`. |
| `first_name` | String | Private chats only. |
| `last_name` | String | Private chats only. |
| `username` | String | Private chats only. |
| `title` | String | Groups only. |

### Message

| Field | Type | Description |
|---|---|---|
| `message_id` | Integer | Message ID. |
| `date` | Integer | Unix timestamp. |
| `from` | User | Sender. |
| `chat` | Chat | Conversation containing the message. |
| `text` | String | Present on text messages. |
| `entities` | MessageEntity[] | Optional structured formatting for `text`. Offsets and lengths use UTF-16 code units. |
| `caption` | String | Present when a media message has a caption. |
| `caption_entities` | MessageEntity[] | Optional structured formatting for `caption`. |
| `photo` | PhotoSize[] | Present on photo messages. |
| `document` | Document | Present on document messages. |
| `checklist` | Checklist | Present on checklist messages. |

### MessageEntity

Each entity has `type`, `offset`, and `length`. Imgram currently supports `mention`, `hashtag`, `cashtag`, `bot_command`, `url`, `email`, `phone_number`, `bold`, `italic`, `underline`, `strikethrough`, `spoiler`, `code`, `pre`, `text_link`, `text_mention`, `blockquote`, `expandable_blockquote`, and `custom_emoji`.

Depending on the type, an entity can additionally contain `url`, `language`, `custom_emoji_id`, or `user`. Like Telegram, offsets and lengths count UTF-16 code units, so most emoji count as two.

### Checklist

| Field | Type | Description |
|---|---|---|
| `title` | String | Checklist title. |
| `tasks` | ChecklistTask[] | One to 30 tasks. |
| `others_can_append` | Boolean | Whether chat participants may add tasks. |
| `others_can_complete` | Boolean | Whether chat participants may change completion state. |

Each task contains `id`, `text`, and `completed`. A completed task additionally contains `completed_by_user_id` and `completion_date`.

### Update

```json
{
  "update_id": 42,
  "message": {
    "message_id": 8,
    "date": 1787990400,
    "from": {"id": 123456, "is_bot": false, "first_name": "Lin"},
    "chat": {"id": 123456, "type": "private", "first_name": "Lin"},
    "text": "hello"
  }
}
```

An update contains either `message` for a new incoming message or `edited_message` for a change. Checklist completion changes are delivered as `edited_message`, including changes to a checklist originally sent by the bot.

## Supported methods

| Method | Required parameters | Optional parameters | Returns |
|---|---|---|---|
| `getMe` | — | — | User |
| `sendMessage` | `chat_id`, `text` | `parse_mode`, `entities`, `reply_to_message_id` | Message |
| `sendPhoto` | `chat_id`, multipart `photo` | `caption`, `parse_mode`, `caption_entities`, `reply_to_message_id` | Message |
| `sendDocument` | `chat_id`, multipart `document` | `caption`, `parse_mode`, `caption_entities`, `reply_to_message_id` | Message |
| `sendChatAction` | `chat_id`, `action` | — | `true` |
| `setMessageReaction` | `chat_id`, `message_id` | `reaction`, `is_big` | `true` |
| `sendChecklist` | `chat_id`, `checklist` | `reply_to_message_id` | Message |
| `editMessageText` | `chat_id`, `message_id`, `text` | `parse_mode`, `entities` | Message |
| `deleteMessage` | `message_id` | — | `true` |
| `pinChatMessage` | `chat_id`, `message_id` | — | `true` |
| `unpinChatMessage` | `chat_id`, `message_id` | — | `true` |
| `toggleChecklist` | `chat_id`, `message_id` | `completed`, `incompleted` | Message |
| `appendChecklist` | `chat_id`, `message_id`, `tasks` | — | Message |
| `getUpdates` | — | `offset`, `limit`, `timeout` | Update[] |
| `setWebhook` | `url` | `secret_token` | `true` |
| `deleteWebhook` | — | — | `true` |
| `getWebhookInfo` | — | — | WebhookInfo |

### getMe

Tests a token and returns the bot account.

```bash
curl "$IMGRAM_API_ROOT/bot$IMGRAM_BOT_TOKEN/getMe"
```

### sendMessage

Sends text with optional Telegram-style formatting. `parse_mode` accepts `HTML`, `MarkdownV2`, or legacy `Markdown`. Alternatively, pass `entities` as an array in JSON requests or as a JSON-encoded array in form requests. Do not specify both `parse_mode` and `entities`.

When neither `parse_mode` nor `entities` is supplied, Imgram tolerantly recognizes the common Agent Markdown forms `**bold**`, `~~strikethrough~~`, `||spoiler||`, inline/fenced code, and inline links. Unmatched markers remain literal. This compatibility fallback exists for Agent frameworks that emit CommonMark but omit Telegram's `parse_mode`; explicit formatting is still preferred.

Bare `@usernames` are recognized as mention entities automatically, including when they follow Chinese text or punctuation. If a mention entity is supplied explicitly, Imgram keeps a single entity for that range.

HTML example with bold text and a spoiler:

```bash
curl -X POST "$IMGRAM_API_ROOT/bot$IMGRAM_BOT_TOKEN/sendMessage" \
  -H 'Content-Type: application/json' \
  -d '{
    "chat_id": 123456,
    "text": "<b>Result</b>: <tg-spoiler>hidden detail</tg-spoiler>",
    "parse_mode": "HTML"
  }'
```

Supported HTML tags include `b`, `strong`, `i`, `em`, `u`, `ins`, `s`, `strike`, `del`, `span class="tg-spoiler"`, `tg-spoiler`, `a`, `code`, `pre`, `blockquote`, and `tg-emoji`. MarkdownV2 supports bold, italic, underline, strikethrough, spoilers, inline code, fenced code, inline links, custom emoji, and block quotations.

```bash
curl -X POST "$IMGRAM_API_ROOT/bot$IMGRAM_BOT_TOKEN/sendMessage" \
  --data-urlencode 'chat_id=-120031' \
  --data-urlencode 'reply_to_message_id=11' \
  --data-urlencode 'text=Received'
```

### sendPhoto and sendDocument

Upload a photo or ordinary file using the same multipart field names as Telegram. Multipart uploads and `attach://<field>` references are supported; remote HTTP URLs and previously returned `file_id` values are not yet accepted as upload input. Files are limited to 50 MiB.

```bash
curl -X POST "$IMGRAM_API_ROOT/bot$IMGRAM_BOT_TOKEN/sendDocument" \
  -F 'chat_id=123456' \
  -F 'document=@report.csv;type=text/csv' \
  -F 'caption=<b>Daily report</b>' \
  -F 'parse_mode=HTML'
```

Use `photo=@image.png` with `sendPhoto`. Captions accept `parse_mode` or `caption_entities` and use the same formatting behavior as `sendMessage`.

### sendChatAction

Publishes a transient Telegram-style status in the chat. For example, call `typing` before an Agent starts a slow response and refresh it periodically while generation continues.

```bash
curl -X POST "$IMGRAM_API_ROOT/bot$IMGRAM_BOT_TOKEN/sendChatAction" \
  --data-urlencode 'chat_id=123456' \
  --data-urlencode 'action=typing'
```

Supported actions are `typing`, `upload_photo`, `record_video`, `upload_video`, `record_voice`, `upload_voice`, `upload_document`, `choose_sticker`, `find_location`, `record_video_note`, and `upload_video_note`.

### setMessageReaction

Adds or replaces the bot's reaction using Telegram's `ReactionTypeEmoji` JSON shape. Imgram v1 accepts one of `👍 👎 ❤ 🔥 😁 🤔`. Both `❤` and `❤️` are accepted. Send an empty `reaction` array, or omit it, to clear the bot's current reaction.

```bash
curl -X POST "$IMGRAM_API_ROOT/bot$IMGRAM_BOT_TOKEN/setMessageReaction" \
  -H 'Content-Type: application/json' \
  -d '{
    "chat_id": 123456,
    "message_id": 42,
    "reaction": [{"type": "emoji", "emoji": "🔥"}]
  }'
```

Custom emoji and multiple simultaneous reactions are not supported in v1. `is_big` is accepted. Imgram's Android client bundles and renders the corresponding animated reaction assets without connecting to Telegram's cloud.

### sendChecklist

Sends an Imgram native checklist. `checklist` accepts an object in JSON requests or a JSON-encoded string in form requests.

```bash
curl -X POST "$IMGRAM_API_ROOT/bot$IMGRAM_BOT_TOKEN/sendChecklist" \
  -H 'Content-Type: application/json' \
  -d '{
    "chat_id": -120031,
    "checklist": {
      "title": "Weekend plan",
      "tasks": [
        {"id": 1, "text": "Choose a place"},
        {"id": 2, "text": "Prepare supplies"},
        {"id": 3, "text": "Confirm departure time"}
      ],
      "others_can_append": true,
      "others_can_complete": true
    }
  }'
```

The title must not be empty. A checklist must contain 1–30 non-empty tasks. Positive task IDs must be unique within the checklist. When omitted, IDs are assigned from 1 in list order. Both permission fields default to `true`.

The checklist fields may also be supplied at the top level, but the nested `checklist` object is preferred.

### editMessageText

Edits a text message using `chat_id`, `message_id`, and a non-empty `text`. It accepts the same `parse_mode` or `entities` formatting parameters as `sendMessage`. This method does not edit checklist contents.

### deleteMessage

Deletes a message using `message_id`. Unlike Telegram's method signature, Imgram v1 does not currently read `chat_id` for deletion.

### pinChatMessage and unpinChatMessage

Pins or unpins the specified message. Pinning is silent in the current implementation.

### toggleChecklist

Marks task IDs complete or incomplete and returns the resulting Message. `completed` and `incompleted` are arrays of positive task IDs.

```bash
curl -X POST "$IMGRAM_API_ROOT/bot$IMGRAM_BOT_TOKEN/toggleChecklist" \
  -H 'Content-Type: application/json' \
  -d '{
    "chat_id": -120031,
    "message_id": 14,
    "completed": [1, 2],
    "incompleted": [3]
  }'
```

### appendChecklist

Appends one to 30 tasks to an existing checklist. `tasks` accepts the same task array used by `sendChecklist`.

```bash
curl -X POST "$IMGRAM_API_ROOT/bot$IMGRAM_BOT_TOKEN/appendChecklist" \
  -H 'Content-Type: application/json' \
  -d '{
    "chat_id": -120031,
    "message_id": 14,
    "tasks": [{"id": 4, "text": "Book tickets"}]
  }'
```

### getUpdates

Uses long polling to receive Update objects.

```bash
curl "$IMGRAM_API_ROOT/bot$IMGRAM_BOT_TOKEN/getUpdates?offset=1&limit=100&timeout=30"
```

- `limit` defaults to 100 and is capped at 100.
- `timeout` is measured in seconds and capped at 30.
- After processing update `N`, request `offset=N+1` to confirm older updates and avoid receiving them again.
- `getUpdates` returns HTTP 409 while a webhook is configured.
- `allowed_updates` is not currently supported.

## Webhooks

Set an HTTPS webhook:

```bash
curl -X POST "$IMGRAM_API_ROOT/bot$IMGRAM_BOT_TOKEN/setWebhook" \
  --data-urlencode 'url=https://agent.example/imgram-update' \
  --data-urlencode 'secret_token=replace-with-a-separate-random-secret'
```

Imgram POSTs one JSON Update at a time. When `secret_token` is set, requests include:

```text
X-Telegram-Bot-Api-Secret-Token: <secret_token>
```

Respond with any HTTP `2xx` status to acknowledge the update. Failed deliveries remain pending and are retried by the current worker. Production accepts HTTPS webhook URLs only.

Inspect or remove the webhook:

```bash
curl "$IMGRAM_API_ROOT/bot$IMGRAM_BOT_TOKEN/getWebhookInfo"
curl -X POST "$IMGRAM_API_ROOT/bot$IMGRAM_BOT_TOKEN/deleteWebhook"
```

`getWebhookInfo` returns `url`, `has_custom_certificate`, `pending_update_count`, `last_error_date`, and `last_error_message`.

## Finding chat IDs

1. Open the bot in Imgram and send it a message, or add it to a group and send a message there.
2. Call `getUpdates`.
3. Read `message.chat.id` from the update.

Private chat IDs are positive. Basic group IDs are negative.

## Current boundary

Notable unsupported Telegram Bot API features include bot-side file downloads, inline keyboards and callback queries, bot command menus, channels, and supergroups. See [COMPATIBILITY.md](COMPATIBILITY.md) before using a Telegram library or connector unchanged.
