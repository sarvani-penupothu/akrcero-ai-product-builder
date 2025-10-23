"""Shared heuristics for agent reasoning without external LLM dependencies."""

from __future__ import annotations

import re
from collections import Counter
from typing import Dict, List

STOPWORDS = {
    "the",
    "and",
    "for",
    "with",
    "that",
    "from",
    "into",
    "this",
    "your",
    "their",
    "about",
    "will",
    "make",
    "build",
    "help",
    "using",
    "through",
    "across",
    "data",
    "user",
    "users",
    "product",
    "ai",
    "artificial",
    "intelligence",
    "system",
    "platform",
    "experience",
    "solution",
    "create",
    "creating",
    "design",
    "digital",
    "idea",
    "ideas",
    "team",
    "teams",
}

DOMAIN_CATEGORY = {
    "Healthcare & Wellness": "Healthcare",
    "Finance & Fintech": "Finance",
    "Education & Learning": "Education",
    "Commerce & Retail": "Commerce",
    "Productivity & Collaboration": "Productivity",
    "Customer Experience": "Customer",
    "Developer Tools": "Developer",
    "Marketing & Growth": "Marketing",
    "Sustainability & Climate": "Sustainability",
    "Manufacturing & Industry": "Industry",
    "Technology & Innovation": "Innovation",
}

ATTRIBUTE_KEYWORDS: Dict[str, set[str]] = {
    "regulatory": {
        "regulation",
        "regulated",
        "compliance",
        "hipaa",
        "gdpr",
        "sox",
        "audit",
        "risk",
        "governance",
    },
    "marketplace": {
        "marketplace",
        "two-sided",
        "multi-sided",
        "buyers",
        "sellers",
        "vendors",
        "matching",
    },
    "hardware": {
        "hardware",
        "device",
        "sensor",
        "iot",
        "wearable",
        "embedded",
    },
    "realtime": {
        "real-time",
        "realtime",
        "live",
        "streaming",
        "instant",
        "event-driven",
    },
    "data_heavy": {
        "analytics",
        "warehouse",
        "lakehouse",
        "big data",
        "data",
        "insight",
        "forecast",
    },
    "mobile": {"mobile", "ios", "android", "smartphone"},
    "enterprise": {"enterprise", "fortune", "corporate", "global"},
    "community": {"community", "social", "network", "member"},
    "developer": {"developer", "api", "sdk", "cli", "devops"},
    "ai_native": {"agent", "agents", "multi-agent", "autonomous"},
}

COMPLEXITY_WEIGHTS: Dict[str, int] = {
    "regulatory": 2,
    "marketplace": 2,
    "hardware": 2,
    "enterprise": 1,
    "data_heavy": 1,
    "realtime": 1,
    "developer": 1,
    "mobile": 1,
    "community": 1,
}

