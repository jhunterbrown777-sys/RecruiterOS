# RecruiterOS Domain ERD

Status: Draft, for review. Design document only — no code or schema
changed as part of this document.

Relationship to [`DOMAIN_MODEL_REVIEW.md`](DOMAIN_MODEL_REVIEW.md): that
document's §2–3 proposed `Candidate (1) ──owns──> (N) Job`. This document
**supersedes that specific relationship** per the decisions below: Job is
candidate-agnostic, and `Opportunity` — not a direct Candidate→Job link —
is the per-candidate wrapper. Everything else in the prior review
(Assessment/Document consolidation, tuple→object findings, the
Excel/SQLite split) still holds and is incorporated here.

---

## Decisions this ERD incorporates

1. **SQLite is the canonical datastore.** Excel is import/export/reporting
   only, never a primary system of record. See "ADR Recommendation" below.
2. **Candidate is a first-class entity** — the person RecruiterOS
   represents. Owns profile/preferences/skills data directly, and owns
   `Opportunity` records (through which Applications, Interviews,
   Documents, and Assessments are transitively owned — see note under
   Entity List).
3. **Job is not candidate-specific.** A Job is a discovered posting,
   global to the system. The same Job may become relevant to multiple
   Candidates.
4. **Opportunity is candidate-specific** and is the main product concept:
   the wrapper connecting Candidate + Job + Company + Assessment +
   Application + Contacts + Documents + Activities.
5. **Assessment exists internally**, storing scoring history and
   explainable reasoning. An Opportunity may have many Assessments over
   time (e.g., re-scored after a profile update).
6. **Contact is a general entity.** Recruiter, hiring manager, employee
   referral, mentor, or other useful person are all *roles* a Contact can
   have, not separate entities.
7. **Document is generic and typed** (resume, cover letter, ATS report,
   recruiter message, portfolio, interview notes, etc.), not fixed
   columns on Application.

---

## Canonical ERD

```text
┌─────────────┐        ┌──────────────┐
│  Candidate  │1      N│ Opportunity  │
│             ├───────>│              │
└──────┬──────┘  has   └──────┬───────┘
       │                      │N
       │ owns directly:       │
       │ profile, preferences,│1
       │ skills, master resume│
       │                      v
       │               ┌─────────────┐        ┌─────────────┐
       │               │     Job     │N      1│   Company   │
       │               │             ├───────>│             │
       │               └─────────────┘ posted └──────┬──────┘
       │                      ^          by           │1
       │                      │N                      │
       │                      │  (same Job may be      │N
       │                      │   referenced by many    v
       │                      │   Opportunities)  ┌─────────────┐
       │                      │                   │   Contact   │
       │                      └───────────────────┤ (recruiter, │
       │                          about (via Opp)  │ hiring mgr, │
       │                                           │ referral…)  │
       │                                           └──────┬──────┘
       │                                                  │N
       │                                                  │
       │                                          M:N join│
       │                                                  v
┌──────┴──────┐  N      1  ┌──────────────┐        ┌─────────────┐
│ Opportunity │───────────>│  Assessment  │        │ Opportunity │
│  (repeat)   │    has 0..N│ (score, tags,│        │  ↔ Contact  │
└──────┬──────┘            │  reasoning)  │        │ (join table)│
       │1                  └──────────────┘        └─────────────┘
       │
       │ has 0..1 (0..N future)
       v
┌─────────────┐  1      N  ┌──────────────┐
│ Application │───────────>│  Interview   │
│ (status,    │    has 0..N│ (stage, date,│
│  dates)     │            │  outcome)    │
└─────────────┘            └──────────────┘

Opportunity (1) ──has──> (0..N) Document   [resume, cover letter, ATS report,
                                             recruiter message, portfolio,
                                             interview notes, ...]

Opportunity (1) ──has──> (0..N) Activity   [polymorphic timeline entry;
Candidate/Job/Company/Contact can also    also attachable to other entities]
be Activity subjects]
```

---

## Entity list

