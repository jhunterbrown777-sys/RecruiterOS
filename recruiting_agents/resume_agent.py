import json

from agents import Agent
from pydantic import BaseModel

from recruiting_agents.context import RecruiterContext


class ResumeOutput(BaseModel):
    resume_title: str
    professional_summary: str
    core_skills: list[str]
    technical_skills: list[str]
    selected_experience: list[str]
    selected_projects: list[str]
    education: list[str]
    certifications: list[str]
    resume_strategy: str
    ats_keywords_included: list[str]
    honesty_notes: list[str]


def create_resume_agent(context: RecruiterContext) -> Agent:
    candidate = context.candidate

    return Agent(
        name="Resume Agent",
        instructions=f"""
You are the Resume Agent for the active profile: {candidate.name}.

Your job is to generate an honest, ATS-optimized resume structure for a specific job.

MASTER RESUME DATABASE:
{json.dumps(candidate.master_resume, indent=2)}

CANDIDATE PROFILE:
{candidate.candidate_profile}

JOB SEARCH PREFERENCES:
{json.dumps(candidate.preferences, indent=2)}

TECHNICAL SKILLS PROFILE:
{json.dumps(candidate.technical_skills, indent=2)}

Rules:
- Never invent experience.
- Never invent certifications.
- Never claim Cisco CCNA certification.
- Never claim completed Security+ certification.
- Use only the profile's source data.
- Select only the most relevant experience and projects for the job.
- Prioritize ATS keywords from the job description when truthful.
- If a requirement is not supported, list it in honesty_notes instead of fabricating it.
- Output only structured data matching the ResumeOutput schema.
""",
        output_type=ResumeOutput,
    )