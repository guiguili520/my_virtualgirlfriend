#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Tests for Virtual Girlfriend 2.0 online model API client."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from models.api_client import (
    OnlineModelClient,
    get_provider_presets,
    resolve_model_settings,
)
from models.inference import GirlfriendChatModel


class DummyResponse:
    def __init__(self, payload, status_code=200):
        self._payload = payload
        self.status_code = status_code
        self.text = str(payload)

    def json(self):
        return self._payload


class DummySession:
    def __init__(self, payload):
        self.payload = payload
        self.calls = []

    def post(self, url, json, headers, timeout):
        self.calls.append({
            "url": url,
            "json": json,
            "headers": headers,
            "timeout": timeout,
        })
        return DummyResponse(self.payload)


def test_provider_presets_include_2_0_shortcuts():
    providers = {item["key"]: item for item in get_provider_presets()}

    for key in ["openai", "anthropic", "deepseek", "glm", "kimi"]:
        assert key in providers

    assert providers["deepseek"]["api_format"] == "openai"
    assert providers["glm"]["base_url"].endswith("/v4")
    assert providers["kimi"]["base_url"].endswith("/v1")


def test_missing_api_key_uses_mock_fallback(monkeypatch):
    for name in ["VG_MODEL_API_KEY", "OPENAI_API_KEY", "DEEPSEEK_API_KEY"]:
        monkeypatch.delenv(name, raising=False)

    settings = resolve_model_settings(provider="openai")

    assert settings.mock is True
    assert settings.mock_reason.startswith("missing_api_key")


def test_openai_format_request_and_response():
    session = DummySession({
        "choices": [
            {"message": {"content": "你好呀，我在这里陪你~ 😊"}}
        ]
    })
    client = OnlineModelClient(session=session)
    settings = resolve_model_settings(
        provider="openai",
        api_key="test-key",
        model="gpt-test",
        base_url="https://example.test/v1",
    )

    response = client.generate("你好", [], settings)

    assert response == "你好呀，我在这里陪你~ 😊"
    call = session.calls[0]
    assert call["url"] == "https://example.test/v1/chat/completions"
    assert call["headers"]["Authorization"] == "Bearer test-key"
    assert call["json"]["model"] == "gpt-test"
    assert call["json"]["messages"][0]["role"] == "system"
    assert call["json"]["messages"][-1]["content"] == "你好"


def test_anthropic_format_request_and_response():
    session = DummySession({
        "content": [
            {"type": "text", "text": "我会温柔地陪着你哦~ 💕"}
        ]
    })
    client = OnlineModelClient(session=session)
    settings = resolve_model_settings(
        provider="anthropic",
        api_key="test-key",
        model="claude-test",
        base_url="https://anthropic.example",
    )

    response = client.generate("你好", [], settings)

    assert response == "我会温柔地陪着你哦~ 💕"
    call = session.calls[0]
    assert call["url"] == "https://anthropic.example/v1/messages"
    assert call["headers"]["x-api-key"] == "test-key"
    assert call["headers"]["anthropic-version"] == "2023-06-01"
    assert "system" in call["json"]
    assert call["json"]["messages"][0]["role"] == "user"


def test_girlfriend_model_accepts_per_request_provider():
    model = GirlfriendChatModel(use_mock=True)

    response = model.generate_reply(
        "【用户问题】\n我今天好累\n\n请回答",
        opts={"model_provider": "deepseek"},
    )

    assert isinstance(response, str)
    assert "陪" in response
    assert model.get_model_info({"model_provider": "deepseek"})["provider"] == "deepseek"
