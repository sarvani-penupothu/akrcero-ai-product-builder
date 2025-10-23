"""Akcero AI Product Builder — Streamlit Edition."""

from __future__ import annotations

import asyncio
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Any, Coroutine, Dict, Optional, Tuple

import streamlit as st
from dotenv import load_dotenv

from agents import (
    BusinessAgent,
    DesignAgent,
    IdeaAgent,
    MarketAgent,
    TechAgent,
    TimelineAgent,
)
from core.umbrella_agent import UmbrellaAgent
from core.deps import get_llm
from core.schemas import ProductBlueprint
from utils.report_generator import build_pdf
from utils.storage import StorageManager, get_db
from utils.theming import render_rich_card, set_page

load_dotenv()
set_page()

AGENT_CARD_METADATA: Dict[str, Tuple[str, str]] = {
    "idea": ("Problem & Solution", "💡"),
    "business": ("Business Model", "💼"),
    "tech": ("Tech Stack & Architecture", "🛠️"),
    "design": ("UI/UX Suggestions", "🎨"),
    "market": ("Market & Competitors", "📊"),
    "timeline": ("Roadmap & Timeline", "🗺️"),
}

SAMPLE_IDEA = (
    "An AI-native studio that helps climate-tech founders transform raw ideas into investor-ready product "
    "roadmaps. Specialized agents validate market gaps, propose data-backed business models, design immersive "
    "experiences, and sequence delivery with measurable milestones."
)


@st.cache_resource(show_spinner=False)
def init_services() -> Tuple[UmbrellaAgent, StorageManager]:
    """Instantiate LLM, agents, umbrella orchestrator, and storage backend."""

    llm = get_llm()
    idea_agent = IdeaAgent(llm)
    business_agent = BusinessAgent(llm)
    tech_agent = TechAgent(llm)
    design_agent = DesignAgent(llm)
    market_agent = MarketAgent(llm)
    timeline_agent = TimelineAgent(llm)

    umbrella = UmbrellaAgent(
        idea_agent=idea_agent,
        business_agent=business_agent,
        tech_agent=tech_agent,
        design_agent=design_agent,
        market_agent=market_agent,
        timeline_agent=timeline_agent,
        llm=llm,
    )
    storage = get_db()
    return umbrella, storage


