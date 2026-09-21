import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from docx import Document

from app.analyzer import analyze_pages
from app.extractors.docx import extract_docx


class DOCXPipelineTests(unittest.TestCase):
    def test_extracts_and_detects_email_in_paragraph(self):
        with TemporaryDirectory() as directory:
            docx_path = Path(directory) / "synthetic.docx"

            document = Document()
            document.add_paragraph("No email in this paragraph.")
            document.add_paragraph("Contact: demo@example.com")
            document.save(str(docx_path))

            paragraphs = extract_docx(str(docx_path))
            entities = analyze_pages(paragraphs)

            self.assertEqual(len(paragraphs), 2)
            self.assertEqual(len(entities), 1)

            entity = entities[0]

            self.assertEqual(entity.type, "EMAIL")
            self.assertEqual(entity.value, "demo@example.com")
            self.assertIsNone(entity.page)

            paragraph_text = paragraphs[1]["text"]
            self.assertEqual(
                paragraph_text[entity.start:entity.end],
                entity.value,
            )