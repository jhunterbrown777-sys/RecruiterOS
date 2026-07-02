import json
import sqlite3
from datetime import datetime
from pathlib import Path

from database.schema import (
    CREATE_ACTIVITIES_TABLE,
    CREATE_APPLICATIONS_TABLE,
    CREATE_ASSESSMENTS_TABLE,
    CREATE_CANDIDATES_TABLE,
    CREATE_COMPANIES_TABLE,
    CREATE_DOCUMENTS_TABLE,
    CREATE_INTERVIEWS_TABLE,
    CREATE_JOBS_TABLE,
    CREATE_OPPORTUNITIES_TABLE,
    CREATE_RECRUITERS_TABLE,
)
from models.assessment import Assessment
from models.candidate import Candidate
from models.job import Job
from models.opportunity import Opportunity
from models.recruiter import Recruiter
from models.interview import Interview


class SQLiteManager:
    def __init__(self, db_path: str = "database/recruiteros.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.initialize_database()

    def connect(self):
        return sqlite3.connect(self.db_path)

    def initialize_database(self):
        with self.connect() as conn:
            cursor = conn.cursor()
            cursor.execute(CREATE_CANDIDATES_TABLE)
            cursor.execute(CREATE_COMPANIES_TABLE)
            cursor.execute(CREATE_JOBS_TABLE)
            cursor.execute(CREATE_OPPORTUNITIES_TABLE)
            cursor.execute(CREATE_ASSESSMENTS_TABLE)
            cursor.execute(CREATE_APPLICATIONS_TABLE)
            cursor.execute(CREATE_RECRUITERS_TABLE)
            cursor.execute(CREATE_INTERVIEWS_TABLE)
            cursor.execute(CREATE_ACTIVITIES_TABLE)
            cursor.execute(CREATE_DOCUMENTS_TABLE)
            conn.commit()

    def save_candidate(self, candidate: Candidate) -> int:
        with self.connect() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO candidates (
                    name, candidate_profile, master_resume, preferences,
                    technical_skills, created_at, updated_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    candidate.name,
                    candidate.candidate_profile,
                    json.dumps(candidate.master_resume),
                    json.dumps(candidate.preferences),
                    json.dumps(candidate.technical_skills),
                    candidate.created_at.isoformat(),
                    candidate.updated_at.isoformat(),
                ),
            )
            conn.commit()
            return cursor.lastrowid

    def get_candidate(self, candidate_id: int) -> Candidate | None:
        with self.connect() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT id, name, candidate_profile, master_resume, preferences,
                       technical_skills, created_at, updated_at
                FROM candidates
                WHERE id = ?
                """,
                (candidate_id,),
            )
            row = cursor.fetchone()

            if row is None:
                return None

            return self._row_to_candidate(row)

    def get_first_candidate(self) -> Candidate | None:
        with self.connect() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT id, name, candidate_profile, master_resume, preferences,
                       technical_skills, created_at, updated_at
                FROM candidates
                ORDER BY id ASC
                LIMIT 1
                """
            )
            row = cursor.fetchone()

            if row is None:
                return None

            return self._row_to_candidate(row)

    def _row_to_candidate(self, row) -> Candidate:
        return Candidate(
            id=row[0],
            name=row[1],
            candidate_profile=row[2] or "",
            master_resume=json.loads(row[3]) if row[3] else {},
            preferences=json.loads(row[4]) if row[4] else {},
            technical_skills=json.loads(row[5]) if row[5] else {},
            created_at=datetime.fromisoformat(row[6]),
            updated_at=datetime.fromisoformat(row[7]),
        )

    def update_candidate(self, candidate: Candidate) -> None:
        with self.connect() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                UPDATE candidates
                SET name = ?, candidate_profile = ?, master_resume = ?,
                    preferences = ?, technical_skills = ?, updated_at = ?
                WHERE id = ?
                """,
                (
                    candidate.name,
                    candidate.candidate_profile,
                    json.dumps(candidate.master_resume),
                    json.dumps(candidate.preferences),
                    json.dumps(candidate.technical_skills),
                    datetime.utcnow().isoformat(),
                    candidate.id,
                ),
            )
            conn.commit()

    def save_job(self, job: Job) -> int | None:
        with self.connect() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT OR IGNORE INTO jobs (
                    title, company, location, description, url, source,
                    work_arrangement, employment_type, salary, recruiter,
                    date_posted, discovered_at, fit_score, status, applied,
                    notes, company_size, industry, ats_platform, remote
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    job.title,
                    job.company,
                    job.location,
                    job.description,
                    job.url,
                    job.source,
                    job.work_arrangement,
                    job.employment_type,
                    job.salary,
                    job.recruiter,
                    job.date_posted,
                    job.discovered_at.isoformat(),
                    job.fit_score,
                    job.status,
                    int(job.applied),
                    job.notes,
                    job.company_size,
                    job.industry,
                    job.ats_platform,
                    int(job.remote),
                ),
            )
            conn.commit()
            return cursor.lastrowid if cursor.rowcount else None

    def get_job(self, job_id: int) -> Job | None:
        with self.connect() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT id, title, company, location, description, url, source,
                       work_arrangement, employment_type, salary, recruiter,
                       date_posted, discovered_at, fit_score, status, applied,
                       notes, company_size, industry, ats_platform, remote
                FROM jobs
                WHERE id = ?
                """,
                (job_id,),
            )
            row = cursor.fetchone()

            if row is None:
                return None

            return self._row_to_job(row)

    def save_opportunity(self, opportunity: Opportunity) -> int | None:
        with self.connect() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT OR IGNORE INTO opportunities (
                    candidate_id, job_id, status, created_at, updated_at
                )
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    opportunity.candidate_id,
                    opportunity.job_id,
                    opportunity.status,
                    opportunity.created_at.isoformat(),
                    opportunity.updated_at.isoformat(),
                ),
            )
            conn.commit()
            return cursor.lastrowid if cursor.rowcount else None

    def get_opportunity(self, opportunity_id: int) -> Opportunity | None:
        with self.connect() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT id, candidate_id, job_id, status, created_at, updated_at
                FROM opportunities
                WHERE id = ?
                """,
                (opportunity_id,),
            )
            row = cursor.fetchone()

            if row is None:
                return None

            return self._row_to_opportunity(row)

    def get_opportunities(self, candidate_id: int) -> list[Opportunity]:
        with self.connect() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT id, candidate_id, job_id, status, created_at, updated_at
                FROM opportunities
                WHERE candidate_id = ?
                ORDER BY updated_at DESC
                """,
                (candidate_id,),
            )
            rows = cursor.fetchall()

            return [self._row_to_opportunity(row) for row in rows]

    def _row_to_opportunity(self, row) -> Opportunity:
        return Opportunity(
            id=row[0],
            candidate_id=row[1],
            job_id=row[2],
            status=row[3],
            created_at=datetime.fromisoformat(row[4]),
            updated_at=datetime.fromisoformat(row[5]),
        )

    def save_assessment(self, assessment: Assessment) -> int:
        with self.connect() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO assessments (
                    opportunity_id, score, fit_score, posting_age_score,
                    company_score, remote_score, salary_score, ats_score,
                    recommendation, reasoning, created_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    assessment.opportunity_id,
                    assessment.score,
                    assessment.fit_score,
                    assessment.posting_age_score,
                    assessment.company_score,
                    assessment.remote_score,
                    assessment.salary_score,
                    assessment.ats_score,
                    assessment.recommendation,
                    assessment.reasoning,
                    assessment.created_at.isoformat(),
                ),
            )
            conn.commit()
            return cursor.lastrowid

    def get_assessment(self, assessment_id: int) -> Assessment | None:
        with self.connect() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT id, opportunity_id, score, fit_score, posting_age_score,
                       company_score, remote_score, salary_score, ats_score,
                       recommendation, reasoning, created_at
                FROM assessments
                WHERE id = ?
                """,
                (assessment_id,),
            )
            row = cursor.fetchone()

            if row is None:
                return None

            return self._row_to_assessment(row)

    def get_assessments(self, opportunity_id: int) -> list[Assessment]:
        with self.connect() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT id, opportunity_id, score, fit_score, posting_age_score,
                       company_score, remote_score, salary_score, ats_score,
                       recommendation, reasoning, created_at
                FROM assessments
                WHERE opportunity_id = ?
                ORDER BY created_at DESC
                """,
                (opportunity_id,),
            )
            rows = cursor.fetchall()

            return [self._row_to_assessment(row) for row in rows]

    def _row_to_assessment(self, row) -> Assessment:
        return Assessment(
            id=row[0],
            opportunity_id=row[1],
            score=row[2],
            fit_score=row[3],
            posting_age_score=row[4],
            company_score=row[5],
            remote_score=row[6],
            salary_score=row[7],
            ats_score=row[8],
            recommendation=row[9],
            reasoning=row[10],
            created_at=datetime.fromisoformat(row[11]),
        )

    def save_recruiter(self, recruiter: Recruiter) -> int:
        with self.connect() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO recruiters (
                    name, company, title, linkedin_url, email, phone, source,
                    notes, last_contacted_at, follow_up_at, created_at, updated_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    recruiter.name,
                    recruiter.company,
                    recruiter.title,
                    recruiter.linkedin_url,
                    recruiter.email,
                    recruiter.phone,
                    recruiter.source,
                    recruiter.notes,
                    recruiter.last_contacted_at.isoformat() if recruiter.last_contacted_at else None,
                    recruiter.follow_up_at.isoformat() if recruiter.follow_up_at else None,
                    recruiter.created_at.isoformat(),
                    recruiter.updated_at.isoformat(),
                ),
            )
            conn.commit()
            return cursor.lastrowid

    def save_interview(self, interview: Interview) -> int:
        with self.connect() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO interviews (
                    job_id, company, role, stage, interview_date, interviewer_names,
                    interview_format, notes, technical_questions, behavioral_questions,
                    outcome, created_at, updated_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    interview.job_id,
                    interview.company,
                    interview.role,
                    interview.stage,
                    interview.interview_date.isoformat() if interview.interview_date else None,
                    interview.interviewer_names,
                    interview.interview_format,
                    interview.notes,
                    interview.technical_questions,
                    interview.behavioral_questions,
                    interview.outcome,
                    interview.created_at.isoformat(),
                    interview.updated_at.isoformat(),
                ),
            )
            conn.commit()
            return cursor.lastrowid

    def log_activity(self, entity_type: str, entity_id: int, action: str, notes: str = "") -> int:
        with self.connect() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO activities (entity_type, entity_id, action, notes, created_at)
                VALUES (?, ?, ?, ?, datetime('now'))
                """,
                (entity_type, entity_id, action, notes),
            )
            conn.commit()
            return cursor.lastrowid

    def save_document(self, job_id: int, document_type: str, file_path: str) -> int:
        with self.connect() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO documents (job_id, document_type, file_path, created_at)
                VALUES (?, ?, ?, datetime('now'))
                """,
                (job_id, document_type, file_path),
            )
            conn.commit()
            return cursor.lastrowid

    def get_all_jobs(self) -> list[Job]:
        with self.connect() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT id, title, company, location, description, url, source,
                       work_arrangement, employment_type, salary, recruiter,
                       date_posted, discovered_at, fit_score, status, applied,
                       notes, company_size, industry, ats_platform, remote
                FROM jobs
                ORDER BY discovered_at DESC
                """
            )
            rows = cursor.fetchall()

            return [self._row_to_job(row) for row in rows]

    def get_new_jobs(self) -> list[Job]:
        with self.connect() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT id, title, company, location, description, url, source,
                       work_arrangement, employment_type, salary, recruiter,
                       date_posted, discovered_at, fit_score, status, applied,
                       notes, company_size, industry, ats_platform, remote
                FROM jobs
                WHERE status = 'NEW'
                ORDER BY discovered_at DESC
                """
            )
            rows = cursor.fetchall()

            return [self._row_to_job(row) for row in rows]

    def _row_to_job(self, row) -> Job:
        return Job(
            id=row[0],
            title=row[1],
            company=row[2],
            location=row[3] or "",
            description=row[4] or "",
            url=row[5] or "",
            source=row[6] or "",
            work_arrangement=row[7] or "",
            employment_type=row[8] or "",
            salary=row[9],
            recruiter=row[10],
            date_posted=row[11],
            discovered_at=datetime.fromisoformat(row[12]) if row[12] else datetime.utcnow(),
            fit_score=row[13],
            status=row[14] or "NEW",
            applied=bool(row[15]),
            notes=row[16] or "",
            company_size=row[17] or "",
            industry=row[18] or "",
            ats_platform=row[19] or "",
            remote=bool(row[20]),
        )

    def get_recruiters(self):
        with self.connect() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM recruiters ORDER BY created_at DESC")
            return cursor.fetchall()

    def get_interviews(self):
        with self.connect() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM interviews ORDER BY interview_date DESC")
            return cursor.fetchall()