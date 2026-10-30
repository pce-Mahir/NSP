import json
import logging
from typing import Any, Dict, List, Optional

from backend.services.gemini_client import generate_text

logger = logging.getLogger('ats_resume_scorer')


def _profile_blob(profile: Dict[str, Any]) -> str:
    compact = {
        "name": profile.get("name") or "",
        "professional_summary": profile.get("professional_summary") or "",
        "skills": profile.get("skills") or [],
        "experience": profile.get("experience") or [],
        "education": profile.get("education") or [],
        "certifications": profile.get("certifications") or [],
        "projects": profile.get("projects") or [],
        "target_role": profile.get("target_role") or "",
        "career_interests": profile.get("career_interests") or "",
        "experience_level": profile.get("experience_level") or "",
        "job_description": (profile.get("job_description") or "")[:4000],
    }
    return json.dumps(compact, ensure_ascii=False, indent=2)


def _parse_json(text: str) -> Dict[str, Any]:
    cleaned = text.strip()
    if cleaned.startswith("```"):
        first_newline = cleaned.index("\n") if "\n" in cleaned else len(cleaned)
        cleaned = cleaned[first_newline + 1:]
        if cleaned.endswith("```"):
            cleaned = cleaned[:-3]
        cleaned = cleaned.strip()
    return json.loads(cleaned)


def recommend_pathways(profile: Dict[str, Any]) -> Dict[str, Any]:
    system = (
        "You are a career counselor for an AI-Enhanced Career Guidance System "
        "for Personalized Career Pathways. Recommend realistic, personalized "
        "career paths from the candidate profile. Return ONLY valid JSON."
    )
    user = f"""Based on this candidate profile, recommend 3 to 5 personalized career pathways.

Return JSON:
{{
  "profile_summary": "2-3 sentence snapshot of the candidate",
  "pathways": [
    {{
      "title": "pathway name",
      "fit_score": 0,
      "why_it_fits": "why this path matches the profile",
      "typical_roles": ["role titles"],
      "required_skills": ["skills"],
      "skills_you_have": ["skills already present"],
      "skills_to_build": ["skills to learn"],
      "next_12_months": ["concrete milestones"],
      "outlook": "hiring demand and growth in one sentence"
    }}
  ]
}}

fit_score is 0-100. Be specific to this profile, not generic advice.

Candidate profile:
{_profile_blob(profile)}
"""
    raw = generate_text(system, user, temperature=0.4, json_mode=True)
    try:
        data = _parse_json(raw)
    except json.JSONDecodeError:
        logger.warning("Pathway JSON parse failed; retrying")
        raw = generate_text(system, user + "\nReturn raw JSON only.", temperature=0.2, json_mode=True)
        data = _parse_json(raw)
    data.setdefault("profile_summary", "")
    data.setdefault("pathways", [])
    return data


def build_skills_roadmap(profile: Dict[str, Any]) -> Dict[str, Any]:
    system = (
        "You are a career skills coach. Build a personalized 30/60/90-day "
        "learning roadmap from a candidate profile and target role. Return ONLY JSON."
    )
    target = profile.get("target_role") or "the most suitable next role for this profile"
    user = f"""Create a skills-gap analysis and learning roadmap toward: {target}

Return JSON:
{{
  "target_role": "",
  "readiness_score": 0,
  "skill_gaps": [
    {{
      "skill": "",
      "priority": "high|medium|low",
      "how_to_learn": "",
      "estimated_weeks": 0
    }}
  ],
  "plan_30_days": ["actions"],
  "plan_60_days": ["actions"],
  "plan_90_days": ["actions"],
  "recommended_resources": [
    {{"title": "", "type": "course|book|project|certification", "reason": ""}}
  ]
}}

readiness_score is 0-100. Keep resources realistic and widely available.

Candidate profile:
{_profile_blob(profile)}
"""
    raw = generate_text(system, user, temperature=0.35, json_mode=True)
    try:
        data = _parse_json(raw)
    except json.JSONDecodeError:
        raw = generate_text(system, user + "\nReturn raw JSON only.", temperature=0.2, json_mode=True)
        data = _parse_json(raw)
    for key, default in [
        ("target_role", target),
        ("readiness_score", 0),
        ("skill_gaps", []),
        ("plan_30_days", []),
        ("plan_60_days", []),
        ("plan_90_days", []),
        ("recommended_resources", []),
    ]:
        data.setdefault(key, default)
    return data


def generate_interview_prep(profile: Dict[str, Any]) -> Dict[str, Any]:
    system = (
        "You are an interview coach. Generate targeted interview practice from "
        "the candidate's resume and target role. Return ONLY JSON."
    )
    target = profile.get("target_role") or "a role that fits this resume"
    user = f"""Generate interview prep for: {target}

Return JSON:
{{
  "target_role": "",
  "focus_areas": ["areas to study"],
  "questions": [
    {{
      "type": "behavioral|technical|situational",
      "question": "",
      "why_it_matters": "",
      "sample_answer": "STAR-style answer grounded in this resume",
      "tips": ["short tips"]
    }}
  ]
}}

Include 8-10 questions mixing behavioral, technical, and situational. Ground sample answers in the resume.

Candidate profile:
{_profile_blob(profile)}
"""
    raw = generate_text(system, user, temperature=0.45, json_mode=True)
    try:
        data = _parse_json(raw)
    except json.JSONDecodeError:
        raw = generate_text(system, user + "\nReturn raw JSON only.", temperature=0.2, json_mode=True)
        data = _parse_json(raw)
    data.setdefault("target_role", target)
    data.setdefault("focus_areas", [])
    data.setdefault("questions", [])
    return data


def career_chat(
    profile: Dict[str, Any],
    message: str,
    history: Optional[List[Dict[str, str]]] = None,
) -> str:
    system = (
        "You are a supportive career advisor in an AI-Enhanced Career Guidance "
        "System for Personalized Career Pathways. Use the candidate profile when "
        "it is provided. Give practical, specific guidance. Do not invent employers "
        "or credentials the candidate does not have. Keep answers concise."
    )
    turns = ""
    for item in (history or [])[-8:]:
        role = item.get("role", "user")
        content = item.get("content", "")
        turns += f"{role}: {content}\n"
    user = f"""Candidate profile:
{_profile_blob(profile)}

Conversation so far:
{turns or "(none)"}

User: {message}

Reply as the career advisor."""
    return generate_text(system, user, temperature=0.5, json_mode=False, max_output_tokens=2048)