BUSINESS_TEMPLATES: Dict[str, Dict[str, object]] = {
    "Healthcare": {
        "model": "Compliance-first SaaS with expert enablement",
        "pricing": "Pilot-based pricing tied to clinical outcomes and scale",
        "revenue": [
            "Clinical innovation subscription for care teams",
            "Implementation & interoperability services",
            "Outcome analytics add-ons for administrators",
        ],
        "gtm": "Co-create with {audience} and hospital innovation programs, spotlighting measurable patient impact in the {domain} space.",
        "partners": [
            "Hospital innovation labs",
            "EHR / HL7 integration specialists",
            "Clinical research networks",
        ],
        "key_metrics": [
            "Patient outcome uplift after pilot",
            "Compliance audit pass rate",
            "Care team activation within 60 days",
        ],
        "enablement": [
            "Clinical validation briefs",
            "Security & compliance FAQ",
            "ROI calculator tailored to administrators",
        ],
        "expansion": "Expand into adjacent care pathways once regulatory approvals are secured.",
    },
    "Finance": {
        "model": "Risk-aware SaaS with premium analytics services",
        "pricing": "Tiered pricing aligned to assets under management and automation throughput",
        "revenue": [
            "Core compliance & automation subscription",
            "Premium risk analytics dashboards",
            "Advisory integrations and onboarding services",
        ],
        "gtm": "Leverage {audience} relationships and fintech sandboxes, emphasising trust, controls, and measurable ROI in {domain}.",
        "partners": [
            "Fintech accelerators & regulatory sandboxes",
            "Core banking and payment processors",
            "Audit and compliance consultancies",
        ],
        "key_metrics": [
            "Time-to-compliance reduction",
            "Automation-driven cost savings",
            "Portfolio coverage within 90 days",
        ],
        "enablement": [
            "Regulator-ready security brief",
            "Value justification deck with benchmarks",
            "Integration playbooks for core systems",
        ],
        "expansion": "Layer on adjacent risk products once trust is established with early adopters.",
    },
    "Education": {
        "model": "Learning innovation platform with cohort services",
        "pricing": "Per-program licensing with learner volume accelerators",
        "revenue": [
            "Institutional subscription",
            "Curriculum design & accreditation services",
            "Learning analytics premium module",
        ],
        "gtm": "Activate {audience} champions within universities and bootcamps, pairing thought leadership with credentialed pilots across {domain}.",
        "partners": [
            "Edtech accelerators",
            "Curriculum design experts",
            "Learning management vendors",
        ],
        "key_metrics": [
            "Learner engagement score",
            "Time-to-curriculum refresh",
            "Placement or certification uplift",
        ],
        "enablement": [
            "Instructional design case studies",
            "Learner journey storyboard",
            "Funding & grants negotiation toolkit",
        ],
        "expansion": "Extend to corporate enablement and lifelong learning marketplaces once initial programs excel.",
    },
    "Commerce": {
        "model": "Experience-led commerce platform with monetised insights",
        "pricing": "GMV-linked SaaS with performance-based boosters",
        "revenue": [
            "Core storefront intelligence subscription",
            "Conversion-optimisation services",
            "Data monetisation via benchmarks",
        ],
        "gtm": "Target {audience} within high-growth brands, co-market with ecosystem agencies, and prove conversion lift across {domain} segments.",
        "partners": [
            "E-commerce agencies",
            "Logistics & fulfilment networks",
            "Payment providers",
        ],
        "key_metrics": [
            "Average order value lift",
            "Checkout conversion increase",
            "Customer lifetime value expansion",
        ],
        "enablement": [
            "Merchandising playbook",
            "Experiment roadmap template",
            "Executive dashboard mockups",
        ],
        "expansion": "Scale into new verticals via channel partnerships and white-label intelligence.",
    },
    "Productivity": {
        "model": "Workflow orchestration platform with analytics add-ons",
        "pricing": "Seat-based pricing with outcome accelerators",
        "revenue": [
            "Core workspace subscription",
            "Automation marketplace",
            "Insights & governance module",
        ],
        "gtm": "Launch with {audience} inside product-led organisations, emphasising measurable cross-team velocity in the {domain} arena.",
        "partners": [
            "Product-led growth communities",
            "Product ops consultancies",
            "Integration partners (Slack, Atlassian)",
        ],
        "key_metrics": [
            "Workflow completion velocity",
            "Cross-team alignment score",
            "Automation adoption within 30 days",
        ],
        "enablement": [
            "Change management toolkit",
            "Operational maturity benchmark",
            "Executive summary narrative",
        ],
        "expansion": "Expand into adjacent departments once flagship workspace metrics are achieved.",
    },
    "Customer": {
        "model": "Customer intelligence hub with service automation",
        "pricing": "Tiered pricing aligned to customer volume and SLAs",
        "revenue": [
            "Insight subscription",
            "Service automation add-ons",
            "Voice of customer analytics",
        ],
        "gtm": "Equip {audience} with proof of CSAT gains and time-to-resolution improvements within {domain} teams.",
        "partners": [
            "CX consultancies",
            "CRM vendors",
            "Support community programs",
        ],
        "key_metrics": [
            "CSAT / NPS uplift",
            "First-response automation coverage",
            "Retention increase across segments",
        ],
        "enablement": [
            "Executive listening tour agenda",
            "Customer journey storyboard",
            "Automation ROI worksheet",
        ],
        "expansion": "Layer in revenue enablement offerings once support motion proves value.",
    },
    "Developer": {
        "model": "Usage-based API platform with collaboration seats",
        "pricing": "Pay-as-you-go API meters plus enterprise support plans",
        "revenue": [
            "Core API consumption",
            "Premium orchestration add-ons",
            "Enterprise success engineering",
        ],
        "gtm": "Drive adoption through {audience}, open-source showcases, and deep integration tutorials tailored to {domain} builders.",
        "partners": [
            "Developer advocacy communities",
            "Cloud marketplaces",
            "Systems integrators",
        ],
        "key_metrics": [
            "Active developers",
            "Time-to-first-integration",
            "Production usage retention",
        ],
        "enablement": [
            "Reference architecture kits",
            "Postman / SDK bundles",
            "Proof-of-concept accelerator scripts",
        ],
        "expansion": "Grow into ecosystem marketplaces and private deployments as enterprise demand matures.",
    },
    "Marketing": {
        "model": "Campaign intelligence platform with experiment services",
        "pricing": "Channel-based tiering with performance bonuses",
        "revenue": [
            "Growth intelligence subscription",
            "Managed experiment services",
            "Attribution analytics add-on",
        ],
        "gtm": "Collaborate with {audience} to launch lighthouse growth experiments and publish benchmark reports across {domain}.",
        "partners": [
            "Growth agencies",
            "Ad platforms",
            "Influencer networks",
        ],
        "key_metrics": [
            "Cost per acquisition improvement",
            "Campaign experiment velocity",
            "Pipeline contribution",
        ],
        "enablement": [
            "Campaign hypothesis library",
            "Executive revenue alignment narrative",
            "Attribution modelling toolkit",
        ],
        "expansion": "Introduce ecosystem marketplaces and co-marketing alliances after initial channel mastery.",
    },
    "Sustainability": {
        "model": "Impact data platform with advisory overlays",
        "pricing": "Subscription indexed to emissions footprint and reporting scope",
        "revenue": [
            "ESG reporting subscription",
            "Carbon reduction advisory",
            "Marketplace of certified partners",
        ],
        "gtm": "Activate {audience} and sustainability leads, uniting regulatory compliance with innovation narratives in {domain}.",
        "partners": [
            "Climate tech alliances",
            "Regulatory consultants",
            "Data providers (emissions, offsets)",
        ],
        "key_metrics": [
            "Emission reduction verified",
            "Reporting cycle compression",
            "Partner program expansion",
        ],
        "enablement": [
            "ESG storytelling kit",
            "Regulatory mapping template",
            "Executive sustainability heatmap",
        ],
        "expansion": "Scale into supply chain transparency once carbon accounting flywheel spins.",
    },
    "Industry": {
        "model": "Operational intelligence platform with edge services",
        "pricing": "Footprint-based pricing with production outcome bonuses",
        "revenue": [
            "Factory orchestration subscription",
            "Predictive maintenance services",
            "Supply-chain visibility add-ons",
        ],
        "gtm": "Partner with {audience} and industrial innovation labs to prove downtime reduction across {domain} plants.",
        "partners": [
            "Systems integrators",
            "IoT hardware vendors",
            "Manufacturing associations",
        ],
        "key_metrics": [
            "Downtime reduction",
            "Yield improvement",
            "Throughput increase",
        ],
        "enablement": [
            "Operational excellence playbook",
            "Factory data readiness assessment",
            "Change management workshop kit",
        ],
        "expansion": "Expand regionally via strategic OEM alliances and reseller channels.",
    },
    "Innovation": {
        "model": "Multi-agent SaaS with advisory overlays",
        "pricing": "Tiered SaaS plus outcomes-based accelerator programs",
        "revenue": [
            "Core multi-agent workspace",
            "Strategic advisory sprints",
            "Data & integration marketplace",
        ],
        "gtm": "Inspire {audience} through founder stories, live blueprint showcases, and community-led launches across {domain}.",
        "partners": [
            "Venture studios",
            "Startup communities",
            "Tooling ecosystems",
        ],
        "key_metrics": [
            "Blueprint completion velocity",
            "Pilot conversion to build",
            "Founder NPS",
        ],
        "enablement": [
            "Investor storytelling pack",
            "Blueprint KPI dashboard",
            "Launch playbook for co-marketing",
        ],
        "expansion": "Add vertical-specific playbooks once initial cohorts show repeatable wins.",
    },
}

