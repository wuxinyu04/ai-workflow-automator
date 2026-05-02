"""
LLM client adapters for MiMo and Claude.
"""

import json
import time
from typing import Optional

import requests


class BaseLLMClient:
    def chat(self, system: str, user: str, temperature: float = 0.2) -> str:
        raise NotImplementedError


class MiMoClient(BaseLLMClient):
    """
    Client for MiMo long-context model API.
    Optimized for large codebase analysis (supports 128k context window).
    """

    DEFAULT_MODEL = "mimo-vl-7b-rl"  # use larger model for complex tasks
    MAX_RETRIES = 3
    RETRY_DELAY = 2.0

    def __init__(self, api_key: str, base_url: str = "https://api.mimo.ai/v1"):
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        })

    def chat(
        self,
        system: str,
        user: str,
        temperature: float = 0.2,
        model: Optional[str] = None,
        max_tokens: int = 4096,
    ) -> str:
        payload = {
            "model": model or self.DEFAULT_MODEL,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            "temperature": temperature,
            "max_tokens": max_tokens,
        }

        for attempt in range(self.MAX_RETRIES):
            try:
                resp = self.session.post(
                    f"{self.base_url}/chat/completions",
                    json=payload,
                    timeout=120,
                )
                resp.raise_for_status()
                data = resp.json()
                return data["choices"][0]["message"]["content"]
            except requests.HTTPError as e:
                if e.response.status_code == 429 and attempt < self.MAX_RETRIES - 1:
                    time.sleep(self.RETRY_DELAY * (attempt + 1))
                    continue
                raise
        return ""

    def count_tokens(self, text: str) -> int:
        """Rough estimate: 1 token ≈ 3.5 chars for mixed code/English."""
        return len(text) // 3


class ClaudeClient(BaseLLMClient):
    """Anthropic Claude client (fallback / comparison testing)."""

    DEFAULT_MODEL = "claude-3-5-sonnet-20241022"

    def __init__(self, api_key: str):
        self.api_key = api_key
        try:
            import anthropic
            self._client = anthropic.Anthropic(api_key=api_key)
        except ImportError:
            raise ImportError("anthropic package required: pip install anthropic")

    def chat(
        self,
        system: str,
        user: str,
        temperature: float = 0.2,
        model: Optional[str] = None,
        max_tokens: int = 4096,
    ) -> str:
        msg = self._client.messages.create(
            model=model or self.DEFAULT_MODEL,
            max_tokens=max_tokens,
            system=system,
            messages=[{"role": "user", "content": user}],
            temperature=temperature,
        )
        return msg.content[0].text
