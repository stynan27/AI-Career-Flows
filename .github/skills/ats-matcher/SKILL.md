---
name: ats-matcher
description: Assess a resume against a job description using a conservative weighted match estimate, evidence, and gap analysis.
argument-hint: "resume and job description"
user-invocable: true
---

# ATS Match Analysis

Obtain a resume and job description as text, files, or a job URL. Verify file
paths; if extraction or URL access fails, ask for pasted text. Never use
fictional examples as evidence of a real applicant's experience. Keep real
inputs and saved reports outside the public checkout.

## Compare and score

Extract required and preferred skills, duties, experience, and education.
Map each major requirement to specific resume evidence. Distinguish strong
matches, partial matches, and missing evidence. Ask the user before treating
an uncertain equivalent or unlisted experience as confirmed.

Provide a conservative, explainable 0-100 estimate using:

| Component | Maximum | Evidence |
|---|---:|---|
| Keywords and skills | 40 | Required and preferred qualifications supported by the resume |
| Job duties | 30 | Relevant responsibilities supported by accomplishments |
| Experience | 20 | Supported experience level and seniority relative to requirements |
| Education | 10 | Degree and field relative to stated requirements |

Explain the scoring method, component scores, and any unassessed or unstated
requirements. Do not infer missing qualifications or invent equivalence.
Scores are subjective heuristics, not measurements or predictions of an
employer's ATS. Give matched evidence, missing qualifications, strengths,
gaps, and actionable recommendations that do not introduce unsupported claims.

For skills, distinguish required from preferred qualifications; the original
workflow weights a preferred qualification at half a required qualification.
Show the weighted matched and total counts used for the 40-point calculation.
For duties, identify the resume evidence behind each relevance assessment.
Compare years and seniority only when supported by both documents, and assess
education against the actual stated requirement. If a category cannot be
assessed, state the limitation and scoring treatment rather than inventing a
requirement or presenting the result as precise.

When comparing original and tailored resumes, apply the same criteria to both
and report both scores without assuming improvement. With company and role
context, save a full report under the private company folder as
`ats_matches/ATS_MATCH_ANALYSIS_[RoleSlug]_[ReqNumber].md`. Use the shared
role slug and sanitized requisition; omit the suffix if unavailable. Without
company context, report in chat unless the user supplies a private output path.

For `job-tracker`, return the match percentage, each component score and
maximum, gaps, strengths, and report path when saved. The structured result
uses `matchPercentage`, a `breakdown` with `keywords`, `duties`, `experience`,
and `education` score/max pairs, plus `gaps` and `strengths`. Do not submit
applications.
