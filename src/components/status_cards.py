"""Reusable metric and status card renderers."""

import streamlit as st

from src.utils.constants import STATUS_COLORS, ProgramStatus


def metric_card(label: str, value: str, delta: str | None = None, color: str = "#1B6AC9"):
    """Render a single metric card with optional delta."""
    delta_html = ""
    if delta:
        delta_color = "#2E8B57" if not delta.startswith("-") else "#C0392B"
        delta_html = f'<div style="font-size:0.85rem;color:{delta_color};">{delta}</div>'

    st.markdown(
        f"""
        <div style="
            background: white;
            border-left: 4px solid {color};
            border-radius: 8px;
            padding: 1rem 1.2rem;
            box-shadow: 0 1px 3px rgba(0,0,0,0.08);
            margin-bottom: 0.5rem;
        ">
            <div style="font-size:0.8rem;color:#6B7280;text-transform:uppercase;
                         letter-spacing:0.05em;">{label}</div>
            <div style="font-size:1.8rem;font-weight:700;color:{color};
                         margin:0.2rem 0;">{value}</div>
            {delta_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


def status_badge(status: ProgramStatus) -> str:
    """Return an HTML badge string for a program status."""
    color = STATUS_COLORS.get(status, "#95A5A6")
    return (
        f'<span style="background:{color};color:white;padding:3px 10px;'
        f'border-radius:12px;font-size:0.75rem;font-weight:600;">'
        f"{status.value}</span>"
    )


def program_card(name: str, status: ProgramStatus, pct: float, department: str, owner: str):
    """Render a program summary card."""
    color = STATUS_COLORS.get(status, "#95A5A6")
    bar_color = color
    st.markdown(
        f"""
        <div style="
            background: white;
            border-radius: 10px;
            padding: 1.2rem;
            box-shadow: 0 1px 4px rgba(0,0,0,0.08);
            margin-bottom: 0.8rem;
            border-top: 3px solid {color};
        ">
            <div style="display:flex;justify-content:space-between;align-items:center;">
                <div style="font-size:1.05rem;font-weight:600;color:#1A1A2E;">{name}</div>
                {status_badge(status)}
            </div>
            <div style="font-size:0.8rem;color:#6B7280;margin:0.4rem 0;">
                {department} &middot; {owner}
            </div>
            <div style="background:#E5E7EB;border-radius:6px;height:8px;margin-top:0.6rem;">
                <div style="background:{bar_color};width:{pct}%;height:100%;
                            border-radius:6px;transition:width 0.3s;"></div>
            </div>
            <div style="font-size:0.75rem;color:#6B7280;margin-top:0.3rem;text-align:right;">
                {pct:.0f}% complete
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
