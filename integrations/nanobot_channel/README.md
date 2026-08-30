# nanobot imGram channel overlay

This overlay targets `nanobot-ai==0.3.0` and keeps the official Telegram
runtime as its superclass.

Install it with the Python executable from the nanobot environment:

```bash
/path/to/nanobot/venv/bin/python install.py
```

Then configure `channels.imgram` as documented in
[`../nanobot.md`](../nanobot.md) and restart the gateway.

The overlay also handles Telegram-compatible `checklist_tasks_done` service
messages. It forwards the actor, changed task IDs and titles, and the complete
resulting checklist state into the Agent session as both readable context and
structured inbound metadata.

For group messages, the overlay projects the authenticated sender's display
name, user ID, optional username, and first/last names into nanobot's trusted
model-only runtime context. The visible chat text is left unchanged, while the
Agent can reliably distinguish and address group participants even when an
imGram account has no public username.

Run the regression test from an environment containing nanobot and pytest:

```bash
python -m pytest tests/test_imgram_runtime.py
```
