"""BusinessAgent develops a nuanced commercial strategy for the product."""

from __future__ import annotations

from typing import Dict

from agents.agent_utils import (
    assess_complexity,
    detect_attributes,
    get_business_playbook,
    infer_audience,
    infer_domain,
)
from agents.base_agent import BaseAgent
from core.deps import LLMClient


class BusinessAgent(BaseAgent):
    """Transforms idea insights into a market-ready business blueprint."""

    def __init__(self, llm: LLMClient) -> None:
        super().__init__(name="BusinessAgent")
        self.llm = llm

    def _detect_model(self, text: str) -> str:
        lowered = text.lower()
        if any(keyword in lowered for keyword in ["marketplace", "network", "two-sided"]):
            return "Marketplace commissions with premium workflow subscriptions"
        if "api" in lowered or "developer" in lowered:
            return "Usage-based API platform augmented with enterprise plans"
        if "mobile" in lowered or "app" in lowered:
            return "Freemium mobile experience with pro subscription unlocks"
        if "consulting" in lowered or "services" in lowered:
            return "Hybrid subscription plus expert services retainer"
        if "hardware" in lowered or "iot" in lowered:
            return "Hardware-enabled subscription with device leasing"
        return "Tiered SaaS subscription with outcome-based add-ons"

    def _pricing_strategy(self, text: str) -> str:
        lowered = text.lower()
        if "enterprise" in lowered:
            return "Enterprise annual agreements anchored to ROI milestones"
        if "startup" in lowered or "founder" in lowered:
            return "Founders-first pricing: free discovery tier, $249/mo accelerator tier"
        if "marketplace" in lowered:
            return "1.9% transaction fee plus $99/mo curated vendor spotlight"
        return "Layered pricing mixing usage meters with collaborative seats"

    def run(self, payload: Dict[str, object]) -> Dict[str, object]:
        idea_context = payload.get("idea_context") or {}
        idea_text = (payload.get("idea") or "").strip()

        domain = idea_context.get("domain") or infer_domain(idea_text)
        audience = idea_context.get("target_audience") or infer_audience(idea_text)
        attributes = idea_context.get("attributes") or detect_attributes(idea_text)
        complexity = idea_context.get("execution_complexity") or assess_complexity(idea_text, attributes)

        model = self._detect_model(idea_text)
        playbook = get_business_playbook(
            domain,
            audience,
            attributes,
            complexity,
            base_model=model,
        )

        pricing_hint = self._pricing_strategy(idea_text)
        if pricing_hint and pricing_hint.lower() not in playbook["pricing_strategy"].lower():
            playbook["pricing_strategy"] = f"{playbook['pricing_strategy']}. {pricing_hint}."

        expansion_strategy = playbook.pop("expansion_strategy")
        if getattr(self.llm, "provider", "") != "stub":
            llm_expansion = self.llm.generate(
                "Craft a crisp expansion narrative (2 sentences) that highlights scale opportunities and risk controls.",
                f"Domain: {domain}\nAudience: {audience}\nModel: {playbook['model']}\nGTM: {playbook['go_to_market']}\nComplexity: {complexity}",
                max_tokens=150,
                temperature=0.4,
            ).strip()
            if llm_expansion:
                expansion_strategy = llm_expansion

        monetisation_notes = (
            f"Lead with {playbook['revenue_streams'][0]} while layering "
            f"{playbook['revenue_streams'][1] if len(playbook['revenue_streams']) > 1 else 'scalable add-ons'} "
            f"to reinforce predictable ARR."
        )

        playbook.update(
            {
                "expansion_strategy": expansion_strategy,
                "monetisation_notes": monetisation_notes,
            }
        )
        return playbook
