CREATE_CANDIDATES_TABLE = """
CREATE TABLE IF NOT EXISTS candidates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    candidate_profile TEXT,
    master_resume TEXT,
    preferences TEXT,
    technical_skills TEXT,
    created_at TEXT,
    updated_at TEXT
);
"""


CREATE_COMPANIES_TABLE = """
CREATE TABLE IF NOT EXISTS companies (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    website TEXT,
    linkedin_url TEXT,
    careers_url TEXT,
    industry TEXT,
    company_size TEXT,
    headquarters TEXT,
    glassdoor_rating REAL,
    notes TEXT,
    created_at TEXT,
    updated_at TEXT
);
"""


CREATE_JOBS_TABLE = """
CREATE TABLE IF NOT EXISTS jobs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    company TEXT NOT NULL,
    location TEXT,
    description TEXT,
    url TEXT UNIQUE,
    source TEXT,
    work_arrangement TEXT,
    employment_type TEXT,
    salary TEXT,
    recruiter TEXT,
    date_posted TEXT,
    discovered_at TEXT,
    fit_score INTEGER,
    status TEXT,
    applied INTEGER,
    notes TEXT,
    company_size TEXT,
    industry TEXT,
    ats_platform TEXT,
    remote INTEGER
);
"""


CREATE_OPPORTUNITIES_TABLE = """
CREATE TABLE IF NOT EXISTS opportunities (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    candidate_id INTEGER NOT NULL,
    job_id INTEGER NOT NULL,
    status TEXT,
    created_at TEXT,
    updated_at TEXT,
    FOREIGN KEY(candidate_id) REFERENCES candidates(id),
    FOREIGN KEY(job_id) REFERENCES jobs(id),
    UNIQUE(candidate_id, job_id)
);
"""


CREATE_APPLICATIONS_TABLE = """
CREATE TABLE IF NOT EXISTS applications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    job_id INTEGER,
    company_id INTEGER,
    status TEXT,
    resume_path TEXT,
    cover_letter_path TEXT,
    recruiter_message_path TEXT,
    ats_report_path TEXT,
    applied_at TEXT,
    follow_up_at TEXT,
    notes TEXT,
    created_at TEXT,
    updated_at TEXT,
    FOREIGN KEY(job_id) REFERENCES jobs(id),
    FOREIGN KEY(company_id) REFERENCES companies(id)
);
"""


CREATE_RECRUITERS_TABLE = """
CREATE TABLE IF NOT EXISTS recruiters (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    company TEXT,
    title TEXT,
    linkedin_url TEXT,
    email TEXT,
    phone TEXT,
    source TEXT,
    notes TEXT,
    last_contacted_at TEXT,
    follow_up_at TEXT,
    created_at TEXT,
    updated_at TEXT
);
"""


CREATE_INTERVIEWS_TABLE = """
CREATE TABLE IF NOT EXISTS interviews (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    job_id INTEGER,
    company TEXT,
    role TEXT,
    stage TEXT,
    interview_date TEXT,
    interviewer_names TEXT,
    interview_format TEXT,
    notes TEXT,
    technical_questions TEXT,
    behavioral_questions TEXT,
    outcome TEXT,
    created_at TEXT,
    updated_at TEXT,
    FOREIGN KEY(job_id) REFERENCES jobs(id)
);
"""


CREATE_ACTIVITIES_TABLE = """
CREATE TABLE IF NOT EXISTS activities (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    entity_type TEXT,
    entity_id INTEGER,
    action TEXT,
    notes TEXT,
    created_at TEXT
);
"""


CREATE_DOCUMENTS_TABLE = """
CREATE TABLE IF NOT EXISTS documents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    job_id INTEGER,
    document_type TEXT,
    file_path TEXT,
    created_at TEXT,
    FOREIGN KEY(job_id) REFERENCES jobs(id)
);
"""