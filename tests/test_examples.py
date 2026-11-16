import sys
import tempfile
import unittest
from pathlib import Path
from zipfile import ZipFile
from xml.etree import ElementTree as ET

from docx import Document

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from cover_letter_cloner import generate_cover_letter_from_template
from create_example_templates import build_templates
from resume_cloner import generate_resume_from_template

W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
REL = "{http://schemas.openxmlformats.org/package/2006/relationships}"


def document_text(path):
    with ZipFile(path) as archive:
        root = ET.fromstring(archive.read("word/document.xml"))
        return " ".join(node.text or "" for node in root.iter(f"{W}t"))


class ExampleGenerationTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)
        self.resume_template, self.letter_template = build_templates(self.root)

    def test_resume_renders_all_sections_and_project_hyperlink(self):
        output = self.root / "resume.docx"
        generate_resume_from_template(
            str(ROOT / "examples/resume/Example_Resume_BASELINE.md"),
            str(self.resume_template), str(output),
        )
        text = document_text(output)
        sections = ["Employment", "Software Projects", "Education", "Skills"]
        positions = [text.index(section) for section in sections]
        self.assertEqual(positions, sorted(positions))
        for expected in (
            "Example Applicant", "Software Developer", "Example Company",
            "Sample Task Board", "Example University", "JavaScript",
        ):
            self.assertIn(expected, text)
        with ZipFile(output) as archive:
            relationships = ET.fromstring(archive.read("word/_rels/document.xml.rels"))
            targets = [rel.get("Target") for rel in relationships]
        self.assertIn("https://example.com/projects/task-board", targets)

    def test_cover_letter_replaces_dynamic_content_and_keeps_static_identity(self):
        output = self.root / "letter.docx"
        generate_cover_letter_from_template(
            str(ROOT / "examples/cover_letter/Example_CoverLetter_BASELINE.md"),
            str(self.letter_template), str(output), date_text="February 03, 2026",
        )
        text = document_text(output)
        for expected in (
            "Example Applicant", "applicant@example.com", "123 Example Street",
            "February 03, 2026", "Dear Hiring Team,", "Python utilities",
            "Best regards,",
        ):
            self.assertIn(expected, text)
        self.assertNotIn("January 01, 2026", text)
        self.assertNotIn("Fictional example body paragraph.", text)
        self.assertNotIn("No claims below describe a real applicant", text)

    def test_missing_signing_name_uses_fictional_default(self):
        markdown = self.root / "unsigned.md"
        markdown.write_text("---\nDear Hiring Team,\n\nDemonstration.\n", encoding="utf-8")
        output = self.root / "unsigned.docx"
        generate_cover_letter_from_template(
            str(markdown), str(self.letter_template), str(output)
        )
        self.assertTrue(document_text(output).endswith("Best regards, Example Applicant"))

    def test_templates_contain_only_reviewable_xml_and_example_links(self):
        for template in (
            self.resume_template, self.letter_template,
            ROOT / "examples/resume/Example_Resume_TEMPLATE.docx",
            ROOT / "examples/cover_letter/Example_CoverLetter_TEMPLATE.docx",
        ):
            with self.subTest(template=template), ZipFile(template) as archive:
                for name in archive.namelist():
                    self.assertTrue(name.endswith((".xml", ".rels")), name)
                    self.assertNotIn("customXml", name)
                    self.assertNotIn("comments", name)
                    root = ET.fromstring(archive.read(name))
                    self.assertFalse(list(root.iter(f"{W}ins")), name)
                    self.assertFalse(list(root.iter(f"{W}del")), name)
                    if name.endswith(".rels"):
                        for relation in root.findall(f"{REL}Relationship"):
                            if relation.get("TargetMode") == "External":
                                target = relation.get("Target", "")
                                self.assertTrue(
                                    target.startswith("https://example.com/")
                                    or target == "mailto:applicant@example.com",
                                    target,
                                )
            properties = Document(template).core_properties
            self.assertEqual(properties.author, "")
            self.assertEqual(properties.last_modified_by, "")

    def test_builder_refuses_to_replace_existing_templates(self):
        original_resume = self.resume_template.read_bytes()
        original_letter = self.letter_template.read_bytes()
        with self.assertRaises(FileExistsError):
            build_templates(self.root)
        self.assertEqual(self.resume_template.read_bytes(), original_resume)
        self.assertEqual(self.letter_template.read_bytes(), original_letter)


if __name__ == "__main__":
    unittest.main()