TECH_TEMPLATES: Dict[str, Dict[str, object]] = {
    "Healthcare": {
        "architecture": "HIPAA-ready service mesh with governed clinical knowledge lake and audit-first workflows",
        "stack": [
            "FastAPI microservices",
            "React / Next.js experience layer",
            "FHIR-compatible PostgreSQL + pgvector",
            "Airflow & dbt for governed pipelines",
            "Event bus via Kafka",
        ],
        "ai": [
            "Retrieval-augmented generation over clinical protocols",
            "Agent triage for risk stratification",
            "Quality guardrails monitoring hallucinations and compliance",
        ],
        "service": [
            "Identity & consent management",
            "Clinical evidence tagging engine",
            "Blueprint orchestration service",
        ],
        "data": "Govern protected health information via encrypted data lake, lineage tracking, and role-based access.",
        "devops": [
            "Terraform IaC with environment blueprints",
            "GitHub Actions → Argo Rollouts for progressive delivery",
            "Automated compliance checks & audit logging",
        ],
        "integration": [
            "EHR / EMR platforms",
            "Analytics warehouse (Snowflake / BigQuery)",
            "Customer success tooling",
        ],
    },
    "Finance": {
        "architecture": "Zero-trust microservices with streaming risk engine and immutable audit ledger",
        "stack": [
            "Python FastAPI or JVM services",
            "React + Ant Design ops console",
            "PostgreSQL + Vitess for ledgering",
            "Kafka Streams for real-time scoring",
            "Lakehouse via Delta or Iceberg",
        ],
        "ai": [
            "Compliance-aware reasoning agents",
            "Anomaly detection on transactional data",
            "Scenario simulation co-pilots",
        ],
        "service": [
            "Policy engine & rules studio",
            "Risk dashboard",
            "Partner integration hub",
        ],
        "data": "Encrypted columnar storage with fine-grained entitlements and immutable audit trails.",
        "devops": [
            "Terraform & Atlantis workflows",
            "Chaos testing in non-prod",
            "Continuous compliance scanners",
        ],
        "integration": [
            "Core banking systems",
            "Identity providers",
            "RegTech feeds",
        ],
    },
    "Education": {
        "architecture": "Modular learning fabric with adaptive content engine and analytics lake",
        "stack": [
            "FastAPI or NestJS services",
            "Next.js / Tailwind front-end",
            "Postgres + pgvector for content",
            "Superset or Metabase analytics",
            "Event streaming via Redpanda",
        ],
        "ai": [
            "Curriculum summarisation agents",
            "Personalised learning coach",
            "Assessment feedback generator",
        ],
        "service": [
            "Persona & cohort manager",
            "Content tagging & recommendation",
            "Credentialing & assessment",
        ],
        "data": "Capture learner telemetry into lakehouse with privacy-preserving segmentation.",
        "devops": [
            "Terraform + GitHub Actions",
            "Feature flag orchestration",
            "Observability stack (OpenTelemetry)",
        ],
        "integration": [
            "LMS platforms",
            "Video & conferencing APIs",
            "Student information systems",
        ],
    },
    "Commerce": {
        "architecture": "Event-driven commerce core with personalization engine and experimentation layer",
        "stack": [
            "Node.js / FastAPI microservices",
            "React storefront & design system",
            "PostgreSQL + Redis for sessions",
            "Segment + Snowflake analytics",
            "Kafka / Pulsar event backbone",
        ],
        "ai": [
            "Dynamic merchandising agent",
            "Pricing optimiser",
            "Customer journey summariser",
        ],
        "service": [
            "Catalog enrichment",
            "Experiment management",
            "Marketplace orchestration",
        ],
        "data": "Unify shopper telemetry and transactions within governed lakehouse for omni-channel insights.",
        "devops": [
            "Infrastructure as code (Terraform)",
            "Canary deploys via Argo",
            "Synthetic journey monitoring",
        ],
        "integration": [
            "Payment gateways",
            "Logistics APIs",
            "Marketing automation",
        ],
    },
    "Productivity": {
        "architecture": "Composable workspace fabric with knowledge graph and automation bus",
        "stack": [
            "Python FastAPI",
            "React + Chakra UI",
            "PostgreSQL + Neo4j knowledge graph",
            "Celery / Dramatiq workers",
            "ClickHouse analytics",
        ],
        "ai": [
            "Workflow summarisation agents",
            "Meeting synthesis",
            "Decision memory assistant",
        ],
        "service": [
            "Workspace orchestration",
            "Playbook library",
            "Integration controller",
        ],
        "data": "Capture work artefacts in searchable embeddings with strict workspace boundaries.",
        "devops": [
            "Terraform + GitHub Actions",
            "Service level objectives with SLO dashboards",
            "Feature toggle guardrails",
        ],
        "integration": [
            "Slack / Teams",
            "Project management suites",
            "Identity providers",
        ],
    },
    "Customer": {
        "architecture": "Unified customer intelligence lakehouse with service automation rail",
        "stack": [
            "Python / Go services",
            "React + Storybook",
            "Postgres + ClickHouse",
            "Airbyte ingestion",
            "Snowflake warehouse",
        ],
        "ai": [
    "Sentiment clustering agents",
    "Playbook recommendation",
    "Auto-generated QBR narratives",
        ],
        "service": [
            "Signal ingestion",
            "Success planning",
            "Feedback triage",
        ],
        "data": "Blend CS data sources with customer journey signals into governed warehouse.",
        "devops": [
            "IaC + policy-as-code",
            "Golden signal monitoring",
            "Incident simulation",
        ],
        "integration": [
            "CRM suites",
            "Support platforms",
            "Product analytics",
        ],
    },
    "Developer": {
        "architecture": "API-first control plane with event mesh and developer experience portal",
        "stack": [
            "Go / Rust core services",
            "GraphQL gateway",
            "PostgreSQL + Redis",
            "OpenTelemetry everywhere",
            "Vectordb (Weaviate / Pinecone)",
        ],
        "ai": [
            "Code assistant for integrations",
            "Runbook summariser",
            "API anomaly detection",
        ],
        "service": [
            "Usage analytics",
            "Credential & secret vault",
            "Extension marketplace",
        ],
        "data": "Track usage telemetry and error budgets with redaction for customer data.",
        "devops": [
            "GitOps with Argo",
            "Progressive delivery with Flagger",
            "CLIs for multi-tenant ops",
        ],
        "integration": [
            "Cloud marketplaces",
            "CI/CD tooling",
            "Developer analytics",
        ],
    },
    "Marketing": {
        "architecture": "Channel intelligence graph with experimentation and attribution layers",
        "stack": [
            "Python services",
            "Next.js marketing workbench",
            "PostgreSQL + DuckDB",
            "Airflow / dbt",
            "Reverse ETL (Hightouch)",
        ],
        "ai": [
            "Campaign narrative generator",
            "Creative brief assistant",
            "Attribution explainer agent",
        ],
        "service": [
            "Segment harmoniser",
            "Experiment launcher",
            "Insights studio",
        ],
        "data": "Blend paid, owned, and earned channel data with privacy-aware segmentation.",
        "devops": [
            "IaC with Terraform",
            "Data quality monitors",
            "Automated backtesting",
        ],
        "integration": [
            "Ad platforms",
            "CRM & marketing automation",
            "Revenue systems",
        ],
    },
    "Sustainability": {
        "architecture": "Impact data backbone with scenario modelling engine",
        "stack": [
            "Python services",
            "React + D3 visual stories",
            "PostgreSQL + Timescale",
            "Airflow sustainability pipelines",
            "Vector store for ESG policies",
        ],
        "ai": [
            "Carbon hotspot detection agent",
            "ESG report drafter",
            "Supplier classification assistant",
        ],
        "service": [
            "Emission data ingestion",
            "Target planning studio",
            "Partner marketplace",
        ],
        "data": "Aggregate scope 1-3 data sources with provenance tracking and assurance.",
        "devops": [
            "Terraform + Vault",
            "Automated assurance tests",
            "Forecast monitoring",
        ],
        "integration": [
            "ERP systems",
            "Supply chain data feeds",
            "Offset registries",
        ],
    },
    "Industry": {
        "architecture": "Edge-aware industrial platform with digital twin and predictive loop",
        "stack": [
            "Go / Rust edge services",
            "FastAPI control plane",
            "Time-series DB (Influx / Timescale)",
            "Event backbone via Kafka",
            "Lakehouse on Delta",
        ],
        "ai": [
            "Predictive maintenance agents",
            "Anomaly root-cause analysis",
            "Production optimisation co-pilot",
        ],
        "service": [
            "Asset registry",
            "Work order automation",
            "Supplier orchestration",
        ],
        "data": "Sync edge telemetry into secure lakehouse with lineage and replay.",
        "devops": [
            "Infrastructure automation",
            "Blue/green for edge updates",
            "Site reliability playbooks",
        ],
        "integration": [
            "MES/SCADA",
            "ERP & PLM",
            "Quality management systems",
        ],
    },
    "Innovation": {
        "architecture": "Multi-agent orchestration fabric with shared knowledge graph and event bus",
        "stack": [
            "FastAPI orchestrators",
            "React + Radix UI",
            "PostgreSQL + pgvector",
            "LangChain or LlamaIndex",
            "Temporal for workflow choreography",
        ],
        "ai": [
            "Persona-specific ideation agents",
            "Blueprint synthesiser",
            "Risk/assumption tracker",
        ],
        "service": [
            "Idea ingestion",
            "Narrative engine",
            "Metrics cockpit",
        ],
        "data": "Maintain living product knowledge graph with traceable rationale and embeddings.",
        "devops": [
            "IaC with Terraform",
            "Feature flags + experimentation",
            "Observability (OpenTelemetry, Grafana)",
        ],
        "integration": [
            "Product analytics",
            "CRM & pipeline",
            "Documentation hubs",
        ],
    },
}

