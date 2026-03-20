from __future__ import annotations
import os
from dataclasses import dataclass
from typing import Any, Dict, List

@dataclass
class LLMProvider:
    provider: str
    model: str

    @staticmethod
    def from_env_or_config(cfg: Dict[str, Any]) -> "LLMProvider":
        provider = os.getenv("LLM_PROVIDER") or cfg.get("llm_provider", "mock")
        model = os.getenv("LLM_MODEL") or cfg.get("llm_model", "mock-001")
        return LLMProvider(provider=provider, model=model)

    def complete(
        self,
        system: str,
        messages: List[Dict[str, str]],
        user: str,
        refusal_prompt: str,
        mode: str = "normal",
    ) -> str:
        """
        Swap this with a real provider call.
        Keep the signature stable so students only change this file.
        """
        if self.provider == "mock":
            return self._mock_response(system, messages, user, refusal_prompt, mode)

        elif self.provider == "openai":
            from openai import OpenAI
            import os

            client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

            response = client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system},
                    *messages,
                    {"role": "user", "content": user}
                ],
                temperature=0.7
            )

            return response.choices[0].message.content

        else:
            raise NotImplementedError(f"Provider {self.provider} not supported")

        # Placeholder for real integrations:
        # - call your provider SDK
        # - pass system + messages + user
        # - return text
    
    def _mock_response(
        self, system: str, messages: List[Dict[str, str]], user: str, refusal_prompt: str, mode: str
    ) -> str:
        if mode == "refusal":
            return (
                "I can’t help with that request.\n"
                "Reason: it appears to violate a course policy for safe/ethical behavior.\n"
                "Safe alternatives: I can explain the risks, provide defensive best practices, or help reframe the task."
            )

        # Simple “agent-like” behavior for offline testing
        if "summarize" in user.lower():
            return "Summary (mock): I can summarize once you paste the text or describe the source."
        if "recommend" in user.lower():
            return "Recommendation (mock): Tell me your goal + constraints, and I’ll suggest options."
        return "Response (mock): I understand. Say 'summarize', 'recommend', or ask a specific question."
