"""
cover_letter_cloner.py

Generate a cover letter DOCX by cloning Example_CoverLetter_TEMPLATE.docx.

Design principle: the header (name), contact line (with real hyperlinks),
decorative divider, sender name, and sender address are ALL STATIC across
every job application -- they live untouched in the template and are never
parsed from markdown or regenerated. Only the date, salutation, body
paragraphs, and closing signature are dynamic per-letter content.

This avoids the historical bug where clearing/rebuilding the contact line
left orphaned <w:hyperlink> elements in place (python-docx's
`paragraph.runs` does not see runs wrapped in <w:hyperlink>, so naive
"clear all runs" logic silently failed to remove them).

Public entry point:
    generate_cover_letter_from_template(markdown_path, template_path, output_docx_path) -> str
"""

import os
import sys
import re
from datetime import date
from docx import Document

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from docx_fragment_utils import (
    add_shaped_paragraph,
    get_run_mold,
    append_run,
    set_single_run_text,
    parse_inline_markdown,
)

# Fixed template paragraph indices (see examples/cover_letter/Example_CoverLetter_TEMPLATE.docx)
IDX_DATE = 4
IDX_SALUTATION_SHAPE = 8
IDX_BODY_SHAPE = 9
IDX_FIRST_DYNAMIC = 8  # everything from here onward is cleared and rebuilt

DEFAULT_CLOSING_NAME = "Example Applicant"


class CoverLetterCloner:
    """Clone the cover letter template and insert only the dynamic content."""

    def __init__(self, template_path: str):
        self.template_path = template_path
        # Pristine copy used only as a source of formatting "shapes" -- never modified/saved.
        self.template_doc = Document(template_path)
        self.doc = None

    def clone_template(self):
        self.doc = Document(self.template_path)

    def clear_dynamic_content(self):
        """Remove salutation/body/closing placeholder paragraphs, keep [0:8] static."""
        while len(self.doc.paragraphs) > IDX_FIRST_DYNAMIC:
            p = self.doc.paragraphs[-1]._element
            p.getparent().remove(p)

    def update_date(self, date_text: str):
        set_single_run_text(self.doc.paragraphs[IDX_DATE], date_text)

    def add_salutation(self, text: str):
        shape = self.template_doc.paragraphs[IDX_SALUTATION_SHAPE]._element
        para = add_shaped_paragraph(self.doc, shape)
        mold = get_run_mold(shape)
        append_run(para, mold, text)

    def add_body_paragraph(self, text: str):
        shape = self.template_doc.paragraphs[IDX_BODY_SHAPE]._element
        para = add_shaped_paragraph(self.doc, shape)
        mold = get_run_mold(shape)
        for seg_text, bold, italic in parse_inline_markdown(text):
            if seg_text:
                append_run(para, mold, seg_text, bold=bold, italic=italic)

    def add_closing(self, closing_lines):
        """Closing has no template placeholder (template ends after body).
        Reuse the body paragraph shape (same font/spacing) for visual consistency."""
        shape = self.template_doc.paragraphs[IDX_BODY_SHAPE]._element
        mold = get_run_mold(shape)
        for line in closing_lines:
            para = add_shaped_paragraph(self.doc, shape)
            append_run(para, mold, line)

    def parse_markdown(self, markdown_content: str) -> dict:
        """
        Extract only the dynamic parts of the letter: salutation, body
        paragraphs, and closing name. Header/contact/address lines (if
        present in the source markdown) are intentionally ignored -- that
        content is static and lives in the template already.
        """
        lines = markdown_content.strip().split('\n')
        parsed = {"salutation": "", "paragraphs": [], "closing_name": DEFAULT_CLOSING_NAME}

        i = 0
        # Skip everything up through the divider line (title, name, contact, address)
        divider_idx = None
        for idx, line in enumerate(lines):
            if line.strip().startswith('---'):
                divider_idx = idx
                break

        if divider_idx is not None:
            i = divider_idx + 1
        else:
            i = 0

        # Skip empty lines
        while i < len(lines) and not lines[i].strip():
            i += 1

        # Salutation
        if i < len(lines) and lines[i].strip().startswith('Dear'):
            parsed["salutation"] = lines[i].strip()
            i += 1

        while i < len(lines) and not lines[i].strip():
            i += 1

        # Body paragraphs until closing indicator
        current_para = ""
        closing_lines = []
        in_closing = False

        while i < len(lines):
            line = lines[i].strip()

            if not in_closing and (line.lower().startswith('best regards') or line.lower().startswith('sincerely')):
                if current_para.strip():
                    parsed["paragraphs"].append(current_para.strip())
                    current_para = ""
                in_closing = True
                i += 1
                continue

            if in_closing:
                if line:
                    closing_lines.append(line)
                i += 1
                continue

            if not line:
                if current_para.strip():
                    parsed["paragraphs"].append(current_para.strip())
                    current_para = ""
            else:
                current_para = (current_para + " " + line).strip()
            i += 1

        if current_para.strip():
            parsed["paragraphs"].append(current_para.strip())

        if closing_lines:
            # Last non-empty closing line is treated as the signer's name
            parsed["closing_name"] = closing_lines[-1]

        return parsed

    def generate_docx(self, markdown_content: str, output_path: str, date_text: str = None):
        parsed = self.parse_markdown(markdown_content)

        self.clone_template()
        self.clear_dynamic_content()

        self.update_date(date_text or date.today().strftime("%B %d, %Y"))
        self.add_salutation(parsed["salutation"])
        for para_text in parsed["paragraphs"]:
            self.add_body_paragraph(para_text)
        self.add_closing(["Best regards,", parsed["closing_name"]])

        self.doc.save(output_path)
        return output_path


def generate_cover_letter_from_template(
    markdown_path: str,
    template_path: str,
    output_docx_path: str,
    date_text: str = None,
) -> str:
    """
    Generate a styled cover letter DOCX from a markdown source, using
    Example_CoverLetter_TEMPLATE.docx (or any compatible template) for all
    static formatting.

    Markdown conventions expected (also described in README.md):
      - Everything before the `---` divider (title/name/contact/address) is
        ignored -- static content lives in the template.
      - First non-empty line after the divider must be the salutation
        ("Dear ...,").
      - Body paragraphs are blank-line separated; **bold**/*italic* inline
        markdown is supported.
      - A "Best regards," (or "Sincerely,") line followed by a name marks
        the closing; if omitted, defaults to "Example Applicant".
    """
    with open(markdown_path, 'r', encoding='utf-8') as f:
        markdown_content = f.read()

    cloner = CoverLetterCloner(template_path)
    return cloner.generate_docx(markdown_content, output_docx_path, date_text=date_text)


if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Usage: python cover_letter_cloner.py <markdown_path> <template_path> <output_docx_path>")
        sys.exit(1)
    out = generate_cover_letter_from_template(sys.argv[1], sys.argv[2], sys.argv[3])
    print("Generated:", out)
