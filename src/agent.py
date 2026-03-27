from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from .memory import Memory
from .policies import PolicyEngine, PolicyResult
from .llm_provider import LLMProvider
from .utils import safe_format

@dataclass
class Agent:
    cfg: Dict[str, Any]
    policies: Dict[str, Any]
    prompts: Dict[str, str]
    logger: Any

    def __post_init__(self) -> None:
        self.name = self.cfg.get("agent_name", "Agent")
        self.memory = Memory(enabled=self.cfg.get("memory", {}).get("enabled", True),
                             max_messages=self.cfg.get("memory", {}).get("max_messages", 12))
        self.policy_engine = PolicyEngine(self.policies)
        self.llm = LLMProvider.from_env_or_config(self.cfg)

    def _build_system_prompt(self) -> str:
        base = safe_format(self.prompts["system"], agent_name=self.name)
        style = self.prompts["style"]
        return f"{base}\n\n{style}".strip()

    def respond(self, user_text: str) -> str:
        if not user_text.strip():
            reply = "Please provide the text you want summarized or a specific question about the source."
            self.logger.info("USER: %s", user_text)
            self.logger.info("ASSISTANT: %s", reply)
            return reply

        # 1) Policy check (governance layer)
        policy: PolicyResult = self.policy_engine.evaluate(user_text)

        self.logger.info("USER: %s", user_text)
        self.logger.info("POLICY: %s", policy.to_dict())

        if policy.action == "REFUSE":
            refusal = self.prompts["refusal"]
            reply = self.llm.complete(
                system=self._build_system_prompt(),
                messages=self.memory.messages(),
                user=user_text,
                refusal_prompt=refusal,
                mode="refusal",
            )
            self.memory.add(user_text, reply)
            self.logger.info("ASSISTANT: %s", reply)
            return reply

        # 2) Normal completion
        reply = self.llm.complete(
            system=self._build_system_prompt(),
            messages=self.memory.messages(),
            user=user_text,
            refusal_prompt=self.prompts["refusal"],
            mode="normal",
        )

        self.memory.add(user_text, reply)
        self.logger.info("ASSISTANT: %s", reply)
        return reply
