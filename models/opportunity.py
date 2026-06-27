from dataclasses import dataclass


@dataclass
class Opportunity:

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