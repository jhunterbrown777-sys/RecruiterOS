# RecruiterOS Implementation Backlog

Status: Draft, for review. This is the master engineering backlog,
superseding the previous version of this file. Derived from `PRODUCT.md`,
`ROADMAP.md`, `docs/DOMAIN_MODEL_REVIEW.md`, `docs/DOMAIN_ERD.md`,
`docs/WORKSPACE_ARCHITECTURE.md`, `docs/SYSTEM_OVERVIEW.md`, and
`docs/adr/`. No code is included — every item below is a task
description, not an implementation. Architecture is treated as stable per
your instruction; nothing here proposes new architecture, only sequences
already-documented work.

**Priority:** Critical = blocks the MVP critical path (see below). High =
required for the target architecture to function end-to-end, not
MVP-blocking. Medium = materially improves the product, deferrable past
MVP. Low = future/extensibility.

**Complexity:** S = under a day, single file. M = a few files, one
commit's worth. L = multiple files/commits, a full sprint item. XL = a
new subsystem.

**Milestones:**

- **M0** — Foundational decisions (zero/near-zero code)
- **M1** — MVP: Domain & Persistence foundation (Candidate, Job.id, Opportunity, Assessment)
- **M2** — MVP: Services & Opportunity/Resume Workspaces
- **M3** — MVP: cross-cutting GUI, security hygiene, testing
- **M4** — Post-MVP: Companies & Contacts workspaces
- **M5** — Post-MVP: Automation approval gate, Interview/Analytics/Settings GUI
- **M6** — Real integrations & hardening
- **M7** — Future agents & extensibility

---

## Core Platform

| ID | Title | Description | Dependencies | Priority | Complexity | User-facing value | Milestone |
|---|---|---|---|---|---|---|---|
| ENG-001 | Author ADR-0003 | Write `docs/adr/0003-sqlite-as-canonical-datastore.md` from the recommendation already drafted in `docs/DOMAIN_ERD.md`. | None | Critical | S | None directly — unblocks confident SQLite-first development for everything below, avoiding rework. | M0 |
| ENG-002 | Resolve `MemoryManager` disposition | Confirm with project owner whether `memory/memory_manager.py` is obsolete, deprecated, or reserved (ADR-0001); act on the answer. | Decision from project owner | Medium | S | None — internal cleanup, does not block MVP. | M6 |
| ENG-003 | Resolve `run_application_workflow` disposition | Same as ENG-002, for `orchestrator/chief_recruiter.py::run_application_workflow`. | Decision from project owner | Medium | S | None — internal cleanup, does not block MVP. | M6 |
| ENG-004 | Resolve `models.Opportunity`/`OpportunityScore` duplication | Confirm disposition of the existing unused `models/opportunity.py::Opportunity` before it's redefined under ENG-041 — same name, incompatible shape today. | Decision from project owner | Critical | S | Blocks ENG-041, which the whole Opportunity Workspace depends on. | M0 |
| ENG-005 | Rework `app.py` to read/write via SQLite instead of Excel | Replace `tools/excel_tracker.py`-based intake/writes in `app.py::main()` with the `opportunities`/`assessments` tables. **Not MVP-blocking** — the new GUI-native flow (Opportunity/Resume Workspace) is built directly on SQLite from day one and does not route through `app.py`'s Excel-based CLI at all; this task retires the old path once the new one is proven, rather than fixing the old path first. | ENG-001, ENG-034, ENG-036 | Medium | XL | Candidate no longer has two disconnected records of "what I've analyzed." | M6 |
| ENG-006 | Retire Excel tracker to import/export-only | Repurpose `tools/excel_tracker.py` per ADR-0003 once ENG-005 lands. | ENG-005 | Medium | M | None directly — completes the cleanup ENG-005 starts. | M6 |
| ENG-007 | Wire `WorkflowQueue` as the orchestrator's execution backbone | `orchestrator/queue.py` is fully shaped but never constructed anywhere; give it an enqueue path and consumer loop. | None | Medium | L | Long-running actions (discovery, scoring) stop blocking the UI once paired with ENG-008/ENG-053. | M5 |
| ENG-008 | Move discovery pipeline execution off the GUI thread | `DiscoveryPipeline.run()` runs synchronously on the calling thread today, freezing the UI for its duration. | ENG-007 | Medium | L | Candidate can keep using the app while a discovery pass runs instead of the UI locking up. | M5 |

