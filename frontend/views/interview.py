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
    st.title("🎤 Tailored Interview Coach")
    st.markdown(
        "AI generates role-specific interview questions with STAR-framework sample answers grounded in your ATS-analyzed resume."
    )

    token = require_auth()
    if not token:
        return

    analysis = st.session_state.get("scorer_analysis")
    target_role, interests, level = render_goal_inputs()
    did_regenerate = st.session_state.pop("career_needs_regenerate", False)

    should_generate = did_regenerate or (
        bool(analysis) and "career_interview" not in st.session_state
    )

    if not analysis and "career_interview" not in st.session_state:
        if st.button("🚀 Generate Interview Questions with Gemini", type="primary", use_container_width=True):
            should_generate = True

    if should_generate:
        profile = build_profile(target_role, interests, level)
        try:
            with st.spinner("🤖 Automatically tailoring interview questions and sample answers to your resume..."):
                data = api_client.career_interview(profile, token)
            st.session_state["career_interview"] = data
            st.rerun()
        except requests.RequestException as exc:
            show_backend_error(exc)
            return

    data = st.session_state.get("career_interview")
    if not data:
        return

    role_label = data.get("target_role") or target_role or "your target role"
    st.markdown(f"### 🎯 Interview Simulation for **{role_label}**")
    if data.get("focus_areas"):
        st.info("💡 **Core Competencies & Focus Areas:** " + ", ".join(data["focus_areas"]))

    st.markdown("---")
    for i, q in enumerate(data.get("questions") or [], start=1):
        q_type = q.get("type", "Question").upper()
        badge_color = "#3b82f6" if "TECH" in q_type else "#8b5cf6" if "BEHAV" in q_type else "#06b6d4"
        with st.expander(f"{i}. [{q_type}] {q.get('question', '')}", expanded=(i <= 2)):
            st.markdown(f"**🎯 Evaluator Context (Why this matters):** {q.get('why_it_matters', '')}")
            st.markdown("💬 **Exemplary Answer (Anchored in your profile):**")
            st.info(q.get("sample_answer", ""))
            tips = q.get("tips") or []
            if tips:
                st.markdown("📌 **Interview Tips & Talking Points:**")
                for tip in tips:
                    st.markdown(f"- {tip}")
