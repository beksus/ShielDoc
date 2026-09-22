import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from docx import Document
from zipfile import ZipFile

from docx.opc.constants import RELATIONSHIP_TYPE as RT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

from app.analyzer import analyze_pages
from app.extractors.docx import extract_docx
from app.redactors.docx import redact_docx


class DOCXRedactorTests(unittest.TestCase):
    def test_redacts_copy_and_preserves_original(self):
        with TemporaryDirectory() as directory:
            source = Path(directory) / "synthetic.docx"
            output = Path(directory) / "redacted.docx"

            document = Document()
            document.add_paragraph("Email: demo@example.com")
            document.add_paragraph("")
            document.add_paragraph("Email: demo@example.com")
            document.add_paragraph("Keep this paragraph.")
            document.save(str(source))

            original_bytes = source.read_bytes()
            entities = analyze_pages(extract_docx(str(source)))

            redact_docx(source, output, entities)

            saved = Document(str(output))

            self.assertEqual(
                [paragraph.text for paragraph in saved.paragraphs],
                [
                    "Email: [REDACTED]",
                    "",
                    "Email: [REDACTED]",
                    "Keep this paragraph.",
                ],
            )
            self.assertEqual(source.read_bytes(), original_bytes)
            remaining_entities = analyze_pages(
                extract_docx(str(output))
            )
            self.assertEqual(remaining_entities, [])

    def test_refuses_to_overwrite_source(self):
        with TemporaryDirectory() as directory:
            source = Path(directory) / "synthetic.docx"
            Document().save(str(source))

            original_bytes = source.read_bytes()

            with self.assertRaises(ValueError):
                redact_docx(source, source, [])

            self.assertEqual(source.read_bytes(), original_bytes)

    def test_refuses_to_overwrite_existing_output(self):
        with TemporaryDirectory() as directory:
            source = Path(directory) / "synthetic.docx"
            output = Path(directory) / "existing.docx"

            Document().save(str(source))
            Document().save(str(output))
            original_bytes = output.read_bytes()

            with self.assertRaises(FileExistsError):
                redact_docx(source, output, [])

            self.assertEqual(output.read_bytes(), original_bytes)

    def test_removes_email_target_and_preserves_other_links(self):
        def add_link(paragraph, text, target):
            relationship_id = paragraph.part.relate_to(
                target,
                RT.HYPERLINK,
                is_external=True,
            )

            hyperlink = OxmlElement("w:hyperlink")
            hyperlink.set(qn("r:id"), relationship_id)

            run = OxmlElement("w:r")
            text_element = OxmlElement("w:t")
            text_element.text = text

            run.append(text_element)
            hyperlink.append(run)
            paragraph._p.append(hyperlink)

        with TemporaryDirectory() as directory:
            source = Path(directory) / "synthetic.docx"
            output = Path(directory) / "redacted.docx"

            shared_url = "https://example.org/help"
            unrelated_url = "https://example.org/about"

            document = Document()

            sensitive = document.add_paragraph("Email: ")
            add_link(
                sensitive,
                "demo@example.com",
                "mailto:demo@example.com",
            )
            sensitive.add_run(" | ")
            add_link(sensitive, "Help", shared_url)

            # Reuses the relationship also present in the changed paragraph.
            shared = document.add_paragraph()
            add_link(shared, "Help", shared_url)

            unrelated = document.add_paragraph()
            add_link(unrelated, "About", unrelated_url)

            document.save(str(source))
            original_bytes = source.read_bytes()

            entities = analyze_pages(extract_docx(str(source)))
            self.assertEqual(len(entities), 1)
            self.assertEqual(entities[0].type, "EMAIL")

            redact_docx(source, output, entities)

            saved = Document(str(output))
            self.assertEqual(
                saved.paragraphs[0].text,
                "Email: [REDACTED] | Help",
            )
            self.assertEqual(
                saved.paragraphs[1].hyperlinks[0].url,
                shared_url,
            )
            self.assertEqual(
                saved.paragraphs[2].hyperlinks[0].url,
                unrelated_url,
            )

            with ZipFile(output) as package:
                relationships = package.read(
                    "word/_rels/document.xml.rels"
                )
                self.assertNotIn(b"demo@example.com", relationships)
                self.assertIn(shared_url.encode(), relationships)
                self.assertIn(unrelated_url.encode(), relationships)

                self.assertNotIn(
                    b"demo@example.com",
                    package.read("word/document.xml"),
                )

            self.assertEqual(source.read_bytes(), original_bytes)