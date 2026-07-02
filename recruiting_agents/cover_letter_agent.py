import json

from agents import Agent
from pydantic import BaseModel

from recruiting_agents.context import RecruiterContext


class CoverLetterOutput(BaseModel):
    cover_letter_title: str
    salutation: str
    opening_paragraph: str
    body_paragraphs: list[str]
    closing_paragraph: str
    signoff: str
    strategy_notes: str
    honesty_notes: list[str]


def create_cover_letter_agent(context: RecruiterContext) -> Agent:
    candidate = context.candidate

    return Agent(
        name="Cover Letter Agent",
        instructions=f"""
You are the Cover Letter Agent for the active profile: {candidate.name}.

Your job is to generate an honest, targeted cover letter for a specific job.

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
- Address the specific company and role, not a generic template.
- Reference the Assessment's reasoning when it supports genuine enthusiasm or fit.
- Keep it concise: 3-4 body paragraphs, professional tone.
- If a requirement is not supported, do not fabricate it -- list it in honesty_notes instead.
- Output only structured data matching the CoverLetterOutput schema.
""",
        output_type=CoverLetterOutput,
    )
