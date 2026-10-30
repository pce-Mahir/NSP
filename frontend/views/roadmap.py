import requests
import streamlit as st

from frontend.services import api_client
from frontend.views.career_shared import (
    build_profile,
    render_goal_inputs,
    require_auth,
    show_backend_error,
)


def render() -> None:
    st.title("🗺️ Skills Gap & Learning Roadmap")
    st.markdown("A personalized 30 / 60 / 90-day learning plan automatically targeting your ATS skill gaps.")

    token = require_auth()
    if not token:
        return

    analysis = st.session_state.get("scorer_analysis")
    target_role, interests, level = render_goal_inputs()
    did_regenerate = st.session_state.pop("career_needs_regenerate", False)

    should_generate = did_regenerate or (
        bool(analysis) and "career_roadmap" not in st.session_state
    )

    if not analysis and "career_roadmap" not in st.session_state:
        if st.button("🚀 Build Roadmap with Gemini", type="primary", use_container_width=True):
            should_generate = True

    if should_generate:
        profile = build_profile(target_role, interests, level)
        try:
            with st.spinner("🤖 Automatically generating skills roadmap and 30/60/90-day plan from ATS data..."):
                data = api_client.career_roadmap(profile, token)
            st.session_state["career_roadmap"] = data
            st.rerun()
        except requests.RequestException as exc:
            show_backend_error(exc)
            return

    data = st.session_state.get("career_roadmap")
    if not data:
        return

    role_name = data.get("target_role") or target_role or "Target Role"
    readiness = data.get("readiness_score", 0)

    st.markdown(f"### 🎯 Readiness Assessment: **{role_name}**")
    st.progress(min(1.0, max(0.0, readiness / 100.0)))
    st.caption(f"Estimated role readiness: **{readiness}/100** based on verified skills vs role requirements.")

    st.markdown("### 🧩 Identified Skill Gaps")
    gaps = data.get("skill_gaps") or []
    if not gaps:
        st.write("No major skill gaps detected! Ready to apply.")
    for gap in gaps:
        priority = gap.get("priority", "medium").upper()
        badge_color = "#ef4444" if priority == "HIGH" else "#f59e0b" if priority == "MEDIUM" else "#10b981"
        st.markdown(
            f"**{gap.get('skill', 'Skill')}** &nbsp; "
            f"<span style='background-color:{badge_color}; color:white; padding:2px 8px; border-radius:10px; font-size:0.8rem;'>{priority}</span> &nbsp; "
            f"⏱️ ~{gap.get('estimated_weeks', '?')} weeks",
            unsafe_allow_html=True,
        )
        if gap.get("how_to_learn"):
            st.caption(f"💡 Strategy: {gap['how_to_learn']}")

    st.markdown("---")
    st.markdown("### 🗓️ Actionable 30 / 60 / 90-Day Execution Plan")
    t30, t60, t90 = st.tabs(["⚡ Days 1–30 (Immediate Gaps)", "📈 Days 31–60 (Project Depth)", "🎯 Days 61–90 (Mastery & Polish)"])
    with t30:
        for item in data.get("plan_30_days") or []:
            st.markdown(f"- {item}")
    with t60:
        for item in data.get("plan_60_days") or []:
            st.markdown(f"- {item}")
    with t90:
        for item in data.get("plan_90_days") or []:
            st.markdown(f"- {item}")

    resources = data.get("recommended_resources") or []
    if resources:
        st.markdown("---")
        st.markdown("### 📚 Recommended High-Yield Resources")
        for res in resources:
            res_type = res.get("type", "Course/Resource").capitalize()
            st.markdown(f"- 🔗 **{res.get('title', 'Resource')}** (`{res_type}`): {res.get('reason', '')}")
