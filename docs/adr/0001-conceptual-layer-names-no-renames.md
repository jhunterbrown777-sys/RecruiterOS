# ADR-0001: Keep documented layer names conceptual, not directory names

## Status

Accepted

## Context

`CLAUDE.md` and `ARCHITECTURE.md` describe a target architecture with
top-level modules named `kernel`, `domain`, `services`, `automation`,
`plugins`, `gui`, `ui`, and `memory`, and a strict inward dependency
direction (`GUI → Services → Kernel → Domain`).

The actual codebase does not use these directory names. It has
`orchestrator/`, `recruiting_agents/`, `models/`, `profiles/`, `services/`,
`pipelines/`, `gui/`, `memory/`, and `database/` instead. Functionally,
several of these map onto the intended layers (`orchestrator` behaves as
the kernel, `models` as the domain layer), but nothing in the codebase
documented that mapping, and two modules — `memory/` and `profiles/` —
overlap in responsibility without a stated relationship:

- `memory/memory_manager.py::MemoryManager` and
  `profiles/profile_manager.py::ProfileManager` both load the same four
  profile files (`candidate_profile.md`, `master_resume.json`,
  `preferences.json`, `technical_skills.json`) from what is effectively the
  same directory, using different profile-selection logic
  (`MemoryManager` reads `ACTIVE_PROFILE` from the environment;
  `ProfileManager` reads `settings.default_profile`).
- A grep across the codebase shows `MemoryManager` is never imported
  anywhere outside its own file. `ProfileManager` is used throughout
  `recruiting_agents/*` and is covered by `tests/test_profile_manager.py`.
- `orchestrator/chief_recruiter.py::run_application_workflow` does
  `import app; app.main()` inside the method — the orchestration layer
  reaching upward into the top-level script. A grep shows zero call sites
  for this method outside its own definition.

Renaming directories to match the documented layer names exactly was
considered and rejected for this pass: it would touch a large number of
import statements across the codebase for no behavioral benefit, and
conflicts with the stated priorities of minimizing drift through small,
reviewable changes rather than a large-scale rewrite.

Separately: whether `MemoryManager` and `run_application_workflow` are
truly obsolete, intentionally deprecated, incomplete, or reserved for
planned future architecture has not yet been confirmed with the project
owner. No source file is deleted on the assumption that "unused" means
"safe to remove" — see the Architecture Alignment Plan (Sprint 2) for the
explicit confirm-then-act sequence.

## Decision

1. The layer names in `CLAUDE.md` / `ARCHITECTURE.md` (`kernel`, `domain`,
   `plugins`, `ui`) remain conceptual descriptions of responsibility, not
   directory names. No top-level directory is renamed as part of this
   architecture alignment effort.
2. `ARCHITECTURE.md` §"Current & Target Architecture" is the authoritative,
   maintained mapping from real directories to these conceptual layers.
   When directory responsibilities change, that section is updated rather
   than the directories being renamed to match the doc.
3. The disposition of `MemoryManager` and `run_application_workflow`
   (deprecate in place vs. remove) is decided explicitly with the project
   owner before any code changes, per the ground rule that no file is
   deleted for appearing unused. That decision, once made, will be recorded
   as a follow-up ADR or an update to this one.

## Consequences

- Contributors (human or AI) reading `CLAUDE.md`/`ARCHITECTURE.md` must
  cross-reference the mapping table rather than expecting directories named
  `kernel/`, `domain/`, etc. to exist.
- The `memory/` vs `profiles/` duplication and the `run_application_workflow`
  inversion remain in the codebase, documented as known drift, until
  Sprint 2 resolves them with an explicit decision rather than a unilateral
  deletion.
- If a future decision is made to rename directories to match the
  documented layer names literally, that would warrant its own ADR
  superseding this one, since it changes ground rule 2 of the Architecture
  Alignment Plan.