---

## Domain

| ID | Title | Description | Dependencies | Priority | Complexity | User-facing value | Milestone |
|---|---|---|---|---|---|---|---|
| ENG-009 | Add `id` to `models.Job` | No identity field today despite other tables needing to FK to it. | None | Critical | S | Enables an Opportunity to reliably point at "this exact posting." | M1 |
| ENG-010 | Create `models.Candidate` | New dataclass backing `candidate_profile`, `master_resume`, `preferences`, `technical_skills` — today's file-read `profiles.Profile` content, made identity-bearing. | None | Critical | S | Foundation for every other MVP entity; no user-visible change alone. | M1 |
| ENG-011 | Create `models.Document` | No dataclass exists today for the generic document concept — only ad hoc path fields on `Application`. | None | High | S | Candidate's generated resumes/cover letters/ATS reports become one consistent, findable thing instead of scattered files. | M2 |
| ENG-012 | Create `models.Activity` | The `activities` table has no corresponding dataclass. | None | Low | S | Enables a future audit/timeline view; no direct MVP value. | M5 |
| ENG-013 | Update `models.Application` | Add `opportunity_id`; drop the four fixed document-path columns once ENG-011/ENG-030 land. | ENG-011, ENG-030 | High | S | Application status stays accurate as documents are added/replaced, instead of pointing at stale fixed slots. | M2 |
| ENG-014 | Update `models.Interview` | Add `application_id`; deprecate denormalized `company`/`role` text once derivable through the chain. | ENG-013 | Medium | S | Interview records stay consistent with the Opportunity they belong to. | M5 |

---

## Persistence

| ID | Title | Description | Dependencies | Priority | Complexity | User-facing value | Milestone |
|---|---|---|---|---|---|---|---|
| ENG-015 | Create `candidates` table + persistence methods | Migrate the single implicit profile (`private_memory/hunter/`) into one row. | ENG-010 | Critical | M | The candidate's data survives as a real record instead of only files re-read on every access. | M1 |
| ENG-016 | Implement `save_application`/`get_application(s)` | `applications` table exists with zero persistence code today. | ENG-013, ENG-030 | High | M | Application status/history actually persists instead of only living in memory during a session. | M2 |
| ENG-017 | Wire `documents` table to `opportunity_id` | `documents` table + `save_document()` exist with zero callers. Add the FK, wire real call sites. | ENG-011, ENG-030 | High | M | Every generated document is retrievable later, not just in the run folder it was created in. | M2 |
| ENG-018 | Add `application_id` column to `interviews` table | Schema counterpart to ENG-014. | ENG-016 | Medium | S | Supports Interview Workspace once built. | M5 |
| ENG-019 | Replace raw tuple returns with typed objects | `get_all_jobs()`, `get_new_jobs()`, `get_recruiters()`, `get_interviews()` all return raw `sqlite3` tuples; `get_all_jobs()` is already consumed positionally (`job[14]`, `job[15]`) in `gui/controller.py`. | ENG-009 | High | M | Removes a real correctness risk (a schema reorder silently breaking the dashboard) — indirect user value via reliability. | M3 |
| ENG-020 | Define SQLite backup/durability strategy | No backup/corruption-recovery plan exists for `database/recruiteros.db` today. | None | Medium | S | Candidate's accumulated job-search history isn't one disk failure from gone. | M6 |
| ENG-021 | Add indexes for common query patterns | No indexes beyond primary keys exist today. | ENG-030 | Low | S | Keeps list views fast as data volume grows. | M6 |

---

## Services

