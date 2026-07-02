# RecruiterOS Architecture

RecruiterOS is built around five principles.

1. Kernel orchestrates work.

2. Workers execute tasks.

3. Plugins extend capabilities.

4. Domain objects represent business entities.

5. UI consumes services.

Nothing should bypass these layers.

The dependency direction should always move inward.

GUI

↓

Services

↓

Kernel

↓

Domain

---

## Current & Target Architecture

This section exists to close the gap between the five principles above and
the actual directory layout, per
[docs/adr/0001-conceptual-layer-names-no-renames.md](docs/adr/0001-conceptual-layer-names-no-renames.md).

`Kernel`, `Domain`, `Plugins`, and `UI` above are **conceptual layers**, not
directory names. No top-level directory is renamed to match them at this
time. The mapping from real directories to these layers is:

| Layer (principle)     | Current directory / directories                          |
|------------------------|-----------------------------------------------------------|
| UI                     | `gui/` (PySide6 desktop shell)                             |
| Services               | `services/` — today holds job-provider integrations (`ashby.py`, `greenhouse.py`, `lever.py`, `workday.py`, `google_jobs.py`, `manual_provider.py`) behind `base_provider.py`. It does **not** yet expose a general-purpose interface for the GUI — see Target below. |
| Kernel                 | `orchestrator/` (`chief_recruiter.py`, `workflow.py`, `state.py`, `queue.py`) |
| Workers / Plugins      | `recruiting_agents/` (per-task agents: resume, ATS, recruiter, job scout, opportunity scorer) and the provider classes under `services/` |
| Domain                 | `models/` (`Job`, `Company`, `Application`, `Interview`, `Recruiter`) |
| Memory                 | `profiles/` (`ProfileManager`, actively used) — `memory/` also exists and overlaps; status tracked in [docs/adr/0001](docs/adr/0001-conceptual-layer-names-no-renames.md) |
| Persistence            | `database/` (`sqlite_manager.py`, `schema.py`) |
| Pipelines / Workers    | `pipelines/` (`discovery_pipeline.py`) |

### Target dependency direction

Per [docs/adr/0002-service-layer-as-gui-interface.md](docs/adr/0002-service-layer-as-gui-interface.md),
the target chain is:

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

`Services` is intended to become the **only** interface the GUI depends on.
Today `gui/controller.py` calls `database/` and `pipelines/` directly,
bypassing `Services` and `Orchestrator` entirely — this is tracked as known
drift to be resolved incrementally (see the Architecture Alignment Plan,
Sprint 2), not fixed in this documentation pass.

### Known drift (not yet resolved in code)

- GUI bypasses Services/Orchestrator and calls `database/` and `pipelines/`
  directly (`gui/controller.py`).
- `orchestrator/chief_recruiter.py::run_application_workflow` reaches
  upward into the top-level `app.py` script rather than depending only on
  code below it in the chain. Status (deprecated / planned / obsolete) is
  under review — see [docs/adr/0001](docs/adr/0001-conceptual-layer-names-no-renames.md).
- `memory/` and `profiles/` both implement profile loading; `profiles/ProfileManager`
  is the one actually used. Status under review — see the same ADR.
- The GUI reads raw database rows by positional index rather than the
  `Job` domain object.