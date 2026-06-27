import json

from agents import Agent
from pydantic import BaseModel

from profiles.profile_manager import ProfileManager


class OpportunityScore(BaseModel):
    title: str
    company: str
    score: int
    fit_score: int
    posting_age_score: int
    company_score: int
    remote_score: int
    salary_score: int
    ats_score: int
    priority: str
    recommendation: str
    reasoning: str


def create_opportunity_scorer(profile_name: str | None = None) -> Agent:
    profile = ProfileManager().load(profile_name)

    return Agent(
        name="Opportunity Scoring Agent",
        instructions=f"""
You are the Opportunity Scoring Agent for the active profile: {profile.name}.

Your job is to rank job opportunities by interview probability and strategic value.

Candidate Profile:
{profile.candidate_profile}

Job Search Preferences:
{json.dumps(profile.preferences, indent=2)}

Technical Skills:
{json.dumps(profile.technical_skills, indent=2)}

Scoring dimensions:
- fit_score: match between the candidate and the job
- posting_age_score: newer jobs score higher
- company_score: company quality and strategic career value
- remote_score: alignment with remote/hybrid/location preferences
- salary_score: alignment with target compensation
- ats_score: likelihood that resume can be tailored truthfully for ATS success

Final score:
- 90-100 = High priority
- 75-89 = Medium priority
- 60-74 = Low priority
- Below 60 = Not recommended

Rules:
- Optimize for interview probability, not raw application volume.
- Do not over-prioritize jobs just because they are easy apply.
- Penalize jobs requiring certifications or experience not supported by the profile.
- Prioritize roles that create a path toward cloud, cybersecurity, infrastructure, AI automation, business analysis, or digital operations.
- Output only structured data matching the OpportunityScore schema.
""",
        output_type=OpportunityScore,
    )