| ID | Title | Description | Dependencies | Priority | Complexity | User-facing value | Milestone |
|---|---|---|---|---|---|---|---|
| ENG-022 | Build `CandidateService` | Wraps `ProfileManager`, transitioning it toward the DB-backed `candidates` table. | ENG-015 | Critical | M | The rest of the app can reliably ask "who is the active candidate" from one place. | M1 |
| ENG-023 | Build `DocumentService` | Generate/list/version documents. | ENG-017 | High | M | Backs Resume Workspace's and Documents' generation/listing. | M2 |
| ENG-024 | Build `InterviewService` | Backs a future Interview Workspace. | ENG-018 | Medium | S | No MVP value directly — future workspace enabler. | M5 |
| ENG-025 | Build `AutomationService` | Wraps `WorkflowQueue` and `ChiefRecruiter` run history. | ENG-007 | Medium | M | Candidate can eventually see what AI has queued/done — not needed for MVP's synchronous flow. | M5 |
| ENG-026 | Build `AnalyticsService` | Read-only aggregation over Opportunity/Assessment/Application service reads. | ENG-035, ENG-037 | Low | M | Enables future trend reporting; no MVP value. | M5 |
| ENG-027 | Build `ConfigurationService` | Exposes `config/settings.py`'s automation thresholds and provider toggles as editable. | None | Low | S | Candidate can tune scoring thresholds without editing code — post-MVP convenience. | M5 |

---

## GUI

