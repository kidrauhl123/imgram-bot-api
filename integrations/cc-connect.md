# CC Connect

Status: **a small maintained imGram platform patch is supplied.**

CC Connect's Telegram channel already contains the UX we want to inherit:
long polling, group mention routing, command registration, typing refresh,
streamed edits, retry behaviour, and media routing. Its Go Telegram SDK also
supports a custom server URL. Upstream CC Connect simply does not expose that
URL or an `imgram` platform name yet.

Do not put an imGram token in unchanged `type = "telegram"`: its default
endpoint is Telegram. Apply the small patch below instead. It registers an
isolated `imgram` platform, defaults it to `https://bot.premsir.com`, keeps
imGram sessions separate (`imgram:<chat>:…`), uses the same host for file
downloads, and rejects an accidental `api.telegram.org` override.

## Install

The patch is pinned to CC Connect commit
`b39c11f42cb7b507677f9b3d044aca18139231de`. From that checkout:

```bash
git apply /path/to/imgram-bot-api/integrations/cc-connect/0001-imgram-platform.patch
go test ./platform/telegram
go build ./cmd/cc-connect
```

The patch is deliberately limited to the existing Telegram platform; it does
not fork or rewrite its chat lifecycle. Re-audit it when CC Connect changes
that platform or upgrades `github.com/go-telegram/bot`.

## Configuration

```toml
[[projects.platforms]]
type = "imgram"

[projects.platforms.options]
token = "${IMGRAM_BOT_TOKEN}"
# Optional for a staging/self-hosted imGram service. Production already
# defaults to https://bot.premsir.com.
# api_base = "https://bot.premsir.com"

# Existing Telegram-channel behaviours, inherited unchanged.
progress_style = "compact" # default: one message is edited while streaming
group_reply_all = false
enable_reactions = true
```

`setMyCommands` is retained, so CC Connect command registration powers
imGram's command menu. The existing media path calls `getFile` and derives its
download URL from the configured root, so incoming photos/documents and
outgoing photo/document/voice/audio delivery stay on imGram.

## v1 capability boundary

The inherited basic transport supports the documented Telegram-style subset:
text/formatting, streaming edits, typing, reactions, command menu, replies,
polling, and supported media. imGram v1 does not provide inline keyboards or
callback queries, so do not enable CC Connect flows that require buttons.

Native imGram checklists and articles are separate typed Agent operations, not
ordinary CC Connect reply messages. Give the Agent the
[adapter guide](../ADAPTER_GUIDE.md) and [Bot API reference](../BOT_API.md)
when adding those tools; a tool must call `sendChecklist`/`sendRichMessage` and
check `ok=true`, never merely answer that it completed an action.

Reference: [CC Connect Telegram platform](https://github.com/chenhg5/cc-connect/tree/main/platform/telegram).
