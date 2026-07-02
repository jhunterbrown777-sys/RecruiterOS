# RecruiterOS System Overview

Status: Draft, for review. Document only — no implementation, no code, no
schema changes made as part of this document.

This is the synthesis document: it pulls together `ARCHITECTURE.md`,
`docs/DOMAIN_ERD.md`, `docs/WORKSPACE_ARCHITECTURE.md`, `docs/adr/`, and
direct inspection of the running code into one high-level picture. Every
section distinguishes **current state** (what's actually wired up and
runs today, verified by reading the code) from **target state** (what
the architecture is designed to become). Where the two differ, that's
called out explicitly rather than presented as already true.

---

## 1. Overall architecture diagram

```text
                              ┌───────────────────────┐
                              │   Candidate (user)     │
                              └───────────┬─────────────┘
                                          │
                              ┌───────────▼─────────────┐
                              │   GUI (PySide6)          │   gui/
                              │   Workspaces — see        │   Dashboard, Opportunity,
                              │   WORKSPACE_ARCHITECTURE  │   Recruiter, Company, Resume,
                              │                            │   Interview, Automation,
                              └───────────┬─────────────┘   Documents, Analytics, Settings
                                          │
                              ┌───────────▼─────────────┐
                              │        Services           │   services/
                              │  GUI-facing façade         │   - discovery_service.py (exists)
                              │  (today also holds the     │   - target: Opportunity/Assessment/
                              │   job-provider plugins)    │     Company/Contact/Document/...
                              └───────────┬─────────────┘     services (not yet built)
                                          │
                              ┌───────────▼─────────────┐
                              │  Orchestrator (Kernel)    │   orchestrator/
                              │  ChiefRecruiter,           │   chief_recruiter.py, workflow.py,
                              │  WorkflowRun/State,        │   state.py, queue.py
                              │  WorkflowQueue             │
                              └───────────┬─────────────┘
                       ┌──────────────────┼──────────────────────┐
                       │                  │                       │
            ┌──────────▼───────┐ ┌────────▼─────────┐  ┌──────────▼──────────┐
            │  Pipelines /      │ │  Recruiting        │  │  Job Providers        │
            │  Workers          │ │  Agents (AI)        │  │  (plugins)            │
            │  pipelines/       │ │  recruiting_agents/ │  │  services/*.py        │
            │  - discovery_     │ │  - recruiter.py     │  │  ashby, greenhouse,   │
            │    pipeline.py    │ │  - resume_agent.py  │  │  lever, workday,      │
            └──────────┬────────┘ │  - ats_agent.py     │  │  google_jobs, manual  │
                       │           │  - opportunity_     │  │  (all stub/demo data  │
                       │           │    scorer.py (dormant)│  today — see §4)     │
                       │           │  - job_scout.py     │  └───────────────────────┘
                       │           │    (dormant)         │
                       │           │  - chief_recruiter.py│
                       │           │    (result summary)  │
                       │           └──────────┬───────────┘
                       │                      │ OpenAI Agents SDK
                       │           ┌──────────▼───────────┐
                       │           │      OpenAI API        │  external
                       │           └────────────────────────┘
                       │
            ┌──────────▼──────────────────────────────────┐
            │                 Persistence                    │
            │  database/     SQLite — target canonical store  │
            │  private_memory/  candidate profile, file-based,│
            │                    one dir per profile_name      │
            │  data/outputs/     generated artifacts, one dir  │
            │                    per analysis run               │
            │  data/JOB_TRACKER_AGENT_MVP.xlsx                  │
            │                    legacy second store —          │
            │                    ADR-0003 recommends retiring   │
            │                    it to import/export only        │
            └──────────────────────────────────────────────────┘
```

The single most important fact this diagram encodes: **there are
currently two independent paths through the system**, not one. The GUI
path (top-to-bottom through Services → Orchestrator → Pipelines →
SQLite) and `app.py`'s analysis path (which bypasses the orchestrator
entirely and reads/writes the Excel file directly) do not currently
meet. See §9 (Persistence) and `docs/DOMAIN_MODEL_REVIEW.md` finding 1.

---

## 2. Layer diagram

```text
GUI
 ↓
Services
 ↓
Orchestrator (Kernel)
 ↓
Pipelines / Workers
 ↓
Persistence
```

This is `ARCHITECTURE.md`'s target chain, restated. Current adherence,
directory-by-directory:

