# ADR-0002: Introduce an explicit Service layer as the GUI's only dependency

## Status

Accepted (documentation only — implementation begins in Sprint 2 of the
Architecture Alignment Plan)

## Context

`ARCHITECTURE.md` states the dependency direction should always move
inward, with the UI consuming services rather than reaching into lower
layers directly.

In the current codebase, `gui/controller.py::AppController` violates this:

- It imports and instantiates `database.sqlite_manager.SQLiteManager`
  directly (persistence layer).
- Its `run_discovery()` method imports and instantiates
  `pipelines.discovery_pipeline.DiscoveryPipeline` directly (pipeline
  layer), bypassing `orchestrator/chief_recruiter.py::ChiefRecruiter`,
  which already wraps that same pipeline call with state tracking, logging,
  and error handling (and is the version covered by
  `tests/test_orchestrator.py`).
- Separately, `app_discovery.py` (a standalone CLI entry point) also
  instantiates `DiscoveryPipeline` directly. Between the GUI, the CLI
  script, and the orchestrator, there are three independent call sites for
  the same discovery pipeline invocation, only one of which is tested and
  gets orchestration behavior.
- `services/` currently only holds job-provider integrations
  (`ashby.py`, `greenhouse.py`, `lever.py`, `workday.py`, `google_jobs.py`,
  `manual_provider.py` behind `base_provider.py`). It does not expose any
  general-purpose interface for the GUI to depend on.

## Decision

The target dependency chain is:

```text
GUI → Services → Orchestrator (Kernel) → Pipelines/Workers → Persistence
```

`Services` becomes the sole interface the GUI is allowed to depend on. The
GUI stops importing `database/` or `pipelines/` directly. Concretely (to be
implemented in Sprint 2, one commit per item):

1. A new, additive service (e.g. `services/discovery_service.py`) wraps
   `orchestrator.chief_recruiter.ChiefRecruiter` for the discovery
   workflow. No existing files are moved or renamed.
2. `gui/controller.py::AppController.run_discovery()` is changed to call
   the new service instead of instantiating `DiscoveryPipeline` directly.
3. `app_discovery.py` is changed to call the same service, so there is
   exactly one supported way to run discovery, with orchestration
   (state/logging/error handling) applied consistently everywhere.

This ADR does not cover data-access boundaries (e.g. the GUI reading raw
SQLite row tuples instead of `models.Job`) — that is tracked separately as
Sprint 3 of the Architecture Alignment Plan.

## Consequences

- The GUI's runtime behavior for discovery is unchanged (same underlying
  `DiscoveryPipeline`), but it gains the orchestrator's logging, state
  tracking, and error containment for free.
- Future GUI features that need application data go through `services/`,
  giving `services/` a second responsibility (provider integrations +
  GUI-facing façade) that should be kept in clearly separate files within
  that directory rather than blurring the two.
- `orchestrator/chief_recruiter.py::run_application_workflow`'s disposition
  (see ADR-0001) affects whether the new service can also cover the
  application workflow later, or whether that path needs separate design
  work.
