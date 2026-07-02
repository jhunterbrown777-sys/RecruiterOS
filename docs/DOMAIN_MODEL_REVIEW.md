# Domain Model Review

Status: Draft, for review. Design document only — no code changed as part of
this review, per the pause before Sprint 3.

Method: direct inspection of `models/*.py`, `database/schema.py`,
`database/sqlite_manager.py`, `profiles/profile.py`,
`recruiting_agents/*.py` (agent output schemas), `tools/excel_tracker.py`,
`pipelines/discovery_pipeline.py`, `app.py`, and `gui/controller.py`, plus
grep for every call site of each persistence method and each agent
factory, to establish what's actually wired up versus merely declared.

---

## Findings that precede the model (read this first)

These are more consequential than any individual field-naming decision,
so they're stated up front rather than buried in the tables below.

1. **There are two disconnected "Job" data stores.** `pipelines/discovery_pipeline.py`
   writes discovered postings into the SQLite `jobs` table via
   `models.Job` / `SQLiteManager.save_job()`. Separately, `app.py`'s entire
   analysis-and-application pipeline (`main()`) reads jobs from an Excel
   workbook (`data/JOB_TRACKER_AGENT_MVP.xlsx`, via `tools/excel_tracker.py`)
   and writes analysis results back into that same workbook. **Neither
   pipeline touches the other's store.** A job discovered via the GUI's
   "Discover" action has no path into the Excel tracker that `app.py`
   consumes, and vice versa. There is no shared identifier between a
   SQLite `jobs.id` and an Excel "Job ID" column.
2. **Of the 7 tables in `database/schema.py`, only `jobs` is actually
   read or written by any running code path.** Grep confirms
   `save_recruiter`, `save_interview`, `save_document`, `log_activity`,
   `get_recruiters`, and `get_interviews` are all defined on
   `SQLiteManager` but have **zero callers** anywhere in the codebase.
   `companies` and `applications` have no persistence methods at all —
   no `save_company`, no `save_application`. These six tables are schema
   scaffolding for the "Career CRM" goals in `ROADMAP.md` v0.5.0, not
   working data paths.
3. **`models.Job` and `models.Company` have no `id` field**, even though
   `applications.company_id` and `interviews.job_id` are foreign keys
   that assume one exists. Any code that wants to reference a saved Job
   or Company by identity today has to separately track the
   `cursor.lastrowid` returned by `save_job()` — the domain object itself
   can't carry its own persisted identity.
4. **`models.Opportunity` duplicates `recruiting_agents/opportunity_scorer.py::OpportunityScore`
   field-for-field** (title, company, score, fit_score, posting_age_score,
   company_score, remote_score, salary_score, ats_score, priority,
   recommendation, reasoning) — one as a dataclass, one as a Pydantic
   model. Grep confirms **neither is ever instantiated or referenced**
   anywhere else in the codebase. This looks like scaffolding for ranking
   (`PRODUCT.md`: "Rank opportunities", "Explain rankings") that was
   started twice and wired into nothing.
5. **Three overlapping representations of "how good is this job" exist
   with no reconciliation:** the `jobs.fit_score` column, `JobAnalysis.fit_score`
   (the `recruiting_agents/recruiter.py` agent's output, actually used by
   `app.py`), and `OpportunityScore.fit_score` (unused). They are not the
   same number computed three ways — they're three independent fields
   that happen to share a name.
6. **`JobScoutDecision` (`recruiting_agents/job_scout.py`) is fully
   implemented but never invoked.** `DiscoveryPipeline.run()` saves every
   job returned by every provider unconditionally; there is no filtering
   or scoring step at discovery time despite the agent existing to do
   exactly that.
7. **There is no persisted "candidate" entity.** `profiles.Profile` is
   read fresh from disk on every call (`ProfileManager.load()`), has no
   `id`, and the system assumes exactly one active profile at a time via
   `ACTIVE_PROFILE` / `settings.default_profile`. Nothing in the schema
   references a candidate/profile at all — `jobs`, `applications`, etc.
   are implicitly global, single-tenant tables.
