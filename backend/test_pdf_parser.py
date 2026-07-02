"""Manual test script for app.services.pdf_parser.

Covers: a normal text PDF, an empty/blank PDF, and a corrupted file.
Run with: python test_pdf_parser.py
"""

import fitz

from app.services.pdf_parser import PDFParseError, extract_text_from_pdf


def make_normal_pdf() -> bytes:
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text(
        (72, 72),
        "Jane Doe\nSoftware Engineer\n\nSkills: Python, React, AWS\n\n"
        "Experience:\nBuilt REST APIs using Flask and deployed on AWS.",
    )
    pdf_bytes = doc.tobytes()
    doc.close()
    return pdf_bytes


def make_empty_pdf() -> bytes:
    doc = fitz.open()
    doc.new_page()  # page with no text/content at all
    pdf_bytes = doc.tobytes()
    doc.close()
    return pdf_bytes


def make_corrupted_file() -> bytes:
    return b"this is not a real PDF file, just garbage bytes %PDF-broken"


def run_case(name: str, pdf_bytes: bytes):
    print(f"--- {name} ---")
    try:
        text = extract_text_from_pdf(pdf_bytes)
        print(f"OK, extracted {len(text)} chars:")
        print(repr(text[:200]))
    except PDFParseError as e:
        print(f"PDFParseError (expected/handled): {e}")
    print()


if __name__ == "__main__":
    run_case("Normal PDF", make_normal_pdf())
    run_case("Empty PDF (blank page)", make_empty_pdf())
    run_case("Empty bytes", b"")
    run_case("Corrupted file", make_corrupted_file())
