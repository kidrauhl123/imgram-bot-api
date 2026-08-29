# Connect an AI agent to Imgram

This page is the canonical starting point for humans and AI coding agents.

## Connection contract

You need two values:

```text
API root: https://bot.premsir.com
Bot token: supplied by the Imgram user
```

Construct method URLs as:

```text
<API root>/bot<token>/<method>
```

The API root must not include `/bot<TOKEN>`. Never send an Imgram token to Telegram or any unrelated host.

## Instructions for an AI agent

When a user asks you to connect their Imgram bot:

1. Treat the token as a secret. Do not quote it back, commit it, print it in logs, or put it in a public command example.
2. Read [COMPATIBILITY.md](COMPATIBILITY.md) before choosing a Telegram SDK or an existing connector.
3. Verify credentials with `getMe` against the Imgram API root.
4. Prefer raw HTTP for v1 unless the selected connector supports both a custom API root and the methods Imgram implements.
5. Choose exactly one update transport: `getUpdates` or webhook.
6. Persist the last successfully processed `update_id`; acknowledge it by using `offset=update_id+1` on the next poll.
7. Make handlers idempotent because an update can be delivered more than once around failures.

Do not silently fall back to `api.telegram.org`. A failure against Imgram should remain visible to the user.

## Minimal polling loop

The following Python example uses only the standard library:

```python
import json
import os
import urllib.parse
import urllib.request

root = os.environ.get("IMGRAM_API_ROOT", "https://bot.premsir.com").rstrip("/")
token = os.environ["IMGRAM_BOT_TOKEN"]
base = f"{root}/bot{token}"
offset = 0

def call(method, params=None):
    body = urllib.parse.urlencode(params or {}).encode()
    request = urllib.request.Request(f"{base}/{method}", data=body, method="POST")
    with urllib.request.urlopen(request, timeout=35) as response:
        payload = json.load(response)
    if not payload.get("ok"):
        raise RuntimeError(payload.get("description", "Imgram API error"))
    return payload["result"]

print(call("getMe"))

while True:
    for update in call("getUpdates", {"offset": offset, "timeout": 30}):
        message = update.get("message") or update.get("edited_message")
        if message and message.get("text"):
            call("sendMessage", {
                "chat_id": message["chat"]["id"],
                "text": f"You said: {message['text']}",
            })
        offset = update["update_id"] + 1
```

For production, persist `offset` outside process memory, add exponential backoff, handle HTTP errors, and shut down cleanly.

## Existing agent frameworks

- [OpenClaw](integrations/openclaw.md): closest path because it exposes a custom Telegram API root, but currently experimental with Imgram.
- [CC Connect](integrations/cc-connect.md): requires a dedicated Imgram adapter or an upstream endpoint option.
- [Hermes Agent](integrations/hermes.md): requires a custom endpoint option or adapter.

These short guides document connector-specific facts. The Bot API reference remains the source of truth; a separate guide is not needed for every agent framework that can make ordinary HTTP requests.
