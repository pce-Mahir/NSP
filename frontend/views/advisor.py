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
    st.title("💬 AI Career Advisor")
    st.markdown("Direct conversation with Gemini grounded in your ATS resume data, career goals, and skill gaps.")

    token = require_auth()
    if not token:
        return

    analysis = st.session_state.get("scorer_analysis")
    target_role, interests, level = render_goal_inputs()

    if "career_chat" not in st.session_state or not st.session_state["career_chat"]:
        profile_data = (analysis or {}).get("parsed_profile") or {}
        cand_name = profile_data.get("name") or "there"
        ats_score = (analysis or {}).get("ats_score", (analysis or {}).get("ATS_score", 0))
        role_text = target_role or "your target role"

        if analysis:
            intro_msg = (
                f"Hello {cand_name}! 👋 I've loaded your ATS resume analysis (ATS Score: **{ats_score:.0f}/100**) "
                f"targeting **{role_text}** ({level}). "
                f"I can help you address skill gaps, prepare for interviews, or strategize your next career move. "
                f"What would you like to discuss today?"
            )
        else:
            intro_msg = (
                "Hello! 👋 I'm your AI Career Advisor. Ask me anything about career pathways, "
                "resume positioning, interview prep, or skills to build. "
                "You can also score your resume on the ATS Scorer page anytime to anchor our advice in your exact background!"
            )
        st.session_state["career_chat"] = [{"role": "assistant", "content": intro_msg}]

    # Quick prompt chips if user hasn't asked many questions yet
    if len(st.session_state["career_chat"]) <= 1:
        st.markdown("###### 💡 Quick Questions:")
        c1, c2, c3 = st.columns(3)
        quick_prompt = None
        with c1:
            if st.button("📈 How can I boost my ATS score?", use_container_width=True):
                quick_prompt = "Based on my resume ATS analysis, what are the top 3 highest-ROI changes I can make to boost my score?"
        with c2:
            if st.button("🚀 Which skills should I learn first?", use_container_width=True):
                quick_prompt = "Looking at my missing skills and target role, what skill should I learn first and how?"
        with c3:
            if st.button("💼 How should I pitch my experience?", use_container_width=True):
                quick_prompt = "How can I best pitch my past projects and experience during an interview for this role?"
    else:
        quick_prompt = None

    for turn in st.session_state["career_chat"]:
        with st.chat_message(turn["role"]):
            st.write(turn["content"])

    user_input = st.chat_input("Ask about roles, skills, interviews, or career transitions...")
    prompt = quick_prompt or user_input

    if not prompt:
        return

    st.session_state["career_chat"].append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

    profile = build_profile(target_role, interests, level)
    history = [
        {"role": t["role"], "content": t["content"]}
        for t in st.session_state["career_chat"][:-1]
    ]
    try:
        with st.spinner("Career Advisor is thinking..."):
            reply = api_client.career_chat(profile, prompt, token, history)
    except requests.RequestException as exc:
        show_backend_error(exc)
        st.session_state["career_chat"].pop()
        return

    st.session_state["career_chat"].append({"role": "assistant", "content": reply})
    st.rerun()
