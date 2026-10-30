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
    st.title("🧭 Personalized Career Pathways")
    st.markdown(
        "AI maps your ATS-analyzed resume to realistic next roles, skill gaps, and a 12-month trajectory."
    )

    token = require_auth()
    if not token:
        return

    analysis = st.session_state.get("scorer_analysis")
    target_role, interests, level = render_goal_inputs()
    did_regenerate = st.session_state.pop("career_needs_regenerate", False)

    should_generate = did_regenerate or (
        bool(analysis) and "career_pathways" not in st.session_state
    )

    if not analysis and "career_pathways" not in st.session_state:
        if st.button("🚀 Generate Pathways with Gemini", type="primary", use_container_width=True):
            should_generate = True

    if should_generate:
        profile = build_profile(target_role, interests, level)
        try:
            with st.spinner("🤖 Automatically analyzing ATS profile and building career pathways with Gemini..."):
                data = api_client.career_pathways(profile, token)
            st.session_state["career_pathways"] = data
            st.rerun()
        except requests.RequestException as exc:
            show_backend_error(exc)
            return

    data = st.session_state.get("career_pathways")
    if not data:
        return

    if data.get("profile_summary"):
        st.markdown("### 📋 Profile Snapshot")
        st.info(data["profile_summary"])

    st.markdown("### 🎯 Recommended Pathways")
    for path in data.get("pathways") or []:
        title = path.get("title", "Pathway")
        score = path.get("fit_score", 0)
        with st.expander(f"✨ {title} — Fit Score: {score}/100", expanded=True):
            st.markdown(f"**Why it fits:** {path.get('why_it_fits', '')}")
            c1, c2 = st.columns(2)
            with c1:
                st.markdown("💼 **Typical roles**")
                st.write(", ".join(path.get("typical_roles") or []) or "—")
                st.markdown("✅ **Skills you already have**")
                st.write(", ".join(path.get("skills_you_have") or []) or "—")
            with c2:
                st.markdown("🚀 **Skills to build**")
                st.write(", ".join(path.get("skills_to_build") or []) or "—")
                st.markdown("📈 **Industry Outlook**")
                st.write(path.get("outlook") or "—")
            st.markdown("🗓️ **Next 12-Month Milestones**")
            for item in path.get("next_12_months") or []:
                st.markdown(f"- {item}")
