from agents import Runner

from config.settings import settings
from database.sqlite_manager import SQLiteManager
from models.assessment import Assessment
from models.job import Job
from models.opportunity import Opportunity
from recruiting_agents.opportunity_scorer import create_opportunity_scorer


class AssessmentService:
    """Service-layer interface for Assessment data.

    Wraps SQLiteManager's assessment persistence methods so callers
    depend on the service layer instead of the persistence layer
    directly.
    """

    def __init__(self):
        self.db = SQLiteManager()

    def create_assessment(self, assessment: Assessment) -> int:
        """Persist a new Assessment and return its id."""
        return self.db.save_assessment(assessment)

    def get_assessment(self, assessment_id: int) -> Assessment | None:
        """Fetch an Assessment by id, or None if not found."""
        return self.db.get_assessment(assessment_id)

    def list_assessments(self, opportunity_id: int) -> list[Assessment]:
        """List all Assessments for a given Opportunity, most recent first."""
        return self.db.get_assessments(opportunity_id)

    def generate_assessment(self, opportunity: Opportunity, job: Job) -> Assessment:
        """Score an Opportunity's Job with AI and persist the result."""
        agent = create_opportunity_scorer(settings.default_profile)
        prompt = self._build_prompt(job)

        result = Runner.run_sync(agent, prompt)
        score = result.final_output

        assessment = Assessment(
            opportunity_id=opportunity.id,
            score=score.score,
            fit_score=score.fit_score,
            posting_age_score=score.posting_age_score,
            company_score=score.company_score,
            remote_score=score.remote_score,
            salary_score=score.salary_score,
            ats_score=score.ats_score,
            recommendation=score.recommendation,
            reasoning=score.reasoning,
        )

        assessment.id = self.create_assessment(assessment)

        return assessment

    def _build_prompt(self, job: Job) -> str:
        return f"""
Score this job opportunity.

Job Title: {job.title}
Company: {job.company}
Location: {job.location}
Work Arrangement: {job.work_arrangement}
Employment Type: {job.employment_type}
Salary: {job.salary or "Not specified"}
Date Posted: {job.date_posted or "Unknown"}
Remote: {job.remote}
Company Size: {job.company_size or "Unknown"}
Industry: {job.industry or "Unknown"}
Source: {job.source}

Job Description:

{job.description}
"""
