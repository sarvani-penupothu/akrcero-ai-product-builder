"""Shared schemas and types for the Akcero AI Product Builder."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, TypedDict
from typing_extensions import NotRequired


class IdeaDetails(TypedDict):
    problem: str
    solution: str
    target_audience: str
    domain: str
    keywords: List[str]
    value_propositions: NotRequired[List[str]]
    success_metrics: NotRequired[List[str]]
    top_opportunities: NotRequired[List[str]]
    narrative: NotRequired[str]
    attributes: NotRequired[Dict[str, bool]]
    execution_complexity: NotRequired[str]
    attribute_highlights: NotRequired[List[str]]


class BusinessDetails(TypedDict):
    model: str
    revenue_streams: List[str]
    go_to_market: str
    partners: List[str]
    pricing_strategy: NotRequired[str]
    key_metrics: NotRequired[List[str]]
    sales_enablement: NotRequired[List[str]]
    expansion_strategy: NotRequired[str]
    monetisation_notes: NotRequired[str]
    complexity_profile: NotRequired[str]


class TechDetails(TypedDict):
    architecture: str
    stack: List[str]
    ai_components: List[str]
    scalability: str
    service_components: NotRequired[List[str]]
    data_strategy: NotRequired[str]
    devops: NotRequired[List[str]]
    integration_points: NotRequired[List[str]]
    resilience_notes: NotRequired[str]


class DesignDetails(TypedDict):
    experience_principles: List[str]
    key_screens: List[str]
    brand_voice: str
    interaction_patterns: NotRequired[List[str]]
    visual_language: NotRequired[str]
    content_tone: NotRequired[str]
    inspiration_references: NotRequired[str]
    design_complexity: NotRequired[str]


class MarketDetails(TypedDict):
    segment: str
    competitors: List[str]
    differentiators: List[str]
    launch_strategy: str
    personas: NotRequired[List[str]]
    marketing_channels: NotRequired[List[str]]
    market_challenges: NotRequired[List[str]]
    positioning_statement: NotRequired[str]
    momentum_notes: NotRequired[str]
    go_to_market_intent: NotRequired[str]


class TimelinePhase(TypedDict):
    phase: str
    duration: str
    focus: str
    owner: NotRequired[str]
    exit_criteria: NotRequired[str]


class TimelineDetails(TypedDict):
    phases: List[TimelinePhase]
    total_duration_weeks: int
    milestones: NotRequired[List[str]]
    cadence_notes: NotRequired[str]
    risk_watchlist: NotRequired[str]
    business_alignment: NotRequired[str]
    tech_alignment: NotRequired[str]


class ProductBlueprint(TypedDict):
    idea: IdeaDetails
    business_model: BusinessDetails
    tech_stack: TechDetails
    ui_design: DesignDetails
    market_analysis: MarketDetails
    timeline: TimelineDetails
    summary: str


@dataclass
class StoredRun:
    """Representation of a persisted product blueprint run."""

    id: str
    idea_text: str
    blueprint: ProductBlueprint
    created_at: datetime = field(default_factory=datetime.utcnow)