DESIGN_TEMPLATES: Dict[str, Dict[str, object]] = {
    "Healthcare": {
        "principles": [
            "Empathetic clarity with clinician-first language",
            "Trust signals via audit trails and explainability",
            "Assistive automation that keeps humans in control",
        ],
        "key_screens": [
            "Clinical opportunity map",
            "Compliance command centre",
            "Patient impact dashboard",
            "Care pathway timeline",
        ],
        "interaction": [
            "Guided playbooks with safety checkpoints",
            "Evidence trace overlays",
            "Scenario comparison mode",
        ],
        "voice": "Reassuring, expert, compliance-aware",
        "visual": "Calming neutrals with Akcero blue accents and data-rich panels",
        "tone": "Evidence-led storytelling that balances innovation with safety",
    },
    "Finance": {
        "principles": [
            "Control and auditability",
            "Scenario thinking at a glance",
            "Signal prioritisation for analysts",
        ],
        "key_screens": [
            "Risk cockpit",
            "Regulatory action log",
            "Portfolio automation canvas",
            "Executive reporting suite",
        ],
        "interaction": [
            "Explainable AI drilldowns",
            "Playbook builder",
            "Threshold alert designer",
        ],
        "voice": "Trusted, precise, and accountability-driven",
        "visual": "High-contrast dashboards with precise typography and data density",
        "tone": "Commanding confidence while highlighting safeguards",
    },
    "Education": {
        "principles": [
            "Guided creation with playful clarity",
            "Community feedback loops",
            "Celebration of learner progress",
        ],
        "key_screens": [
            "Curriculum atelier",
            "Learner journey mapper",
            "Engagement analytics",
            "Credential showcase",
        ],
        "interaction": [
            "Commentary threads",
            "Interactive storyboards",
            "Adaptive preview",
        ],
        "voice": "Encouraging, human, future-positive",
        "visual": "Warm neutrals with energetic accent gradients",
        "tone": "Inspiring craftsmanship with practical scaffolding",
    },
    "Commerce": {
        "principles": [
            "Conversion clarity",
            "Revenue storytelling",
            "Fast iteration loops",
        ],
        "key_screens": [
            "Revenue command centre",
            "Experiment tracker",
            "Marketplace health",
            "Customer journey heatmap",
        ],
        "interaction": [
            "Scenario toggles",
            "Smart playbook suggestions",
            "Live funnel overlays",
        ],
        "voice": "Energetic, growth-minded, and data-backed",
        "visual": "Bold hero stats with modular cards and high-contrast calls-to-action",
        "tone": "Outcome-obsessed yet grounded in feasibility",
    },
    "Productivity": {
        "principles": [
            "Narrative alignment",
            "Transparency of agent decisions",
            "Momentum cues",
        ],
        "key_screens": [
            "Unified mission brief",
            "Dependency radar",
            "AI assistant timeline",
            "Insights backlog",
        ],
        "interaction": [
            "Command palette",
            "Timeline scrubber",
            "Focus mode",
        ],
        "voice": "Strategic, energising, partner-like",
        "visual": "Layered cards, subtle glassmorphism, and rich whitespace",
        "tone": "Confident acceleration without overwhelm",
    },
    "Customer": {
        "principles": [
            "Empathy showcased by design",
            "Signal-to-action mapping",
            "Moments of celebration for wins",
        ],
        "key_screens": [
            "Customer health overview",
            "Journey timeline",
            "Executive briefing suite",
            "Renewal planner",
        ],
        "interaction": [
            "Success pulse checks",
            "Playbook branching",
            "Collaboration co-editing",
        ],
        "voice": "Supportive, pragmatic, north-star oriented",
        "visual": "Soft gradients with crisp data cards and personable iconography",
        "tone": "Empathetic authority that rallies teams",
    },
    "Developer": {
        "principles": [
            "Make power visible",
            "Surfacing telemetry without noise",
            "Shortcut-first execution",
        ],
        "key_screens": [
            "Service topology",
            "Usage analytics",
            "API playground",
            "Incident retros",
        ],
        "interaction": [
            "Command palette + CLI parity",
            "Split-pane diff view",
            "Automations panel",
        ],
        "voice": "Direct, expert, builder-to-builder",
        "visual": "Dark theme with neon accents and monospace highlights",
        "tone": "Matter-of-fact, unlocking mastery and velocity",
    },
    "Marketing": {
        "principles": [
            "Narrative framing of data",
            "Experiment storytelling",
            "Collaboration rituals",
        ],
        "key_screens": [
            "Campaign studio",
            "Audience intelligence",
            "Budget orchestration",
            "Launch calendar",
        ],
        "interaction": [
            "What-if toggles",
            "Creative inspiration wall",
            "Auto-generated executive briefs",
        ],
        "voice": "Bold, visionary, momentum-building",
        "visual": "Vibrant gradient washes with crisp typography and video-friendly layouts",
        "tone": "Ambitious with proof at every step",
    },
    "Sustainability": {
        "principles": [
            "Transparency",
            "Collaborative accountability",
            "Hopeful pragmatism",
        ],
        "key_screens": [
            "Impact dashboard",
            "Target tracking",
            "Supplier alignment space",
            "Investor-ready narrative",
        ],
        "interaction": [
            "Scenario sliders",
            "Compliance checklists",
            "Goal visualisations",
        ],
        "voice": "Purposeful, optimistic, evidence-rich",
        "visual": "Earthy neutrals with crisp data overlays and optimism cues",
        "tone": "Inspiring urgency backed by action",
    },
    "Industry": {
        "principles": [
            "Operational clarity",
            "Proactive alerts",
            "Human + machine partnership",
        ],
        "key_screens": [
            "Factory digital twin",
            "Maintenance planner",
            "Supply chain monitor",
            "Executive value cockpit",
        ],
        "interaction": [
            "Drill-through timelines",
            "Command centre quick actions",
            "Augmented reality overlays (roadmap)",
        ],
        "voice": "Assured, precision-focused, efficiency obsessed",
        "visual": "High-contrast industrial UI with data-rich modules",
        "tone": "Operationally authoritative with clear ROI",
    },
    "Innovation": {
        "principles": [
            "Story-driven intelligence",
            "Actionable transparency",
            "Momentum you can feel",
        ],
        "key_screens": [
            "Idea intake cockpit",
            "Opportunity canvas",
            "Blueprint narrative board",
            "Roadmap scenario explorer",
        ],
        "interaction": [
            "Multiplayer editing",
            "Timeline scrubbing",
            "Agent rationale reveals",
        ],
        "voice": "Visionary, expert, energising",
        "visual": "Luminous blues with clean glassmorphism and statement typography",
        "tone": "Confident storytelling that rallies investors and teams",
    },
}

