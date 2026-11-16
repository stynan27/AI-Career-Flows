"""
resume_cloner.py

Generate a resume DOCX by cloning Example_Resume_TEMPLATE.docx.

Design principle: the header (name) and contact line (with real
hyperlinks) are STATIC and never parsed/rewritten. All body content is
rebuilt by deep-cloning representative paragraph "shapes" from the
template (section headers with bottom borders, right-tab job/education/
project lines, numPr bullets, tiered skill lines) so generated documents
are formatting-identical to the template -- not a manual reconstruction.

Fixed section order matches the template exactly and cannot be reordered:
    Employment -> Software Projects -> Education -> Skills
There is no Professional Summary placeholder in the template; this
cloner does not support one.

Public entry point:
    generate_resume_from_template(markdown_path, template_path, output_docx_path) -> str
"""

import os
import re
import sys
from docx import Document

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from docx_fragment_utils import (
    add_shaped_paragraph,
    get_run_mold,
    append_run,
    append_tab_run,
    add_hyperlink_run,
    parse_inline_markdown,
)

# Fixed template paragraph indices (see examples/resume/Example_Resume_TEMPLATE.docx)
IDX_SECTION_HEADER = 2   # "Employment" heading shape (Heading1 + bottom border) -- reused for all 4 headers
IDX_JOB_LINE = 3         # bold company/location + italic title + right-tab date
IDX_BULLET = 4           # numPr bulleted list paragraph
IDX_PROJECT_LINE = 15    # bold name + hyperlink + right-tab date
IDX_EDUCATION_LINE = 19  # bold school + plain degree + right-tab year
IDX_SKILL_LINE = 21      # bold label + italic (proficient)/(familiar) tiers

SECTION_LINK_RE = re.compile(r'\[(.*?)\]\((.*?)\)')
SKILL_LINE_RE = re.compile(
    r'\*\*(.+?)\*\*:\s*\(proficient\):\s*(.+?)(?:\.\s*\(familiar\):\s*(.+))?$'
)


