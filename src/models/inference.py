#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Virtual Girlfriend 2.0 model inference interface.

2.0 uses online model APIs by default. Local model loading is no longer part of
the chat serving path; when no API key is configured the wrapper falls back to a
small mock responder so the web app and tests still run.
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional

from .api_client import (
    ModelSettings,
    OnlineModelClient,
    get_provider_presets,
    resolve_model_settings,
)

_MODEL_SINGLETON: Optional["GirlfriendChatModel"] = None


class GirlfriendChatModel:
    """Unified online model wrapper used by the inference pipeline."""

    def __init__(
        self,
        model_path: Optional[str] = None,
        use_mock: bool = False,
        provider: Optional[str] = None,
        api_format: Optional[str] = None,
        model: Optional[str] = None,
        base_url: Optional[str] = None,
        api_key: Optional[str] = None,
        client: Optional[OnlineModelClient] = None,
    ):
        # model_path is kept only for backwards compatibility with old callers.
        self.model_path = model_path
        self._forced_mock = use_mock
        self.client = client or OnlineModelClient()
        self.default_settings = resolve_model_settings(
            provider=provider,
            api_format=api_format,
            model=model,
            base_url=base_url,
            api_key=api_key,
            use_mock=use_mock,
        )
        self.use_mock = self.default_settings.mock

    def generate_reply(
        self,
        prompt: str,
        context: Optional[List[Dict[str, str]]] = None,
        opts: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Generate a reply through the selected online API format."""
        settings = self._settings_from_opts(opts or {})
        response = self.client.generate(prompt, context, settings)
        if not response:
            return "抱歉呀，我刚才没有组织好语言~ 能再说一遍吗？😊"
        self.use_mock = settings.mock
        self.default_settings = settings
        return response

    def _settings_from_opts(self, opts: Dict[str, Any]) -> ModelSettings:
        return resolve_model_settings(
            provider=opts.get("model_provider") or opts.get("provider"),
            api_format=opts.get("api_format") or opts.get("model_api_format"),
            model=opts.get("model_name") or opts.get("model"),
            base_url=opts.get("base_url") or opts.get("model_base_url"),
            api_key=opts.get("api_key"),
            use_mock=self._forced_mock or bool(opts.get("use_mock_model")),
        )

    def get_model_info(self, opts: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Return non-sensitive model settings for logs and UI."""
        return self._settings_from_opts(opts or {}).public_dict()


def init_model(
    model_path: Optional[str] = None,
    use_mock: Optional[bool] = None,
    provider: Optional[str] = None,
    api_format: Optional[str] = None,
    model: Optional[str] = None,
    base_url: Optional[str] = None,
    api_key: Optional[str] = None,
) -> None:
    """Initialize the global model instance."""
    global _MODEL_SINGLETON
    if _MODEL_SINGLETON is not None:
        return
    _MODEL_SINGLETON = GirlfriendChatModel(
        model_path=model_path,
        use_mock=bool(use_mock),
        provider=provider,
        api_format=api_format,
        model=model,
        base_url=base_url,
        api_key=api_key,
    )


def get_model_instance() -> GirlfriendChatModel:
    global _MODEL_SINGLETON
    if _MODEL_SINGLETON is None:
        init_model()
    assert _MODEL_SINGLETON is not None
    return _MODEL_SINGLETON


def generate_girlfriend_reply(
    text: str,
    context: Optional[List[Dict[str, str]]] = None,
    opts: Optional[Dict[str, Any]] = None,
) -> str:
    """Compatibility helper for legacy imports."""
    return get_model_instance().generate_reply(text, context=context, opts=opts)


__all__ = [
    "GirlfriendChatModel",
    "generate_girlfriend_reply",
    "get_model_instance",
    "get_provider_presets",
    "init_model",
]