MARKET_TEMPLATES: Dict[str, Dict[str, object]] = {
    "Healthcare": {
        "segment": "Healthcare innovators seeking compliant AI copilots for faster validation",
        "competitors": [
            "Notable Health",
            "Abridge",
            "Kahun",
        ],
        "differentiators": [
            "Multi-agent workflow tuned for clinical governance",
            "Explainable narratives linked to compliance artifacts",
            "Out-of-the-box audit telemetry",
        ],
        "personas": [
            "Chief Innovation Officer",
            "Clinical transformation lead",
            "Digital health startup founder",
        ],
        "channels": [
            "Healthcare innovation forums",
            "Regulatory roundtables",
            "Clinical podcast circuit",
        ],
        "challenges": [
            "Procurement scrutiny around data residency",
            "Proof of clinical efficacy required",
        ],
        "positioning": "Akcero turns fragmented clinical ideas into rigorously governed product blueprints in days, not quarters.",
        "launch": "Secure lighthouse health systems, publish de-identified case outcomes, and host a compliance-focused launch webinar.",
    },
    "Finance": {
        "segment": "Fintech and financial ops teams pursuing supervised AI automation",
        "competitors": [
            "Veryfi",
            "OpenRisk",
            "Canoe Intelligence",
        ],
        "differentiators": [
            "Continuous compliance baked into agent workflows",
            "Decision trails for auditors",
            "Real-time scenario modelling",
        ],
        "personas": [
            "Head of Operations",
            "Chief Risk Officer",
            "Fintech founder",
        ],
        "channels": [
            "Fintech accelerators",
            "RegTech conferences",
            "LinkedIn thought leadership series",
        ],
        "challenges": [
            "Regulatory approval timelines",
            "Risk-averse buyers demand references",
        ],
        "positioning": "Akcero delivers supervised AI blueprints that pass risk and compliance checks without slowing product velocity.",
        "launch": "Co-host sandbox demos with regulators and publish risk-case tear-downs showing measurable ROI.",
    },
    "Education": {
        "segment": "Edtech builders modernising curriculum and learner engagement with AI",
        "competitors": [
            "Instructure AI",
            "Knewton",
            "Sana",
        ],
        "differentiators": [
            "Human-first storytelling for instructors",
            "Agent collaboration tuned for learning design",
            "Embedded metrics for outcomes and equity",
        ],
        "personas": [
            "Academic innovation dean",
            "Program director",
            "Learning design lead",
        ],
        "channels": [
            "Edtech communities",
            "Teacher influencer partnerships",
            "Conference workshops",
        ],
        "challenges": [
            "Budget cycles and accreditation",
            "Need to prove learner impact quickly",
        ],
        "positioning": "Akcero helps educators ship future-proof programs with agents that co-design, validate, and measure learning impact.",
        "launch": "Curate design partner cohort across universities and publish before/after learner stories.",
    },
    "Commerce": {
        "segment": "Commerce operators chasing conversion breakthroughs with AI-led planning",
        "competitors": [
            "Triple Whale",
            "Malomo",
            "Shopify Sidekick",
        ],
        "differentiators": [
            "Multi-agent GTM orchestrations",
            "Narratives linking conversion gains to roadmap",
            "Real-time marketplace telemetry",
        ],
        "personas": [
            "VP Growth",
            "Head of Merchandising",
            "Founder / operator",
        ],
        "channels": [
            "DTC communities",
            "Performance marketing podcasts",
            "Product Hunt launch",
        ],
        "challenges": [
            "Crowded tooling category",
            "Proof required on conversion lift",
        ],
        "positioning": "Akcero transforms raw commerce ideas into conversion-maximising blueprints orchestrated by specialised agents.",
        "launch": "Partner with 3 flagship brands, televise experiment wins, and run joint launch live streams.",
    },
    "Productivity": {
        "segment": "Product & strategy teams aligning cross-functional delivery",
        "competitors": [
            "Productboard",
            "Aha!",
            "Notion AI",
        ],
        "differentiators": [
            "Agent swarm translating narrative to execution",
            "Executive-ready storytelling",
            "Telemetry that links decision to outcome",
        ],
        "personas": [
            "Head of Product",
            "Strategy lead",
            "Chief of Staff",
        ],
        "channels": [
            "Product leadership roundtables",
            "Founder communities",
            "Thought leadership newsletter",
        ],
        "challenges": [
            "Need to reframe beyond classic roadmap tools",
            "Stakeholder trust in AI decisions",
        ],
        "positioning": "Akcero's multi-agent studio makes every product idea investor, exec, and team ready in one collaborative motion.",
        "launch": "Host live blueprint showcases with design partners and release template library on launch week.",
    },
    "Customer": {
        "segment": "Customer success leaders scaling narrative-driven retention",
        "competitors": [
            "Gainsight AI",
            "Catalyst",
            "Vitally",
        ],
        "differentiators": [
            "Blueprints connecting customer voice to roadmap",
            "Executive-grade narratives auto-generated",
            "Playbooks measured by revenue impact",
        ],
        "personas": [
            "VP Customer Success",
            "Revenue operations director",
            "CS Ops lead",
        ],
        "channels": [
            "CS leadership communities",
            "Revenue forums",
            "Webinars with customer heroes",
        ],
        "challenges": [
            "Proving attribution to revenue",
            "Integration expectations",
        ],
        "positioning": "Akcero turns customer signals into boardroom-ready blueprints that close renewals and expansions faster.",
        "launch": "Run a lighthouse cohort with CS leaders, publish revenue turnaround stories, and launch on G2/Product Hunt.",
    },
    "Developer": {
        "segment": "Platform and infrastructure leaders building AI-enabled tooling",
        "competitors": [
            "Vercel AI",
            "Postman Intelligence",
            "Buildkite Copilot",
        ],
        "differentiators": [
            "Agentic design tailored for technical buyers",
            "Traceable architecture narratives",
            "CLI and API parity",
        ],
        "personas": [
            "Head of Platform",
            "Staff engineer",
            "DevRel lead",
        ],
        "channels": [
            "Open-source launches",
            "Developer conferences",
            "Technical AMAs",
        ],
        "challenges": [
            "Need to prove reliability",
            "Sophisticated buyer expectations",
        ],
        "positioning": "Akcero augments platform teams with agentic blueprints that ship resilient architecture and developer joy.",
        "launch": "Release reference architectures, run live coding streams, and create integration challenges with partners.",
    },
    "Marketing": {
        "segment": "Marketing leaders orchestrating AI-powered growth engines",
        "competitors": [
            "Jasper",
            "Mutiny",
            "June.so",
        ],
        "differentiators": [
            "Narrative-first GTM agent collective",
            "Attribution-aware action plans",
            "Investor-ready storytelling",
        ],
        "personas": [
            "Chief Marketing Officer",
            "Growth director",
            "Brand strategist",
        ],
        "channels": [
            "CMO circles",
            "Growth podcasts",
            "Thought leadership reports",
        ],
        "challenges": [
            "Saturation of AI copy tools",
            "Need for proven attribution",
        ],
        "positioning": "Akcero architects growth engines that connect creative ambition to pipeline reality through specialised agents.",
        "launch": "Release growth benchmark report, run joint webinars with design partners, and seed community challenges.",
    },
    "Sustainability": {
        "segment": "Climate innovators and ESG leaders translating targets into action",
        "competitors": [
            "Watershed",
            "Persefoni",
            "Sweep",
        ],
        "differentiators": [
            "Agent collective linking carbon data to product decisions",
            "Investor-grade reporting narratives",
            "Marketplace for certified partners",
        ],
        "personas": [
            "Chief Sustainability Officer",
            "Product sustainability lead",
            "Impact entrepreneur",
        ],
        "channels": [
            "Climate accelerators",
            "ESG analyst forums",
            "Impact investor networks",
        ],
        "challenges": [
            "Data quality and proof of impact",
            "Evolving regulations globally",
        ],
        "positioning": "Akcero compresses sustainability roadmapping from quarters to weeks with agentic rigor and measurable impact.",
        "launch": "Publish impact scorecards with design partners and host a climate innovation summit.",
    },
    "Industry": {
        "segment": "Industrial innovators digitising operations with AI co-pilots",
        "competitors": [
            "Sight Machine",
            "Augury",
            "GE Predix",
        ],
        "differentiators": [
            "Agentic orchestration spanning plant to exec",
            "Digital twin storytelling",
            "Operational telemetry fused with product insights",
        ],
        "personas": [
            "VP Operations",
            "Digital transformation lead",
            "Innovation lab head",
        ],
        "channels": [
            "Industry consortiums",
            "Manufacturing events",
            "Public-private innovation programs",
        ],
        "challenges": [
            "Lengthy procurement",
            "Integration with legacy systems",
        ],
        "positioning": "Akcero accelerates industrial transformation with agentic blueprints that tie plant telemetry to board-level narratives.",
        "launch": "Co-host factory innovation tours and publish ROI benchmarks with early adopters.",
    },
    "Innovation": {
        "segment": "Founders and venture studios moving from concept to conviction",
        "competitors": [
            "Notion AI",
            "Gamma",
            "FigJam",
        ],
        "differentiators": [
            "Six specialised agents collaborating in real-time",
            "Investor-ready executive narrative",
            "Proof loops that quantify traction",
        ],
        "personas": [
            "Founder",
            "Head of Product",
            "Studio partner",
        ],
        "channels": [
            "Founder communities",
            "Product Hunt",
            "Venture newsletters",
        ],
        "challenges": [
            "Signal vs noise in AI tooling",
            "Ensuring outcomes feel proprietary",
        ],
        "positioning": "Akcero makes every founder idea investor, customer, and team-ready through orchestrated AI agents.",
        "launch": "Host live multi-agent blueprint showcases and publish the Akcero Product Builder playbook.",
    },
}

