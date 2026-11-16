---
name: cover-letter-generator
description: Create a truthful role-specific cover letter from a resume and job description using a compatible DOCX template.
argument-hint: "job description, resume, and private output directory"
user-invocable: true
---

# Cover Letter Generator

## Inputs and privacy

Obtain a factual resume, job description, company, private working directory,
and compatible private cover-letter template. Prefer the selected tailored
resume when available. Extract a requisition number if present; ask for missing
information or pasted text if a job URL cannot be read.

The shipped examples are fictional. Keep real inputs, personalized templates,
and outputs outside the public checkout. Verify name, contact details, and
sender address in the private DOCX template: these are static and are not
replaced from Markdown. Preserve template paragraph positions.

## Draft and confirm

Identify the role, relevant duties, qualifications, and culture cues. Ask
about uncertain hiring-manager name, emphasis, tone, and accomplishments.
Use `Dear Hiring Team,` if no name is known and the user accepts it. Make
every claim traceable to the resume or explicit user confirmation; do not
invent experience, metrics, or company facts.

Use the README's cover-letter format: a `---` divider, a salutation beginning
with `Dear`, blank-line-separated body paragraphs, a closing, and the explicit
signing name. Content before the divider is ignored. The template supplies the
sender address; there is no generated recipient address block. The renderer
always outputs `Best regards,` even if the input uses another supported closing.

## Generate and deliver

Save Markdown in private `cover_letters/` as
`Applicant_CoverLetter_[RoleSlug]_[ReqNumber].md`, using a title-case
underscore role slug and sanitized requisition. Omit the entire requisition
suffix if unavailable. DOCX and PDF use the same stem.

Call `cover_letter_workflow.generate_cover_letter_pdf(markdown_path,
template_path, output_docx_path, date_text=None, target_pages=1)` from the
toolkit's `scripts/` directory using the private template. Do not manually
rebuild template formatting. Check `result["on_target"]`; shorten the body
and regenerate if the letter exceeds one page. Request visual review and
return the Markdown, DOCX, PDF, and page count. For `job-tracker`, provide
the PDF path relative to the company folder.
