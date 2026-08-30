"""Regression seams for the official-runtime imGram overlay."""

import asyncio
from types import SimpleNamespace

import pytest

from nanobot.channels.imgram.runtime import (
    ImgramChannel,
    ImgramConfig,
    _checklist_tasks_done_payload,
)
from nanobot.channels.telegram.runtime import TelegramChannel


def test_imgram_inherits_official_telegram_runtime():
    assert issubclass(ImgramChannel, TelegramChannel)
    assert ImgramChannel.send is TelegramChannel.send
    assert ImgramChannel.send_delta is TelegramChannel.send_delta
    assert ImgramChannel._process_message_update is not TelegramChannel._process_message_update


def test_api_root_is_imgram_and_never_telegram():
    config = ImgramConfig(token="test")
    assert config.api_root == "https://bot.premsir.com"
    with pytest.raises(ValueError):
        ImgramConfig(token="test", api_root="https://api.telegram.org")


def test_sessions_are_isolated_from_telegram():
    class Message:
        chat_id = 42
        message_thread_id = 9

    assert ImgramChannel._derive_topic_session_key(Message()) == "imgram:42:topic:9"
    assert ImgramChannel._queue_key_for_message(Message()) == "imgram:42:topic:9"


def test_checklist_status_event_names_actor_changed_tasks_and_current_state():
    actor = SimpleNamespace(id=42, first_name="老八", last_name=None, username="laoba")
    task_actor = SimpleNamespace(id=42, first_name="老八", last_name=None, username="laoba")
    tasks = [
        SimpleNamespace(id=1, text="整理桌面", completed_by_user=task_actor, completion_date=object()),
        SimpleNamespace(id=2, text="回复重要消息", completed_by_user=None, completion_date=None),
    ]
    checklist_message = SimpleNamespace(
        message_id=143,
        checklist=SimpleNamespace(title="今日简单核对清单", tasks=tasks),
    )
    message = SimpleNamespace(
        from_user=actor,
        checklist_tasks_done=SimpleNamespace(
            checklist_message=checklist_message,
            marked_as_done_task_ids=(1,),
            marked_as_not_done_task_ids=(2,),
        ),
    )

    content, metadata = _checklist_tasks_done_payload(message)

    assert "老八" in content
    assert "user_id=42" in content
    assert "Marked completed: [1] 整理桌面" in content
    assert "Marked not completed: [2] 回复重要消息" in content
    assert "[x] [1] 整理桌面" in content
    assert "[ ] [2] 回复重要消息" in content
    assert metadata == {
        "checklist_message_id": 143,
        "marked_as_done_task_ids": [1],
        "marked_as_not_done_task_ids": [2],
    }


def test_checklist_status_event_is_published_to_agent_bus():
    class Bus:
        def __init__(self):
            self.inbound = []

        async def publish_inbound(self, message):
            self.inbound.append(message)

    actor = SimpleNamespace(id=42, first_name="老八", last_name=None, username="laoba")
    task = SimpleNamespace(
        id=1,
        text="整理桌面",
        completed_by_user=actor,
        completed_by_chat=None,
        completion_date=object(),
    )
    checklist_message = SimpleNamespace(
        message_id=143,
        checklist=SimpleNamespace(title="今日简单核对清单", tasks=[task]),
    )
    message = SimpleNamespace(
        message_id=144,
        message_thread_id=None,
        chat_id=42,
        chat=SimpleNamespace(type="private", is_forum=False),
        from_user=actor,
        reply_to_message=checklist_message,
        checklist_tasks_done=SimpleNamespace(
            checklist_message=checklist_message,
            marked_as_done_task_ids=(1,),
            marked_as_not_done_task_ids=(),
        ),
    )
    update = SimpleNamespace(message=message, effective_user=actor)
    bus = Bus()
    channel = ImgramChannel(ImgramConfig(token="test", allow_from=["*"]), bus)

    asyncio.run(channel._process_message_update(update, None))

    assert len(bus.inbound) == 1
    inbound = bus.inbound[0]
    assert inbound.channel == "imgram"
    assert inbound.sender_id == "42|laoba"
    assert "Marked completed: [1] 整理桌面" in inbound.content
    assert inbound.metadata["checklist_tasks_done"]["marked_as_done_task_ids"] == [1]
