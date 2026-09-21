import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

import pymupdf

from app.analyzer import analyze_pages
from app.extractors.pdf import extract_pdf


class PDFPipelineTests(unittest.TestCase):
    def test_extracts_and_detects_email_on_correct_page(self):
        with TemporaryDirectory() as directory:
            pdf_path = Path(directory) / "synthetic.pdf"

            # Create a PDF containing only synthetic data.
            with pymupdf.open() as document:
                first_page = document.new_page()
                first_page.insert_text((72, 72), "No email on this page.")

                second_page = document.new_page()
                second_page.insert_text(
                    (72, 72),
                    "Contact: demo@example.com",
                )

                document.save(str(pdf_path))

            # Run the actual application pipeline.
            pages = extract_pdf(str(pdf_path))
            entities = analyze_pages(pages)

            self.assertEqual(len(pages), 2)
            self.assertEqual(len(entities), 1)

            entity = entities[0]

            self.assertEqual(entity.type, "EMAIL")
            self.assertEqual(entity.value, "demo@example.com")
            self.assertEqual(entity.page, 2)

            page_text = pages[1]["text"]
            self.assertEqual(
                page_text[entity.start:entity.end],
                entity.value,
            )

    def test_detects_email_and_phone_from_pdf(self):
        with TemporaryDirectory() as directory:
            pdf_path = Path(directory) / "synthetic_contacts.pdf"

            with pymupdf.open() as document:
                page = document.new_page()
                page.insert_text(
                    (72, 72),
                    "Email: demo@example.com\n"
                    "Phone: +998 00 000-00-00",
                )
                document.save(str(pdf_path))

            pages = extract_pdf(str(pdf_path))
            entities = analyze_pages(pages)

            self.assertEqual(
                [(entity.type, entity.value) for entity in entities],
                [
                    ("EMAIL", "demo@example.com"),
                    ("PHONE", "+998 00 000-00-00"),
                ],
            )

            extracted_text = pages[0]["text"]

            for entity in entities:
                self.assertEqual(entity.page, 1)
                self.assertEqual(
                    extracted_text[entity.start:entity.end],
                    entity.value,
                )