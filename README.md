# RecruiterOS

RecruiterOS is an AI-powered desktop application for managing a job search:
discovering and scoring opportunities, tailoring resumes, generating
application artifacts, and tracking recruiters and companies. See
[PRODUCT.md](PRODUCT.md) for the full product vision and
[ARCHITECTURE.md](ARCHITECTURE.md) for the architecture.

It combines a PySide6 desktop UI with an OpenAI-Agents-SDK-based pipeline
that analyzes job descriptions, scores fit, tailors resume strategy,
generates cover letters, writes recruiter outreach messages, updates an
Excel job tracker, and generates application artifacts.

## Current Features

- Desktop dashboard (Mission Control) built on PySide6
- Multi-provider job discovery (Google Jobs, Greenhouse, Lever, Ashby, Workday, manual) into a SQLite job database
- Senior Recruiting Agent
- Resume Agent
- ATS Agent and ATS report generation
- Profile-based candidate memory
- Excel job tracker integration
- Fit scoring
- Apply / Maybe / Skip recommendations
- Tailored resume notes
- Cover letter draft generation
- Recruiter message generation
- DOCX output generation
- Output folders per job

## Tech Stack

- Python
- PySide6
- OpenAI Agents SDK
- OpenAI API
- Pydantic
- SQLite
- openpyxl
- python-docx
- Cursor IDE
- VS Code
- GitHub

## Project Structure

Top-level modules — see [ARCHITECTURE.md](ARCHITECTURE.md) for how these
map to the architectural layers (kernel, domain, services, etc.) and the
target dependency direction:

```text
RecruiterOS/
├── gui/                 # PySide6 desktop UI
├── services/             # job-provider integrations (Google Jobs, Greenhouse, Lever, Ashby, Workday, manual)
├── orchestrator/         # workflow orchestration (chief recruiter, state, queue)
├── recruiting_agents/    # per-task agents (resume, ATS, recruiter, job scout, opportunity scorer)
├── pipelines/            # multi-step workflows (discovery pipeline)
├── models/               # domain objects (Job, Company, Application, Interview, Recruiter)
├── profiles/             # candidate profile loading (active memory implementation)
├── memory/               # legacy profile-loading code; status under review, see docs/adr/
├── database/             # SQLite schema and access
├── config/                # settings, logging, CLI
├── tools/                 # document/report generation (DOCX, Excel)
├── tests/
├── docs/                  # provider/pipeline docs, ADRs (docs/adr/)
├── app.py                 # application pipeline entry point
├── app_gui.py              # desktop app entry point
├── app_discovery.py        # discovery-only CLI entry point
├── requirements.txt
└── README.md
```