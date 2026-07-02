# RecruiterOS Workspace Architecture

Status: Draft, for review. Design document only — no UI code, no Python,
no other code written as part of this document. This replaces the prior
draft of this same file with the structure requested below.

## Framing

RecruiterOS is treated here as an **AI Career Operating System**, not a
job-search application: a system the candidate lives in across an entire
career, not just a single search. That framing shapes two things below —
the per-workspace "AI capabilities" sections (several go beyond
`PRODUCT.md`'s current explicit goals), and the recommended-additional-
workspaces section at the end, which leans toward career-lifecycle
concerns rather than only search-lifecycle ones.

This builds directly on:

- `ARCHITECTURE.md`'s target chain: `GUI → Services → Orchestrator (Kernel) → Pipelines/Workers → Persistence`.
- `docs/DOMAIN_ERD.md`'s entities: Candidate, Job, Company, **Opportunity**
  (the per-Candidate/Job wrapper — the central entity), Assessment,
  Application, Contact, Document, Interview, Activity.
- `CLAUDE.md`'s AI guardrail: AI assists but never takes an irreversible
  action automatically — submitting applications, deleting data, and
  modifying important profile information all require human approval.
  Every workspace's "Automation modules" / "AI capabilities" sections
  below respect this explicitly rather than leaving it implicit.

## Design principles

1. **Workspace ≠ entity table.** A workspace is where work happens; most
   touch more than one entity.
2. **Opportunity, not Job, is the pipeline's spine.** Per the ERD, Job is
   candidate-agnostic (the catalog); Opportunity is the candidate-specific
   pursuit of a Job. There is no standalone "Discover" workspace in the
   required set below — raw-catalog browsing and promotion into a tracked
   Opportunity are folded into the **Opportunity Workspace** itself (see
   its Purpose). Whether that should later split into its own workspace
   is addressed in the recommendations section.
3. **Drill-down, not sprawl.** A single record's detail (one Opportunity,
   one Company, one Contact) is a view reached *from* a workspace, not a
   separate top-level nav entry.
4. **AI-suggests vs. AI-acts**, stated per workspace: what AI may
   generate/recommend unattended versus what always requires a human
   click. **Automation Workspace** (below) is the concrete home for this
   principle — the place pending approvals actually live, not just an
   abstract rule.
5. **Services are the only thing a workspace talks to**, per ADR-0002 —
   never `database/`, `pipelines/`, or `recruiting_agents/` directly.

---

## Dashboard

**Purpose.** Single-glance, cross-workspace command center — daily
orientation ("where do I start," "what needs my attention"). Already
implemented today as `gui/dashboard.py::MissionControlPage`; this
document treats "Dashboard" as its canonical name going forward.

**Primary entities.** None owned here — reads a summary slice across
Opportunity, Application, Assessment, Interview, and Activity.

