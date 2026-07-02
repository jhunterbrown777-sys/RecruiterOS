import json

from agents import Runner

from database.sqlite_manager import SQLiteManager
from models.assessment import Assessment
from models.job import Job
from models.resume import Resume
from recruiting_agents.context import RecruiterContextBuilder
from recruiting_agents.resume_agent import create_resume_agent


class ResumeService:
    """Service-layer interface for Resume data.

    Wraps SQLiteManager's resume persistence methods so callers depend
    on the service layer instead of the persistence layer directly.
    """

    def __init__(self):
        self.db = SQLiteManager()
        self.context_builder = RecruiterContextBuilder()

    def create_resume(self, resume: Resume) -> int:
        """Persist a new Resume and return its id."""
        return self.db.save_resume(resume)

    def get_resume(self, resume_id: int) -> Resume | None:
        """Fetch a Resume by id, or None if not found."""
        return self.db.get_resume(resume_id)

    def list_resumes(self, candidate_id: int) -> list[Resume]:
        """List all Resumes belonging to a Candidate, most recently updated first."""
        return self.db.get_resumes(candidate_id)

    def update_resume(self, resume: Resume) -> None:
        """Persist changes to an existing Resume."""
        self.db.update_resume(resume)

    def generate_tailored_resume(self, job: Job, assessment: Assessment | None) -> Resume:
        """Generate a tailored resume via AI for a Job and persist it.

        assessment is optional -- an Opportunity that hasn't been
        analyzed yet can still have a resume generated for it.
        """
        context = self.context_builder.build_default()
        agent = create_resume_agent(context)
        prompt = self._build_generation_prompt(job, assessment)

        result = Runner.run_sync(agent, prompt)
        resume_output = result.final_output

        resume = Resume(
            candidate_id=context.candidate.id,
            title=resume_output.resume_title,
            content=json.dumps(resume_output.model_dump(), indent=2),
        )
        resume.id = self.create_resume(resume)

        return resume

    def _build_generation_prompt(self, job: Job, assessment: Assessment | None) -> str:
        assessment_section = "No prior Assessment available for this Opportunity."

        if assessment is not None:
            assessment_section = f"""Fit Score: {assessment.fit_score}
Recommendation: {assessment.recommendation}
Reasoning: {assessment.reasoning}"""

        return f"""
Create an ATS-optimized tailored resume structure for this job.

Job Title: {job.title}
Company: {job.company}
Location: {job.location}
Work Arrangement: {job.work_arrangement}

Job Description:
{job.description}

Assessment:
{assessment_section}

Requirements:
- Generate a real resume structure, not notes.
- Prioritize truthful ATS keyword alignment.
- Do not invent experience.
- Do not claim completed Security+.
- Do not claim CCNA certification.
"""
