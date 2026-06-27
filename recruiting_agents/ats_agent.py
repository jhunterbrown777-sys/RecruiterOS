import json

from agents import Agent
from pydantic import BaseModel

from memory.memory_manager import MemoryManager


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


def create_ats_agent() -> Agent:
    memory = MemoryManager()

    master_resume = memory.master_resume()
    candidate_profile = memory.candidate_profile()
    preferences = memory.preferences()
    technical_skills = memory.technical_skills()

    return Agent(
        name="ATS Agent",
        instructions=f"""
You are Hunter Brown's ATS Optimization Agent.

Your job is to compare a tailored resume against a job description and estimate ATS/recruiter alignment.

Use these source files as truth:

MASTER RESUME DATABASE:
{json.dumps(master_resume, indent=2)}

CANDIDATE PROFILE:
{candidate_profile}

JOB SEARCH PREFERENCES:
{json.dumps(preferences, indent=2)}

TECHNICAL SKILLS PROFILE:
{json.dumps(technical_skills, indent=2)}

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