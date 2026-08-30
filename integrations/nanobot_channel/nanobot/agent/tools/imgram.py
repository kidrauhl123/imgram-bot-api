"""Typed imGram actions that return real Bot API results to the Agent."""

from __future__ import annotations

import json
from typing import Any
from urllib.parse import urlparse

import httpx

from nanobot.agent.tools.base import Tool
from nanobot.agent.tools.context import current_request_context
from nanobot.config.loader import load_config, resolve_config_env_vars


def _imgram_config() -> dict[str, Any]:
    config = resolve_config_env_vars(load_config())
    section = getattr(config.channels, "imgram", None)
    if hasattr(section, "model_dump"):
        section = section.model_dump(mode="json", by_alias=True)
    if not isinstance(section, dict):
        return {}
    return section


class ImgramActionTool(Tool):
    """Perform observable imGram message actions in the active conversation."""

    @classmethod
    def enabled(cls, _ctx) -> bool:
        try:
            return bool(_imgram_config().get("enabled"))
        except Exception:
            return False

    @property
    def name(self) -> str:
        return "imgram_action"

    @property
    def description(self) -> str:
        return (
            "Perform a real imGram message operation and verify the Bot API result. "
            "Use this instead of claiming that a message was pinned, edited, reacted to, "
            "deleted, or that a native checklist/article was sent. Defaults to the active "
            "imGram chat and, for message operations, the triggering message."
        )

    @property
    def parameters(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": [
                        "pin", "unpin", "react", "edit", "delete",
                        "send_checklist", "toggle_checklist", "append_checklist",
                        "send_article",
                    ],
                    "description": "The imGram operation to perform.",
                },
                "chat_id": {"type": ["string", "null"], "description": "Optional target chat ID."},
                "message_id": {"type": ["integer", "null"], "description": "Target message ID."},
                "text": {"type": ["string", "null"], "description": "New text for edit."},
                "emoji": {"type": ["string", "null"], "description": "Reaction emoji; empty removes it."},
                "title": {"type": ["string", "null"], "description": "Checklist title."},
                "tasks": {
                    "type": ["array", "null"],
                    "items": {
                        "oneOf": [
                            {"type": "string"},
                            {
                                "type": "object",
                                "properties": {
                                    "id": {"type": "integer"},
                                    "text": {"type": "string"},
                                },
                                "required": ["text"],
                            },
                        ]
                    },
                    "description": "Checklist task strings or {id,text} objects.",
                },
                "completed": {"type": ["array", "null"], "items": {"type": "integer"}},
                "incompleted": {"type": ["array", "null"], "items": {"type": "integer"}},
                "others_can_append": {"type": ["boolean", "null"]},
                "others_can_complete": {"type": ["boolean", "null"]},
                "markdown": {"type": ["string", "null"], "description": "Native article Markdown."},
            },
            "required": ["action"],
            "additionalProperties": False,
        }

    async def execute(
        self,
        action: str,
        chat_id: str | None = None,
        message_id: int | None = None,
        text: str | None = None,
        emoji: str | None = None,
        title: str | None = None,
        tasks: list[Any] | None = None,
        completed: list[int] | None = None,
        incompleted: list[int] | None = None,
        others_can_append: bool | None = None,
        others_can_complete: bool | None = None,
        markdown: str | None = None,
    ) -> str:
        request = current_request_context()
        if request is None or request.channel != "imgram":
            return self.error("imgram_action is only available during an imGram turn")

        config = _imgram_config()
        token = str(config.get("token") or "").strip()
        api_root = str(config.get("apiRoot") or config.get("api_root") or "").strip().rstrip("/")
        parsed = urlparse(api_root)
        if not token or parsed.scheme not in {"http", "https"} or not parsed.netloc:
            return self.error("imGram token or apiRoot is not configured")
        if parsed.hostname in {"api.telegram.org", "telegram.org"}:
            return self.error("refusing to send an imGram token to Telegram")

        target_chat = chat_id or request.chat_id
        target_message = message_id
        if target_message is None and request.message_id:
            try:
                target_message = int(request.message_id)
            except ValueError:
                target_message = None

        method = ""
        payload: dict[str, Any] = {"chat_id": target_chat}
        if action in {"pin", "unpin", "react", "edit", "delete", "toggle_checklist", "append_checklist"}:
            if not target_message:
                return self.error(f"message_id is required for {action}")
            payload["message_id"] = target_message

        if action == "pin":
            method = "pinChatMessage"
        elif action == "unpin":
            method = "unpinChatMessage"
        elif action == "react":
            method = "setMessageReaction"
            payload["reaction"] = [] if not emoji else [{"type": "emoji", "emoji": emoji}]
        elif action == "edit":
            if not text:
                return self.error("text is required for edit")
            method = "editMessageText"
            payload["text"] = text
        elif action == "delete":
            method = "deleteMessage"
        elif action == "send_checklist":
            if not title or not tasks:
                return self.error("title and tasks are required for send_checklist")
            method = "sendChecklist"
            payload["checklist"] = {
                "title": title,
                "tasks": tasks,
                "others_can_append": bool(others_can_append),
                "others_can_complete": True if others_can_complete is None else others_can_complete,
            }
        elif action == "toggle_checklist":
            method = "toggleChecklist"
            payload["completed"] = completed or []
            payload["incompleted"] = incompleted or []
        elif action == "append_checklist":
            if not tasks:
                return self.error("tasks are required for append_checklist")
            method = "appendChecklist"
            payload["tasks"] = tasks
        elif action == "send_article":
            if not markdown:
                return self.error("markdown is required for send_article")
            method = "sendRichMessage"
            payload["rich_message"] = {"markdown": markdown}
        else:
            return self.error(f"unsupported imGram action: {action}")

        url = f"{api_root}/bot{token}/{method}"
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(url, json=payload)
            data = response.json()
        except Exception as exc:
            return self.error(f"imGram Bot API request failed: {exc}")
        if response.status_code >= 400 or not data.get("ok"):
            description = data.get("description") if isinstance(data, dict) else None
            return self.error(description or f"imGram Bot API returned HTTP {response.status_code}")

        result = data.get("result")
        if isinstance(result, dict) and result.get("message_id") is not None:
            return json.dumps(
                {"ok": True, "action": action, "message_id": result["message_id"]},
                ensure_ascii=False,
            )
        return json.dumps({"ok": True, "action": action, "result": result}, ensure_ascii=False)
