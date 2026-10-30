from typing import Any, Dict, Tuple
import requests
import streamlit as st


def show_backend_error(exc: Exception) -> None:
    if isinstance(exc, requests.ConnectionError):
        st.error("Could not reach the backend. Is it running on port 8000?")
    elif isinstance(exc, requests.Timeout):
        st.error("The Gemini request took too long. Try again in a moment.")
    elif isinstance(exc, requests.HTTPError) and exc.response is not None:
        try:
            detail = exc.response.json().get("detail", exc.response.text)
        except ValueError:
            detail = exc.response.text
        st.error(f"Backend returned {exc.response.status_code}: {detail}")
    else:
        st.error(f"Unexpected error: {exc}")


def require_auth() -> str | None:
    access_token = st.session_state.get("access_token")
    if not access_token:
        st.warning("Sign in from the sidebar (or continue as guest) to use career guidance.")
        return None
    return access_token


def infer_target_role(analysis: Dict[str, Any]) -> str:
    """Infer target role automatically from the ATS analysis."""
    if not analysis:
        return ""
    # 1. Direct field from backend
    if analysis.get("target_role"):
        return analysis["target_role"]
    # 2. Parsed profile field
    profile = analysis.get("parsed_profile") or {}
    if profile.get("target_role"):
        return profile["target_role"]
    # 3. JD job title if present
    jd_comp = analysis.get("jd_comparison") or analysis.get("jd_match_analysis") or {}
    if isinstance(jd_comp, dict) and jd_comp.get("job_title"):
        return jd_comp["job_title"]
    # 4. First experience job title
    exps = profile.get("experience") or []
    if exps and isinstance(exps, list) and isinstance(exps[0], dict) and exps[0].get("job_title"):
        return exps[0]["job_title"]
    # 5. First skill
    skills = profile.get("skills") or analysis.get("skills") or []
    if skills:
        return f"{skills[0]} Specialist"
    return "Software Engineer"


def infer_experience_level(analysis: Dict[str, Any]) -> str:
    """Infer candidate experience level from parsed duration."""
    if not analysis:
        return "Mid-level"
    months = analysis.get("experience_months", 0)
    profile = analysis.get("parsed_profile") or {}
    if not months and profile.get("experience"):
        months = sum(int(e.get("duration_months", 0)) for e in profile.get("experience", []) if isinstance(e, dict))

    if months <= 12:
        return "Entry-level"
    elif months <= 48:
        return "Mid-level"
    else:
        return "Senior"


def infer_interests(analysis: Dict[str, Any]) -> str:
    """Infer interests and focus areas from ATS missing keywords and strengths."""
    if not analysis:
        return ""
    missing = analysis.get("missing_keywords") or []
    strengths = analysis.get("strengths") or []
    parts = []
    if missing:
        parts.append(f"Strengthen key skill gaps identified by ATS: {', '.join(missing[:4])}")
    if strengths:
        parts.append(f"Build upon strength in {strengths[0].lower()}")
    return ". ".join(parts) if parts else "Accelerate technical growth and target high-impact roles."


def render_goal_inputs() -> Tuple[str, str, str, bool]:
    """
    Renders automatic ATS-driven configuration with an optional customize expander.
    Returns (target_role, career_interests, experience_level, did_regenerate).
    """
    analysis = st.session_state.get("scorer_analysis") or {}
    profile = analysis.get("parsed_profile") or {}

    # Initialize inferred values if not already explicitly customized
    if not st.session_state.get("career_target_role"):
        st.session_state["career_target_role"] = infer_target_role(analysis)
    if not st.session_state.get("career_level"):
        st.session_state["career_level"] = infer_experience_level(analysis)
    if not st.session_state.get("career_interests"):
        st.session_state["career_interests"] = infer_interests(analysis)

    default_role = st.session_state.get("career_target_role", "")
    default_interests = st.session_state.get("career_interests", "")
    default_level = st.session_state.get("career_level", "Mid-level")

    has_ats_data = bool(analysis)
    did_regenerate = False

    if has_ats_data:
        cand_name = profile.get("name") or "Candidate"
        skills_count = len(profile.get("skills") or analysis.get("skills") or [])
        ats_score = analysis.get("ats_score", analysis.get("ATS_score", 0))
        st.success(
            f"🎯 **Automated Career Guidance Active** — Tailored directly to your ATS resume analysis: "
            f"**{cand_name}** | ATS Score: **{ats_score:.0f}/100** | Target: **{default_role}** ({default_level}) | **{skills_count}** skills parsed."
        )
    else:
        st.info("💡 **Tip:** Score a resume on the **ATS Scorer** page first to get automatically generated personalized career guidance.")

    with st.expander("⚙️ Customize Goals & Role Inputs (Optional)", expanded=not has_ats_data):
        col1, col2 = st.columns(2)
        with col1:
            target_role = st.text_input(
                "Target role or pathway",
                value=default_role,
                placeholder="e.g. Data Analyst, Backend Engineer, Solutions Architect",
                key="target_role_input",
            )
        with col2:
            level_options = ["Student / intern", "Entry-level", "Mid-level", "Senior", "Career switcher"]
            level_index = level_options.index(default_level) if default_level in level_options else 2
            experience_level = st.selectbox(
                "Experience level",
                level_options,
                index=level_index,
                key="experience_level_input",
            )
        career_interests = st.text_area(
            "Interests, constraints, or goals",
            value=default_interests,
            placeholder="e.g. prefer remote work, interested in ML pipelines, transitioning to engineering management",
            height=80,
            key="career_interests_input",
        )

        if st.button("🔄 Apply Custom Settings & Regenerate", type="secondary", use_container_width=True):
            st.session_state["career_target_role"] = target_role
            st.session_state["career_interests"] = career_interests
            st.session_state["career_level"] = experience_level
            st.session_state["career_needs_regenerate"] = True
            st.rerun()

    # Persist values
    st.session_state["career_target_role"] = target_role
    st.session_state["career_interests"] = career_interests
    st.session_state["career_level"] = experience_level

    return target_role, career_interests, experience_level


def build_profile(target_role: str, career_interests: str, experience_level: str) -> Dict[str, Any]:
    analysis = st.session_state.get("scorer_analysis") or {}
    parsed = dict(analysis.get("parsed_profile") or {})
    if not parsed.get("skills"):
        parsed["skills"] = analysis.get("skills") or []
    parsed["target_role"] = target_role
    parsed["career_interests"] = career_interests
    parsed["experience_level"] = experience_level
    parsed["job_description"] = st.session_state.get("last_job_description", "")
    return parsed
