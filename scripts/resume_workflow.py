"""
resume_workflow.py

Single entry point that runs the full resume generation pipeline:
markdown -> DOCX (via resume_cloner's fragment cloning) -> PDF (via
LibreOffice) -> page-count verification. Wraps resume_cloner.py +
pdf_utils.py so a caller only needs one function call to get a submission-
ready PDF, instead of remembering to run a separate PDF-conversion step.

Public entry point:
    generate_resume_pdf(markdown_path, template_path, output_docx_path, target_pages=1) -> dict
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from resume_cloner import generate_resume_from_template
from pdf_utils import convert_docx_to_pdf, get_pdf_page_count


def generate_resume_pdf(
    markdown_path: str,
    template_path: str,
    output_docx_path: str,
    target_pages: int = 1,
) -> dict:
    """
    Generate a styled resume DOCX + PDF from markdown in one call.

    Auto-creates the output directory if it doesn't exist (so this is
    safe to call even if the target Careers/[Company]/resumes/ folder
    hasn't been created yet).

    Returns:
        {
            "docx_path": str,
            "pdf_path": str,
            "pages": int,
            "on_target": bool,  # True if pages <= target_pages
        }
    """
    os.makedirs(os.path.dirname(os.path.abspath(output_docx_path)), exist_ok=True)

    docx_path = generate_resume_from_template(markdown_path, template_path, output_docx_path)
    pdf_path = convert_docx_to_pdf(docx_path)
    pages = get_pdf_page_count(pdf_path)

    return {
        "docx_path": docx_path,
        "pdf_path": pdf_path,
        "pages": pages,
        "on_target": pages <= target_pages,
    }


if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Usage: python resume_workflow.py <markdown_path> <template_path> <output_docx_path> [target_pages]")
        sys.exit(1)
    target = int(sys.argv[4]) if len(sys.argv) > 4 else 1
    result = generate_resume_pdf(sys.argv[1], sys.argv[2], sys.argv[3], target_pages=target)
    print(result)
    if not result["on_target"]:
        print(f"WARNING: resume is {result['pages']} pages, exceeds target of {target}. Trim content and re-run.")
