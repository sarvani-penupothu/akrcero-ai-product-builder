"""MarketAgent studies positioning and competitive landscape."""

from __future__ import annotations

from typing import Dict

from agents.agent_utils import (
    assess_complexity,
    detect_attributes,
    get_market_playbook,
    infer_audience,
    infer_domain,
)
from agents.base_agent import BaseAgent
from core.deps import LLMClient


class MarketAgent(BaseAgent):
    """Identifies market segments, competitors, and differentiation angles."""

    def __init__(self, llm: LLMClient) -> None:
        super().__init__(name="MarketAgent")
        self.llm = llm

    def run(self, payload: Dict[str, object]) -> Dict[str, object]:
        idea_text = (payload.get("idea") or "").strip()
        domain = str(payload.get("idea_context", {}).get("domain") or infer_domain(idea_text.lower()))
        audience = payload.get("idea_context", {}).get("target_audience") or infer_audience(idea_text.lower())
        attributes = payload.get("idea_context", {}).get("attributes") or detect_attributes(idea_text.lower())
        complexity = (
            payload.get("idea_context", {}).get("execution_complexity")
            or assess_complexity(idea_text.lower(), attributes)
        )

        playbook = get_market_playbook(domain, audience, attributes, complexity)

        positioning = playbook["positioning_statement"]
        if getattr(self.llm, "provider", "") != "stub":
            llm_positioning = self.llm.generate(
                "Write a crisp positioning statement (1 sentence) naming the wedge and momentum.",
                f"Idea: {idea_text}\nDomain: {domain}\nAudience: {audience}\nDifferentiators: {playbook['differentiators']}",
                max_tokens=120,
                temperature=0.55,
            ).strip()
            if llm_positioning:
                positioning = llm_positioning

        momentum = (
            "Near-term focus: secure lighthouse design partners, publish quantified wins, and capture narrative authority."
        )
        if getattr(self.llm, "provider", "") != "stub":
            llm_momentum = self.llm.generate(
                "Provide a momentum insight (1 sentence) highlighting urgency and proof loops.",
                f"Segment: {playbook['segment']}\nChallenges: {playbook['market_challenges']}\nChannels: {playbook['marketing_channels']}",
                max_tokens=80,
                temperature=0.45,
            ).strip()
            if llm_momentum:
                momentum = llm_momentum

        playbook.update(
            {
                "positioning_statement": positioning,
                "momentum_notes": momentum,
            }
        )
        return playbook
