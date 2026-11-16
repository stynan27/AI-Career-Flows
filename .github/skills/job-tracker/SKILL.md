---
name: job-tracker
description: Track job applications by company; add, update, list, or report on private records and coordinate resumes, cover letters, and ATS analysis.
argument-hint: "company, job description, or action (add/update/list/report)"
user-invocable: true
---

# Job Application Tracker

## Privacy and inputs

Ask for the user's private working directory outside this public repository.
Never use the fictional examples as real experience or save personal records
inside the public checkout. Obtain a company and job description for additions;
fetch a supplied URL if possible, otherwise ask the user to provide the text.
Confirm uncertain details. Never invent salary, dates, skills, or application
status.

## Add an application

1. Extract the role, requisition number if present, description, required and
   preferred skills, and job URL. Ask for missing information and confirm
   uncertain fields. Default status to `interested`.
2. Resolve a safe company folder under the private working directory. Create
   `jobs.json` as an empty array and `resumes/`, `cover_letters/`, and
   `ats_matches/` if absent; preserve existing files.
3. Use the requisition number as `id` if available; otherwise generate an
   unused company-based ID. Do not silently overwrite an existing ID.
4. Ask whether to use existing files, generate them, or leave them unattached.
   For a new resume, invoke `resume-tailor`; for a new cover letter, invoke
   `cover-letter-generator`. When an existing resume lacks an ATS score, offer
   `ats-matcher`. Use the tailored score and report when generated.
5. Before saving, validate every non-null attachment path exists and is
   relative to the company folder. Prefer generated PDFs for submission.
   Preserve null for unavailable dates, attachments, scores, or salary.
6. Append a record using the fields in `examples/company/jobs.example.json`:
   `id`, `role`, `reqNumber`, `jobUrl`, `description`, `skills`, `status`,
   `dateAdded`, `applicationDate`, `interviewDate`, `resumeUsed`,
   `coverLetterUsed`, `atsMatchPercentage`, `notes`, and `salaryRange`.
   Set `dateAdded` to the current date; record application/interview dates
   only when known. Confirm the saved record and linked files.

Allowed statuses: `interested`, `reviewed`, `applied`, `interview`, `offer`,
`accepted`, `rejected`. Typical flow is interested to reviewed to applied to
interview to offer to accepted; rejection can occur during the process.

Use the same `Title_Case_With_Underscores` role slug and sanitized requisition
suffix across Markdown, DOCX, PDF, and ATS report filenames. Omit the entire
suffix when no requisition number exists. See `AGENTS.md` for naming examples.

## Update, list, and report

- **Update:** identify the company and unique record; ask when ambiguous.
  Update only requested fields, validate all non-null attachment paths before
  saving, and report changes. Do not invent dates when statuses change.
- **List:** load private company `jobs.json` arrays; filter by requested company
  or status and show role, ID, status, relevant dates, and ATS score.
- **Report:** summarize counts by company/status and upcoming interviews;
  include ATS averages only for recorded scores. Do not invent missing values.

If JSON is invalid, an attachment is missing, a URL cannot be read, or an ID
conflicts, report the issue and ask for correction rather than silently
discarding or overwriting data. Tracking and scoring are agent-assisted;
the Python scripts do not implement a tracker or submit applications.
