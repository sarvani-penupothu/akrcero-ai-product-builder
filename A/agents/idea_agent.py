"""IdeaAgent extracts the core problem, solution, and audience from raw ideas."""

from __future__ import annotations

from typing import Dict, List

from agents.agent_utils import (
    assess_complexity,
    craft_value_props,
    detect_attributes,
    derive_success_metrics,
    extract_keywords,
    infer_audience,
    infer_domain,
    tokenize_sentences,
)
from agents.base_agent import BaseAgent
from core.deps import LLMClient


class IdeaAgent(BaseAgent):
    """Derives the foundational understanding of the user's startup idea."""

    def __init__(self, llm: LLMClient) -> None:
        super().__init__(name="IdeaAgent")
        self.llm = llm

    def _select_problem(self, sentences: List[str]) -> str:
        for sentence in sentences:
            lowered = sentence.lower()
            if any(token in lowered for token in ["problem", "struggle", "pain", "friction", "challenge"]):
                return sentence
        return sentences[0] if sentences else "Founders need a sharper way to translate ideas into products."

    def _select_solution(self, sentences: List[str], fallback: str) -> str:
        for sentence in sentences:
            lowered = sentence.lower()
            if any(token in lowered for token in ["solution", "platform", "tool", "product", "service", "assistant"]):
                return sentence
        return fallback

    def run(self, payload: Dict[str, str]) -> Dict[str, object]:
        idea = (payload.get("idea") or "").strip()
        if not idea:
            idea = "An AI copilot that turns founder vision statements into validated product roadmaps."

        sentences = tokenize_sentences(idea)
        problem = self._select_problem(sentences)

        llm_hint = ""
        if getattr(self.llm, "provider", "") != "stub":
            llm_hint = self.llm.generate(
                "Extract a crisp solution phrase for the concept.",
                idea,
                max_tokens=120,
            )

        solution_hint = (
            llm_hint
            or "The platform orchestrates expert agents to translate founder intent into a validated blueprint."
        )
        solution = self._select_solution(sentences, solution_hint)

        domain = infer_domain(idea)
        audience = infer_audience(idea)
        keywords = extract_keywords(idea, limit=10)
        value_props = craft_value_props(domain, audience)
        success_metrics = derive_success_metrics(domain)
        attributes = detect_attributes(idea)
        complexity = assess_complexity(idea, attributes)
        attribute_highlights = [
            label.replace("_", " ").title() for label, active in attributes.items() if active
        ]

        top_opportunities = [
            f"{domain} opportunity: unlock {kw.replace('-', ' ')} leverage for {audience.lower()}"
            for kw in keywords[:3]
        ]

        narrative = ""
        if getattr(self.llm, "provider", "") != "stub":
            narrative = self.llm.generate(
                "Craft a bold two-sentence product narrative emphasising problem-solution fit and audience impact.",
                f"Problem: {problem}\nSolution: {solution}\nAudience: {audience}\nDomain: {domain}\nComplexity: {complexity}",
                max_tokens=140,
                temperature=0.5,
            )
        if not narrative:
            narrative = (
                f"Akcero refines the {domain.lower()} challenge of \"{problem}\" into a blueprint that empowers "
                f"{audience.lower()} with a differentiated, agent-powered solution."
            )

        return {
            "problem": problem,
            "solution": solution,
            "target_audience": audience,
            "domain": domain,
            "keywords": keywords,
            "value_propositions": value_props,
            "success_metrics": success_metrics,
            "attributes": attributes,
            "execution_complexity": complexity,
            "top_opportunities": top_opportunities,
            "attribute_highlights": attribute_highlights,
            "narrative": narrative.strip(),
        }