8. **Documents are represented two incompatible ways.** `Application` has
   four fixed columns (`resume_path`, `cover_letter_path`,
   `recruiter_message_path`, `ats_report_path`), while a separate generic
   `documents` table (`document_type`, `file_path`, FK to `job_id`) exists
   for the same concept and is unused. Neither is populated by `app.py`
   today — generated files actually land in per-run timestamped folders
   under `data/outputs/`, referenced by neither table.

---

## 1. Core business entities (as they exist or are implied today)

| Entity | Where represented | Persisted in practice? | Notes |
|---|---|---|---|
| Job | `models/job.py` (dataclass) + `jobs` table; **also** an ad hoc `dict` read from the Excel tracker in `app.py` | Yes (SQLite side only) | Two disconnected representations — see finding 1. No `id` field. |
| Company | `models/company.py` (dataclass) + `companies` table | No | Table exists, dataclass exists, zero persistence code. `Job.company` is a denormalized string, not an FK. |
| Application | `models/application.py` (dataclass) + `applications` table | No | Represents the "decided to pursue" lifecycle; no code ever creates one. |
| Recruiter | `models/recruiter.py` (dataclass) + `recruiters` table | No (methods exist, unused) | `Job.recruiter` is a free-text string, not a link to this entity. |
| Interview | `models/interview.py` (dataclass) + `interviews` table | No (methods exist, unused) | Denormalizes `company`/`role` as text instead of deriving via `job_id`. |
| Candidate / Profile | `profiles/profile.py` (dataclass), file-backed | N/A (not DB-backed) | No identity, no history, singular/global per process. |
| Activity (audit log) | `activities` table only | No | No dataclass at all; polymorphic `(entity_type, entity_id)` design is reasonable but nothing writes to it. |
| Document | `documents` table (generic) **and** 4 fixed columns on `Application` | No (neither path used) | Actual generated files live in `data/outputs/<timestamp>_<title>/`, tracked by neither. |
| JobAnalysis (fit assessment) | `recruiting_agents/recruiter.py::JobAnalysis` (Pydantic, agent output) | Only as Excel columns + a JSON file per run | Not linked to `jobs.id`. |
| OpportunityScore / Opportunity | `recruiting_agents/opportunity_scorer.py::OpportunityScore` (Pydantic) + `models/opportunity.py::Opportunity` (dataclass) | No — both unused | Duplicate models, see finding 4. |
| ATSReview | `recruiting_agents/ats_agent.py::ATSReview` (Pydantic, agent output) | Only as a JSON file + DOCX per run | Not linked to any Job/Application id. |
| ResumeOutput | `recruiting_agents/resume_agent.py::ResumeOutput` (Pydantic, agent output) | Only as a JSON file + DOCX per run | Payload of what should be a "resume" Document. |
| JobScoutDecision | `recruiting_agents/job_scout.py::JobScoutDecision` (Pydantic) | N/A — never invoked | Would gate discovery if wired in. |
| ChiefRecruiterResult | `recruiting_agents/chief_recruiter.py::summarize_run()` output | No, transient | Summary-of-a-run object, not a business entity. |
| WorkflowRun / WorkflowState / QueueItem | `orchestrator/{workflow,state,queue}.py` | In-memory only | Process/orchestration state, **not** business domain — correctly kept out of `models/`. |

---

## 2. Recommended canonical domain model

Conceptual shape only — no code, no field types beyond what's needed to
convey intent. Each entity below assumes it gets an `id: int` (or UUID)
once persisted, even where not called out explicitly.

- **Candidate** — the person the system represents. Holds (or points to)
  the candidate-profile content currently loaded ad hoc by
  `ProfileManager` (`candidate_profile`, `master_resume`, `preferences`,
  `technical_skills`). Becomes the tenant boundary everything else hangs
  off of.
