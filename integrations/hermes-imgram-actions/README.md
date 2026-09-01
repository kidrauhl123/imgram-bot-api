# Hermes imGram actions

This optional plugin supplies the native operations that are not ordinary
Hermes text replies: pin/unpin, reactions, checklists, checklist changes, and
articles. The normal Hermes Telegram adapter still owns message receiving,
typing, streaming, formatting, commands, and media.

Install it as a Hermes user plugin:

```bash
mkdir -p ~/.hermes/plugins
cp -R /path/to/imgram-bot-api/integrations/hermes-imgram-actions \
  ~/.hermes/plugins/imgram-actions
hermes plugins doctor ~/.hermes/plugins/imgram-actions --ci
hermes tools enable imgram --platform telegram
```

Configure Hermes' Telegram platform with the imGram `base_url` and
`base_file_url` from [`../hermes.md`](../hermes.md). The plugin reads the token
from `TELEGRAM_BOT_TOKEN` or Hermes' Telegram configuration; an
`IMGRAM_BOT_TOKEN` environment variable may override it. It defaults to
`https://bot.premsir.com` and refuses `api.telegram.org`.

The Agent sees one `imgram_action` tool. It cannot choose another chat ID: the
tool derives the current chat and triggering message from Hermes' task-local
session context. An action is successful only when its returned JSON has
`ok:true`.
