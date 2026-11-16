"""
pdf_utils.py

Shared PDF conversion + verification helpers used by resume_workflow.py
and cover_letter_workflow.py. Kept separate from the DOCX cloners so
either cloner can be used standalone (DOCX only) or wrapped for the full
markdown -> DOCX -> PDF -> page-count-check pipeline.

Public functions:
    convert_docx_to_pdf(docx_path, outdir=None) -> str
    get_pdf_page_count(pdf_path) -> int
"""

import os
import subprocess

from pypdf import PdfReader

# Overridable via env var for portability; defaults to the standard Windows install path.
SOFFICE_PATH = os.environ.get(
    "SOFFICE_PATH", r"C:\Program Files\LibreOffice\program\soffice.exe"
)


def convert_docx_to_pdf(docx_path: str, outdir: str = None) -> str:
    """
    Convert a DOCX file to PDF via headless LibreOffice. Returns the
    resulting PDF path (same basename as the DOCX, in `outdir` or the
    DOCX's own directory if `outdir` is omitted).
    """
    docx_path = os.path.abspath(docx_path)
    if not os.path.exists(docx_path):
        raise FileNotFoundError(f"DOCX not found: {docx_path}")

    outdir = os.path.abspath(outdir) if outdir else os.path.dirname(docx_path)
    os.makedirs(outdir, exist_ok=True)

    result = subprocess.run(
        [SOFFICE_PATH, "--headless", "--convert-to", "pdf", "--outdir", outdir, docx_path],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(
            f"LibreOffice PDF conversion failed (exit {result.returncode}):\n"
            f"stdout: {result.stdout}\nstderr: {result.stderr}"
        )

    pdf_name = os.path.splitext(os.path.basename(docx_path))[0] + ".pdf"
    pdf_path = os.path.join(outdir, pdf_name)
    if not os.path.exists(pdf_path):
        raise RuntimeError(f"Expected PDF not found after conversion: {pdf_path}")
    return pdf_path


def get_pdf_page_count(pdf_path: str) -> int:
    """Return the number of pages in a PDF file."""
    return len(PdfReader(pdf_path).pages)
