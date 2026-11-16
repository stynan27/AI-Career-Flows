"""Build fictional DOCX templates with the paragraph shapes the cloners require."""

import argparse
from datetime import datetime, timezone
from pathlib import Path

from docx import Document
from docx.document import Document as DocumentType
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_TAB_ALIGNMENT
from docx.opc.constants import RELATIONSHIP_TYPE as RT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Pt
from docx.text.paragraph import Paragraph

from docx_fragment_utils import add_hyperlink_run


def new_document() -> DocumentType:
    doc = Document()
    section = doc.sections[0]
    section.page_width = Inches(8.5)
    section.page_height = Inches(11)
    section.top_margin = section.bottom_margin = Inches(0.55)
    section.left_margin = section.right_margin = Inches(0.65)
    normal = doc.styles["Normal"]
    normal.font.name = "Calibri"
    normal.font.size = Pt(10)
    normal.paragraph_format.space_after = Pt(4)
    normal.paragraph_format.line_spacing = 1
    properties = doc.core_properties
    properties.author = ""
    properties.last_modified_by = ""
    properties.title = "Fictional example template"
    properties.subject = "Demonstration only; not a real applicant"
    properties.comments = ""
    properties.keywords = "fictional, example"
    properties.created = properties.modified = datetime(2000, 1, 1, tzinfo=timezone.utc)
    for owner in (doc.part.package, doc.part):
        for rel_id, relationship in list(owner.rels.items()):
            if relationship.reltype in (RT.THUMBNAIL, RT.CUSTOM_XML):
                del owner.rels[rel_id]

    name = doc.add_paragraph()
    name.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = name.add_run("Example Applicant")
    run.bold = True
    run.font.size = Pt(18)
    contact = doc.add_paragraph()
    contact.alignment = WD_ALIGN_PARAGRAPH.CENTER
    mold = contact.add_run("Contact: ")._element
    add_hyperlink_run(
        doc, contact, mold, "applicant@example.com", "mailto:applicant@example.com"
    )
    contact.add_run(" | ")
    add_hyperlink_run(
        doc, contact, mold, "example.com/portfolio", "https://example.com/portfolio"
    )
    return doc


def add_border(paragraph: Paragraph) -> None:
    borders = OxmlElement("w:pBdr")
    bottom = OxmlElement("w:bottom")
    for key, value in (("val", "single"), ("sz", "6"), ("color", "404040")):
        bottom.set(qn(f"w:{key}"), value)
    borders.append(bottom)
    paragraph._p.get_or_add_pPr().append(borders)


def add_heading(doc: DocumentType, text: str) -> None:
    paragraph = doc.add_paragraph()
    paragraph.paragraph_format.space_before = Pt(6)
    paragraph.paragraph_format.keep_with_next = True
    paragraph.add_run(text).bold = True
    add_border(paragraph)


def add_tabbed_line(
    doc: DocumentType, parts: list[tuple[str, bool, bool]]
) -> Paragraph:
    paragraph = doc.add_paragraph()
    paragraph.paragraph_format.tab_stops.add_tab_stop(
        Inches(7.2), WD_TAB_ALIGNMENT.RIGHT
    )
    paragraph.paragraph_format.keep_with_next = True
    for text, bold, italic in parts:
        run = paragraph.add_run(text)
        run.bold = bold
        run.italic = italic
    return paragraph


def resume_document() -> DocumentType:
    doc = new_document()
    add_heading(doc, "Employment")
    add_tabbed_line(doc, [
        ("Example Company - Sample City - ", True, False),
        ("Software Developer", False, True),
        ("\t2024 - Present", False, False),
    ])
    # Preserve the cloner's fixed project, education, and skill mold positions.
    for _ in range(10):
        doc.add_paragraph(
            "Fictional example: replace with a verified accomplishment.",
            style="List Bullet",
        )
    add_heading(doc, "Software Projects")
    project = add_tabbed_line(doc, [("Sample Project - ", True, False)])
    add_hyperlink_run(
        doc, project, project.runs[0]._element,
        "Project", "https://example.com/project",
    )
    project.add_run("\t2024")
    doc.add_paragraph("Fictional demonstration project.", style="List Bullet")
    doc.add_paragraph("Replace with supported project details.", style="List Bullet")
    add_heading(doc, "Education")
    add_tabbed_line(doc, [
        ("Example University - ", True, False),
        ("B.S. Computer Science", False, False),
        ("\t2023", False, False),
    ])
    add_heading(doc, "Skills")
    skills = doc.add_paragraph()
    skills.add_run("Languages: ").bold = True
    skills.add_run("(proficient)").italic = True
    skills.add_run(": ")
    skills.add_run("Python, SQL")
    return doc


def cover_letter_document() -> DocumentType:
    doc = new_document()
    add_border(doc.add_paragraph())
    doc.add_paragraph("")
    doc.add_paragraph("January 01, 2026")
    doc.add_paragraph("Example Applicant")
    doc.add_paragraph("123 Example Street")
    doc.add_paragraph("Sample City, ST 00000")
    doc.add_paragraph("Dear Hiring Team,")
    doc.add_paragraph("Fictional example body paragraph. Replace with verified facts.")
    return doc


def build_templates(output_root: Path, *, overwrite: bool = False) -> tuple[Path, Path]:
    resume = output_root / "examples/resume/Example_Resume_TEMPLATE.docx"
    letter = output_root / "examples/cover_letter/Example_CoverLetter_TEMPLATE.docx"
    for path in (resume, letter):
        if path.exists() and not overwrite:
            raise FileExistsError(f"Refusing to overwrite template: {path}")
    for path, factory in ((resume, resume_document), (letter, cover_letter_document)):
        path.parent.mkdir(parents=True, exist_ok=True)
        factory().save(path)
    return resume, letter


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output-root", type=Path, default=Path(__file__).resolve().parents[1]
    )
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()
    for template in build_templates(args.output_root, overwrite=args.overwrite):
        print(template)
