# RecruiterOS Agents

## Chief Recruiter

Coordinates the overall recruiting workflow.

Current role:
- Summarizes completed runs
- Reports fit score
- Reports next action

Future role:
- Orchestrate Recruiter Agent
- Orchestrate Resume Agent
- Orchestrate ATS Agent
- Orchestrate Cover Letter Agent
- Orchestrate Outreach Agent

## Recruiter Agent

Evaluates job fit.

Outputs:
- Fit score
- Apply decision
- Reason
- Missing skills
- Resume notes
- Cover letter draft
- Recruiter message
- Next action

## Resume Agent

Creates an honest ATS-optimized resume structure.

Rules:
- Never invent experience
- Never claim completed Security+
- Never claim CCNA certification
- Use master_resume.json as source of truth

## ATS Agent

Reviews tailored resume against job description.

Outputs:
- ATS score
- Keyword match score
- Matched keywords
- Missing keywords
- Resume strengths
- Resume weaknesses
- Improvement suggestions
- Regeneration recommendation

## Future Agents

- Job Scout Agent
- Cover Letter Agent
- Outreach Agent
- Company Research Agent
- Interview Coach
- Browser Worker