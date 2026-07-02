import importlib.util
import json
from datetime import datetime
from pathlib import Path

from agents import Runner
from dotenv import load_dotenv

from recruiting_agents.chief_recruiter import summarize_run
from recruiting_agents.context import RecruiterContext, RecruiterContextBuilder
from tools.ats_report_docx import create_ats_report_docx
from tools.docx_generator import create_docx
from tools.excel_tracker import (
    find_next_pending_job,
    load_tracker,
    read_job,
    save_tracker,
    update_job_analysis,
)
from tools.resume_docx import create_resume_docx

load_dotenv()


def load_agent_from_file(
    module_path: str,
    function_name: str,
    context: RecruiterContext,
):
    path = Path(module_path)
    spec = importlib.util.spec_from_file_location(path.stem, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    return getattr(module, function_name)(context)


def load_recruiter_agent(context: RecruiterContext):
    return load_agent_from_file(
        "recruiting_agents/recruiter.py",
        "create_recruiter",
        context,
    )


def load_resume_agent(context: RecruiterContext):
    return load_agent_from_file(
        "recruiting_agents/resume_agent.py",
        "create_resume_agent",
        context,
    )


def load_ats_agent(context: RecruiterContext):
    return load_agent_from_file(
        "recruiting_agents/ats_agent.py",
        "create_ats_agent",
        context,
    )


def safe_folder_name(value: str) -> str:
    return "".join(c if c.isalnum() else "_" for c in value).strip("_")


def save_outputs(job, analysis, resume_output=None, ats_review=None):
    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    title = job.get("Job Title") or "Unknown_Job"
    safe_title = safe_folder_name(title)

    output_dir = Path("data/outputs") / f"{timestamp}_{safe_title}"
    output_dir.mkdir(parents=True, exist_ok=True)

    analysis_dict = analysis.model_dump()

    (output_dir / "full_analysis.json").write_text(
        json.dumps(analysis_dict, indent=2),
        encoding="utf-8",
    )

    (output_dir / "tailored_resume_notes.txt").write_text(
        analysis.tailored_resume_notes or "",
        encoding="utf-8",
    )

    (output_dir / "cover_letter_draft.txt").write_text(
        analysis.cover_letter_draft or "",
        encoding="utf-8",
    )

    (output_dir / "recruiter_message.txt").write_text(
        analysis.recruiter_message or "",
        encoding="utf-8",
    )

    create_docx(
        title="Tailored Resume Notes",
        content=analysis.tailored_resume_notes or "",
        output_path=output_dir / "tailored_resume_notes.docx",
    )

    create_docx(
        title="Cover Letter",
        content=analysis.cover_letter_draft or "",
        output_path=output_dir / "cover_letter.docx",
    )

    create_docx(
        title="Recruiter Message",
        content=analysis.recruiter_message or "",
        output_path=output_dir / "recruiter_message.docx",
    )

    if resume_output is not None:
        resume_dict = resume_output.model_dump()

        (output_dir / "tailored_resume.json").write_text(
            json.dumps(resume_dict, indent=2),
            encoding="utf-8",
        )

        create_resume_docx(
            resume=resume_output,
            output_path=output_dir / "tailored_resume.docx",
        )

    if ats_review is not None:
        ats_dict = ats_review.model_dump()

        (output_dir / "ats_review.json").write_text(
            json.dumps(ats_dict, indent=2),
            encoding="utf-8",
        )

        create_ats_report_docx(
            ats_review=ats_review,
            output_path=output_dir / "ats_report.docx",
        )

    return output_dir


def main():
    context = RecruiterContextBuilder().build_default()

    wb, ws = load_tracker()
    row = find_next_pending_job(ws)

    if row is None:
        print("No pending jobs found.")
        return

    job = read_job(ws, row)

    recruiter_agent = load_recruiter_agent(context)
    resume_agent = load_resume_agent(context)
    ats_agent = load_ats_agent(context)

    job_prompt = f"""
Analyze this job for Hunter Brown.

Job Title: {job.get("Job Title")}
Company: {job.get("Company")}
Location: {job.get("Location")}
Work Arrangement: {job.get("Work Arrangement")}
Source: {job.get("Source")}
Job URL: {job.get("Job URL")}

Job Description:

{job.get("Job Description")}
"""

    recruiter_result = Runner.run_sync(recruiter_agent, job_prompt)
    analysis = recruiter_result.final_output

    resume_prompt = f"""
Create an ATS-optimized tailored resume structure for Hunter Brown.

Use the job description and the recruiting analysis below.

Job Title: {job.get("Job Title")}
Company: {job.get("Company")}
Location: {job.get("Location")}
Work Arrangement: {job.get("Work Arrangement")}

Job Description:
{job.get("Job Description")}

Recruiting Analysis:
Fit Score: {analysis.fit_score}
Apply Decision: {analysis.apply_decision}
Reason: {analysis.reason}
Missing Skills: {analysis.missing_skills}
Tailored Resume Notes: {analysis.tailored_resume_notes}

Requirements:
- Generate a real resume structure, not notes.
- Prioritize truthful ATS keyword alignment.
- Do not invent experience.
- Do not claim completed Security+.
- Do not claim CCNA certification.
"""

    resume_result = Runner.run_sync(resume_agent, resume_prompt)
    resume_output = resume_result.final_output

    ats_prompt = f"""
Review this tailored resume against the job description for ATS optimization.

Job Title: {job.get("Job Title")}
Company: {job.get("Company")}

Job Description:
{job.get("Job Description")}

Tailored Resume Structure:
{json.dumps(resume_output.model_dump(), indent=2)}

Recruiting Analysis:
{json.dumps(analysis.model_dump(), indent=2)}

Requirements:
- Score ATS alignment from 0 to 100.
- Identify matched and missing keywords.
- Recommend whether the resume should be regenerated.
- Do not suggest false claims.
"""

    ats_result = Runner.run_sync(ats_agent, ats_prompt)
    ats_review = ats_result.final_output

    update_job_analysis(ws, row, analysis)
    save_tracker(wb)

    output_dir = save_outputs(job, analysis, resume_output, ats_review)
    summary = summarize_run(analysis, output_dir, resume_generated=True)

    print(f"Analyzed row: {row}")
    print(f"Fit Score: {analysis.fit_score}")
    print(f"Decision: {analysis.apply_decision}")
    print(f"ATS Score: {ats_review.ats_score}")
    print(f"Regenerate Resume: {ats_review.should_regenerate_resume}")
    print("Saved workbook: data/JOB_TRACKER_AGENT_MVP.xlsx")
    print(f"Saved outputs: {output_dir}")
    print(f"Generated resume: {output_dir / 'tailored_resume.docx'}")
    print(f"Generated ATS report: {output_dir / 'ats_report.docx'}")
    print(f"Chief Recruiter Status: {summary.status}")
    print(f"Next Step: {summary.next_step}")


if __name__ == "__main__":
    main()