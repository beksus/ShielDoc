import unittest

import pymupdf
from pathlib import Path
from tempfile import TemporaryDirectory

from app.redactors.pdf import redact_pdf
from app.detectors.email import detect_emails
from app.redactors.pdf import find_entity_rectangle


class PDFLocationTests(unittest.TestCase):
    def test_locates_email_without_changing_page(self):
        with pymupdf.open() as document:
            page = document.new_page()
            page.insert_text((72, 72), "Email: demo@example.com")

            original_text = page.get_text()
            entity = detect_emails(original_text, page=1)[0]

            rectangle = find_entity_rectangle(page, entity)

            self.assertFalse(rectangle.is_empty)
            self.assertEqual(
                page.get_textbox(rectangle),
                "demo@example.com",
            )
            self.assertEqual(page.get_text(), original_text)

    def test_rejects_repeated_value(self):
        with pymupdf.open() as document:
            page = document.new_page()
            page.insert_text((72, 72), "demo@example.com")
            page.insert_text((72, 100), "demo@example.com")

            entity = detect_emails(page.get_text(), page=1)[0]

            with self.assertRaises(ValueError):
                find_entity_rectangle(page, entity)

    def test_rejects_wrong_page(self):
        with pymupdf.open() as document:
            page = document.new_page()
            page.insert_text((72, 72), "demo@example.com")

            entity = detect_emails(page.get_text(), page=2)[0]

            with self.assertRaises(ValueError):
                find_entity_rectangle(page, entity)

    def test_redacts_saved_copy_and_preserves_original(self):
        with TemporaryDirectory() as directory:
            source = Path(directory) / "synthetic.pdf"
            output = Path(directory) / "redacted.pdf"

            with pymupdf.open() as document:
                page = document.new_page()
                page.insert_text((72, 72), "Email: demo@example.com")
                page.insert_text((72, 110), "Keep this sentence.")
                document.save(str(source))

            original_bytes = source.read_bytes()

            with pymupdf.open(str(source)) as document:
                entities = detect_emails(
                    document[0].get_text(),
                    page=1,
                )

            redact_pdf(source, output, entities)

            with pymupdf.open(str(output)) as document:
                text = document[0].get_text()

                self.assertNotIn("demo@example.com", text)
                self.assertIn("Email:", text)
                self.assertIn("Keep this sentence.", text)
                self.assertEqual(
                    document[0].search_for("demo@example.com"),
                    [],
                )

            self.assertEqual(source.read_bytes(), original_bytes)

    def test_refuses_to_overwrite_source(self):
        with TemporaryDirectory() as directory:
            source = Path(directory) / "synthetic.pdf"

            with pymupdf.open() as document:
                document.new_page()
                document.save(str(source))

            original_bytes = source.read_bytes()

            with self.assertRaises(ValueError):
                redact_pdf(source, source, [])

            self.assertEqual(source.read_bytes(), original_bytes)

    def test_refuses_to_overwrite_existing_output(self):
        with TemporaryDirectory() as directory:
            source = Path(directory) / "synthetic.pdf"
            output = Path(directory) / "existing.pdf"

            with pymupdf.open() as document:
                document.new_page()
                document.save(str(source))

            output.write_bytes(source.read_bytes())
            original_bytes = output.read_bytes()

            with self.assertRaises(FileExistsError):
                redact_pdf(source, output, [])

            self.assertEqual(output.read_bytes(), original_bytes)