def _ensure_session_state() -> None:
    """Initialize expected session state keys if they are missing."""

    defaults = {
        "idea_input": "",
        "blueprint": None,
        "agents_output": None,
        "pitch_text": "",
        "latest_run_id": "",
        "loaded_run_id": "",
        "pitch_mode": False,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


async def _generate_blueprint(
    umbrella: UmbrellaAgent,
    idea_text: str,
    *,
    pitch_mode: bool,
    status_slots: Dict[str, Any],
) -> Dict[str, Any]:
    """Run the umbrella agent asynchronously with progress callbacks."""

    def update(agent_name: str, status: str) -> None:
        placeholder = status_slots.get(agent_name)
        if not placeholder:
            return
        if status == "running":
            placeholder.info(f"{agent_name} is crafting insights…")
        else:
            placeholder.success(f"{agent_name} completed")

    return await umbrella.build_blueprint(
        idea_text,
        pitch_mode=pitch_mode,
        callback=update,
    )


def _run_async(coro: Coroutine[Any, Any, Any]) -> Any:
    """Run an asyncio coroutine with a safe fallback loop."""

    try:
        return asyncio.run(coro)
    except RuntimeError:
        loop = asyncio.new_event_loop()
        try:
            return loop.run_until_complete(coro)
        finally:
            loop.close()


def _render_history(storage: StorageManager) -> None:
    """Display run history in the sidebar and allow loading previous results."""

    with st.sidebar:
        st.image("assets/logo.png", use_column_width=True)
        st.markdown("### Akcero AI Product Builder")
        st.caption("From Idea to Product.")

        history = storage.list_runs(limit=20)
        if history:
            options = {f"{entry['created_at'][:16]} — {entry['idea_text'][:60]}": entry["id"] for entry in history}
            selection = st.selectbox(
                "Run Library",
                options=["- New Run -"] + list(options.keys()),
                key="history_select",
            )
            if selection and selection != "- New Run -":
                run_id = options[selection]
                if st.session_state.get("loaded_run_id") != run_id:
                    record = storage.get_run(run_id)
                    if record:
                        st.session_state["idea_input"] = record.get("idea_text", "")
                        st.session_state["blueprint"] = record.get("blueprint")
                        st.session_state["agents_output"] = record.get("agents_output")
                        st.session_state["pitch_text"] = record.get("pitch", "")
                        st.session_state["loaded_run_id"] = run_id
                        st.session_state["latest_run_id"] = run_id
                        st.experimental_rerun()
        else:
            st.caption("Your generated product blueprints will appear here.")


def _render_hero() -> None:
    """Showcase the hero section with product positioning."""

    st.markdown(
        """
        <div class="akcero-hero">
            <h1>Akcero AI Product Builder</h1>
            <p>Go from raw idea to a multi-dimensional product blueprint crafted by a squad of specialist AI agents.
            Capture the problem, model the business, architect the tech, and plan the launch in minutes.</p>
            <div class="akcero-chip-row">
                <span class="akcero-chip">IdeaAgent → Narrative Clarity</span>
                <span class="akcero-chip">BusinessAgent → Monetization Strategy</span>
                <span class="akcero-chip">TechAgent → Architecture Stack</span>
                <span class="akcero-chip">DesignAgent → Signature UX</span>
                <span class="akcero-chip">MarketAgent → Positioning Intel</span>
                <span class="akcero-chip">TimelineAgent → Launch Roadmap</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _display_cards(blueprint: ProductBlueprint) -> None:
    """Render the agent cards for the blueprint output."""

    if not blueprint:
        return

    columns = st.columns(2)
    card_order = [
        ("idea", blueprint.get("idea", {})),
        ("business", blueprint.get("business_model", {})),
        ("tech", blueprint.get("tech_stack", {})),
        ("design", blueprint.get("ui_design", {})),
        ("market", blueprint.get("market_analysis", {})),
        ("timeline", blueprint.get("timeline", {})),
    ]
    for idx, (key, data) in enumerate(card_order):
        title, icon = AGENT_CARD_METADATA[key]
        formatted: Dict[str, Any] = {}
        if isinstance(data, dict):
            for k, v in data.items():
                label = k.replace("_", " ").title()
                formatted[label] = v
        column = columns[idx % 2]
        with column:
            render_rich_card(title, icon, formatted)

    summary = blueprint.get("summary", "")
    if summary:
        st.markdown("<div class='akcero-summary'><strong>Executive Summary</strong><br/>{}</div>".format(summary), unsafe_allow_html=True)


def _render_pitch(pitch_text: str) -> None:
    """Render the optional elevator pitch block."""

    if not pitch_text:
        return
    st.markdown(
        f"<div class='akcero-pitch'><strong>Elevator Pitch</strong><br/>{pitch_text}</div>",
        unsafe_allow_html=True,
    )
    st.code(pitch_text)


def _render_cta_row(blueprint: ProductBlueprint, storage: StorageManager, pitch: str) -> None:
    """Display the CTA buttons for PDF download and saving runs."""

    if not blueprint:
        return

    col1, col2 = st.columns([2, 1])

    with col1:
        tmp_path: Optional[Path] = None
        try:
            tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf", dir=Path("storage"))
            tmp_path = Path(tmp_file.name)
            tmp_file.close()
            build_pdf(blueprint, tmp_path)
            with tmp_path.open("rb") as handle:
                pdf_data = handle.read()
            st.download_button(
                label="Download PDF",
                data=pdf_data,
                file_name=f"akcero_blueprint_{datetime.utcnow().strftime('%Y%m%d_%H%M')}.pdf",
                mime="application/pdf",
            )
        except Exception as exc:
            st.error(f"Unable to prepare PDF: {exc}")
        finally:
            if tmp_path and tmp_path.exists():
                tmp_path.unlink(missing_ok=True)

    with col2:
        if st.button("Save to Library", type="secondary"):
            try:
                run_id = storage.save_run(
                    st.session_state.get("idea_input", ""),
                    st.session_state.get("agents_output", {}),
                    blueprint,
                    pitch,
                )
                st.session_state["latest_run_id"] = run_id
                st.success("Blueprint saved to your library.")
            except Exception as exc:
                st.error(f"Unable to save this blueprint: {exc}")


def main() -> None:
    """Streamlit application entrypoint."""

    umbrella, storage = init_services()
    _ensure_session_state()
    _render_history(storage)

    _render_hero()

    idea_col, helper_col = st.columns([3, 1.4])
    with idea_col:
        st.markdown("#### Compose your vision")
        st.session_state["idea_input"] = st.text_area(
            "Your startup idea",
            value=st.session_state.get("idea_input", ""),
            height=220,
            placeholder="Example: An AI platform that turns founder ideas into product roadmaps by orchestrating specialized agents…",
            label_visibility="collapsed",
        )
    with helper_col:
        st.markdown(
            f"""
            <div class='akcero-idea-hint'>
                <h4>Need inspiration?</h4>
                <p>{SAMPLE_IDEA}</p>
                <p><strong>Pro tip:</strong> mention target audience, market, and any launch constraints for richer outputs.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button("Use Sample Idea", type="secondary"):
            st.session_state["idea_input"] = SAMPLE_IDEA
            st.experimental_rerun()

    cta_col1, cta_col2 = st.columns([2.4, 1])
    with cta_col1:
        generate_clicked = st.button(
            "✨ Generate Blueprint", type="primary", use_container_width=True
        )
    with cta_col2:
        st.session_state["pitch_mode"] = st.checkbox(
            "Pitch Mode (30-second elevator pitch)",
            value=st.session_state.get("pitch_mode", False),
            help="Crafts a tight founder pitch from your blueprint.",
        )

    if generate_clicked:
        idea_text = st.session_state.get("idea_input", "").strip()
        if not idea_text:
            st.warning("Please share your idea so the agents can get to work.")
        else:
            row_one = st.columns(3)
            row_two = st.columns(3)
            status_map = {
                "IdeaAgent": row_one[0].empty(),
                "BusinessAgent": row_one[1].empty(),
                "TechAgent": row_one[2].empty(),
                "DesignAgent": row_two[0].empty(),
                "MarketAgent": row_two[1].empty(),
                "TimelineAgent": row_two[2].empty(),
            }
            for placeholder in status_map.values():
                placeholder.info("Queued…")

            with st.spinner("Agents collaborating on your blueprint…"):
                result = _run_async(
                    _generate_blueprint(
                        umbrella,
                        idea_text,
                        pitch_mode=st.session_state.get("pitch_mode", False),
                        status_slots=status_map,
                    )
                )

            blueprint: ProductBlueprint = result.get("blueprint", {})  # type: ignore[assignment]
            agents_output = result.get("agents", {})
            pitch_text = result.get("pitch", "")

            st.session_state["blueprint"] = blueprint
            st.session_state["agents_output"] = agents_output
            st.session_state["pitch_text"] = pitch_text

            try:
                run_id = storage.save_run(idea_text, agents_output, blueprint, pitch_text)
                st.session_state["latest_run_id"] = run_id
                st.session_state["loaded_run_id"] = run_id
                st.success("Fresh blueprint generated and saved to your library.")
            except Exception as exc:
                st.warning(f"Blueprint generated but could not be saved automatically: {exc}")

    blueprint_state: ProductBlueprint = st.session_state.get("blueprint")  # type: ignore[assignment]
    if blueprint_state:
        _display_cards(blueprint_state)
        _render_pitch(st.session_state.get("pitch_text", ""))
        _render_cta_row(blueprint_state, storage, st.session_state.get("pitch_text", ""))


if __name__ == "__main__":
    main()
