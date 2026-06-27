import json

from agents import Agent
from pydantic import BaseModel

from profiles.profile_manager import ProfileManager


class ATSReview(BaseModel):
    ats_score: int
    keyword_match_score: int
    missing_keywords: list[str]
    matched_keywords: list[str]
    resume_strengths: list[str]
    resume_weaknesses: list[str]
    improvement_suggestions: list[str]
    should_regenerate_resume: bool
    final_recommendation: str


def create_ats_agent(profile_name: str | None = None) -> Agent:
    profile = ProfileManager().load(profile_name)

    return Agent(
        name="ATS Agent",
        instructions=f"""
You are the ATS Optimization Agent for the active profile: {profile.name}.

Your job is to compare a tailored resume against a job description and estimate ATS/recruiter alignment.

MASTER RESUME DATABASE:
{json.dumps(profile.master_resume, indent=2)}

CANDIDATE PROFILE:
{profile.candidate_profile}

JOB SEARCH PREFERENCES:
{json.dumps(profile.preferences, indent=2)}

TECHNICAL SKILLS PROFILE:
{json.dumps(profile.technical_skills, indent=2)}

Rules:
- Never suggest adding false experience.
- Never suggest claiming completed Security+.
- Never suggest claiming Cisco CCNA certification.
- Missing keywords should only include terms that appear important in the job description.
- If a missing keyword is not truthfully supported, say so in improvement suggestions.
- Score ATS alignment from 0 to 100.
- Recommend resume regeneration if ATS score is below 85.
- Output only structured data matching the ATSReview schema.
""",
        output_type=ATSReview,
    )