from __future__ import annotations
import os
from dataclasses import dataclass
from typing import Any, Dict, List

from dotenv import load_dotenv
from openai import OpenAI


@dataclass
class LLMProvider:
    provider: str
    model: str

    @staticmethod
    def from_env_or_config(cfg: Dict[str, Any]) -> "LLMProvider":
        # Load variables from the repo-root .env file, if present.
        # This makes both app.py and tests/stage2_test.py work automatically.
        load_dotenv()

        provider = os.getenv("LLM_PROVIDER") or cfg.get("llm_provider", "mock")
        model = os.getenv("LLM_MODEL") or cfg.get("llm_model", "gpt-4o-mini")
        return LLMProvider(provider=provider, model=model)

    def complete(
        self,
        system: str,
        messages: List[Dict[str, str]],
        user: str,
        refusal_prompt: str,
        mode: str = "normal",
    ) -> str:
        if self.provider == "mock":
            return self._mock_response(system, messages, user, refusal_prompt, mode)

        if self.provider == "openai":
            return self._openai_response(system, messages, user, refusal_prompt, mode)

        raise ValueError(f"Unsupported LLM provider: {self.provider}")

    def _openai_response(
        self,
        system: str,
        messages: List[Dict[str, str]],
        user: str,
        refusal_prompt: str,
        mode: str,
    ) -> str:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError(
                "OPENAI_API_KEY is missing. Add it to your .env file at the repo root."
            )

        client = OpenAI(api_key=api_key)

        chat_messages: List[Dict[str, str]] = []
        chat_messages.append({"role": "system", "content": system})

        # Memory/history messages from your agent
        for msg in messages:
            chat_messages.append(msg)

        # For refusals, add an extra system instruction to shape the refusal tone
        if mode == "refusal":
            chat_messages.append({"role": "system", "content": refusal_prompt})

        # Current user turn
        chat_messages.append({"role": "user", "content": user})

        response = client.chat.completions.create(
            model=self.model,
            messages=chat_messages,
            temperature=0.3,
        )

        text = response.choices[0].message.content
        return text.strip() if text else ""

    def _mock_response(
        self,
        system: str,
        messages: List[Dict[str, str]],
        user: str,
        refusal_prompt: str,
        mode: str,
    ) -> str:
        if mode == "refusal":
            return (
                "I can’t help with that request.\n"
                "Reason: it appears to violate a course policy for safe/ethical behavior.\n"
                "Safe alternatives: I can explain the risks, provide defensive best practices, or help reframe the task."
            )

        if "summarize" in user.lower():
            return "Summary (mock): I can summarize once you paste the text or describe the source."
        if "recommend" in user.lower():
            return "Recommendation (mock): Tell me your goal + constraints, and I’ll suggest options."
        return "Response (mock): I understand. Say 'summarize', 'recommend', or ask a specific question."