class ResumeCloner:
    """Clone the resume template and insert content in the template's fixed section order."""

    def __init__(self, template_path: str):
        self.template_path = template_path
        # Pristine copy used only as a source of formatting "shapes" -- never modified/saved.
        self.template_doc = Document(template_path)
        self.doc = None

    def clone_template(self):
        self.doc = Document(self.template_path)

    def clear_dynamic_content(self):
        """Keep only [0,1] (name, contact-with-hyperlinks); delete everything else."""
        while len(self.doc.paragraphs) > 2:
            p = self.doc.paragraphs[-1]._element
            p.getparent().remove(p)

    # --- shape-cloning builders -------------------------------------------------

    def add_section_header(self, text: str):
        shape = self.template_doc.paragraphs[IDX_SECTION_HEADER]._element
        para = add_shaped_paragraph(self.doc, shape)
        mold = get_run_mold(shape, 0)
        append_run(para, mold, text)

    def add_job_line(self, bold_prefix: str, italic_title: str, date_text: str):
        shape = self.template_doc.paragraphs[IDX_JOB_LINE]._element
        para = add_shaped_paragraph(self.doc, shape)
        bold_mold = get_run_mold(shape, 0)
        italic_mold = get_run_mold(shape, 1)
        tab_mold = get_run_mold(shape, 2)
        append_run(para, bold_mold, bold_prefix, bold=True, italic=False)
        append_run(para, italic_mold, italic_title, bold=False, italic=True)
        append_tab_run(para, tab_mold, date_text, bold=False, italic=False)
        return para

    def add_bullet(self, text: str):
        shape = self.template_doc.paragraphs[IDX_BULLET]._element
        para = add_shaped_paragraph(self.doc, shape)
        mold = get_run_mold(shape, 0)
        for seg_text, bold, italic in parse_inline_markdown(text):
            if seg_text:
                append_run(para, mold, seg_text, bold=bold, italic=italic)

    def add_project_line(self, name: str, link_text: str, link_url: str, date_text: str):
        shape = self.template_doc.paragraphs[IDX_PROJECT_LINE]._element
        para = add_shaped_paragraph(self.doc, shape)
        bold_mold = get_run_mold(shape, 0)
        tab_mold = get_run_mold(shape, 1)
        if name and name != link_text:
            append_run(para, bold_mold, name + " - ", bold=True, italic=False)
        add_hyperlink_run(self.doc, para, bold_mold, link_text, link_url)
        append_tab_run(para, tab_mold, date_text, bold=False, italic=False)
        return para

    def add_education_line(self, school: str, degree: str, year: str):
        shape = self.template_doc.paragraphs[IDX_EDUCATION_LINE]._element
        para = add_shaped_paragraph(self.doc, shape)
        bold_mold = get_run_mold(shape, 0)
        plain_mold = get_run_mold(shape, 1)
        tab_mold = get_run_mold(shape, 2)
        append_run(para, bold_mold, school + " - ", bold=True, italic=False)
        append_run(para, plain_mold, degree, bold=False, italic=False)
        append_tab_run(para, tab_mold, year, bold=False, italic=False)

    def add_skill_line(self, label: str, proficient_text: str, familiar_text: str = None):
        shape = self.template_doc.paragraphs[IDX_SKILL_LINE]._element
        para = add_shaped_paragraph(self.doc, shape)
        bold_mold = get_run_mold(shape, 0)
        italic_mold = get_run_mold(shape, 1)
        plain_mold = get_run_mold(shape, 3)

        append_run(para, bold_mold, label + ": ", bold=True, italic=False)
        append_run(para, italic_mold, "(", bold=False, italic=True)
        append_run(para, italic_mold, "proficient", bold=False, italic=True)
        suffix = ". " if familiar_text else ""
        append_run(para, plain_mold, "): " + proficient_text + suffix, bold=False, italic=False)

        if familiar_text:
            append_run(para, italic_mold, "(", bold=False, italic=True)
            append_run(para, italic_mold, "familiar", bold=False, italic=True)
            append_run(para, plain_mold, "): " + familiar_text, bold=False, italic=False)

    # --- markdown parsing ---------------------------------------------------

    def parse_resume_markdown(self, markdown_content: str) -> dict:
        """
        Parse resume markdown. Required section headers (## Employment,
        ## Software Projects, ## Education, ## Skills) may appear in any
        order in the source file, but are always rendered in the fixed
        template order regardless. Name/contact lines are ignored (static).

        Conventions:
          Employment entry:
            ### Title, Company — Location | Date Range
            - bullet
            - bullet
          Software Projects entry:
            ### Name - [Link Label](https://url) | Date
            - bullet
            ### [Project Name](https://url) | Date
            - bullet
          Education entry:
            **School** — Degree | Year
          Skills entry:
            **Label**: (proficient): item, item. (familiar): item, item
        """
        lines = markdown_content.strip().split('\n')
        parsed = {"employment": [], "projects": [], "education": [], "skills": []}

        current_section = None
        i = 0

        while i < len(lines):
            line = lines[i]
            stripped = line.strip()

            if stripped.startswith('## '):
                current_section = stripped[3:].strip().lower()
                i += 1
                continue

            if not stripped or stripped.startswith('# '):
                i += 1
                continue

            if current_section == "employment" and stripped.startswith('### '):
                job, i = self._parse_job_entry(stripped[4:].strip(), lines, i + 1)
                parsed["employment"].append(job)
                continue

            if current_section == "software projects" and stripped.startswith('### '):
                project, i = self._parse_project_entry(stripped[4:].strip(), lines, i + 1)
                parsed["projects"].append(project)
                continue

            if current_section == "education" and '—' in stripped:
                edu = self._parse_education_entry(stripped)
                if edu:
                    parsed["education"].append(edu)
                i += 1
                continue

            if current_section == "skills":
                skill = self._parse_skill_entry(stripped)
                if skill:
                    parsed["skills"].append(skill)
                i += 1
                continue

            i += 1

        return parsed

    def _parse_job_entry(self, header_text: str, lines: list, start: int):
        parts = header_text.split('|')
        dates = parts[1].strip() if len(parts) > 1 else ""
        main = parts[0].strip()

        if '—' in main:
            left, location = main.split('—', 1)
            location = location.strip()
        else:
            left, location = main, ""

        if ',' in left:
            title, company = left.split(',', 1)
            title, company = title.strip(), company.strip()
        else:
            title, company = left.strip(), ""

        bullets = []
        i = start
        while i < len(lines):
            l = lines[i].strip()
            if l.startswith('###') or l.startswith('##'):
                break
            if l.startswith('- '):
                bullets.append(l[2:].strip())
            i += 1

        job = {"company": company, "location": location, "title": title, "dates": dates, "bullets": bullets}
        return job, i

    def _parse_project_entry(self, header_text: str, lines: list, start: int):
        parts = header_text.split('|')
        date_text = parts[1].strip() if len(parts) > 1 else ""
        main = parts[0].strip()

        link_match = SECTION_LINK_RE.search(main)
        if link_match:
            link_text = link_match.group(1)
            link_url = link_match.group(2)
            name = main[:link_match.start()].rstrip(' -').strip()
            if not name:
                name = link_text
        else:
            link_text, link_url, name = "", "", main.rstrip(' -').strip()

        bullets = []
        i = start
        while i < len(lines):
            l = lines[i].strip()
            if l.startswith('###') or l.startswith('##'):
                break
            if l.startswith('- '):
                bullets.append(l[2:].strip())
            i += 1

        project = {"name": name, "link_text": link_text, "link_url": link_url, "date": date_text, "bullets": bullets}
        return project, i

    def _parse_education_entry(self, line: str):
        clean = line.replace('**', '')
        if '—' not in clean:
            return None
        school, rest = clean.split('—', 1)
        rest = rest.strip()
        if '|' in rest:
            degree, year = rest.split('|', 1)
        else:
            degree, year = rest, ""
        return {"school": school.strip(), "degree": degree.strip(), "year": year.strip()}

    def _parse_skill_entry(self, line: str):
        m = SKILL_LINE_RE.match(line)
        if not m:
            return None
        label = m.group(1).strip()
        proficient = m.group(2).strip().rstrip('.').strip()
        familiar = m.group(3).strip() if m.group(3) else None
        return {"label": label, "proficient": proficient, "familiar": familiar}

    # --- generation orchestration -------------------------------------------

    def generate_docx(self, markdown_path: str, output_path: str):
        with open(markdown_path, 'r', encoding='utf-8') as f:
            content = f.read()

        parsed = self.parse_resume_markdown(content)

        self.clone_template()
        self.clear_dynamic_content()

        if parsed["employment"]:
            self.add_section_header("Employment")
            for job in parsed["employment"]:
                bold_prefix = "{} - {} - ".format(job["company"], job["location"]) if job["location"] else "{} - ".format(job["company"])
                self.add_job_line(bold_prefix, job["title"], job["dates"])
                for bullet in job["bullets"]:
                    self.add_bullet(bullet)

        if parsed["projects"]:
            self.add_section_header("Software Projects")
            for project in parsed["projects"]:
                self.add_project_line(project["name"], project["link_text"], project["link_url"], project["date"])
                for bullet in project["bullets"]:
                    self.add_bullet(bullet)

        if parsed["education"]:
            self.add_section_header("Education")
            for edu in parsed["education"]:
                self.add_education_line(edu["school"], edu["degree"], edu["year"])

        if parsed["skills"]:
            self.add_section_header("Skills")
            for skill in parsed["skills"]:
                self.add_skill_line(skill["label"], skill["proficient"], skill["familiar"])

        self.doc.save(output_path)
        return output_path


def generate_resume_from_template(
    markdown_path: str,
    template_path: str,
    output_docx_path: str,
) -> str:
    """
    Generate a styled resume DOCX from a markdown source, using
    Example_Resume_TEMPLATE.docx (or any compatible template) for all
    formatting. See the class docstring and README.md for Markdown conventions.
    """
    cloner = ResumeCloner(template_path)
    return cloner.generate_docx(markdown_path, output_docx_path)


if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Usage: python resume_cloner.py <markdown_path> <template_path> <output_docx_path>")
        sys.exit(1)
    out = generate_resume_from_template(sys.argv[1], sys.argv[2], sys.argv[3])
    print("Generated:", out)
