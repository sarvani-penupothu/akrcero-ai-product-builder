"""TechAgent proposes a detailed tech stack and reference architecture."""

from __future__ import annotations

from typing import Dict

from agents.agent_utils import (
    assess_complexity,
    detect_attributes,
    get_tech_playbook,
    infer_domain,
    resolve_category,
)
from agents.base_agent import BaseAgent
from core.deps import LLMClient


class TechAgent(BaseAgent):
    """Defines the technology foundation aligned with business requirements."""

    def __init__(self, llm: LLMClient) -> None:
        super().__init__(name="TechAgent")
        self.llm = llm

    def run(self, payload: Dict[str, object]) -> Dict[str, object]:
        idea_text = (payload.get("idea") or "").strip()
        domain = str(payload.get("idea_context", {}).get("domain") or infer_domain(idea_text))
        attributes = payload.get("idea_context", {}).get("attributes") or detect_attributes(idea_text)
        complexity = (
            payload.get("idea_context", {}).get("execution_complexity")
            or assess_complexity(idea_text, attributes)
        )

        playbook = get_tech_playbook(domain, attributes, complexity)

        architecture_summary = playbook["architecture"]
        resilience_notes = playbook["resilience_notes"]

        if getattr(self.llm, "provider", "") != "stub":
            llm_architecture = self.llm.generate(
                "Summarise the architecture in one vivid sentence that emphasises reliability and extensibility.",
                (
                    f"Architecture: {architecture_summary}\n"
                    f"Stack: {', '.join(playbook['stack'])}\n"
                    f"AI: {', '.join(playbook['ai_components'])}\n"
                    f"Domain: {domain}\n"
                    f"Complexity: {complexity}"
                ),
                max_tokens=140,
                temperature=0.4,
            ).strip()
            if llm_architecture:
                architecture_summary = llm_architecture

            llm_resilience = self.llm.generate(
                "Provide one sentence on reliability and risk mitigation priorities for this architecture.",
                (
                    f"Domain: {domain}\n"
                    f"Complexity: {complexity}\n"
                    f"Attributes: {attributes}\n"
                    f"Current notes: {resilience_notes}"
                ),
                max_tokens=120,
                temperature=0.3,
            ).strip()
            if llm_resilience:
                resilience_notes = llm_resilience

        scalability = (
            f"{complexity.title()} delivery cadence with guardrails for {resolve_category(domain).lower()} workloads."
        )

        playbook.update(
            {
                "architecture": architecture_summary,
                "resilience_notes": resilience_notes,
                "scalability": scalability,
            }
        )
        return playbook
