"""Theming utilities for the Akcero Streamlit experience."""

from __future__ import annotations

from html import escape
from pathlib import Path
from typing import Any, Dict, Iterable

import streamlit as st

ASSETS_PATH = Path(__file__).resolve().parent.parent / "assets"


PRIMARY_COLOR = "#0077FF"
DARK_TEXT = "#0A0A0A"
LIGHT_BACKGROUND = "#F6F9FE"
CARD_BACKGROUND = "#FFFFFF"


def set_page() -> None:
    """Configure Streamlit page defaults and inject custom CSS."""

    logo_path = ASSETS_PATH / "logo.png"
    st.set_page_config(
        page_title="Akcero AI Product Builder",
        page_icon=str(logo_path) if logo_path.exists() else "✨",
        layout="wide",
        menu_items={
            "Get Help": "https://www.akcero.ai",
            "About": "Akcero AI Product Builder — From Idea to Product",
        },
    )

    css = f"""
    <style>
    :root {{
        --akcero-primary: {PRIMARY_COLOR};
        --akcero-bg: {LIGHT_BACKGROUND};
        --akcero-text: {DARK_TEXT};
    }}
    body, .stApp {{
        background: linear-gradient(180deg, rgba(0, 119, 255, 0.03) 0%, rgba(255, 255, 255, 0.9) 100%);
        color: var(--akcero-text);
    }}
    [data-testid="stSidebar"] {{
        background: #f4f7fb;
        border-right: 1px solid rgba(0, 119, 255, 0.08);
    }}
    .akcero-hero {{
        background: radial-gradient(circle at top left, rgba(0,119,255,0.18), rgba(0,119,255,0.05));
        border-radius: 24px;
        padding: 2.8rem 3.2rem;
        margin-bottom: 1.8rem;
        box-shadow: 0 32px 48px rgba(0, 45, 110, 0.12);
        position: relative;
        overflow: hidden;
    }}
    .akcero-hero:before {{
        content: "";
        position: absolute;
        top: -40px;
        right: -40px;
        width: 220px;
        height: 220px;
        background: rgba(0,119,255,0.15);
        filter: blur(60px);
        border-radius: 50%;
    }}
    .akcero-hero h1 {{
        color: {PRIMARY_COLOR};
        font-size: 2.45rem;
        margin-bottom: 0.4rem;
    }}
    .akcero-hero p {{
        font-size: 1.1rem;
        opacity: 0.85;
        max-width: 720px;
    }}
    .akcero-chip-row {{
        margin-top: 0.6rem;
        display: flex;
        flex-wrap: wrap;
        gap: 0.45rem;
    }}
    .akcero-chip {{
        display: inline-flex;
        align-items: center;
        padding: 0.35rem 0.75rem;
        background: rgba(0, 119, 255, 0.12);
        border-radius: 999px;
        font-size: 0.82rem;
        color: {PRIMARY_COLOR};
        border: 1px solid rgba(0,119,255,0.18);
    }}
    .akcero-status-grid {{
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
        gap: 0.8rem;
        margin-bottom: 1.2rem;
    }}
    .akcero-idea-hint {{
        background: rgba(255, 255, 255, 0.8);
        border: 1px solid rgba(0,119,255,0.15);
        border-radius: 18px;
        padding: 1.2rem 1.4rem;
        box-shadow: 0 14px 28px rgba(4, 42, 90, 0.08);
    }}
    .akcero-idea-hint h4 {{
        margin-top: 0;
        color: {PRIMARY_COLOR};
        font-size: 1.05rem;
        margin-bottom: 0.5rem;
    }}
    .akcero-idea-hint p {{
        font-size: 0.95rem;
        margin-bottom: 0.8rem;
    }}
    .akcero-card {{
        background: {CARD_BACKGROUND};
        border-radius: 18px;
        padding: 1.4rem 1.6rem;
        box-shadow: 0 18px 38px rgba(21, 72, 150, 0.08);
        border: 1px solid rgba(0, 119, 255, 0.08);
        min-height: 200px;
    }}
    .akcero-card h3 {{
        color: {PRIMARY_COLOR};
        font-size: 1.28rem;
        margin-bottom: 0.75rem;
        display: flex;
        align-items: center;
        gap: 0.55rem;
    }}
    .akcero-card-icon {{
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: 38px;
        height: 38px;
        border-radius: 14px;
        background: rgba(0, 119, 255, 0.12);
        border: 1px solid rgba(0, 119, 255, 0.18);
        font-size: 1.2rem;
    }}
    .akcero-pill {{
        display: inline-flex;
        align-items: center;
        padding: 0.25rem 0.7rem;
        background: rgba(0, 119, 255, 0.1);
        border-radius: 999px;
        font-size: 0.8rem;
        color: {PRIMARY_COLOR};
        margin-right: 0.4rem;
        margin-bottom: 0.4rem;
    }}
    .akcero-summary {{
        background: {LIGHT_BACKGROUND};
        border-left: 4px solid {PRIMARY_COLOR};
        padding: 1.5rem;
        border-radius: 12px;
        font-size: 1.05rem;
        box-shadow: inset 0 0 0 1px rgba(0, 119, 255, 0.12);
    }}
    .akcero-pitch {{
        background: linear-gradient(135deg, rgba(0,119,255,0.12), rgba(0,119,255,0.03));
        border: 1px solid rgba(0, 119, 255, 0.25);
        border-radius: 16px;
        padding: 1.2rem;
        margin-top: 1rem;
    }}
    .akcero-download-row {{
        display: flex;
        gap: 1rem;
        flex-wrap: wrap;
        margin-top: 1.2rem;
    }}
    .akcero-section {{
        margin-bottom: 1.1rem;
        border-bottom: 1px solid rgba(0, 119, 255, 0.08);
        padding-bottom: 0.6rem;
    }}
    .akcero-section:last-child {{
        border-bottom: none;
        padding-bottom: 0;
        margin-bottom: 0;
    }}
    .akcero-section-title {{
        font-size: 0.78rem;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        color: rgba(10, 10, 10, 0.6);
        font-weight: 600;
        margin-bottom: 0.45rem;
    }}
    .akcero-bullet {{
        display: flex;
        gap: 0.45rem;
        align-items: flex-start;
        background: rgba(0, 119, 255, 0.06);
        border: 1px solid rgba(0, 119, 255, 0.12);
        border-radius: 12px;
        padding: 0.45rem 0.6rem;
        margin-bottom: 0.35rem;
        font-size: 0.95rem;
        line-height: 1.45;
        color: #1a2440;
    }}
    .akcero-bullet:last-child {{
        margin-bottom: 0;
    }}
    .akcero-bullet-icon {{
        color: {PRIMARY_COLOR};
        font-size: 0.65rem;
        margin-top: 0.35rem;
    }}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)


def render_card(title: str, items: Iterable[str], icon: str) -> None:
    """Render a consistent card layout for agent output."""

    with st.container():
        st.markdown(
            f"<div class='akcero-card'><h3><span class='akcero-card-icon'>{escape(icon)}</span>{escape(title)}</h3>",
            unsafe_allow_html=True,
        )
        for item in items:
            st.markdown(f"<div class='akcero-pill'>{escape(str(item))}</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)


def render_rich_card(title: str, icon: str, body: Dict[str, Any]) -> None:
    """Render structured content where values require more than pills."""

    with st.container():
        st.markdown(
            f"<div class='akcero-card'><h3><span class='akcero-card-icon'>{escape(icon)}</span>{escape(title)}</h3>",
            unsafe_allow_html=True,
        )
        sections: list[str] = []
        for key, value in body.items():
            label = escape(key.replace("_", " ").title())
            section_parts: list[str] = [f"<div class='akcero-section'><div class='akcero-section-title'>{label}</div>"]

            if isinstance(value, list) and value and all(isinstance(item, str) for item in value):
                if all(len(item) <= 40 for item in value):
                    chips = "".join(
                        f"<span class='akcero-chip'>{escape(item)}</span>" for item in value
                    )
                    section_parts.append(f"<div class='akcero-chip-row'>{chips}</div>")
                else:
                    for entry in value:
                        entry_text = escape(str(entry))
                        section_parts.append(
                            f"<div class='akcero-bullet'><span class='akcero-bullet-icon'>◆</span>{entry_text}</div>"
                        )
            elif isinstance(value, list):
                for entry in value:
                    if isinstance(entry, dict):
                        parts = [
                            f"{escape(inner_key.replace('_', ' ').title())}: {escape(str(inner_value))}"
                            for inner_key, inner_value in entry.items()
                        ]
                        entry_text = " | ".join(parts)
                    else:
                        entry_text = escape(str(entry))
                    section_parts.append(
                        f"<div class='akcero-bullet'><span class='akcero-bullet-icon'>◆</span>{entry_text}</div>"
                    )
            elif isinstance(value, dict):
                for entry_key, entry_value in value.items():
                    entry_text = (
                        f"{escape(entry_key.replace('_', ' ').title())}: {escape(str(entry_value))}"
                    )
                    section_parts.append(
                        f"<div class='akcero-bullet'><span class='akcero-bullet-icon'>◆</span>{entry_text}</div>"
                    )
            else:
                section_parts.append(
                    f"<div class='akcero-bullet'><span class='akcero-bullet-icon'>◆</span>{escape(str(value))}</div>"
                )

            section_parts.append("</div>")
            sections.append("".join(section_parts))

        st.markdown("".join(sections), unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