TIMELINE_NOTES: Dict[str, Dict[str, str]] = {
    "Healthcare": {
        "milestone": "Clinical advisory board validates pilot protocol",
        "launch": "Coordinate regulatory sign-off and publish patient impact case study",
    },
    "Finance": {
        "milestone": "Regulatory sandbox approval achieved",
        "launch": "Risk & compliance go-live checklist completed",
    },
    "Education": {
        "milestone": "Curriculum accreditation secured",
        "launch": "Learner showcase event executed",
    },
    "Commerce": {
        "milestone": "Dual-sided pilot conversion benchmarks hit",
        "launch": "Public launch paired with flagship brand testimonial",
    },
    "Productivity": {
        "milestone": "Cross-functional operating rhythm locked",
        "launch": "Company-wide rollout playbook activated",
    },
    "Customer": {
        "milestone": "Executive renewal narrative approved",
        "launch": "Customer advisory board celebrates early wins",
    },
    "Developer": {
        "milestone": "Public API GA with reliability SLAs",
        "launch": "Developer advocacy tour launched",
    },
    "Marketing": {
        "milestone": "Signature growth experiment proves pipeline lift",
        "launch": "Category narrative published with partner amplification",
    },
    "Sustainability": {
        "milestone": "Verified carbon reduction report delivered",
        "launch": "Impact summit with ecosystem partners",
    },
    "Industry": {
        "milestone": "Predictive maintenance ROI validated",
        "launch": "Factory leadership alignment summit",
    },
    "Innovation": {
        "milestone": "Investor-ready blueprint deck signed off",
        "launch": "Public beta with ambassador cohort",
    },
}

TIMELINE_WINDOWS = {
    "lean": ["Weeks 1-2", "Weeks 3-5", "Weeks 6-9", "Weeks 10-13", "Weeks 14-16"],
    "standard": ["Weeks 1-3", "Weeks 4-7", "Weeks 8-13", "Weeks 14-18", "Weeks 19-22"],
    "complex": ["Weeks 1-4", "Weeks 5-9", "Weeks 10-16", "Weeks 17-22", "Weeks 23-26"],
}

TIMELINE_TOTAL = {"lean": 16, "standard": 22, "complex": 26}


def normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text.strip())


def tokenize_sentences(text: str) -> List[str]:
    sentences = re.split(r"[.!?]\s+", text)
    return [normalize(sentence) for sentence in sentences if normalize(sentence)]


def extract_keywords(text: str, limit: int = 8) -> List[str]:
    words = re.findall(r"[a-zA-Z][a-zA-Z0-9-]+", text.lower())
    filtered = [w for w in words if w not in STOPWORDS and len(w) > 2]
    ranking = Counter(filtered)
    keywords = [word for word, _ in ranking.most_common(limit)]
    return keywords or ["innovation", "blueprint"]


def resolve_category(domain: str) -> str:
    return DOMAIN_CATEGORY.get(domain, domain.split("&")[0].strip() or "Innovation")


def detect_attributes(text: str) -> Dict[str, bool]:
    lowered = text.lower()
    return {
        name: any(keyword in lowered for keyword in keywords)
        for name, keywords in ATTRIBUTE_KEYWORDS.items()
    }


def assess_complexity(text: str, attributes: Dict[str, bool] | None = None) -> str:
    if attributes is None:
        attributes = detect_attributes(text)
    score = 1
    for attr, active in attributes.items():
        if not active:
            continue
        score += COMPLEXITY_WEIGHTS.get(attr, 1)
    word_count = len(text.split())
    if word_count > 140:
        score += 1
    if word_count > 220:
        score += 1
    if attributes.get("regulatory") and attributes.get("marketplace"):
        score += 1
    if score >= 6:
        return "complex"
    if score >= 3:
        return "standard"
    return "lean"


