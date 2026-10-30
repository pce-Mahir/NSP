from typing import Any, Dict
import streamlit as st


def display_career_guidance_section(analysis: Dict[str, Any]) -> None:
    """
    Renders an integrated Career Guidance section directly inside the ATS Results Dashboard.
    Connects ATS scoring output directly to Career Pathways, Roadmap, Interview, and Advisor.
    """
    st.markdown("## 🚀 AI Career Guidance & Growth Roadmap")
    st.markdown(
        "Your resume has been analyzed! Based on your parsed skills, experience depth, and ATS keyword match, "
        "Gemini can automatically generate your personalized career plan below."
    )

    profile = analysis.get("parsed_profile") or {}
    target_role = analysis.get("target_role") or profile.get("target_role") or "Your Target Field"
    missing_count = len(analysis.get("missing_keywords") or [])
    skills_count = len(profile.get("skills") or analysis.get("skills") or [])

    st.info(
        f"🎯 **Automated Profile Active:** Target Role: **{target_role}** | "
        f"**{skills_count}** verified skills | **{missing_count}** ATS keyword opportunities identified."
    )

    col1, col2 = st.columns(2)

    with col1:
        st.markdown(
            """
            <div style="background:#f8fafc; border:1px solid #e2e8f0; border-radius:12px; padding:18px; margin-bottom:12px;">
                <h4 style="margin:0 0 8px 0; color:#1e293b;">🧭 Career Pathways</h4>
                <p style="color:#64748b; font-size:0.9rem; margin-bottom:14px;">
                    Discover 3 to 5 realistic next roles, fit scores, skill gaps to bridge, and a 12-month career progression roadmap.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button("Explore Career Pathways ➔", key="btn_goto_pathways", use_container_width=True, type="primary"):
            st.session_state.current_view = "pathways"
            st.rerun()

        st.markdown(
            """
            <div style="background:#f8fafc; border:1px solid #e2e8f0; border-radius:12px; padding:18px; margin-bottom:12px; margin-top:16px;">
                <h4 style="margin:0 0 8px 0; color:#1e293b;">🎤 Interview Coach</h4>
                <p style="color:#64748b; font-size:0.9rem; margin-bottom:14px;">
                    Practice technical, behavioral, and situational questions with tailored sample answers grounded in your real projects.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button("Practice Interview Questions ➔", key="btn_goto_interview", use_container_width=True):
            st.session_state.current_view = "interview"
            st.rerun()

    with col2:
        st.markdown(
            """
            <div style="background:#f8fafc; border:1px solid #e2e8f0; border-radius:12px; padding:18px; margin-bottom:12px;">
                <h4 style="margin:0 0 8px 0; color:#1e293b;">🗺️ 30 / 60 / 90-Day Roadmap</h4>
                <p style="color:#64748b; font-size:0.9rem; margin-bottom:14px;">
                    Get an actionable execution plan targeting the missing ATS keywords and skills with recommended learning resources.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button("View Learning Roadmap ➔", key="btn_goto_roadmap", use_container_width=True, type="primary"):
            st.session_state.current_view = "roadmap"
            st.rerun()

        st.markdown(
            """
            <div style="background:#f8fafc; border:1px solid #e2e8f0; border-radius:12px; padding:18px; margin-bottom:12px; margin-top:16px;">
                <h4 style="margin:0 0 8px 0; color:#1e293b;">💬 AI Career Advisor</h4>
                <p style="color:#64748b; font-size:0.9rem; margin-bottom:14px;">
                    Chat in real-time about career pivots, salary negotiations, resume bullet improvements, and career strategy.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button("Chat with Career Advisor ➔", key="btn_goto_advisor", use_container_width=True):
            st.session_state.current_view = "advisor"
            st.rerun()
