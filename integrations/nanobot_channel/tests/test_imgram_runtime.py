"""Regression seams for the official-runtime imGram overlay."""

import pytest

from nanobot.channels.imgram.runtime import ImgramChannel, ImgramConfig
from nanobot.channels.telegram.runtime import TelegramChannel


def test_imgram_inherits_official_telegram_runtime():
    assert issubclass(ImgramChannel, TelegramChannel)
    assert ImgramChannel.send is TelegramChannel.send
    assert ImgramChannel.send_delta is TelegramChannel.send_delta
    assert ImgramChannel._process_message_update is TelegramChannel._process_message_update


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
