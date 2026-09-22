import subprocess
import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

import pymupdf


PROJECT_ROOT = Path(__file__).resolve().parents[1]


class CLIErrorTests(unittest.TestCase):
    def assert_cli_error(self, path: Path, expected: str) -> None:
        result = subprocess.run(
            [sys.executable, "-m", "app.main", str(path)],
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
            timeout=30,
        )

        self.assertEqual(result.returncode, 2, result.stderr)
        self.assertIn(expected, result.stderr)
        self.assertNotIn("Traceback", result.stderr)
        self.assertNotIn("No PII detected.", result.stdout)

    def test_missing_file(self):
        with TemporaryDirectory() as directory:
            path = Path(directory) / "missing.pdf"

            self.assert_cli_error(path, "File not found")

    def test_corrupt_documents(self):
        with TemporaryDirectory() as directory:
            for extension in (".pdf", ".docx"):
                with self.subTest(extension=extension):
                    path = Path(directory) / f"broken{extension}"
                    path.write_bytes(b"This is not a document.")

                    self.assert_cli_error(path, "Cannot read document")

    def test_empty_pdf(self):
        with TemporaryDirectory() as directory:
            path = Path(directory) / "empty.pdf"
            path.write_bytes(b"")

            self.assert_cli_error(path, "Cannot read document")

    def test_password_protected_pdf(self):
        with TemporaryDirectory() as directory:
            path = Path(directory) / "protected.pdf"

            with pymupdf.open() as document:
                page = document.new_page()
                page.insert_text((72, 72), "Synthetic test document.")
                document.save(
                    str(path),
                    encryption=pymupdf.PDF_ENCRYPT_AES_256,
                    owner_pw="synthetic-owner",
                    user_pw="synthetic-reader",
                )

            self.assert_cli_error(
                path,
                "Password-protected PDFs are not supported.",
            )