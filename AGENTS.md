# Careers Toolkit Agent Instructions

This public toolkit contains fictional examples and reusable document generators.
Never replace public example files with real applicant information.

## Paths

- Resume baseline: `examples/resume/Example_Resume_BASELINE.md`
- Resume template: `examples/resume/Example_Resume_TEMPLATE.docx`
- Cover-letter baseline: `examples/cover_letter/Example_CoverLetter_BASELINE.md`
- Cover-letter template: `examples/cover_letter/Example_CoverLetter_TEMPLATE.docx`
- Application schema example: `examples/company/jobs.example.json`
- Workflows: `scripts/resume_workflow.py`, `scripts/cover_letter_workflow.py`
- PDF helpers: `scripts/pdf_utils.py`
- Repository skills: `.github/skills/`

Resolve paths from the repository root, not a particular user's machine.
The repository includes four agent skills; no separate skill installation is
required in an agent that discovers `.github/skills/`:

- `job-tracker`: add, update, list, and report on private applications.
- `resume-tailor`: tailor supported resume content and coordinate ATS analysis.
- `cover-letter-generator`: generate a role-specific cover letter.
- `ats-matcher`: assess resume/job alignment and document gaps.

These are sanitized adaptations, not synchronized copies of user-level skills.
Consult their `SKILL.md` files for the detailed workflows.

## Privacy

Keep real baselines, personalized templates, company folders, resumes, letters,
ATS reports, and application records in a separate private directory.
The public `.gitignore` is an allowlist, not a privacy guarantee: tracked files
and forced additions bypass it. Review staged content and DOCX internals before
publishing. Never copy a private repository's `.git` directory or push its history.

## Application Records

Use one `jobs.json` array per company in the private working directory.
Use requisition number as `id` when available; otherwise use a unique local ID.
Document paths must be relative to that company folder and must exist before
recording a non-null `resumeUsed` or `coverLetterUsed`.

Fields and nullability are illustrated in `examples/company/jobs.example.json`.
Statuses: `interested`, `reviewed`, `applied`, `interview`, `offer`, `accepted`,
`rejected`. Typical flow is interested -> reviewed -> applied -> interview ->
offer -> accepted; rejection can occur during the application process.

Use one shared role slug and optional requisition suffix:

```text
resumes/Applicant_Resume_Role_Slug_ReqNumber.md
resumes/Applicant_Resume_Role_Slug_ReqNumber.docx
resumes/Applicant_Resume_Role_Slug_ReqNumber.pdf
cover_letters/Applicant_CoverLetter_Role_Slug_ReqNumber.md
cover_letters/Applicant_CoverLetter_Role_Slug_ReqNumber.docx
cover_letters/Applicant_CoverLetter_Role_Slug_ReqNumber.pdf
ats_matches/ATS_MATCH_ANALYSIS_Role_Slug_ReqNumber.md
```

Omit the entire requisition suffix when none exists. Sanitize filename inputs.

## Generation and Accuracy

1. Compare the job description against the applicant's factual private baseline.
2. Ask before adding unsupported skills, duties, achievements, metrics, dates,
   credentials, or projects. Never treat fictional examples as actual experience.
3. Keep resume sections in the fixed order Employment, Software Projects,
   Education, Skills. Follow the Markdown syntax in the README and examples.
4. Use the existing workflow wrappers and compatible private templates; do not
   reconstruct document formatting per application.
5. Customize static identity/contact/address fields in the private DOCX templates.
   Markdown identity fields do not replace them. Supply the actual closing name.
6. Generate DOCX and PDF, check `result["on_target"]`, and shorten/regenerate if
   the output exceeds one page.
7. Prefer PDF for submission; retain Markdown and DOCX as source/editable output.
8. Validate all referenced files before updating private application records.

ATS scores are heuristic, not predictions of an employer's screening system.
Use conservative weights: keywords/skills 40, duties 30, experience 20, education
10. Record evidence and gaps; never infer missing experience from posting text.

## Development

Keep changes focused. Preserve static template content and parser behavior.
Run `python -m unittest discover -s tests -v` after changing generators or templates.
Run both PDF workflows when changing formatting; see the README for commands.
The template builder creates fictional templates from scratch. It must not read
private templates or depend on local application records.

## Dependencies

Install the external Python packages from the repository root in PowerShell:

```powershell
python -m pip install -r requirements.txt
```

This installs `python-docx` for DOCX generation and `pypdf` for PDF page-count
validation. LibreOffice is also required for PDF conversion:

- Windows: download the installer from the
  [official LibreOffice download page](https://www.libreoffice.org/download/download-libreoffice/)
  and follow its prompts, or run
  `winget install --id TheDocumentFoundation.LibreOffice --exact`.
- Ubuntu/Debian: run `sudo apt update`, then `sudo apt install libreoffice`.
- macOS with Homebrew: run `brew install --cask libreoffice`.

Set `SOFFICE_PATH` to the installed `soffice` executable if it is not at the
default Windows path. See the README for OS-specific path examples.