| ID | Title | Description | Dependencies | Priority | Complexity | User-facing value | Milestone |
|---|---|---|---|---|---|---|---|
| ENG-028 | Refactor `AppController` off direct `database`/`pipelines` access | Remaining direct `SQLiteManager` calls in `gui/controller.py` should route through services (ADR-0002). | ENG-019, ENG-035 | High | M | Dashboard stays correct as the data model evolves underneath it, instead of silently breaking. | M3 |
| ENG-029 | Formalize Dashboard's data sourcing | Route Mission Control's stat/panel data through the new services instead of ad hoc direct queries. | ENG-028 | Medium | M | Dashboard numbers (e.g. today's hardcoded `average_ats: 92`) become real instead of stubbed. | M3 |
| ENG-030 | Update sidebar navigation | Reflect the workspaces actually built (`gui/main_window.py`'s remaining buttons are placeholders today). | ENG-039 (at minimum) | Medium | S | Candidate isn't shown nav buttons that do nothing when clicked. | M3 |
| ENG-031 | Build Documents Workspace GUI | Library/vault view across all Document types. | ENG-023 | Medium | L | Candidate can find and reuse anything generated, not just what's in the current Opportunity. | M5 |
| ENG-032 | Build Interview Workspace GUI | Schedule-first upcoming/past view. | ENG-024 | Low | M | Post-MVP convenience view. | M5 |
| ENG-033 | Build Automation Workspace GUI | Pending-approval queue + run history. | ENG-025 | Medium | L | Candidate sees and controls what AI is about to do, rather than trusting it implicitly. | M5 |
| ENG-034 | Build Analytics Workspace GUI | Funnel/trend reporting views. | ENG-026 | Low | M | Candidate can see whether their strategy is working over time — post-MVP. | M5 |
| ENG-035 | Build Settings GUI | Candidate profile editing, provider toggles, automation threshold editing. | ENG-022, ENG-027 | Medium | M | Candidate can update their profile/preferences without hand-editing JSON files. | M3 |
| ENG-036 | Add pagination/lazy loading for list views | List-based workspaces load entire tables into memory unbounded today. | ENG-019, ENG-021 | Low | M | App stays responsive once job/opportunity volume grows past demo size. | M6 |
| ENG-037 | Add caching for repeated Company/Contact lookups | Avoid redundant repeated queries once detail views join across Company/Contact per record. | ENG-045, ENG-051 | Low | S | Faster detail-view loads once Company/Contact data is real. | M6 |

---

## AI

| ID | Title | Description | Dependencies | Priority | Complexity | User-facing value | Milestone |
|---|---|---|---|---|---|---|---|
| ENG-038 | Centralize agent prompt/context construction | `recruiter.py`, `resume_agent.py`, and `ats_agent.py` each independently rebuild a near-identical profile-context block. | None | Medium | M | Indirect — fewer inconsistencies between agents' understanding of the candidate. | M3 |
| ENG-039 | Make AI agent calls non-blocking | `Runner.run_sync()` is synchronous; blocks the UI once GUI workspaces call agents directly (ENG-041/ENG-052). | ENG-041, ENG-052 | High | M | Candidate isn't staring at a frozen window while a resume tailors or a job is scored. | M2 |
| ENG-040 | Standardize agent-invocation pattern | Extract the repeated `Agent(...) → Runner.run_sync(...) → .final_output` shape across all five agent factories into one shared call path. | ENG-038 | Low | S | Indirect — reduces the chance of one agent silently drifting from the others' error handling. | M6 |

---

## Automation

| ID | Title | Description | Dependencies | Priority | Complexity | User-facing value | Milestone |
|---|---|---|---|---|---|---|---|
| ENG-041 | Consolidate `JobAnalysis`/`OpportunityScore`/`fit_score` into one Assessment flow | Three overlapping "how good is this job" representations exist with no reconciliation. | ENG-046, ENG-047 | Critical | M | Candidate sees one trustworthy score with one explanation, not three inconsistent numbers. | M2 |
| ENG-042 | Wire `JobScoutDecision` into `DiscoveryPipeline` | `recruiting_agents/job_scout.py` is implemented but never invoked; discovery currently saves everything unfiltered. | None | Medium | M | Candidate sees a pre-filtered, higher-signal discovery feed instead of raw noise. | M5 |
| ENG-043 | Implement structural AI-suggests / AI-acts enforcement | Automation Workspace's approval queue should be the only path an "AI-acts" module can reach an irreversible effect through — not just a documented convention. | ENG-025, ENG-033 | Medium | L | Candidate can trust nothing gets submitted/deleted/overwritten without their explicit click, by construction, not just by policy. | M5 |
| ENG-044 | Wire `Activity` logging at entity state transitions | `log_activity()` exists with zero callers; add real call sites at Opportunity stage changes, Application status changes, Document generation. | ENG-012, ENG-050 | Low | M | Candidate gets a real history/timeline instead of no record of what happened when. | M5 |
| ENG-045 | Implement Cover Letter Agent | Split out of `JobAnalysis.cover_letter_draft` into its own agent, per `docs/AGENTS.md`. | ENG-023 | Low | M | Slightly better cover-letter quality/focus — marginal over current combined output. | M7 |
| ENG-046 | Implement Outreach Agent | Drafts outreach/follow-up messages for Contacts; sending always requires ENG-043's gate. | ENG-051, ENG-043 | Low | M | Candidate gets a drafted starting point for recruiter outreach instead of writing from scratch. | M7 |
| ENG-047 | Implement Company Research Agent | Auto-populates Company Workspace research notes. | ENG-057 | Low | M | Candidate gets a research head start on a company instead of doing it manually. | M7 |
| ENG-048 | Implement Interview Coach Agent | Generates prep briefings for Interview Workspace. | ENG-032 | Low | M | Candidate gets tailored interview prep instead of generic advice. | M7 |
| ENG-049 | Implement Browser Worker | Actually submits applications — the clearest irreversible action in the product. Must not execute without ENG-043's gate; highest-risk item in the backlog. | ENG-043, ENG-050 | Low | XL | Saves the candidate manual re-entry of application data on job sites — but only once the safety gate exists. | M7 |

---

## Contacts

| ID | Title | Description | Dependencies | Priority | Complexity | User-facing value | Milestone |
|---|---|---|---|---|---|---|---|
| ENG-050 | Create `models.Contact` | Generalizes `models.Recruiter` with a `role`/`contact_type` field (recruiter, hiring_manager, referral, mentor, other), per `DOMAIN_ERD.md` decision 6. | None | Medium | S | Candidate can track any relevant person, not just recruiters. | M4 |
| ENG-051 | Rename/extend `recruiters` table → `contacts` | Add `role`, `company_id` FK, and the `opportunity_contacts` join table. Lowest-risk migration — nothing currently writes to `recruiters`. | ENG-050, ENG-057 | Medium | M | No behavior loss — nothing depends on the old table today. | M4 |
| ENG-052 | Build `ContactService` | Backs the Contacts/Recruiter workspace. | ENG-051 | Medium | S | Enables ENG-053. | M4 |
| ENG-053 | Build Recruiter (Contacts) Workspace GUI | Directory + detail view, follow-up state. | ENG-052 | Medium | L | Candidate can track who they've talked to and when to follow up. | M4 |

---

## Companies

| ID | Title | Description | Dependencies | Priority | Complexity | User-facing value | Milestone |
|---|---|---|---|---|---|---|---|
| ENG-054 | Add `id` to `models.Company` + `company_id` FK on `jobs` | Add identity to Company; add a real FK from `jobs` to `companies`, replacing the denormalized `jobs.company` text (kept temporarily for read compatibility). Deliberately **not** MVP-critical — the text field is sufficient for the MVP loop's display needs. | ENG-009 | Medium | M | No visible change alone — precondition for Company Workspace. | M4 |
| ENG-055 | Implement `save_company`/`get_company(ies)` | `companies` table exists with zero persistence code today. | ENG-054 | Medium | S | Company research/notes actually persist. | M4 |
| ENG-056 | Build `CompanyService` | Backs Company Workspace. | ENG-055 | Medium | S | Enables ENG-057. | M4 |
| ENG-057 | Build Company Workspace GUI | Directory + detail view (associated Jobs/Opportunities/Contacts). | ENG-056 | Medium | M | Candidate can research and track employers independent of any one posting. | M4 |

---

## Opportunity Workspace

This is the core of the MVP — see "Critical path to MVP" below.

| ID | Title | Description | Dependencies | Priority | Complexity | User-facing value | Milestone |
|---|---|---|---|---|---|---|---|
| ENG-058 | Redefine `models.Opportunity` | Replace the current (unused, `OpportunityScore`-duplicate) shape with the ERD's wrapper shape: `candidate_id`, `job_id`, `status`, timestamps. | ENG-004, ENG-009, ENG-010 | Critical | M | Foundation of the entire candidate-facing pipeline concept. | M1 |
| ENG-059 | Create `opportunities` table + persistence methods | Backfill one Opportunity per existing `jobs` row, owned by the migrated Candidate. | ENG-015, ENG-058 | Critical | L | Candidate's pipeline of pursued jobs is now a real, queryable thing. | M1 |
| ENG-060 | Create `models.Assessment` | Fit score, sub-scores, recommendation, reasoning — consolidating `JobAnalysis`/`OpportunityScore`. | ENG-058 | Critical | M | Candidate gets one explainable score per Opportunity instead of three disconnected numbers. | M1 |
| ENG-061 | Create `assessments` table + persistence methods | An Opportunity can have many Assessments over time. | ENG-059, ENG-060 | Critical | M | Candidate can see how their fit for a job changed as their profile evolved. | M1 |
| ENG-062 | Build `OpportunityService` | Create/list/advance-stage operations. | ENG-059 | Critical | M | Enables the whole Opportunity Workspace GUI. | M2 |
| ENG-063 | Build `AssessmentService` | Score/re-score an Opportunity, wrapping `opportunity_scorer.py`/`recruiter.py`, implementing the consolidation from ENG-041. | ENG-061, ENG-041 | Critical | M | Candidate gets an automatic, explained score the moment a Job is promoted to an Opportunity. | M2 |
| ENG-064 | Persist Assessment reasoning/explainability | Ensure `reasoning`/`missing_skills` are retained per Assessment row, not just written to a one-off JSON file. | ENG-061 | High | S | Candidate can revisit *why* a job was scored the way it was, later, not just immediately after. | M2 |
| ENG-065 | Build Opportunity Workspace GUI | List/board view by stage + detail view (Assessment history, Application status, linked Documents). Promoting a discovered Job into an Opportunity happens here. | ENG-062, ENG-063 | Critical | XL | This **is** the product's daily-use screen — where the candidate actually works. | M2 |

---

## Resume Workspace

| ID | Title | Description | Dependencies | Priority | Complexity | User-facing value | Milestone |
|---|---|---|---|---|---|---|---|
| ENG-066 | Build `ResumeService` | Wraps `recruiting_agents/resume_agent.py` + `tools/resume_docx.py` for the tailoring flow. | ENG-011, ENG-023 | Critical | M | Enables one-click tailored resume generation from an Opportunity. | M2 |
| ENG-067 | Wire ATS Agent review into the Resume Workspace flow | Score the tailored resume against the target Job's description, surfaced alongside the tailoring output. | ENG-066 | High | S | Candidate immediately sees whether the tailored resume will clear ATS screening. | M2 |
| ENG-068 | Build Resume Workspace GUI | Master resume source view + per-Opportunity tailoring/ATS-review flow. | ENG-066, ENG-067 | Critical | L | Candidate can generate and review a tailored, ATS-scored resume without leaving the app. | M2 |
| ENG-069 | Support multiple master-resume variants per target-role track | E.g. IT support vs. cybersecurity track, per `PRODUCT.md`'s multi-role scope. | ENG-010, ENG-068 | Low | M | Candidate targeting more than one career track doesn't have to hand-edit one resume between searches. | M7 |

---

## Security

| ID | Title | Description | Dependencies | Priority | Complexity | User-facing value | Milestone |
|---|---|---|---|---|---|---|---|
| ENG-070 | Centralize environment/secret loading | Only `app.py` calls `load_dotenv()` today; `app_gui.py` doesn't — harmless until a GUI workspace calls an agent directly, which ENG-063/ENG-066 now do. | ENG-063, ENG-066 | Critical | S | Prevents a confusing "it works from the CLI but not the GUI" failure the moment MVP workspaces ship. | M2 |
| ENG-071 | Mitigate prompt-injection risk from job descriptions | Untrusted content is interpolated directly into agent prompts with no sanitization. Low risk today (demo provider data only); real risk once ENG-078 ships. | None | High | M | Protects the candidate's generated documents from being manipulated by a malicious posting. | M6 |
| ENG-072 | Define encryption-at-rest strategy | Deferred — not needed for the current single-user local desktop scope. | ENG-015 | Low | M | Only relevant once RecruiterOS handles data for someone other than the machine's owner. | M7 |
| ENG-073 | Define authentication/authorization model | Same deferral reasoning as ENG-072. | ENG-015 | Low | L | Same as above. | M7 |
| ENG-074 | Add response validation / failure-mode contract to `BaseJobProvider` | The interface only specifies a return type today, no contract for malformed responses, timeouts, or rate limits. | None | High | M | Prevents a bad external response from corrupting the discovery feed once real providers ship. | M6 |
| ENG-075 | Add rate-limit/backoff handling per real provider integration | Each of the six providers is currently hardcoded demo data (verified: zero real HTTP calls in `services/`); real integrations each need this. | ENG-074 | Medium | XL | Discovery keeps working reliably instead of getting the candidate's IP rate-limited or blocked. | M6 |

---

## Testing

| ID | Title | Description | Dependencies | Priority | Complexity | User-facing value | Milestone |
|---|---|---|---|---|---|---|---|
| ENG-076 | Add tests for `DiscoveryService` | Sprint 2's `services/discovery_service.py` and its `RuntimeError`-on-`run.errors` behavior have no dedicated test coverage today. | None | High | S | Indirect — catches discovery regressions before the candidate hits them. | M3 |
| ENG-077 | Add integration test: Job → Opportunity promotion | Covers the core MVP hand-off. | ENG-065 | Critical | M | Indirect — the single most important flow in the product gets a regression guard. | M2 |
| ENG-078 | Add regression test against Excel reintroduction | Once ENG-005/ENG-006 land, assert `app.py`'s critical path has no `tools/excel_tracker.py` dependency. | ENG-006 | Medium | S | Indirect — prevents the dual-store bug from silently coming back. | M6 |
| ENG-079 | Add FK/schema integrity tests | Once ENG-059/ENG-054 land, verify referential integrity is actually enforced. | ENG-059 | Medium | S | Indirect — catches data-corruption bugs before they reach the candidate's real data. | M3 |
| ENG-080 | Set up a CI pipeline | No CI configuration exists in the repository today; `pytest`/`py_compile` are run manually. | None | Medium | M | Indirect — fewer regressions reach the candidate at all. | M3 |
| ENG-081 | Add a GUI smoke-test harness | No automated check exists that the desktop app launches and its wired workspaces render without error. | ENG-065 | Medium | M | Indirect — catches a broken launch before the candidate hits it. | M3 |

---

## Critical path to MVP

MVP defined as: a candidate can discover a job, have it become a tracked
Opportunity with an explainable score, generate a tailored/ATS-reviewed
resume for it, and see that reflected on the Dashboard — end to end, on
SQLite, without touching the legacy Excel-based `app.py` flow at all.

Dependency-ordered sequence (parallel tracks noted where they don't block
each other):

1. **ENG-004** — resolve the Opportunity/OpportunityScore naming conflict (decision, not code — blocks step 4)
2. **ENG-009** — `models.Job.id` *(parallel with 3)*
3. **ENG-010** — `models.Candidate` *(parallel with 2)*
4. **ENG-015** — `candidates` table + persistence (needs 3)
5. **ENG-022** — `CandidateService` (needs 4)
6. **ENG-058** — redefine `models.Opportunity` (needs 1, 2, 3)
7. **ENG-059** — `opportunities` table + persistence, backfill (needs 4, 6)
8. **ENG-060** — `models.Assessment` (needs 6)
9. **ENG-061** — `assessments` table + persistence (needs 7, 8)
10. **ENG-041** — consolidate JobAnalysis/OpportunityScore/fit_score into one Assessment flow (needs 8, 9)
11. **ENG-062** — `OpportunityService` (needs 7)
12. **ENG-063** — `AssessmentService` (needs 9, 10)
13. **ENG-011** — `models.Document` *(parallel with 6–12)*
14. **ENG-023** — `DocumentService` (needs 13, and 17 below for full persistence, but can start against the dataclass alone)
15. **ENG-017** — wire `documents` table (needs 13, and an Opportunity to attach to — needs 7)
16. **ENG-066** — `ResumeService` (needs 13, 14)
17. **ENG-067** — wire ATS review into Resume flow (needs 16)
18. **ENG-070** — centralize secret loading (needs 12, 16 — the first point anything calls an agent from the GUI)
19. **ENG-065** — Opportunity Workspace GUI (needs 11, 12) — **this is the screen that makes the MVP demoable**
20. **ENG-068** — Resume Workspace GUI (needs 16, 17)
21. **ENG-077** — integration test for the Job → Opportunity flow (needs 19)

Everything under **Contacts**, **Companies**, and most of **Automation**,
**Analytics**, **Interview**, and **Settings** GUI is explicitly **not**
on this path — those workspaces materially improve the product but a
candidate can complete the core discover → assess → tailor loop without
any of them. `ENG-005`/`ENG-006` (retiring Excel) are also deliberately
off the critical path: the MVP is built SQLite-native from the start
rather than migrating the legacy CLI flow first.

---

## Recommended first implementation task

**ENG-010 — Create `models.Candidate`.**

Reasoning: it's the one task on the critical path with zero dependencies
and zero pending decisions blocking it (unlike ENG-058, which needs
ENG-004 resolved first). It's S complexity — a single new dataclass file,
same shape as every other file in `models/`. Everything else on the
critical path — `candidates` persistence (ENG-015), `CandidateService`
(ENG-022), and ultimately `Opportunity` itself (ENG-058, which takes
`candidate_id`) — depends on this existing first. `ENG-009`
(`models.Job.id`) is equally unblocked and could run in parallel if you
want two people/sessions working simultaneously, but if this has to be
one task, Candidate is the better starting point since more of the
critical path depends on it transitively.

Before starting it, it would help to get **ENG-004** answered (the
Opportunity/OpportunityScore disposition) in parallel — it's a decision,
not code, and answering it now avoids a blocked step 6 in the sequence
above later.
