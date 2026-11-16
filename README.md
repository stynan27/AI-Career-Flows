# Careers Toolkit

Generate consistently styled resumes and cover letters from Markdown, and keep
application records using a simple JSON convention.

**All shipped applicant information is fictional.** This public starter contains
no real application records or private document history.

## Contents

```text
examples/
  resume/        Example_Resume_BASELINE.md, Example_Resume_TEMPLATE.docx
  cover_letter/  Example_CoverLetter_BASELINE.md, Example_CoverLetter_TEMPLATE.docx
  company/       jobs.example.json (fictional record/schema example)
scripts/         Markdown parsers, DOCX cloners, PDF workflows, template builder
tests/           Example generation and template safety checks
.github/skills/  Sanitized repository agent skills
AGENTS.md        Portable agent workflow and accuracy rules
requirements.txt
```

Reusable generators and agent workflows are included. Personal application
folders, generated submission files, historical archives, machine-specific
diagnostic scripts, virtual environments, caches, and Git history are excluded.

## Agent Skills

The `.github/skills/` directory provides sanitized versions of `job-tracker`,
`resume-tailor`, `cover-letter-generator`, and `ats-matcher`. GitHub Copilot
in VS Code can discover these project skills without a separate installation;
other agents may use different skill locations. Start a new chat in this
workspace and check its skills menu if they do not appear.

These are independent adaptations, not automatically synchronized with any
user-level skills. They instruct an agent; tracking, tailoring, and ATS scoring
are not standalone programs. Keep real inputs and outputs in a separate private
directory, not in this public repository.

## Setup

Requires Python 3.10+ and LibreOffice. This export was tested with Python 3.14.

From the toolkit root in PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

`requirements.txt` installs the toolkit's external Python packages:

- `python-docx>=1.2,<2` — creates and edits DOCX files.
- `pypdf>=6.16.2,<7` — reads generated PDFs for page-count validation.

To install those packages directly instead of using the requirements file:

```powershell
python -m pip install "python-docx>=1.2,<2" "pypdf>=6.16.2,<7"
```

Install LibreOffice separately:

- **Windows with winget:** Run
  `winget install --id TheDocumentFoundation.LibreOffice --exact`.
  Default executable path is `C:\Program Files\LibreOffice\program\soffice.exe`.
  If winget is unavailable, download the Windows installer from the
  [official LibreOffice download page](https://www.libreoffice.org/download/download-libreoffice/),
  run the `.msi`, and follow the installer prompts.
- **Ubuntu/Debian:** Run `sudo apt update`, then `sudo apt install libreoffice`.
- **macOS with Homebrew:** Run `brew install --cask libreoffice`.

If LibreOffice is installed outside the expected path, set `SOFFICE_PATH` to
the executable before starting Python. For Windows:

```powershell
$env:SOFFICE_PATH = 'C:\Program Files\LibreOffice\program\soffice.exe'
```

On Linux/macOS, activate the virtual environment using your shell and set
`SOFFICE_PATH` to the installed executable, for example
`export SOFFICE_PATH=/usr/bin/soffice` on Linux or
`export SOFFICE_PATH=/Applications/LibreOffice.app/Contents/MacOS/soffice` on
macOS.

## Try the Fictional Examples

These commands produce one-page DOCX and PDF files under the ignored `output`
directory:

```powershell
python scripts\resume_workflow.py examples\resume\Example_Resume_BASELINE.md examples\resume\Example_Resume_TEMPLATE.docx output\Example_Resume.docx
python scripts\cover_letter_workflow.py examples\cover_letter\Example_CoverLetter_BASELINE.md examples\cover_letter\Example_CoverLetter_TEMPLATE.docx output\Example_CoverLetter.docx
```

Each workflow prints `docx_path`, `pdf_path`, `pages`, and `on_target`.
Require `on_target` to be true and visually review the output. The command-line
workflow warns about excess pages; it does not automatically trim content or
return a nonzero exit status for that warning.

For DOCX-only generation without LibreOffice, use the same three path arguments
with `scripts\resume_cloner.py` or `scripts\cover_letter_cloner.py`. Create the
output directory first when calling the cloners directly.

Programmatic entry points:

```python
from pathlib import Path
import sys

root = Path.cwd()
sys.path.insert(0, str(root / "scripts"))
from resume_workflow import generate_resume_pdf
from cover_letter_workflow import generate_cover_letter_pdf

result = generate_resume_pdf(
    str(root / "examples/resume/Example_Resume_BASELINE.md"),
    str(root / "examples/resume/Example_Resume_TEMPLATE.docx"),
    str(root / "output/Example_Resume.docx"),
    target_pages=1,
)
assert result["on_target"], result
```

`generate_cover_letter_pdf` takes the same arguments plus optional `date_text`
before `target_pages`. Both wrappers create output directories.

## Create Your Own Private Materials

1. Create a separate private working directory outside this public toolkit.
2. Copy the example Markdown and DOCX templates into that private directory.
3. Replace fictional experience with verified facts.
4. Edit name/contact details inside each private DOCX template. For cover
   letters, edit sender name and address there too.
5. Pass those private paths to the workflows and write outputs privately.

**Identity fields are static in DOCX templates.** Changing a Markdown name or
email does not update the rendered header. Cover-letter signing name is dynamic:
include an explicit closing name; otherwise it defaults to "Example Applicant".
Only the date, greeting, body, and signing name vary in cover-letter generation.

Templates use fixed paragraph positions as formatting molds. Preserve paragraph
order/count when customizing a template; change text/style in place. Removing
or inserting paragraphs can break generation. Header/contact fields are body
paragraphs 0 and 1, not Word header parts.

### Resume Markdown

Use `## Employment`, `## Software Projects`, `## Education`, and `## Skills`.
The generator always renders those sections in that fixed order.

- Employment: `### Title, Company` followed by an em dash (`U+2014`), location,
  `| Date Range`, then `- ` accomplishment bullets.
- Projects: `### Name - [Link Label](https://example.com/project) | Date`, then
  `- ` bullets. The example uses an actual clickable hyperlink.
- Education: `**School**` followed by an em dash (`U+2014`), `Degree | Year`.
- Skills: `**Label**: (proficient): items. (familiar): items`.
  The familiar tier is optional; the punctuation and tier labels matter.

See the [fictional resume](examples/resume/Example_Resume_BASELINE.md) for exact
syntax. There is no Professional Summary placeholder.

### Cover-Letter Markdown

Place optional notes/identity text before a `---` divider. After it:

1. A salutation beginning with `Dear`.
2. Body paragraphs separated by blank lines.
3. `Best regards,` or `Sincerely,` followed by a signing name.

The current renderer always writes `Best regards,` as the closing phrase.
Inline `**bold**` and `*italic*` are supported in resume bullets and letter body
paragraphs. This is a deliberately small Markdown subset, not a general renderer.

### Application Tracking

Copy [jobs.example.json](examples/company/jobs.example.json) to a private
`company/jobs.json`. Use paths relative to that company folder for attachments.
The example's attachment paths and ATS score are null because no application
was made. Tracking and ATS assessment are manual or agent-assisted conventions;
these scripts do not submit applications, scrape postings, or calculate scores.

## Tests and Template Rebuilding

```powershell
python -m unittest discover -s tests -v
```

The included DOCX templates were built from scratch using fictional content,
not redacted from a real applicant's Word files. To create fresh fictional
templates in another directory:

```powershell
python scripts\create_example_templates.py --output-root output\fresh-examples
```

The builder refuses to replace existing templates unless `--overwrite` is
explicitly supplied. Do not use that option on personalized templates.

## Publishing Safely

- Publish this clean export as a **new repository**. Do not change the original
  private repository's visibility, copy its `.git` directory, or push its history.
- Initialize Git only in this clean directory and connect it to a new empty
  remote. No remote or upload is configured by the toolkit.
- The `.gitignore` uses an allowlist. Personal company folders, output, local
  environments, and other unexpected files are ignored by default.
- **Ignore rules do not protect edits to tracked files or `git add --force`.**
  Never personalize the tracked examples; keep real data outside this repository.
- Review every staged file and inspect DOCX ZIP parts, hyperlinks, core
  properties, comments, and embedded data. Visible text alone is insufficient.
- Choose an appropriate license before inviting reuse; none is selected here.
- This export is not connected to a private repository and contains no Git
  history, credentials, or real applicant documents.
