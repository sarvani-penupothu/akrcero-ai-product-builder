"""DesignAgent provides high-fidelity UI/UX recommendations for the product."""

from __future__ import annotations

from typing import Dict

from agents.agent_utils import (
    assess_complexity,
    detect_attributes,
    get_design_palette,
    infer_audience,
    infer_domain,
)
from agents.base_agent import BaseAgent
from core.deps import LLMClient


class DesignAgent(BaseAgent):
    """Shapes the design direction based on the product vision and audience."""

    def __init__(self, llm: LLMClient) -> None:
        super().__init__(name="DesignAgent")
        self.llm = llm

    def run(self, payload: Dict[str, object]) -> Dict[str, object]:
        idea_context = payload.get("idea_context") or {}
        idea_text = (payload.get("idea") or "").strip()
        domain = idea_context.get("domain") or infer_domain(idea_text)
        audience = idea_context.get("target_audience") or infer_audience(idea_text)
        attributes = idea_context.get("attributes") or detect_attributes(idea_text)
        complexity = idea_context.get("execution_complexity") or assess_complexity(idea_text, attributes)

        palette = get_design_palette(domain, audience, attributes, complexity)

        inspiration = (
            "Blend Akcero's luminous minimalism with proven patterns from category-defining "
            f"{domain.lower()} products and high-trust productivity tools."
        )
        if getattr(self.llm, "provider", "") != "stub":
            llm_inspiration = self.llm.generate(
                "Suggest design inspiration references (1 sentence) mixing product and brand cues.",
                f"Domain: {domain}\nAudience: {audience}\nPrinciples: {palette['experience_principles']}\nAttributes: {attributes}",
                max_tokens=120,
                temperature=0.5,
            ).strip()
            if llm_inspiration:
                inspiration = llm_inspiration

        palette["inspiration_references"] = inspiration
        return palette
