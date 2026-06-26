# RecruiterOS

RecruiterOS is a Python-based AI recruiting workflow built with the OpenAI Agents SDK.

It helps manage a job search by analyzing job descriptions, scoring fit, tailoring resume strategy, generating cover letters, writing recruiter outreach messages, updating an Excel job tracker, and generating application artifacts.

## Current Features

- Senior Recruiting Agent
- Resume Agent
- Structured candidate memory
- Excel job tracker integration
- Fit scoring
- Apply / Maybe / Skip recommendations
- Tailored resume notes
- Cover letter draft generation
- Recruiter message generation
- DOCX output generation
- Output folders per job
- Memory Manager architecture

## Tech Stack

- Python
- OpenAI Agents SDK
- OpenAI API
- Pydantic
- openpyxl
- python-docx
- Cursor IDE
- VS Code
- GitHub

## Project Structure

```text
RecruitingOS/
├── agents/
├── data/
├── memory/
├── tools/
├── app.py
├── requirements.txt
└── README.md