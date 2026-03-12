from pathlib import Path

import fitz  # PyMuPDF
from docx import Document as DocxDocument

from app.core.exceptions import DocumentProcessingError


def parse_document(file_path: str) -> list[dict]:
    """
    Returns a list of pages/sections in normalized format:
    [
        {
            "page_number": 1,
            "text": "...",
            "section_title": None
        }
    ]
    """
    ext = Path(file_path).suffix.lower()

    if ext == ".pdf":
        return parse_pdf(file_path)
    if ext == ".docx":
        return parse_docx(file_path)

    raise DocumentProcessingError(f"Unsupported file type for parsing: {ext}")


def parse_pdf(file_path: str) -> list[dict]:
    pages = []
    try:
        doc = fitz.open(file_path)
        for page_index, page in enumerate(doc):
            text = page.get_text("text").strip()
            if text:
                pages.append(
                    {
                        "page_number": page_index + 1,
                        "text": text,
                        "section_title": None,
                    }
                )
        doc.close()
        return pages
    except Exception as exc:
        raise DocumentProcessingError(f"Failed to parse PDF: {exc}") from exc


def parse_docx(file_path: str) -> list[dict]:
    try:
        doc = DocxDocument(file_path)
        paragraphs = [p.text.strip() for p in doc.paragraphs if p.text.strip()]
        joined_text = "\n".join(paragraphs)

        return [
            {
                "page_number": 1,
                "text": joined_text,
                "section_title": None,
            }
        ]
    except Exception as exc:
        raise DocumentProcessingError(f"Failed to parse DOCX: {exc}") from exc