| Layer | Directory | Current state |
|---|---|---|
| GUI | `gui/` | Depends on `database/` directly in places (`AppController.get_all_jobs()` reads raw rows) — known drift, tracked as Sprint 3 in the Architecture Alignment Plan. |
| Services | `services/` | `discovery_service.py` exists and is the only workspace fully routed through this layer (Opportunity Workspace's discovery-trigger path). Everything else in `services/` today is job-provider plugins, not GUI-facing façades — see §4. |
| Orchestrator (Kernel) | `orchestrator/` | `ChiefRecruiter.run_discovery_workflow()` is wired and tested. `run_application_workflow()` exists but is uncalled anywhere — its disposition (deprecate/remove) is still pending your decision per ADR-0001. |
| Pipelines / Workers | `pipelines/` | `DiscoveryPipeline` is the only pipeline; runs synchronously, no queueing despite `orchestrator/queue.py::WorkflowQueue` existing. |
| Persistence | `database/`, plus the untracked Excel/file stores | Split — see §9. |

`recruiting_agents/` (the AI agents) sits alongside Pipelines/Workers in
the diagram above rather than inside any one layer — it's invoked
directly by `app.py` today (bypassing the orchestrator entirely), which
is itself part of the same drift as the Excel/SQLite split.

---

## 3. Service architecture

**Current state.** `services/` holds two unrelated things today:

1. Job-provider integrations (`ashby.py`, `greenhouse.py`, `lever.py`,
   `workday.py`, `google_jobs.py`, `manual_provider.py`), each
   implementing `BaseJobProvider.search_jobs()`. These are plugins (see
   §5), not GUI-facing services.
2. `discovery_service.py::DiscoveryService` — the first real
   GUI-facing service, per ADR-0002, wrapping
   `orchestrator.ChiefRecruiter.run_discovery_workflow()`.

**Target state**, per `docs/WORKSPACE_ARCHITECTURE.md`: one service per
workspace-facing capability, each the *only* thing its workspace's GUI
controller depends on — never `database/`, `pipelines/`, or
`recruiting_agents/` directly:

| Service (target, not yet built except DiscoveryService) | Backs workspace(s) |
|---|---|
| `DiscoveryService` (exists) | Opportunity Workspace's intake |
| Opportunity service | Opportunity Workspace |
| Assessment service | Opportunity Workspace, Analytics Workspace |
| Company service | Company Workspace |
| Contact service | Recruiter Workspace |
| Resume service | Resume Workspace |
| Document service | Documents Workspace, Resume Workspace's output |
| Interview service | Interview Workspace |
| Automation/Orchestration service | Automation Workspace |
| Analytics/Reporting service | Analytics Workspace (composes other services' reads) |
| Candidate/profile + configuration services | Settings |

None of these except `DiscoveryService` exist yet. Building them is
prerequisite to wiring any workspace beyond Dashboard/Opportunity to real
data — this is Sprint 3+ work, not yet scheduled in detail.

---

## 4. Worker architecture

**Current state.** `pipelines/discovery_pipeline.py::DiscoveryPipeline`
is the only worker. It runs **synchronously, in-process**, on the calling
thread — triggered directly by `DiscoveryService`, with no queueing,
retry, or background execution. It iterates every provider × every
hardcoded query string sequentially (`services/discovery_pipeline.py`'s
`queries` list is a fixed 4-item list, not sourced from Candidate
preferences yet).

`orchestrator/queue.py::WorkflowQueue`/`QueueItem` already model
priority, status (PENDING/RUNNING/COMPLETE/FAILED), and retry count
(`attempts`/`max_attempts`) — but **nothing in the codebase ever
constructs a `WorkflowQueue` or a `QueueItem`.** It's fully-shaped,
unused scaffolding, same pattern as the Career-CRM tables in §9.

**Target state.** Workers become the execution layer for anything that
shouldn't block the GUI thread or that benefits from retry/backoff:
discovery runs, Assessment scoring passes, document generation, and
(longer-term) a Browser Worker actually submitting applications. The
existing `WorkflowQueue` shape is a reasonable starting point — it needs
(a) something to enqueue work onto it, and (b) a consumer loop, neither
of which exist today. This is also where Automation Workspace's "pending
approval" concept and "worker execution" concept meet: a worker completes
a step, and if that step is irreversible (per `CLAUDE.md`), it stops at
the queue rather than auto-executing — see §6.

---

## 5. Plugin architecture

**Current state.** The one real plugin pattern in the codebase is
`services/base_provider.py::BaseJobProvider` — an ABC with a single
required method, `search_jobs(query, location) -> list[Job]`, implemented
by six provider classes. This matches `CLAUDE.md`'s "extensible plugin
architecture" goal reasonably well *for this one extension point*.

**Important caveat, verified by reading every provider file:** all six
providers currently return **hardcoded demo data** — `grep` for
`requests.`/`httpx.`/`urlopen` across `services/` returns nothing. No
provider makes a real HTTP call yet. The plugin *interface* is real; the
plugin *implementations* are scaffolding. This matters for §10
(Security) — today's actual external-network attack surface from
providers is zero, but the target state (real API calls to six external
job boards, each needing its own auth/rate-limit handling) is not.

**Target state**, per `CLAUDE.md` and `docs/WORKSPACE_ARCHITECTURE.md`'s
extensibility notes:

- Job-provider plugins become real integrations, each owning its own
  auth (API key or scraping session) and rate-limit handling behind the
  same `BaseJobProvider` interface.
- The plugin *concept* extends beyond job providers: a future plugin
  could contribute an entire workspace (per `WORKSPACE_ARCHITECTURE.md`'s
  future-extensibility notes), a new document type/generator, or a new
  recruiting agent — none of which have an extension point defined yet.
  `BaseJobProvider` is currently the only formalized plugin contract in
  the system.

---

## 6. Automation architecture

**Current state.** "Automation" today means: `ChiefRecruiter` runs a
`DiscoveryPipeline` synchronously and returns a `WorkflowRun` with
captured state/errors (tested, working); and `app.py`'s `main()` runs
three AI agents in a fixed sequence (Recruiter → Resume → ATS) against
one Excel row, entirely outside the orchestrator. There is no automated
*decision-making* about when to run anything — a human always triggers
discovery (via the GUI button or `app_discovery.py`) and always triggers
analysis (via running `app.py`).

**Target state**, unifying `CLAUDE.md`'s AI guardrail with
`docs/WORKSPACE_ARCHITECTURE.md`'s Automation Workspace design:

- Automation is organized as **modules**, one per capability: discovery,
  Assessment scoring, resume tailoring, ATS review, (future) outreach
  drafting, (future) interview prep generation, (future) application
  submission.
- Every module is classified as either **AI-suggests** (may run
  unattended — e.g., scoring a newly discovered Job) or **AI-acts**
  (requires an explicit human confirmation before the real-world effect
  happens — e.g., submitting an application, sending an outreach
  message, overwriting profile data). This classification is spelled out
  per workspace in `docs/WORKSPACE_ARCHITECTURE.md`'s automation tables
  and is not optional — it's `CLAUDE.md`'s existing rule, made concrete.
- Automation Workspace (§ in `WORKSPACE_ARCHITECTURE.md`) is where
  AI-acts items surface as a pending-approval queue, backed by the
  currently-unwired `WorkflowQueue`, rather than each workspace
  implementing its own ad hoc "are you sure" dialog.
- `recruiting_agents/job_scout.py::JobScoutDecision` is a concrete
  example of a module that's implemented but not yet classified or
  wired — it would be AI-suggests (auto-filtering the discovery feed),
  but currently runs nowhere.

---

## 7. Memory architecture

**Current state, verified by grep:** two competing implementations exist
for the same concept — loading a candidate's profile data
(`candidate_profile.md`, `master_resume.json`, `preferences.json`,
`technical_skills.json`) from `private_memory/<profile_name>/`:

- `profiles/profile_manager.py::ProfileManager` — **the one actually
  used.** Every `recruiting_agents/*.py` file depends on it; it's covered
  by `tests/test_profile_manager.py`. Resolves the active profile via
  `settings.default_profile`.
- `memory/memory_manager.py::MemoryManager` — **unused anywhere in the
  codebase** (confirmed by grep). Resolves the active profile via the
  `ACTIVE_PROFILE` environment variable instead — a different mechanism
  than `ProfileManager`, which is itself a latent bug if both were ever
  used interchangeably. Its disposition (deprecate/remove) is still
  pending your decision per ADR-0001; it is untouched pending that.

Both are **file-based, not database-backed**, read fresh from disk on
every call, and carry no identity (no `id`, no history — a profile edit
simply overwrites the file with no record of what changed).

**Target state**, per `docs/DOMAIN_ERD.md`: memory becomes the
`Candidate` entity — `candidate_profile`, `master_resume`, `preferences`,
`technical_skills` become columns/fields on a real, identity-bearing,
persisted record rather than files re-read on every access. This is
listed as Migration Priority 3 in `DOMAIN_ERD.md` — required before
`Opportunity` (priority 4) can exist, since every Opportunity needs a
real `candidate_id` to belong to.

---

## 8. AI architecture

**Current state.** Every AI agent in `recruiting_agents/` follows the
same shape: an `Agent` (OpenAI Agents SDK) constructed with a system
prompt built from the loaded `Profile`, and a Pydantic `output_type`
forcing structured output. Agents and their outputs:

| Agent | Output schema | Invoked from |
|---|---|---|
| `recruiter.py::create_recruiter` | `JobAnalysis` (fit_score, apply_decision, reason, missing_skills, tailored_resume_notes, cover_letter_draft, recruiter_message, next_action) | `app.py` |
| `resume_agent.py::create_resume_agent` | `ResumeOutput` (tailored resume structure) | `app.py` |
| `ats_agent.py::create_ats_agent` | `ATSReview` (ats_score, keyword_match_score, matched/missing keywords, strengths/weaknesses, regeneration recommendation) | `app.py` |
| `opportunity_scorer.py::create_opportunity_scorer` | `OpportunityScore` (multi-dimensional score) | nowhere (dormant — grep confirms zero callers) |
| `job_scout.py::create_job_scout_agent` | `JobScoutDecision` (keep/priority/tags) | nowhere (dormant) |
| `chief_recruiter.py::summarize_run` | `ChiefRecruiterResult` (not an Agent — a plain function) | `app.py` |

Every agent's system prompt includes explicit honesty constraints
("never invent experience," "never claim completed Security+," "never
claim CCNA certification," "use only the profile's source data") — this
is the closest thing to an AI-safety control that exists in the prompts
themselves, separate from `CLAUDE.md`'s human-approval rule (which is a
process control, not a prompt control).

**A concrete risk worth naming, not yet mitigated anywhere:** every
prompt that includes a Job Description interpolates it directly
(`app.py`: `f"Job Description:\n\n{job.get('Job Description')}"`) with no
sanitization. Job descriptions are, in the target architecture, sourced
from external third-party postings (§5) — untrusted content flowing
directly into an LLM prompt is a textbook prompt-injection surface (a
malicious or compromised posting could attempt to override the agent's
instructions). Today's actual exposure is low because all providers
return hardcoded demo text (§5), but this should be addressed before real
provider integrations ship, not after. See §10.

**Target state.** Once Assessment (§ in `DOMAIN_ERD.md`) exists as a
persisted entity, agent outputs stop being one-shot, unlinked JSON files
and become queryable history tied to an Opportunity — enabling
`docs/WORKSPACE_ARCHITECTURE.md`'s Analytics Workspace ("were high-scored
Opportunities actually the ones that converted") and Skills & Growth
Workspace (aggregating `missing_skills` over time) to function at all.

---

## 9. Persistence architecture

**Current state — the split described in `DOMAIN_MODEL_REVIEW.md`
finding 1, restated here because it's the single fact that most affects
every other section:**

- `pipelines/discovery_pipeline.py` writes discovered Jobs to SQLite
  (`database/recruiteros.db`, via `SQLiteManager.save_job()`).
- `app.py`'s entire analysis/application pipeline reads and writes
  `data/JOB_TRACKER_AGENT_MVP.xlsx` instead (via
  `tools/excel_tracker.py`), independently of SQLite, with no shared
  identifier between an Excel "Job ID" and a SQLite `jobs.id`.
- Of the 7 tables `database/schema.py` defines, only `jobs` has a live
  reader/writer. `companies` and `applications` have zero persistence
  code; `recruiters`, `interviews`, `activities`, and `documents` have
  persistence *methods* defined but zero callers (verified by grep).
- Generated artifacts (tailored resumes, cover letters, ATS reports) are
  written as files under `data/outputs/<timestamp>_<job title>/`,
  referenced by neither the `documents` table nor `Application`'s path
  columns — a third, also-disconnected store for the same conceptual
  data.
- Candidate profile data lives as flat files under
  `private_memory/<profile_name>/` (§7) — a fourth store.

**Target state**, per `docs/DOMAIN_ERD.md` and the recommended
**ADR-0003** (not yet written as a file — see that document): SQLite
becomes the single canonical datastore for every domain entity. Excel is
demoted to an import/export and reporting surface only. `data/outputs/`
file generation continues (documents are still files on disk), but each
generated file gets a corresponding `documents` row so it's discoverable
and queryable rather than only reachable by knowing the folder name.
`DOMAIN_ERD.md`'s 8-step migration priority list sequences how this gets
built.

**Backup/durability, not addressed by any current document:** SQLite is
a single local file with no backup, replication, or corruption recovery
strategy. Worth a decision (even a simple "periodic file copy") before
`database/recruiteros.db` is the sole home for candidate/application data
that took real effort to accumulate.

---

## 10. Security architecture

**Current state, verified directly:**

- Secrets: `app.py` calls `load_dotenv()` to load `OPENAI_API_KEY` (and
  presumably future per-provider keys) from a `.env` file, which is
  correctly listed in `.gitignore`. **However, `app_gui.py` and
  `app_discovery.py` never call `load_dotenv()`** — only `app.py` does.
  This works today because the GUI and discovery-only paths don't
  currently need an API key (job providers are hardcoded demo data, §5),
  but it's a gap waiting to surface the moment any GUI workspace calls an
  AI agent directly, per `WORKSPACE_ARCHITECTURE.md`'s target design.
- Data at rest: `.gitignore` correctly excludes `private_memory/`,
  `database/*.db`, `data/outputs/`, and `data/*.xlsx` from version
  control — candidate PII doesn't end up in git history. **Nothing is
  encrypted at rest** — the SQLite database, the profile files, and every
  generated document are plain files on the local disk, readable by
  anything with filesystem access. Reasonable for a single-user local
  desktop app today; worth revisiting if RecruiterOS ever handles data
  for a Candidate who isn't the machine's owner (the recruiter/HR/firm
  use case named in `PRODUCT.md`).
- Authentication/authorization: **none.** There is no login, no user
  account, no permission model — anyone who can run the app has full
  access to whatever `ACTIVE_PROFILE`/`default_profile` currently points
  at. Fine for the current single-Candidate, single-operator design;
  becomes a real gap the moment `docs/WORKSPACE_ARCHITECTURE.md`'s
  recommended Candidate Workspace (multi-Candidate support) is built —
  scoping data by Candidate in the database is necessary but not
  sufficient without something enforcing which Candidate(s) the current
  operator may access.
- Irreversible-action control: `CLAUDE.md`'s human-approval rule (§6, §8
  above) is the system's primary safety control today, and it's
  currently a **process rule described in a document, not an enforced
  code path** — nothing currently prevents a future automation module
  from calling something irreversible directly. It becomes an enforced
  control only once Automation Workspace's approval queue (§6) actually
  exists and every AI-acts module is required to route through it.
- Prompt injection: see §8 — untrusted external content (job
  descriptions from third-party postings) flows directly into LLM
  prompts with no sanitization or instruction-boundary defense. Low risk
  today (demo data only), real risk once providers make live external
  calls.
- External network surface: currently minimal — `manual_provider.py` and
  the other five providers make no real network calls (§5); only the
  OpenAI API is a live external dependency today. This expands
  significantly once real job-board integrations ship, each becoming a
  new trust boundary (a compromised or malicious job board response
  feeding directly into the discovery pipeline and, downstream, into
  agent prompts).

**Target state / recommendations, not yet implemented:**

1. Centralize environment/secret loading (one place all three entry
   points — `app.py`, `app_gui.py`, `app_discovery.py` — go through)
   instead of only `app.py` calling `load_dotenv()`.
2. Sanitize or bound untrusted content (job descriptions) before
   interpolating it into agent prompts, ahead of any real provider
   integration going live.
3. Treat Automation Workspace's approval queue as the enforcement point
   for `CLAUDE.md`'s human-approval rule, not just its documentation —
   an AI-acts module should be structurally unable to bypass it, not
   merely instructed not to.
4. Revisit encryption-at-rest and authentication if/when RecruiterOS
   moves toward the multi-Candidate (recruiter/firm/HR) use case named in
   `PRODUCT.md` — not needed for the current single-user desktop scope.
5. When real provider integrations are built, each needs its own
   rate-limit/backoff handling and response validation before its output
   reaches the discovery pipeline — not addressed by `BaseJobProvider`'s
   current interface, which only specifies `search_jobs() -> list[Job]`
   with no failure-mode contract.

---

## Explicitly out of scope for this document

No code, no schema, no new files beyond this one. This is a snapshot
synthesis of current-vs-target state across all ten areas requested,
cross-referencing `ARCHITECTURE.md`, `docs/DOMAIN_ERD.md`,
`docs/DOMAIN_MODEL_REVIEW.md`, `docs/WORKSPACE_ARCHITECTURE.md`, and
`docs/adr/`. Where this document identifies a gap (the `load_dotenv()`
inconsistency, the prompt-injection surface, the unenforced approval
gate), that's a finding for your prioritization, not an implicit request
for me to act on it.
