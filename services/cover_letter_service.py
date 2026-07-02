import json

from agents import Runner

from database.sqlite_manager import SQLiteManager
from models.assessment import Assessment
from models.cover_letter import CoverLetter
from models.job import Job
from recruiting_agents.context import RecruiterContextBuilder
from recruiting_agents.cover_letter_agent import create_cover_letter_agent


class CoverLetterService:
    """Service-layer interface for CoverLetter data.

    Wraps SQLiteManager's cover letter persistence methods so callers
    depend on the service layer instead of the persistence layer
    directly.
    """

    def __init__(self):
        self.db = SQLiteManager()
        self.context_builder = RecruiterContextBuilder()

    def create_cover_letter(self, cover_letter: CoverLetter) -> int:
        """Persist a new CoverLetter and return its id."""
        return self.db.save_cover_letter(cover_letter)

    def get_cover_letter(self, cover_letter_id: int) -> CoverLetter | None:
        """Fetch a CoverLetter by id, or None if not found."""
        return self.db.get_cover_letter(cover_letter_id)

    def list_cover_letters(self, candidate_id: int) -> list[CoverLetter]:
        """List all CoverLetters belonging to a Candidate, most recently updated first."""
        return self.db.get_cover_letters(candidate_id)

    def update_cover_letter(self, cover_letter: CoverLetter) -> None:
        """Persist changes to an existing CoverLetter."""
        self.db.update_cover_letter(cover_letter)

    def generate_tailored_cover_letter(self, job: Job, assessment: Assessment | None) -> CoverLetter:
        """Generate a tailored cover letter via AI for a Job and persist it.

        assessment is optional -- an Opportunity that hasn't been
        analyzed yet can still have a cover letter generated for it.
        """
        context = self.context_builder.build_default()
        agent = create_cover_letter_agent(context)
        prompt = self._build_generation_prompt(job, assessment)

        result = Runner.run_sync(agent, prompt)
        letter_output = result.final_output

        cover_letter = CoverLetter(
            candidate_id=context.candidate.id,
            title=letter_output.cover_letter_title,
            content=json.dumps(letter_output.model_dump(), indent=2),
        )
        cover_letter.id = self.create_cover_letter(cover_letter)

        return cover_letter

    def _build_generation_prompt(self, job: Job, assessment: Assessment | None) -> str:
        assessment_section = "No prior Assessment available for this Opportunity."

        if assessment is not None:
            assessment_section = f"""Fit Score: {assessment.fit_score}
Recommendation: {assessment.recommendation}
Reasoning: {assessment.reasoning}"""

        return f"""
Write a targeted cover letter for this job.

Job Title: {job.title}
Company: {job.company}
Location: {job.location}
Work Arrangement: {job.work_arrangement}

Job Description:
{job.description}

Assessment:
{assessment_section}

Requirements:
- Write a real cover letter, not notes.
- Address the company and role specifically.
- Do not invent experience.
- Do not claim completed Security+.
- Do not claim CCNA certification.
"""
