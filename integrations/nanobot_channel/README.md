# nanobot imGram channel overlay

This overlay targets `nanobot-ai==0.3.0` and keeps the official Telegram
runtime as its superclass.

Install it with the Python executable from the nanobot environment:

```bash
/path/to/nanobot/venv/bin/python install.py
```

Then configure `channels.imgram` as documented in
[`../nanobot.md`](../nanobot.md) and restart the gateway.

Run the regression test from an environment containing nanobot and pytest:

```bash
python -m pytest tests/test_imgram_runtime.py
```