| Entity | Purpose |
|---|---|
| **Candidate** | The person RecruiterOS represents. Owns `candidate_profile`, `master_resume`, `preferences`, `technical_skills` directly (today's `profiles.Profile` content, made persistent and identity-bearing). Root of the per-user data boundary — every Opportunity belongs to exactly one Candidate. |
| **Job** | A discovered posting: title, company, location, description, source, etc. — today's `models.Job`, gains an `id` and a `company_id` FK. Candidate-agnostic; exists independently of whether any Candidate has looked at it. |
| **Company** | An employer. Gains `id`; `Job.company` becomes `Job.company_id`. Posts Jobs, employs/is associated with Contacts. |
| **Opportunity** | **The central entity.** Represents "this Candidate's relationship to this Job" — from first surfaced/scored, through applying, interviewing, and resolution. One row per (Candidate, Job) pair. Everything Candidate-and-Job-specific hangs off this: Assessments, the Application record, Documents, and Activities. |
| **Assessment** | One scoring/evaluation event: fit score, sub-scores (posting age, company, remote, salary, ATS-likelihood), apply recommendation, reasoning, missing skills. Belongs to an Opportunity (not to Job directly — a score is meaningless without a Candidate to score it against). An Opportunity can have many Assessments over time. Consolidates today's `jobs.fit_score` column, `JobAnalysis`, and the unused `OpportunityScore`/`models.Opportunity`. |
| **Application** | The formal "decided to pursue" record within an Opportunity: status lifecycle (e.g. Ready to Review → Applied → …), `applied_at`/`follow_up_at`. Today's `models.Application`, minus its four fixed document-path columns. |
| **Interview** | One interview event tied to an Application: stage, date, interviewer(s), format, notes, outcome. Today's `models.Interview`, gaining an `application_id` FK (its `job_id`/`company` text become derivable through Application → Opportunity → Job, removing the current denormalization). |
| **Contact** | A person: recruiter, hiring manager, referral, mentor, or other — distinguished by a `role`/`contact_type` field rather than being separate entities. Optionally linked to a Company (`works_at`). Generalizes today's `models.Recruiter` — Recruiter becomes a value of `Contact.role`, not its own entity. |
| **Document** | A generated or attached artifact: resume, cover letter, ATS report, recruiter message, portfolio, interview notes, etc. — typed by `document_type`, with a file path and timestamp. Belongs to an Opportunity (so research notes or a tailored resume can exist even before a formal Application). Replaces both `Application`'s four fixed path columns and today's unused generic `documents` table. |
| **Activity** | Polymorphic audit/timeline entry (`entity_type`, `entity_id`, `action`, `notes`, `created_at`) — already this shape in `database/schema.py`, just needs a dataclass and real call sites. Primarily attached to Opportunity, but the polymorphic design keeps it usable for Candidate-, Job-, or Company-level events too. |

**Note on "Candidate owns applications/interviews/documents/assessments":**
this ERD models that ownership as *transitive*, through Opportunity (and
Application, for Interview) rather than as direct FKs from Candidate to
each of those tables. This keeps one clear parent chain
(`Candidate → Opportunity → {Assessment, Application → Interview, Document, Activity}`)
instead of two ways to reach the same record. Flag if you intended direct
Candidate-level FKs instead — that's a different (flatter, more
denormalized) shape.