def infer_domain(text: str) -> str:
    lowered = text.lower()
    for domain, triggers in DOMAIN_CATEGORY.items():
        # reuse mapping by checking keywords derived from category name
        tokens = [token.strip().lower() for token in domain.replace("&", ",").split(",")]
        if any(token in lowered for token in tokens):
            return domain
    return "Technology & Innovation"


def infer_audience(text: str) -> str:
    lowered = text.lower()
    audience_map = {
        "founder": "Founders and product leaders",
        "startup": "Founders and product leaders",
        "entrepreneur": "Founders and product leaders",
        "operations": "Operations and strategy teams",
        "strategy": "Operations and strategy teams",
        "pm": "Product managers and discovery leads",
        "enterprise": "Enterprise innovation teams",
        "developer": "Developers and technical platform teams",
        "engineer": "Developers and technical platform teams",
        "marketing": "Growth and marketing leadership",
        "growth": "Growth and marketing leadership",
        "customer": "Customer success and revenue leaders",
        "cs": "Customer success and revenue leaders",
        "education": "Learning and enablement leaders",
        "sustain": "Sustainability and impact leaders",
    }
    for keyword, audience in audience_map.items():
        if keyword in lowered:
            return audience
    if "consumer" in lowered:
        return "Design-forward consumers"
    return "Visionary product builders"


def craft_value_props(domain: str, audience: str) -> List[str]:
    base = [
        "Aligns multi-disciplinary teams around a shared product narrative",
        "Transforms fuzzy concepts into execution-ready roadmaps",
        "Surfaces market-ready differentiation in every deliverable",
    ]
    category = resolve_category(domain)
    if category == "Healthcare":
        base.append("Encodes compliance and patient safety considerations by default")
    if category == "Finance":
        base.append("Highlights traceability and risk controls for regulated launch")
    if category == "Commerce":
        base.append("Optimises conversion levers across the buying journey")
    if category == "Developer":
        base.append("Provides deep technical architecture and integration playbooks")
    if category == "Marketing":
        base.append("Maps campaigns to data-backed growth experiments")
    if category == "Sustainability":
        base.append("Connects impact measurement to product delivery choices")
    if "Enterprise" in audience:
        base.append("Supports governance workflows and executive-ready reporting")
    return base[:6]


def derive_success_metrics(domain: str) -> List[str]:
    mapping = {
        "Healthcare & Wellness": [
            "Clinical validation achieved for top three use-cases",
            "HIPAA-aligned data handling sign-off",
        ],
        "Finance & Fintech": [
            "Regulatory review with compliance team completed",
            "Pilot customers reach 20% workflow automation savings",
        ],
        "Education & Learning": [
            "Learner engagement score above 75 NPS in pilot",
            "Curriculum iteration cycle under two weeks",
        ],
        "Commerce & Retail": [
            "Average order value uplift by 15% in beta cohort",
            "Customer acquisition cost payback within three months",
        ],
        "Productivity & Collaboration": [
            "Time-to-decision reduced by 30% across teams",
            "Weekly active usage above 65% of invited members",
        ],
        "Customer Experience": [
            "CSAT improvement of 10 points post-launch",
            "First-response automation covering 40% of tickets",
        ],
        "Developer Tools": [
            "Time-to-first-API-call under 5 minutes",
            "95%+ reliability across key endpoints",
        ],
        "Marketing & Growth": [
            "Pipeline contribution up 25%",
            "Test velocity doubles without infrastructure debt",
        ],
        "Sustainability & Climate": [
            "Verified carbon reduction milestone",
            "Supply chain transparency index uplift",
        ],
        "Manufacturing & Industry": [
            "Downtime reduced by 20% in pilot facilities",
            "Yield and throughput improvements documented",
        ],
    }
    defaults = [
        "100 design partner sessions completed",
        "Launch readiness scorecard signed off by leadership",
    ]
    return mapping.get(domain, defaults) + ["Founders unlock clear investor-ready storytelling"]


def get_business_playbook(
    domain: str,
    audience: str,
    attributes: Dict[str, bool],
    complexity: str,
    base_model: str | None = None,
) -> Dict[str, object]:
    category = resolve_category(domain)
    template = BUSINESS_TEMPLATES.get(category, BUSINESS_TEMPLATES["Innovation"])
    revenue = list(template["revenue"])
    partners = list(template["partners"])
    key_metrics = list(template["key_metrics"])
    enablement = list(template["enablement"])
    pricing_strategy = template["pricing"]
    model = base_model or template["model"]
    if base_model and base_model.lower() not in template["model"].lower():
        model = f"{base_model} | {template['model']}"
    go_to_market = template["gtm"].format(audience=audience, domain=domain.lower())
    expansion_strategy = template["expansion"]
    if attributes.get("marketplace"):
        revenue.append("Curated marketplace commissions and vendor sponsorships")
        go_to_market += " Recruit a dual-sided design partner cohort to validate supply-demand resonance."
    if attributes.get("developer"):
        revenue.append("Usage-based API tier with premium tooling bundles")
        enablement.append("Developer-first documentation and SDK launch kit")
    if attributes.get("community"):
        revenue.append("Community membership and certification programs")
        go_to_market += " Launch ambassador-driven community drops and co-creation labs."
    if attributes.get("regulatory"):
        pricing_strategy += " Include compliance assurance fees for bespoke reviews."
        key_metrics.append("Regulatory milestone velocity")
    if attributes.get("enterprise"):
        partners.append("Enterprise enablement consultancies")
        enablement.append("Executive risk mitigation narrative")
    key_metrics = list(dict.fromkeys(key_metrics))
    revenue = list(dict.fromkeys(revenue))
    partners = list(dict.fromkeys(partners))
    enablement = list(dict.fromkeys(enablement))
    return {
        "model": model,
        "pricing_strategy": pricing_strategy,
        "revenue_streams": revenue,
        "go_to_market": go_to_market,
        "partners": partners,
        "key_metrics": key_metrics,
        "sales_enablement": enablement,
        "expansion_strategy": expansion_strategy,
        "complexity_profile": complexity.title(),
    }


def get_tech_playbook(domain: str, attributes: Dict[str, bool], complexity: str) -> Dict[str, object]:
    category = resolve_category(domain)
    template = TECH_TEMPLATES.get(category, TECH_TEMPLATES["Innovation"])
    stack = list(template["stack"])
    ai_components = list(template["ai"])
    service_components = list(template["service"])
    devops = list(template["devops"])
    integration = list(template["integration"])
    data_strategy = template["data"]
    architecture = template["architecture"]
    if attributes.get("realtime"):
        stack.append("Event streaming backbone (Kafka / Pulsar)")
        ai_components.append("Real-time signal prioritisation agent")
    if attributes.get("marketplace"):
        service_components.append("Supply-demand matching engine")
        ai_components.append("Marketplace liquidity forecaster")
    if attributes.get("hardware"):
        stack.append("IoT ingestion via MQTT/Greengrass")
        service_components.append("Edge device fleet manager")
    if attributes.get("mobile") and all("React Native" not in item for item in stack):
        stack.append("React Native / Expo mobile shell")
    if attributes.get("developer"):
        integration.append("CLI and SDK distribution pipeline")
        devops.append("Developer sandbox orchestration")
    if attributes.get("enterprise"):
        devops.append("Policy-as-code with Conftest / OPA")
    integration = list(dict.fromkeys(integration))
    devops = list(dict.fromkeys(devops))
    service_components = list(dict.fromkeys(service_components))
    return {
        "architecture": architecture,
        "stack": list(dict.fromkeys(stack)),
        "ai_components": list(dict.fromkeys(ai_components)),
        "service_components": service_components,
        "data_strategy": data_strategy,
        "devops": devops,
        "integration_points": integration,
        "resilience_notes": f"{complexity.title()} delivery profile with guardrails for {resolve_category(domain).lower()} workloads.",
    }


