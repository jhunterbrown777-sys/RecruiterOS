from models.job import Job


JOB_COLUMNS = [
    "id",
    "title",
    "company",
    "location",
    "description",
    "url",
    "source",
    "work_arrangement",
    "employment_type",
    "salary",
    "recruiter",
    "date_posted",
    "discovered_at",
    "fit_score",
    "status",
    "applied",
    "notes",
    "company_size",
    "industry",
    "ats_platform",
    "remote",
]


def row_to_job(row) -> Job:
    data = dict(zip(JOB_COLUMNS, row))

    return Job(
        title=data.get("title") or "",
        company=data.get("company") or "",
        location=data.get("location") or "",
        description=data.get("description") or "",
        url=data.get("url") or "",
        source=data.get("source") or "",
        work_arrangement=data.get("work_arrangement") or "",
        employment_type=data.get("employment_type") or "",
        salary=data.get("salary"),
        recruiter=data.get("recruiter"),
        date_posted=data.get("date_posted"),
        fit_score=data.get("fit_score"),
        status=data.get("status") or "NEW",
        applied=bool(data.get("applied")),
        notes=data.get("notes") or "",
        company_size=data.get("company_size") or "",
        industry=data.get("industry") or "",
        ats_platform=data.get("ats_platform") or "",
        remote=bool(data.get("remote")),
    )