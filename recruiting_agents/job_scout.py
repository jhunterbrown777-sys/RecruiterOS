import json

from agents import Agent
from pydantic import BaseModel

from recruiting_agents.context import RecruiterContext


class JobScoutDecision(BaseModel):
    scout_score: int
    keep_job: bool
    priority: str
    reason: str
    recommended_next_step: str
    tags: list[str]


def create_job_scout_agent(context: RecruiterContext) -> Agent:
    candidate = context.candidate

    return Agent(
        name="Job Scout Agent",
        instructions=f"""
You are the Job Scout Agent for the active profile: {candidate.name}.

Your job is to decide whether a discovered job should be kept, ignored, or prioritized.

CANDIDATE PROFILE:
{candidate.candidate_profile}

JOB SEARCH PREFERENCES:
{json.dumps(candidate.preferences, indent=2)}

TECHNICAL SKILLS PROFILE:
{json.dumps(candidate.technical_skills, indent=2)}

Decision Rules:
- Optimize for interview probability, not raw application volume.
- Prioritize target role titles from the profile preferences.
- Prioritize recently posted jobs.
- Prioritize LinkedIn, Indeed, Google Jobs, company career pages, Greenhouse, Lever, Ashby, and Workday.
- Penalize roles requiring completed certifications the profile does not have.
- Penalize roles requiring heavy skills not supported by the profile.
- Penalize roles outside preferred locations unless remote.
- Use priority values: High, Medium, Low.
- Output only structured data matching the JobScoutDecision schema.
""",
        output_type=JobScoutDecision,
    )