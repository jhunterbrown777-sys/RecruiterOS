import json

from agents import Agent
from pydantic import BaseModel

from memory.memory_manager import MemoryManager


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


def create_resume_agent() -> Agent:
    memory = MemoryManager()

    master_resume = memory.master_resume()
    candidate_profile = memory.candidate_profile()
    preferences = memory.preferences()
    technical_skills = memory.technical_skills()

    return Agent(
        name="Resume Agent",
        instructions=f"""
You are Hunter Brown's Resume Agent.

Your job is to generate an honest, ATS-optimized resume structure for a specific job.

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
- Never invent experience.
- Never invent certifications.
- Never claim Cisco CCNA certification.
- Never claim completed Security+ certification.
- You may state Security+ is in progress.
- You may state CCNA-equivalent networking coursework.
- Represent Python, GitHub, GitHub Copilot, Visual Studio Code, Cursor IDE, OpenAI API, and OpenAI Agents SDK honestly as developing unless the technical skills profile says otherwise.
- Select only the most relevant experience and projects for the job.
- Prioritize ATS keywords from the job description when truthful.
- If a requirement is not supported by the master resume, list it in honesty_notes instead of fabricating it.
- Output only structured data matching the ResumeOutput schema.
""",
        output_type=ResumeOutput,
    )