**Services used.** A dashboard/summary service composing the read paths
of the Opportunity, Application, Assessment, and Automation services
below, rather than querying persistence directly (today's
`AppController.get_dashboard_stats()` does this ad hoc against
`SQLiteManager` directly — see `ARCHITECTURE.md`'s "known drift," to be
resolved as this workspace's data is formalized).

**Automation modules.** None run *from* here — this workspace only
displays the output of automation running elsewhere (Opportunity scoring,
Automation Workspace's queue depth, etc.).

**AI capabilities.** No generation of new artifacts. At most, a
natural-language daily-briefing narrative synthesized from underlying
stats ("3 Opportunities scored above 85 this week, 2 interviews
upcoming").

**Navigation relationships.** Entry point into every other workspace —
each panel (Top Opportunities, Recent Jobs, AI Activity, Ready Queue)
links out to the workspace/record it summarizes.

**Future extensibility.** Configurable panel layout; per-Candidate
dashboards once multi-Candidate support exists (see recommendations).

---

## Opportunity Workspace

**Purpose.** The primary daily-driver. Browse newly discovered Jobs and
promote a Job into a tracked Opportunity (Candidate + Job pair); triage
and advance the candidate's active pipeline by stage (e.g., Scouted →
Assessed → Applying → Applied → Interviewing → Offer/Closed); drill into
a single Opportunity to reach everything connected to it — Assessment
history, Application status, Documents, Interviews, and Contacts.

**Primary entities.** Opportunity (owned here), Job (read, source of
promotion), Assessment, Application.

**Services used.** An OpportunityService (create/list/advance-stage), an
AssessmentService (score/re-score), and the existing `DiscoveryService`
(triggers/feeds the raw Job list this workspace promotes from).

**Automation modules.** `pipelines/discovery_pipeline.py` (via
`DiscoveryService`); opportunity/fit scoring
(`recruiting_agents/opportunity_scorer.py`,
`recruiting_agents/recruiter.py`); the currently-unwired
`recruiting_agents/job_scout.py` as a future auto-filter at intake (see
`DOMAIN_MODEL_REVIEW.md` finding 6).

**AI capabilities.** Automatic fit/opportunity scoring with explainable
reasoning (the "Assessment" record — score, sub-scores, recommendation,
reasoning); recommended next action (Apply / Maybe / Skip); flagging
stale Opportunities that haven't moved stage in N days.

**Navigation relationships.** Links to Company Workspace (an
Opportunity's employer), Documents Workspace (artifacts generated for
this Opportunity), Recruiter Workspace (contacts tied to this
Opportunity), Interview Workspace (its scheduled interviews), and
Automation Workspace (any pending approval, e.g. "Apply" itself, which is
never executed from here without confirmation).

**Future extensibility.** Kanban/board view by stage; bulk re-scoring;
multi-Candidate scoping; splitting the raw-catalog browsing portion into
its own workspace as discovery volume grows (see recommendations).

---

## Recruiter Workspace

**Purpose.** Manage the people involved in the job search. Named
"Recruiter Workspace" because recruiters are the dominant contact type in
practice, but built on the ERD's generalized **Contact** entity (a `role`
field distinguishes recruiter / hiring manager / referral / mentor /
other) rather than a recruiter-only data model — this reconciles decision
6 of `DOMAIN_ERD.md` (Contact is general) with the product-facing name
requested here.

**Primary entities.** Contact, with Company and Opportunity as read
relationships.

**Services used.** A ContactService.

**Automation modules.** A future Outreach Agent
(`docs/AGENTS.md`'s "Future Agents") drafting outreach/follow-up
messages; follow-up reminders derived from `last_contacted_at`/
`follow_up_at`.

**AI capabilities.** Draft outreach or follow-up messages (never
auto-sent); relationship-priority ranking ("who to follow up with
today"); future auto-extraction of a recruiter's contact info from a job
posting or forwarded email.

**Navigation relationships.** Reached from Company Workspace (contacts at
a company) and Opportunity Workspace (contacts on an Opportunity); a
drafted, unsent message surfaces as a pending item in Automation
Workspace.

**Future extensibility.** Generalize further into a full professional
network manager beyond active-search contacts (see recommended Network
Workspace below); LinkedIn import/sync.

---

## Company Workspace

**Purpose.** Research and track employers independent of any single
Opportunity — notes, size, industry, Glassdoor rating, and everything
Job/Opportunity/Contact-related tied to that employer.

**Primary entities.** Company, with Job, Opportunity, and Contact as read
relationships.

**Services used.** A CompanyService (currently no persistence methods
exist for Company at all — see `DOMAIN_MODEL_REVIEW.md` finding 2; this
workspace has no working data until that's built).

**Automation modules.** A future Company Research Agent
(`docs/AGENTS.md`) auto-populating size/industry/culture notes from
public sources.

**AI capabilities.** Auto-summarized company research briefing;
quality/risk signals (e.g., a company reposting the same role repeatedly,
or a low Glassdoor rating) surfaced as flags, not silently factored in
without explanation.

**Navigation relationships.** Reached from Opportunity Workspace and
Recruiter Workspace; surfaces its own Jobs, Opportunities, and Contacts.

**Future extensibility.** Company-quality signal feeding directly into
Assessment's `company_score` dimension; watch-listed companies with
new-posting alerts.

---

## Resume Workspace

**Purpose.** Manage the candidate's resume as a living asset: the
canonical master resume (source data) plus AI-tailored variants generated
per Opportunity. This is the *authoring/tailoring* workspace — distinct
from **Documents Workspace**, which is the library where finished
artifacts of every type (including the resumes generated here) live
afterward.

**Primary entities.** Candidate (`master_resume` source data), Document
(`document_type = "resume"` — the tailored outputs this workspace
produces).

**Services used.** A ResumeService (wraps
`recruiting_agents/resume_agent.py` and `tools/resume_docx.py`), and a
CandidateService for the source data.

**Automation modules.** Resume Agent (tailoring); ATS Agent (scoring the
tailored output against the target Job — the score is also visible on
the target Opportunity).

**AI capabilities.** Generate a tailored, ATS-optimized resume structure
per Opportunity, honesty-constrained (the existing agent rules already
forbid inventing experience or claiming incomplete certifications — this
workspace is where that constraint is user-visible); ATS score plus
improvement suggestions; regeneration recommendation when ATS score is
low.

**Navigation relationships.** Invoked from Opportunity Workspace ("tailor
resume for this Opportunity"); its outputs land in Documents Workspace;
its source data is edited via Settings (or the recommended Candidate
Workspace, below).

**Future extensibility.** Version comparison/diffing across Opportunities;
multiple master-resume variants for different target-role tracks (fits
`PRODUCT.md`'s multi-role scope, e.g. IT support vs. cybersecurity).

---

## Interview Workspace

**Purpose.** A schedule-first view — upcoming, then past — of interviews
across every Opportunity, plus prep materials, so the candidate can see
"what do I have this week" without navigating into each Opportunity
individually.

**Primary entities.** Interview (its authoritative parent is Application,
per the ERD — this workspace is a cross-cutting query over the same
data, not a separate store).

**Services used.** An InterviewService.

**Automation modules.** A future Interview Coach agent
(`docs/AGENTS.md`) generating likely questions and prep notes from the
Job description and Company research.

**AI capabilities.** Auto-generated prep briefing (likely
technical/behavioral questions, company talking points, pulled from
Company Workspace and the Opportunity's Job description); post-interview
outcome/notes summarization from the candidate's raw notes — the outcome
itself is always a human-entered fact, never inferred.

**Navigation relationships.** Nested under an Opportunity's Application
in Opportunity Workspace; also a standalone schedule view here; links to
Company Workspace for prep context.

**Future extensibility.** Calendar sync; a conversational mock-interview
practice mode.

---

## Automation Workspace

**Purpose.** The command center for everything AI is doing, has queued,
or is waiting on the candidate to approve. This is the concrete home for
`CLAUDE.md`'s human-approval rule — every irreversible action proposed by
any other workspace's automation surfaces here for explicit confirmation,
rather than the rule being enforced only as scattered inline "are you
sure" dialogs.

**Primary entities.** None of the ERD's business entities directly — this
operates on orchestration/process state (`orchestrator/workflow.py`'s
`WorkflowRun`, `orchestrator/state.py`'s `WorkflowState`,
`orchestrator/queue.py`'s `QueueItem`, currently all in-memory and
partly unwired), plus an approval-queue concept that *references*
whichever business entity is pending action (an Application about to be
marked Applied, a Document about to be finalized, a Contact message about
to be sent).

**Services used.** An AutomationService/OrchestrationService wrapping
`orchestrator.queue.WorkflowQueue` and `orchestrator.chief_recruiter.ChiefRecruiter`
run history.

**Automation modules.** Every other workspace's automation modules report
their status here: discovery runs, Assessment scoring runs, Resume/ATS
generation, Recruiter Workspace outreach drafts, and — most
consequentially — a future Browser Worker
(`docs/AGENTS.md`) actually submitting an application, which is the
clearest irreversible action in the product and must never execute
without a confirm step surfaced here.

**AI capabilities.** No generation of its own — this is the
transparency/control layer over every other workspace's AI output. At
most, a natural-language "what changed since you last looked" summary.

**Navigation relationships.** Every pending-approval item links out to
the workspace/record it concerns (an "Apply" approval → that Opportunity;
a "Send message" approval → that Recruiter Workspace contact).

**Future extensibility.** An automation-rules editor (when to auto-run
scoring vs. hold for review); a full audit trail backed by the
currently-unwired Activity entity; scheduled/recurring automation (e.g.
`ROADMAP.md` v0.7.0's "3x daily search schedule").

---

## Documents Workspace

**Purpose.** The library/vault of every generated or attached artifact
across all Opportunities: cover letters, ATS reports, recruiter messages,
portfolio pieces, interview notes, and — read-only once generated —
tailored resumes produced in Resume Workspace.

**Primary entities.** Document.

**Services used.** A DocumentService.

**Automation modules.** Cover-letter drafting (today folded into
`recruiting_agents/recruiter.py`'s `JobAnalysis.cover_letter_draft`;
`docs/AGENTS.md` names a future standalone Cover Letter Agent); ATS Agent
report generation.

**AI capabilities.** Draft generation across document types; ATS scoring;
future auto-tagging/organization by Opportunity, type, and recency.

**Navigation relationships.** Receives output from Resume Workspace and
from Opportunity Workspace (cover letters, recruiter messages generated
in an Opportunity's context) and Interview Workspace (interview notes);
browsable independently for reuse or comparison across Opportunities.

**Future extensibility.** Version history/diffing; export/sharing; a
template library for manually-authored documents alongside AI-generated
ones.

---

## Analytics Workspace

**Purpose.** Retrospective, read-only insight across the whole
pipeline — is the scoring and strategy actually working, not just what's
currently in flight.

**Primary entities.** Assessment, Application, Activity — aggregated, not
individually browsed.

**Services used.** An AnalyticsService/ReportingService composing the
read paths of the Opportunity, Assessment, and Application services
rather than querying persistence directly.

**Automation modules.** None that act — pure aggregation.

**AI capabilities.** Natural-language trend narration ("response rate
dropped this month"); anomaly flagging (e.g., "ATS scores trending down —
check the master resume in Resume Workspace").

**Navigation relationships.** Fed by every other workspace; feeds nothing
back — a read-only leaf. Dashboard surfaces a glanceable subset of
Analytics as tiles.

**Future extensibility.** Funnel/cohort comparison over time; a custom
report builder; (longer-term, privacy-sensitive) anonymized cross-
Candidate benchmarking if RecruiterOS grows into the multi-Candidate case.

---

## Settings

**Purpose.** Configuration: candidate profile/preferences (today's
`ProfileManager`-backed `candidate_profile`, `master_resume`,
`preferences`, `technical_skills`), provider/service toggles (which
job-board providers are active), and automation thresholds already
present in `config/settings.py` (`minimum_fit_score`,
`ats_regeneration_threshold`), exposed as user-editable rather than
hardcoded.

**Primary entities.** Candidate (profile fields); system configuration
(not an ERD business entity).

**Services used.** A CandidateService (profile) and a
ConfigurationService (wraps `config/settings.py`).

**Automation modules.** None — by design, this is the one workspace with
zero autonomous AI action.

**AI capabilities.** At most a suggestion/review capability ("your
technical_skills profile hasn't been updated in 90 days") — never an
autonomous edit. `CLAUDE.md` names profile modification explicitly as
requiring human approval; this workspace is where that approval is
actually exercised.

**Navigation relationships.** Affects every other workspace going
forward — profile changes affect future Assessment scoring, Resume
Workspace generation, and Opportunity Workspace's discovery queries — but
never retroactively rewrites existing Opportunities/Documents.

**Future extensibility.** A multi-Candidate profile switcher (ties to the
recommended Candidate Workspace below); per-provider API key management;
notification preferences.

---

## Recommended additional workspaces

The ten above satisfy the request as given. The following are not
required but would materially improve the platform under the "AI Career
Operating System" framing specifically — most extend the system's
horizon beyond a single active search, which is what separates an
operating system from a search tool.

- **Candidate Workspace.** Split profile management out of Settings into
  its own workspace once multi-Candidate support matters (per
  `PRODUCT.md`'s stated audience of recruiters/firms/HR managing more
  than one candidate). Primary entity: Candidate. This is the natural
  home for a Candidate switcher and per-Candidate data scoping —
  Settings becomes purely system/provider configuration again.
- **Offers & Negotiation Workspace.** Track and compare multiple
  concurrent offers, counter-offer history, and decision criteria.
  `Application` can reach an "Offer" status today, but nothing helps the
  candidate reason across *multiple* simultaneous offers, which is a
  distinct, high-stakes moment the current pipeline treats as just an
  end state. AI capability: side-by-side comparison narration
  (compensation, growth, risk) — recommendation only, decision always
  human.
- **Skills & Growth Workspace.** Aggregate `Assessment.missing_skills`
  across every Opportunity over time into an actionable development plan
  (what to learn, in what order, and why it would move the needle) —
  turning a currently per-Opportunity, throwaway field into a durable
  career-development signal. This is the clearest "career OS, not job
  search app" addition.
- **Network Workspace.** A broader professional-network manager beyond
  active-search Contacts — mentors, former colleagues, alumni — people
  worth staying in touch with independent of any open Opportunity.
  Recruiter Workspace is scoped to search-relevant people by design;
  this would be the container for relationships that outlast any one
  search.
- **Career Timeline Workspace.** A single-pane view of the candidate's
  whole trajectory across multiple job searches over years — not scoped
  to the current pipeline at all. This is the most direct expression of
  "operating system for careers" from `PRODUCT.md`, and the one most
  clearly out of scope for a job-search application.

---

## Explicitly out of scope for this document

No UI code, no Python, no widget/layout decisions, no service
implementations, no new `gui/` files. This defines workspace purpose,
entities, services, automation, AI capabilities, and navigation only.
Sequencing any of this into actual implementation is a decision for you,
informed by this document plus `DOMAIN_ERD.md`'s migration priorities —
several required workspaces (Company, Recruiter, Interview) have no
working data to display until those migrations land.