- **Job** — a discovered posting. Owns identity (`id`), the fields
  already on `models.Job`, and a reference to `Company` instead of a
  denormalized company-name string. Drops `fit_score` as a bare column in
  favor of a linked `Assessment` history (see below) — a Job can be
  scored more than once as the candidate profile or the market changes.
- **Company** — employer. Gains `id`. `Job.company` becomes
  `Job.company_id`.
- **Assessment** (new — consolidates `JobAnalysis` + `OpportunityScore` +
  `jobs.fit_score`) — one scoring/evaluation of a Job against a
  Candidate at a point in time: fit score, sub-scores (posting age,
  company, remote, salary, ATS-likelihood), apply decision, reasoning,
  missing skills. A Job can have zero, one, or many Assessments over
  time (e.g., re-scored after a profile update); the "current" one is
  whichever is most recent, not a mutable column on Job.
- **Application** — the candidate's decision to formally pursue a Job.
  References `Job` and `Company` (as it already does), gains a status
  lifecycle, and **drops the four fixed document-path columns** in favor
  of owning a collection of `Document`s.
- **Document** — a generated artifact (resume, cover letter, recruiter
  message, ATS report), typed by `document_type`, with a file path and
  timestamp, owned by an `Application`. Replaces both the unused generic
  `documents` table's current shape and `Application`'s fixed path
  columns with one consistent mechanism — adding a 5th document type
  later doesn't require a schema change.
- **Recruiter** — a contact person, optionally linked to `Company`, and
  optionally linked to the `Application`(s)/`Job`(s) they're associated
  with (many-to-many via a join, or a simple FK on Application if one
  recruiter per application is an acceptable simplification).
- **Interview** — one interview event. Linked to `Application` (not just
  `Job`) as the primary FK, since stage/outcome belong to a specific
  pursuit of a job, not the job posting in the abstract; `Job` and
  `Company` are derivable through `Application`, so the current
  denormalized `company`/`role` text fields on `Interview` become
  redundant once that link exists.
- **Activity** — polymorphic audit/timeline entry
  (`entity_type`, `entity_id`, `action`, `notes`, `created_at`), as
  already shaped in the schema. Needs a corresponding dataclass and
  actual call sites at the point each entity's state changes.
- **JobScoutDecision** — recommend keeping this as an ephemeral
  discovery-time filter, *not* a persisted entity. Its effect (keep/drop,
  priority, tags) should be written onto the `Job` row it decided about,
  rather than stored as its own row.

---

## 3. Proposed relationships

```text
Candidate (1) ──owns──> (N) Job
Candidate (1) ──owns──> (N) Application

Job (N) ──posted by──> (1) Company
Job (1) ──scored by──> (0..N) Assessment
Job (0..1) ──pursued via──> (1) Application

Application (1) ──produces──> (0..N) Document
Application (1) ──scheduled for──> (0..N) Interview
Application (0..N) ──involves──> (0..N) Recruiter
Application (N) ──at──> (1) Company        [denormalized copy of Job's company for query convenience, acceptable]

Recruiter (N) ──works at──> (0..1) Company

Activity (1) ──references──> (1) [Job | Company | Application | Recruiter | Interview | Assessment]
```

`Assessment`, `Document`, and `Activity` are all "child of exactly one
parent, queried by parent id" relationships — no new join tables needed
beyond `Application ↔ Recruiter`, which is the only genuine many-to-many
in the model as currently understood.

---

## 4. Where tuple-based data should become domain objects

Every one of these currently returns raw `sqlite3` tuples from
`cursor.fetchall()` rather than typed objects, and every one is
positionally indexed by whatever calls it:

| Method | Returns today | Consumer(s) | Should return |
|---|---|---|---|
| `SQLiteManager.get_all_jobs()` | `list[tuple]` | `gui/controller.py` (`job[14]`, `job[15]`) | `list[Job]` |
| `SQLiteManager.get_new_jobs()` | `list[tuple]` | none currently (defined, unused) | `list[Job]` |
| `SQLiteManager.get_recruiters()` | `list[tuple]` | none currently (defined, unused) | `list[Recruiter]` |
| `SQLiteManager.get_interviews()` | `list[tuple]` | none currently (defined, unused) | `list[Interview]` |

