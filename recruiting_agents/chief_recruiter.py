from pydantic import BaseModel


class ChiefRecruiterResult(BaseModel):
    status: str
    fit_score: int
    apply_decision: str
    output_folder: str
    resume_generated: bool
    next_step: str


def summarize_run(analysis, output_dir, resume_generated: bool = True) -> ChiefRecruiterResult:
    return ChiefRecruiterResult(
        status="completed",
        fit_score=analysis.fit_score,
        apply_decision=analysis.apply_decision,
        output_folder=str(output_dir),
        resume_generated=resume_generated,
        next_step="Review generated resume, cover letter, recruiter message, and prepare application."
    )