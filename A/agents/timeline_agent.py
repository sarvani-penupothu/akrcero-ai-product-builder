"""TimelineAgent composes the execution roadmap based on other agents."""

from __future__ import annotations

from typing import Dict

from agents.agent_utils import (
    assess_complexity,
    detect_attributes,
    get_timeline_blueprint,
    infer_domain,
)
from agents.base_agent import BaseAgent
from core.deps import LLMClient


class TimelineAgent(BaseAgent):
    """Aggregates cross-agent insights into a time-phased roadmap."""

    def __init__(self, llm: LLMClient) -> None:
        super().__init__(name="TimelineAgent")
        self.llm = llm

    def run(self, payload: Dict[str, object]) -> Dict[str, object]:
        idea_context = payload.get("idea_context") or {}
        business_context = payload.get("business_context") or {}
        tech_context = payload.get("tech_context") or {}
        idea_text = (payload.get("idea") or "").strip()

        domain = idea_context.get("domain") or infer_domain(idea_text.lower())
        attributes = idea_context.get("attributes") or detect_attributes(idea_text.lower())
        complexity = (
            idea_context.get("execution_complexity")
            or assess_complexity(idea_text.lower(), attributes)
        )

        timeline = get_timeline_blueprint(domain, attributes, complexity)

        risk_notes = (
            "Monitor scope creep, data readiness, and stakeholder engagement across the orchestration."
        )
        if getattr(self.llm, "provider", "") != "stub":
            llm_risks = self.llm.generate(
                "List the top risk or contingency to watch (1 sentence).",
                f"Idea context: {idea_context}\nBusiness: {business_context}\nTech: {tech_context}\nAttributes: {attributes}",
                max_tokens=80,
                temperature=0.4,
            ).strip()
            if llm_risks:
                risk_notes = llm_risks

        timeline["risk_watchlist"] = risk_notes
        timeline["business_alignment"] = business_context.get("model", "Model TBD")
        timeline["tech_alignment"] = tech_context.get("architecture", "Architecture TBD")
        return timeline