`get_all_jobs()`/`gui/controller.py` is the only one with a live consumer
today and is already flagged as Sprint 3, item 3.1 in the Architecture
Alignment Plan. The other three are worth fixing in the same pass since
they're the same bug shape, even though nothing currently depends on
their tuple output.

---

## 5. Which objects should become first-class entities

Recommend promoting, in priority order:

1. **Candidate** — currently the biggest gap. Nothing else in the model
   can be made properly multi-tenant (a real requirement per
   `PRODUCT.md`'s stated audience of "individuals, recruiters, recruiting
   firms, HR departments") until there's an addressable Candidate with an
   id that Jobs/Applications/etc. belong to.
2. **Assessment** — currently smeared across a bare `fit_score` column,
   an unlinked Excel column, an unlinked JSON file, and an entirely
   unused `Opportunity`/`OpportunityScore` pair. Consolidating into one
   first-class, Job-linked entity removes findings 4 and 5 at once.
3. **Document** — currently smeared across 4 fixed `Application` columns,
   an unused generic table, and untracked files in `data/outputs/`.
   First-class treatment fixes finding 8 and makes new document types
   (e.g., a future "portfolio" or "case study" artifact) additive instead
   of a schema change.
4. **Company, Application, Recruiter, Interview** — these are already
   modeled as dataclasses with schema tables; they need to become
   *actually wired* first-class entities (real save/get methods with real
   callers), not new design work.

`JobScoutDecision`, `ChiefRecruiterResult`, and the orchestration types
(`WorkflowRun`/`WorkflowState`/`QueueItem`) are correctly *not*
recommended for first-class/persisted status — they're process artifacts
or one-shot decisions, not business records.

---

## 6. Missing entities needed for long-term scalability

- **Candidate**, as above — required before any multi-user story
  (recruiter managing several candidates, HR department, recruiting firm)
  is possible. Right now "the user" is an environment variable, not data.
- **User / Account**, distinct from Candidate — if a recruiter or HR
  persona is meant to operate the system on behalf of one or more
  Candidates (per `PRODUCT.md`), that's a different entity than the
  Candidate being represented, with its own permissions boundary. No such
  concept exists today; everything assumes operator == candidate.
- **Assessment** (see above) — needed so "explain rankings" (a stated
  `PRODUCT.md` goal) has something durable to explain; right now a
  ranking rationale exists only inside a per-run JSON file or an Excel
  cell, not queryable.
- **Document** (see above) — needed for "track recruiters," "prepare
  interviews," and general application history to be reviewable later
  rather than living only in dated folders on disk.
- **JobSource** (lighter-weight) — `Job.source`/`ats_platform` are free
  strings today (`"greenhouse"`, `"lever"`, etc.), which is probably fine
  short-term given `services/base_provider.py` already gives providers a
  canonical `provider_name`. Worth revisiting only if provider-specific
  metadata (rate limits, auth state, last-successful-run) needs to be
  tracked per source later — not urgent now.
- **A single source of truth for "Job".** Not a new entity, but the
  precondition for all of the above: as long as `app.py`'s pipeline reads
  from Excel and the discovery/GUI path reads from SQLite, any entity
  that references "a Job" (Assessment, Application, Document, Interview)
  has to pick one store to belong to, and today there's no correct
  answer. This should be resolved — Excel retired in favor of SQLite, or
  an explicit sync step introduced — before Assessment/Application/Document
  work is built on top of it, or that work will inherit the same split.

---

## Explicitly out of scope for this document

No schema migrations, no renamed columns, no new files beyond this one.
This is a description of current state and a recommended target shape
only. Sequencing this into Sprint 3+ (and which parts, if any, warrant
their own ADR before implementation) is a decision for you to make after
reviewing this document.
