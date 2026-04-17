from pathlib import Path

import pdfplumber
from docx import Document


class ResumeParser:
    @staticmethod
    def extract_text(file_path):
        path = Path(file_path)
        suffix = path.suffix.lower()

        if suffix == ".pdf":
            return ResumeParser._extract_pdf_text(path)
        if suffix == ".docx":
            return ResumeParser._extract_docx_text(path)

        raise ValueError("Unsupported file type. Only PDF and DOCX are allowed.")

    @staticmethod
    def _extract_pdf_text(file_path):
        pages = []

        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    pages.append(text.strip())

        return "\n\n".join(pages).strip()

    @staticmethod
    def _extract_docx_text(file_path):
        document = Document(file_path)
        paragraphs = [paragraph.text.strip() for paragraph in document.paragraphs if paragraph.text.strip()]
        return "\n".join(paragraphs).strip()
