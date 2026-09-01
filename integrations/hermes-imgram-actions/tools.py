"""Native imGram actions for a Hermes turn running through imGram."""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.parse
import urllib.request
from typing import Any

_DEFAULT_ROOT = "https://bot.premsir.com"
_SCHEMA = {
    "name": "imgram_action",
    "description": (
        "Perform a native imGram operation in the current chat only. Use it for "
        "pins, reactions, checklists, checklist changes, and native articles. "
        "Never claim success unless this tool returns ok=true."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "action": {"type": "string", "enum": [
                "pin", "unpin", "react", "clear_reaction", "send_checklist",
                "toggle_checklist", "append_checklist", "send_article",
            ]},
            "message_id": {"type": "integer", "description": "Target message; omit to target the current user message."},
            "emoji": {"type": "string", "description": "One documented standard reaction emoji."},
            "checklist": {"type": "object", "description": "Checklist: title, tasks, optional permissions."},
            "completed": {"type": "array", "items": {"type": "integer"}},
            "incompleted": {"type": "array", "items": {"type": "integer"}},
            "tasks": {"type": "array", "items": {"type": "object"}},
            "markdown": {"type": "string", "description": "Native article Markdown."},
        },
        "required": ["action"],
    },
}


def _json(value: dict) -> str:
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"))


def _session(name: str) -> str:
    from gateway.session_context import get_session_env

    return str(get_session_env(name, "") or "").strip()


def _token() -> str:
    for name in ("IMGRAM_BOT_TOKEN", "TELEGRAM_BOT_TOKEN"):
        value = os.getenv(name, "").strip()
        if value:
            return value
    try:
        from gateway.config import Platform, load_gateway_config

        config = load_gateway_config().platforms.get(Platform.TELEGRAM)
        return str(getattr(config, "token", "") or "").strip()
    except Exception:
        return ""


def _root() -> str:
    root = os.getenv("IMGRAM_API_ROOT", _DEFAULT_ROOT).strip().rstrip("/")
    parsed = urllib.parse.urlparse(root)
    if parsed.scheme != "https" or not parsed.netloc:
        raise ValueError("IMGRAM_API_ROOT must be an https URL")
    if (parsed.hostname or "").lower() == "api.telegram.org":
        raise ValueError("IMGRAM_API_ROOT must not be api.telegram.org")
    return root


def _chat_id() -> int:
    try:
        return int(_session("HERMES_SESSION_CHAT_ID"))
    except (TypeError, ValueError) as exc:
        raise ValueError("imGram actions require an active imGram chat") from exc


def _message_id(args: dict[str, Any]) -> int:
    try:
        value = int(args.get("message_id") or _session("HERMES_SESSION_MESSAGE_ID"))
    except (TypeError, ValueError) as exc:
        raise ValueError("message_id is required for this action") from exc
    if value <= 0:
        raise ValueError("message_id must be positive")
    return value


def _call(method: str, payload: dict[str, Any]) -> dict[str, Any]:
    token = _token()
    if not token:
        raise ValueError("set TELEGRAM_BOT_TOKEN or IMGRAM_BOT_TOKEN first")
    request = urllib.request.Request(
        f"{_root()}/bot{token}/{method}",
        data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=30) as response:  # configured root
            response_data = json.load(response)
    except urllib.error.HTTPError as exc:
        try:
            response_data = json.load(exc)
        except Exception:
            response_data = {"ok": False, "error_code": exc.code, "description": "HTTP error"}
    if not isinstance(response_data, dict) or not response_data.get("ok"):
        return {"ok": False, "method": method, "error": response_data}
    return {"ok": True, "method": method, "result": response_data.get("result")}


def imgram_action(args: dict, **_: Any) -> str:
    """Run one explicit native imGram action in the current Hermes chat."""
    try:
        if _session("HERMES_SESSION_PLATFORM").lower() not in {"telegram", "imgram"}:
            raise ValueError("imgram_action is available only in an imGram-backed Hermes chat")
        action, chat_id = str(args.get("action") or "").strip(), _chat_id()
        if action in {"pin", "unpin"}:
            return _json(_call("pinChatMessage" if action == "pin" else "unpinChatMessage", {
                "chat_id": chat_id, "message_id": _message_id(args),
            }))
        if action in {"react", "clear_reaction"}:
            emoji = str(args.get("emoji") or "").strip()
            if action == "react" and not emoji:
                raise ValueError("emoji is required for react")
            reaction = [] if action == "clear_reaction" else [{"type": "emoji", "emoji": emoji}]
            return _json(_call("setMessageReaction", {
                "chat_id": chat_id, "message_id": _message_id(args), "reaction": reaction,
            }))
        if action == "send_checklist":
            checklist = args.get("checklist")
            if not isinstance(checklist, dict):
                raise ValueError("checklist object is required")
            return _json(_call("sendChecklist", {"chat_id": chat_id, "checklist": checklist}))
        if action == "toggle_checklist":
            return _json(_call("toggleChecklist", {
                "chat_id": chat_id, "message_id": _message_id(args),
                "completed": args.get("completed") or [], "incompleted": args.get("incompleted") or [],
            }))
        if action == "append_checklist":
            tasks = args.get("tasks")
            if not isinstance(tasks, list) or not tasks:
                raise ValueError("a non-empty tasks array is required")
            return _json(_call("appendChecklist", {
                "chat_id": chat_id, "message_id": _message_id(args), "tasks": tasks,
            }))
        if action == "send_article":
            markdown = str(args.get("markdown") or "").strip()
            if not markdown:
                raise ValueError("markdown is required for send_article")
            return _json(_call("sendRichMessage", {
                "chat_id": chat_id, "rich_message": {"markdown": markdown},
            }))
        raise ValueError("unknown imGram action")
    except Exception as exc:
        return _json({"ok": False, "error": str(exc)})


def register_tools(ctx) -> None:
    ctx.register_tool(
        name="imgram_action", toolset="imgram", schema=_SCHEMA,
        handler=imgram_action, description=_SCHEMA["description"], emoji="✈️",
    )
