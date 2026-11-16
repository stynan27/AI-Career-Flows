---
name: resume-tailor
description: Tailor a factual resume to a job description, generate styled documents, and report conservative ATS alignment and gaps.
argument-hint: "resume and job description, plus private output directory"
user-invocable: true
---

# Resume Tailor

## Inputs and privacy

Obtain the applicant's factual resume or baseline, target job description,
company, private working directory, and a compatible private DOCX template.
Extract a requisition number when available. Ask for missing inputs or paste
the job description if fetching fails. The shipped resume and template are
fictional demonstrations, not evidence about the user.

Keep all real inputs, personalized templates, and outputs outside this public
checkout. Identity and contact details are static in the DOCX template; confirm
the private template has the correct details before generation. Preserve its
paragraph positions because the cloner uses fixed formatting molds.

## Alignment checkpoint

1. Identify required and preferred qualifications, duties, experience,
   education, and keywords. Map each major requirement to resume evidence.
2. Show strong matches, partial matches, gaps, and low-relevance bullets.
   Ask which bullets to retain, rewrite, replace, or remove and whether the
   applicant can substantiate missing experience.
3. Obtain confirmation before adding or implying new skills, duties, metrics,
   titles, dates, credentials, or projects. Ask for the exact URL and label
   when adding or changing a project link. If the user supplies no new
   evidence, keep unsupported requirements as gaps.
4. Before final generation, obtain the user's decisions or explicit acceptance
   of remaining gaps. Never treat job-posting keywords as applicant evidence.

## Generate

Use the fixed section order `Employment`, `Software Projects`, `Education`,
`Skills`. Follow the exact Markdown syntax in the README and fictional
baseline; there is no Professional Summary placeholder. Reorder or reword
supported bullets without changing their meaning.

In the private company folder, save Markdown under `resumes/` using
`Applicant_Resume_[RoleSlug]_[ReqNumber].md`. Use a title-case underscore
role slug and sanitized requisition; omit its entire suffix if unavailable.
Use the same stem for DOCX and PDF. Generate with
`resume_workflow.generate_resume_pdf(markdown_path, template_path,
output_docx_path, target_pages=1)`, using the toolkit's `scripts/` directory
and the user's compatible private template. Do not rebuild formatting manually.

Check `result["on_target"]`. If false, trim low-impact content and regenerate;
do not report a submission-ready one-page document until it passes. Ask the
user to visually review the output.

## ATS analysis and handoff

Use `ats-matcher` to assess the original and tailored resumes against the same
job description. Save the full report under private
`ats_matches/ATS_MATCH_ANALYSIS_[RoleSlug]_[ReqNumber].md`, omitting the
requisition suffix if unavailable. Include scores, evidence, improvements,
and gaps. Scores are estimates, not predictions of an employer's ATS.

Return the Markdown, DOCX, PDF, page count, report path, and both scores.
When called by `job-tracker`, provide the PDF path relative to the company
folder and the tailored score; do not claim a score improved unless it did.
