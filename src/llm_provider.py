from __future__ import annotations
import asyncio
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
            return self._openai_agents_response(system, messages, user, refusal_prompt, mode)

        else:
            raise NotImplementedError(f"Provider {self.provider} not supported")

        # Placeholder for real integrations:
        # - call your provider SDK
        # - pass system + messages + user
        # - return text

    def _openai_agents_response(
        self,
        system: str,
        messages: List[Dict[str, str]],
        user: str,
        refusal_prompt: str,
        mode: str,
    ) -> str:
        if not os.getenv("OPENAI_API_KEY"):
            raise RuntimeError(
                "OPENAI_API_KEY is not set. Add it to your .env file before using LLM_PROVIDER=openai."
            )

        try:
            from agents import Agent as OpenAIAgent
            from agents import Runner
        except ImportError as exc:
            raise RuntimeError(
                "OpenAI Agents SDK is not installed. Run `pip install -r requirements.txt` "
                "after activating your virtual environment."
            ) from exc

        instructions = self._compose_instructions(system, refusal_prompt, mode)
        agent = OpenAIAgent(
            name="FactSummarizer",
            instructions=instructions,
            model=self.model,
        )

        prompt = self._compose_input(messages, user)
        result = asyncio.run(Runner.run(agent, prompt))
        final_output = result.final_output
        return final_output.strip() if isinstance(final_output, str) else str(final_output).strip()

    def _compose_instructions(self, system: str, refusal_prompt: str, mode: str) -> str:
        if mode == "refusal":
            return (
                f"{system}\n\n"
                "The current request has already been flagged by the policy engine. "
                "Do not comply with the unsafe request. Use the refusal guidance below.\n\n"
                f"{refusal_prompt}"
            ).strip()
        return system.strip()

    def _compose_input(self, messages: List[Dict[str, str]], user: str) -> str:
        if not messages:
            return user

        history_lines: List[str] = []
        for msg in messages:
            role = msg.get("role", "user").upper()
            content = msg.get("content", "").strip()
            if content:
                history_lines.append(f"{role}: {content}")

        history = "\n".join(history_lines)
        return (
            "Conversation so far:\n"
            f"{history}\n\n"
            "Respond to the newest user request below.\n"
            f"USER: {user}"
        )
    
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