def get_design_palette(
    domain: str,
    audience: str,
    attributes: Dict[str, bool],
    complexity: str,
) -> Dict[str, object]:
    category = resolve_category(domain)
    template = DESIGN_TEMPLATES.get(category, DESIGN_TEMPLATES["Innovation"])
    principles = list(template["principles"])
    key_screens = list(template["key_screens"])
    interaction_patterns = list(template["interaction"])
    brand_voice = template["voice"]
    visual_language = template["visual"]
    tone = template["tone"]
    if attributes.get("developer"):
        interaction_patterns.append("Keyboard-first power commands")
        principles.append("Expose system status for advanced users")
    if attributes.get("regulatory"):
        principles.append("Surface compliance guardrails contextually")
        interaction_patterns.append("Audit-ready export flows")
    if attributes.get("marketplace"):
        key_screens.append("Supply & demand orchestration board")
    if attributes.get("community"):
        key_screens.append("Community pulse and ambassador missions")
    if "Enterprise" in audience:
        brand_voice = f"{brand_voice} with executive polish"
        tone = f"{tone}. Always tie outcomes to strategic imperatives."
    principles = list(dict.fromkeys(principles))
    key_screens = list(dict.fromkeys(key_screens))
    interaction_patterns = list(dict.fromkeys(interaction_patterns))
    return {
        "experience_principles": principles,
        "key_screens": key_screens,
        "interaction_patterns": interaction_patterns,
        "brand_voice": brand_voice,
        "visual_language": visual_language,
        "content_tone": tone,
        "design_complexity": complexity.title(),
    }


def get_market_playbook(
    domain: str,
    audience: str,
    attributes: Dict[str, bool],
    complexity: str,
) -> Dict[str, object]:
    category = resolve_category(domain)
    template = MARKET_TEMPLATES.get(category, MARKET_TEMPLATES["Innovation"])
    competitors = list(template["competitors"])
    differentiators = list(template["differentiators"])
    personas = list(template["personas"])
    channels = list(template["channels"])
    challenges = list(template["challenges"])
    positioning = template["positioning"]
    launch_strategy = template["launch"]
    if attributes.get("marketplace"):
        differentiators.append("Orchestrates dual-sided market dynamics with agent intelligence")
        challenges.append("Need to balance supply and demand narratives early")
    if attributes.get("regulatory"):
        differentiators.append("Compliance telemetry wired into every blueprint")
    if attributes.get("community"):
        channels.append("Community-led roundtables and ambassador streams")
    if attributes.get("developer"):
        personas.append("Lead platform engineer")
        channels.append("Open-source and developer relations campaigns")
    competitors = list(dict.fromkeys(competitors))
    differentiators = list(dict.fromkeys(differentiators))
    channels = list(dict.fromkeys(channels))
    challenges = list(dict.fromkeys(challenges))
    personas = list(dict.fromkeys(personas))
    return {
        "segment": template["segment"],
        "competitors": competitors,
        "differentiators": differentiators,
        "personas": personas,
        "marketing_channels": channels,
        "market_challenges": challenges,
        "launch_strategy": launch_strategy,
        "positioning_statement": positioning,
        "go_to_market_intent": complexity.title(),
    }


def get_timeline_blueprint(
    domain: str,
    attributes: Dict[str, bool],
    complexity: str,
) -> Dict[str, object]:
    windows = TIMELINE_WINDOWS[complexity]
    total_duration = TIMELINE_TOTAL[complexity]
    domain_lower = domain.lower()
    base_focus = [
        f"Immerse with {domain_lower} experts, surface pains, and quantify opportunity",
        f"Design signature {domain_lower} experiences and validation flows",
        f"Build core services, harden data pipelines, and wire observability",
        f"Run closed pilots, harvest ROI metrics, and iterate narrative + pricing",
        f"Launch publicly, operationalise GTM motions, and ready scale infrastructure",
    ]
    base_exit = [
        f"Validated {domain_lower} opportunity map and success metrics",
        "Experience prototypes tested with priority personas",
        "Production-ready MVP with telemetry + governance",
        "Pilot cohort delivering quantified wins",
        "Launch scorecard and next-wave backlog approved",
    ]
    owners = [
        "Product discovery lead",
        "Design + research squad",
        "Engineering pod",
        "Customer success & product marketing",
        "Founding leadership & revenue ops",
    ]
    if attributes.get("regulatory"):
        base_focus[0] += "; capture compliance constraints and stakeholders"
        base_focus[2] += "; embed audit logging & access controls"
        base_exit[2] += " with compliance review sign-off"
    if attributes.get("marketplace"):
        base_focus[1] += "; map supply-demand personas and incentives"
        base_focus[3] += "; balance both sides of the marketplace"
        base_exit[3] += " with dual-sided retention signals"
    if attributes.get("hardware"):
        base_focus[1] += "; align hardware/IoT roadmap"
        base_focus[2] += "; integrate edge device telemetry"
    if attributes.get("developer"):
        base_focus[2] += "; expose APIs and CLI early"
        base_focus[4] += "; launch developer advocacy runway"
    notes = TIMELINE_NOTES.get(resolve_category(domain), TIMELINE_NOTES["Innovation"])
    phases = []
    phase_names = [
        "Discovery & Insight Sprint",
        "Experience Blueprinting",
        "MVP Build & Instrumentation",
        "Pilot & Iteration Loop",
        "Launch & Scale Enablement",
    ]
    for idx, name in enumerate(phase_names):
        phases.append(
            {
                "phase": name,
                "duration": windows[idx],
                "focus": base_focus[idx],
                "owner": owners[idx],
                "exit_criteria": base_exit[idx],
            }
        )
    milestones = [
        "Narrative blueprint approved by executive sponsor",
        "Pilot cohort signed with clear success metrics",
        "AI reliability benchmarks achieved (>95% consistency)",
        "Public launch with quantified customer stories",
    ]
    milestone_note = notes.get("milestone")
    if milestone_note and milestone_note not in milestones:
        milestones.append(milestone_note)
    cadence_notes = (
        f"{complexity.title()} cadence with emphasis on {domain_lower} risk mitigation and momentum. "
        f"Launch focus: {notes.get('launch')}"
    )
    return {
        "phases": phases,
        "total_duration_weeks": total_duration,
        "milestones": milestones,
        "cadence_notes": cadence_notes,
    }
