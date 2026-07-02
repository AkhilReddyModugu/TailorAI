# PyMuPDF resume text extraction

import fitz


class PDFParseError(Exception):
    """Raised when a resume PDF cannot be read or contains no usable text."""


def extract_text_from_pdf(pdf_bytes: bytes) -> str:
    """Extract raw text from a resume PDF.

    Raises PDFParseError for corrupted files, empty files, or PDFs with no
    extractable text (e.g. scanned/image-only pages), so callers can fail
    the session with a clear message instead of feeding garbage to Gemini.
    """
    if not pdf_bytes:
        raise PDFParseError("The uploaded file is empty.")

    try:
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    except Exception as exc:
        raise PDFParseError("Could not open the file. It may be corrupted or not a valid PDF.") from exc

    try:
        if doc.page_count == 0:
            raise PDFParseError("The PDF has no pages.")

        pages_text = [page.get_text() for page in doc]
    except PDFParseError:
        raise
    except Exception as exc:
        raise PDFParseError("Could not extract text from this PDF.") from exc
    finally:
        doc.close()

    text = "\n".join(pages_text).strip()

    if len(text) < 20:
        raise PDFParseError(
            "Could not extract text from this PDF. It may be a scanned image "
            "or empty. Please upload a text-based PDF."
        )

    return text
