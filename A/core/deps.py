"""Dependency helpers including LLM accessors."""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Optional

try:
    from openai import OpenAI  # type: ignore
except ImportError:  # pragma: no cover - optional dependency
    OpenAI = None  # type: ignore


@dataclass
class LLMClient:
    """Simple wrapper around an LLM provider with deterministic fallback."""

    provider: str
    model: str
    client: Optional[object] = None

    def generate(
        self,
        system_prompt: str,
        prompt: str,
        *,
        temperature: float = 0.2,
        max_tokens: int = 512,
    ) -> str:
        """Generate a completion using the configured provider or fallback stub."""

        if self.provider == "openai" and self.client is not None:
            try:
                response = self.client.chat.completions.create(  # type: ignore[attr-defined]
                    model=self.model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": prompt},
                    ],
                    temperature=temperature,
                    max_tokens=max_tokens,
                )
                message = response.choices[0].message.content  # type: ignore[index]
                return (message or "").strip()
            except Exception:
                # Fall back to deterministic stub if the provider fails at runtime.
                pass

        # Default deterministic template output.
        blueprint = (
            f"{prompt.strip()}" if prompt.strip() else "No additional insights available."
        )
        return blueprint


class DeterministicLLMStub(LLMClient):
    """LLM fallback that provides deterministic templated responses."""

    def __init__(self) -> None:
        super().__init__(provider="stub", model="rule-template")

    def generate(
        self,
        system_prompt: str,
        prompt: str,
        *,
        temperature: float = 0.2,
        max_tokens: int = 512,
    ) -> str:
        context = prompt.strip() or "the provided concept"
        intent = (
            system_prompt.splitlines()[0]
            if system_prompt
            else "General ideation guidance."
        )
        return f"System Intent: {intent}\nInsight: Focus on {context}."


def get_llm() -> LLMClient:
    """Return an LLM client instance, preferring OpenAI when configured."""

    api_key = os.getenv("OPENAI_API_KEY")
    if api_key and OpenAI is not None:
        try:
            client = OpenAI(api_key=api_key)
            model = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
            return LLMClient(provider="openai", model=model, client=client)
        except Exception:
            pass

    # Default fallback stub ensures offline functionality.
    return DeterministicLLMStub()
