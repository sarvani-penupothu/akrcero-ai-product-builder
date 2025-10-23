"""Umbrella agent orchestrating specialized agents for blueprint generation."""

from __future__ import annotations

import asyncio
from typing import Any, Callable, Dict, Optional

from agents import (
    BusinessAgent,
    DesignAgent,
    IdeaAgent,
    MarketAgent,
    TechAgent,
    TimelineAgent,
)
from agents.base_agent import AgentPayload, AgentResponse
from core.deps import LLMClient
from core.schemas import ProductBlueprint

ProgressCallback = Callable[[str, str], None]


class UmbrellaAgent:
    """Coordinates the multi-agent workflow using hybrid async orchestration."""

    def __init__(
        self,
        *,
        idea_agent: IdeaAgent,
        business_agent: BusinessAgent,
        tech_agent: TechAgent,
        design_agent: DesignAgent,
        market_agent: MarketAgent,
        timeline_agent: TimelineAgent,
        llm: LLMClient,
    ) -> None:
        self.idea_agent = idea_agent
        self.business_agent = business_agent
        self.tech_agent = tech_agent
        self.design_agent = design_agent
        self.market_agent = market_agent
        self.timeline_agent = timeline_agent
        self.llm = llm

    async def run_agent(
        self,
        agent_name: str,
        agent_callable: Callable[[AgentPayload], AgentResponse],
        payload: AgentPayload,
        callback: Optional[ProgressCallback] = None,
    ) -> AgentResponse:
        if callback:
            callback(agent_name, "running")
        result = await asyncio.to_thread(agent_callable, payload)
        if callback:
            callback(agent_name, "completed")
        return result

    async def build_blueprint(
        self,
        idea_text: str,
        *,
        pitch_mode: bool = False,
        callback: Optional[ProgressCallback] = None,
    ) -> Dict[str, Any]:
        """Execute the hybrid orchestration pipeline and return collected outputs."""

        payload: AgentPayload = {"idea": idea_text}

        idea_output = await self.run_agent(
            "IdeaAgent", self.idea_agent.run, payload, callback
        )

        step_two_payload = {"idea": idea_text, "idea_context": idea_output}
        business_task = asyncio.create_task(
            self.run_agent(
                "BusinessAgent", self.business_agent.run, step_two_payload, callback
            )
        )
        tech_task = asyncio.create_task(
            self.run_agent(
                "TechAgent", self.tech_agent.run, step_two_payload, callback
            )
        )
        business_output, tech_output = await asyncio.gather(business_task, tech_task)

        step_three_payload = {
            "idea": idea_text,
            "idea_context": idea_output,
            "business_context": business_output,
            "tech_context": tech_output,
        }
        design_task = asyncio.create_task(
            self.run_agent(
                "DesignAgent", self.design_agent.run, step_three_payload, callback
            )
        )
        market_task = asyncio.create_task(
            self.run_agent(
                "MarketAgent", self.market_agent.run, step_three_payload, callback
            )
        )
        design_output, market_output = await asyncio.gather(design_task, market_task)

        timeline_payload = {
            "idea": idea_text,
            "idea_context": idea_output,
            "business_context": business_output,
            "tech_context": tech_output,
            "design_context": design_output,
            "market_context": market_output,
        }
        timeline_output = await self.run_agent(
            "TimelineAgent", self.timeline_agent.run, timeline_payload, callback
        )

        summary_text = self._summarize(
            idea_output,
            business_output,
            tech_output,
            design_output,
            market_output,
            timeline_output,
        )

        blueprint: ProductBlueprint = {
            "idea": idea_output,
            "business_model": business_output,
            "tech_stack": tech_output,
            "ui_design": design_output,
            "market_analysis": market_output,
            "timeline": timeline_output,
            "summary": summary_text,
        }

        pitch_text = (
            self._build_pitch(blueprint)
            if pitch_mode
            else ""
        )

        return {
            "blueprint": blueprint,
            "agents": {
                "idea": idea_output,
                "business": business_output,
                "tech": tech_output,
                "design": design_output,
                "market": market_output,
                "timeline": timeline_output,
            },
            "pitch": pitch_text.strip(),
        }

    def _summarize(
        self,
        idea: AgentResponse,
        business: AgentResponse,
        tech: AgentResponse,
        design: AgentResponse,
        market: AgentResponse,
        timeline: AgentResponse,
    ) -> str:
        """Generate executive summary text leveraging the configured LLM."""

        prompt = (
            "Create a confident executive summary for the product blueprint. "
            "Highlight the core problem, signature solution, business model + pricing, "
            "technical advantage, design POV, market positioning, and launch momentum. "
            "Cap the summary at 130 words."
        )
        value_props = ", ".join(idea.get("value_propositions", [])[:2])
        key_metrics = ", ".join(business.get("key_metrics", [])[:2])
        channels = ", ".join(market.get("marketing_channels", [])[:2])
        context = "\n".join(
            [
                f"Problem: {idea.get('problem', '')}",
                f"Solution: {idea.get('solution', '')}",
                f"Audience: {idea.get('target_audience', '')}",
                f"Complexity: {idea.get('execution_complexity', '')}",
                f"Value Props: {value_props}",
                f"Business Model: {business.get('model', '')}",
                f"Pricing: {business.get('pricing_strategy', '')}",
                f"GTM: {business.get('go_to_market', '')}",
                f"Key Metrics: {key_metrics}",
                f"Tech Stack: {', '.join(tech.get('stack', []))}",
                f"Architecture: {tech.get('architecture', '')}",
                f"AI Edge: {', '.join(tech.get('ai_components', [])[:2])}",
                f"Design Focus: {', '.join(design.get('experience_principles', []))}",
                f"Market Segment: {market.get('segment', '')}",
                f"Competitors: {', '.join(market.get('competitors', []))}",
                f"Differentiators: {', '.join(market.get('differentiators', []))}",
                f"Positioning: {market.get('positioning_statement', '')}",
                f"Momentum: {market.get('momentum_notes', '')}",
                f"Launch Channels: {channels}",
                f"Timeline: {timeline.get('total_duration_weeks', 0)} weeks",
                f"Cadence: {timeline.get('cadence_notes', '')}",
                f"Risk Watchlist: {timeline.get('risk_watchlist', '')}",
            ]
        )
        return self.llm.generate(prompt, context)

    def _build_pitch(self, blueprint: ProductBlueprint) -> str:
        """Craft a 30-second elevator pitch from the blueprint data."""

        prompt = (
            "Craft a 6 sentence elevator pitch highlighting the problem, "
            "solution, business opportunity, pricing, tech advantage, market traction, "
            "and roadmap. Keep it upbeat and visionary."
        )
        context = (
            f"Problem: {blueprint['idea']['problem']}\n"
            f"Solution: {blueprint['idea']['solution']}\n"
            f"Audience: {blueprint['idea']['target_audience']}\n"
            f"Complexity: {blueprint['idea'].get('execution_complexity', '')}\n"
            f"Business Model: {blueprint['business_model']['model']}\n"
            f"Pricing: {blueprint['business_model'].get('pricing_strategy', '')}\n"
            f"Tech: {', '.join(blueprint['tech_stack']['stack'])}\n"
            f"Differentiator: {', '.join(blueprint['market_analysis']['differentiators'])}\n"
            f"Positioning: {blueprint['market_analysis'].get('positioning_statement', '')}\n"
            f"Momentum: {blueprint['market_analysis'].get('momentum_notes', '')}\n"
            f"Roadmap: {blueprint['timeline']['total_duration_weeks']} week plan"
        )
        return self.llm.generate(prompt, context, temperature=0.4, max_tokens=220)
