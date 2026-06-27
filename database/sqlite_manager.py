import sqlite3
from pathlib import Path

from database.schema import (
    CREATE_ACTIVITIES_TABLE,
    CREATE_APPLICATIONS_TABLE,
    CREATE_COMPANIES_TABLE,
    CREATE_DOCUMENTS_TABLE,
    CREATE_INTERVIEWS_TABLE,
    CREATE_JOBS_TABLE,
    CREATE_RECRUITERS_TABLE,
)
from models.job import Job
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
            cursor.execute(CREATE_COMPANIES_TABLE)
            cursor.execute(CREATE_JOBS_TABLE)
            cursor.execute(CREATE_APPLICATIONS_TABLE)
            cursor.execute(CREATE_RECRUITERS_TABLE)
            cursor.execute(CREATE_INTERVIEWS_TABLE)
            cursor.execute(CREATE_ACTIVITIES_TABLE)
            cursor.execute(CREATE_DOCUMENTS_TABLE)
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

    def get_all_jobs(self):
        with self.connect() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM jobs ORDER BY discovered_at DESC")
            return cursor.fetchall()

    def get_new_jobs(self):
        with self.connect() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM jobs WHERE status = 'NEW' ORDER BY discovered_at DESC")
            return cursor.fetchall()

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