**Note on "resumes" as a Candidate-owned thing:** this ERD treats
`Candidate.master_resume` (the raw source-of-truth resume content, as
already loaded by today's `ProfileManager`) as data owned directly by
Candidate, distinct from a tailored resume **Document** generated per
Opportunity (`document_type = "resume"`). Candidate owns the source;
Opportunity owns the tailored output.

---

## Relationship list

| From | Cardinality | To | Notes |
|---|---|---|---|
| Candidate | 1 → N | Opportunity | A Candidate has many Opportunities. |
| Company | 1 → N | Job | A Company posts many Jobs. |
| Company | 1 → N | Contact | A Company has many associated Contacts (may be null/unknown). |
| Job | 1 → N | Opportunity | The same Job may back Opportunities for multiple Candidates (decision 3). |
| Opportunity | N → 1 | Candidate | — |
| Opportunity | N → 1 | Job | Unique on `(candidate_id, job_id)` — one Opportunity per Candidate per Job. |
| Opportunity | 1 → 0..N | Assessment | Scoring history. |
| Opportunity | 1 → 0..1 | Application | Today's shape (0 or 1). Modeling as 0..N is a future option if re-applications need tracking — not recommended now. |
| Opportunity | 1 → 0..N | Document | — |
| Opportunity | 1 → 0..N | Activity | — |
| Opportunity | M → N | Contact | Join table (e.g. `opportunity_contacts`), since a Contact (a recruiter at Company X) may be involved in more than one Candidate's Opportunity, and an Opportunity may involve more than one Contact. |
| Application | 1 → 0..N | Interview | — |

---

## Recommended future schema direction

Conceptual only — no `database/schema.py` changes made or implied by this
document.

- **`candidates`** — id, candidate_profile (text), master_resume (json),
  preferences (json), technical_skills (json), created_at, updated_at.
  Replaces the file-per-profile convention `profiles/profile_manager.py`
  currently reads, without necessarily changing *how* the source content
  is authored (still markdown/JSON) — just making it identity-bearing and
  queryable.
- **`companies`** (extend existing table — already correctly shaped, just
  unused) — no structural change needed beyond ensuring `id` is actually
  populated and referenced.
- **`jobs`** (extend existing table) — add `company_id` FK; keep
  `company` text temporarily during migration for backward compatibility,
  drop once all readers use the FK.
- **`opportunities`** (new) — id, candidate_id FK, job_id FK,
  status/stage (could subsume some of what's currently
  `jobs.status`), created_at, updated_at. Unique constraint on
  `(candidate_id, job_id)`.
- **`assessments`** (new) — id, opportunity_id FK, fit_score,
  posting_age_score, company_score, remote_score, salary_score,
  ats_score, priority, recommendation, reasoning, created_at. Directly
  absorbs the shape of today's `OpportunityScore`/`JobAnalysis`.
- **`applications`** (extend existing table) — add `opportunity_id` FK;
  drop `resume_path`/`cover_letter_path`/`recruiter_message_path`/
  `ats_report_path` once `documents` is wired up; keep `job_id`/
  `company_id` only if still useful for direct queries, otherwise derive
  through `opportunity_id`.
- **`contacts`** (rename/extend `recruiters`) — add `role`/`contact_type`
  (recruiter, hiring_manager, referral, mentor, other), `company_id` FK.
  Existing `recruiters` columns (name, title, linkedin_url, email, phone,
  source, notes, last_contacted_at, follow_up_at) carry over unchanged.
- **`opportunity_contacts`** (new join table) — opportunity_id,
  contact_id.
- **`interviews`** (extend existing table) — add `application_id` FK;
  deprecate `company`/`role` text columns once derivable through the
  chain.
- **`documents`** (existing table, currently unused — just needs to
  actually be written to) — add `opportunity_id` FK (in addition to or
  instead of `job_id`, since a Document belongs to a Candidate's
  Opportunity, not the Job in the abstract).
- **`activities`** (existing table — already correctly shaped, just
  unused) — no structural change needed, only real call sites.

---

## Migration priorities

Ordered by "what unblocks the most downstream work per unit of risk,"
not by ease of implementation. Each is a candidate for its own sprint/
commit sequence when this moves into implementation — not scoped further
in this document.

1. **Retire Excel as a system of record (decision 1).** Blocks everything
   else — as long as `app.py` reads/writes `data/JOB_TRACKER_AGENT_MVP.xlsx`
   as its primary Job store, no Opportunity/Assessment/Document work built
   against SQLite will see real data from the analysis pipeline. Needs its
   own ADR (see below) before implementation.
2. **Add `id` to Job and Company; add `company_id` FK to Job.** Small,
   mechanical, and every other new table (Opportunity, Assessment,
   Document) needs a real `job_id`/`company_id` to reference.
3. **Introduce `candidates` table; migrate the single implicit profile
   into one row.** Low risk today (there's only one profile in practice),
   but every subsequent table (`opportunities` especially) is designed
   around having a real `candidate_id`.
4. **Introduce `opportunities`, backfilled from existing `jobs` rows**
   (one Opportunity per existing Job, owned by the single migrated
   Candidate). This is the pivot point — once it exists, Assessment,
   Application, Document, and Activity all have the parent they're
   designed to hang off.
5. **Introduce `assessments`; migrate `jobs.fit_score` and any existing
   analysis output into it.** Decommission `models.Opportunity` /
   `OpportunityScore` duplication in favor of this.
6. **Wire `documents` to `opportunity_id`; migrate `Application`'s four
   path columns and stop writing new documents to
   `data/outputs/<timestamp>_<title>/` as the only record.**
7. **Rename/extend `recruiters` → `contacts` with a role field; add the
   `opportunity_contacts` join table.** Lowest urgency — no code
   currently writes to `recruiters` at all, so this has no live behavior
   to preserve.
8. **Add `application_id` to `interviews`; wire real call sites for
   `activities` logging.** Same low-urgency reasoning as #7 — currently
   unused tables, so sequencing them last doesn't block anything real.

---

## ADR Recommendation: SQLite as canonical datastore

This document recommends formalizing decision 1 as **ADR-0003** before any
of the migration priorities above begin. Suggested content, for your
approval before it's written as an actual ADR file:

- **Title:** SQLite is the canonical datastore; Excel is import/export/
  reporting only.
- **Status:** Proposed.
- **Context:** `DOMAIN_MODEL_REVIEW.md` finding 1 — `pipelines/discovery_pipeline.py`
  writes discovered Jobs to SQLite; `app.py`'s entire analysis and
  application pipeline independently reads/writes
  `data/JOB_TRACKER_AGENT_MVP.xlsx` via `tools/excel_tracker.py`. These
  are two disconnected systems of record for the same conceptual entity,
  with no shared identifier.
- **Decision:** SQLite becomes the single canonical datastore for all
  domain entities (Candidate, Job, Company, Opportunity, Assessment,
  Application, Contact, Document, Interview, Activity). Excel is
  demoted to an import/export and reporting surface only — e.g., "export
  current Opportunities to a spreadsheet for manual review," or "bulk-
  import candidate-supplied job leads" — never a store that any pipeline
  step treats as authoritative or reads application state back from.
- **Consequences:** `app.py`'s `main()` (currently
  `load_tracker()` / `find_next_pending_job()` / `read_job()` /
  `update_job_analysis()` / `save_tracker()`) needs to be reworked to
  read pending work from SQLite (once `opportunities` exists) instead of
  the workbook — this is real implementation work, not a documentation
  change, and should be scoped as its own migration-priority item (see
  #1 above) rather than bundled into unrelated Sprint 3 work.
  `tools/excel_tracker.py` is not deleted, but its role changes from
  "primary read/write loop" to "export/import utility," consistent with
  the "prefer deprecation, confirm before removal" rule already in force
  for this project.

This ADR is **not created as a file in this pass** — only recommended
here, per the instruction to produce one document (`docs/DOMAIN_ERD.md`)
in this step. Say the word and I'll write it as
`docs/adr/0003-sqlite-as-canonical-datastore.md` following the same
template as ADR-0001/0002.
