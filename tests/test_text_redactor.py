import unittest

from app.detectors.email import detect_emails
from app.models.pii import PIIEntity
from app.redactors.text import redact_text


class TextRedactorTests(unittest.TestCase):
    def test_redacts_repeated_emails_in_any_entity_order(self):
        text = "Email: demo@example.com; again: demo@example.com."
        entities = detect_emails(text)

        result = redact_text(text, list(reversed(entities)))

        self.assertEqual(
            result,
            "Email: [REDACTED]; again: [REDACTED].",
        )

    def test_merges_overlapping_spans(self):
        text = "abcdefghij"
        entities = [
            PIIEntity("TEST", "cdef", None, 2, 6),
            PIIEntity("TEST", "efgh", None, 4, 8),
        ]

        self.assertEqual(
            redact_text(text, entities),
            "ab[REDACTED]ij",
        )

    def test_duplicate_spans_are_redacted_once(self):
        text = "demo@example.com"
        entities = detect_emails(text)

        self.assertEqual(
            redact_text(text, entities + entities),
            "[REDACTED]",
        )

    def test_no_entities_preserves_text(self):
        self.assertEqual(redact_text("Nothing to replace.", []),
                         "Nothing to replace.")
        self.assertEqual(redact_text("", []), "")

    def test_rejects_invalid_offsets(self):
        entity = PIIEntity("TEST", "abc", None, -1, 3)

        with self.assertRaises(ValueError):
            redact_text("abc", [entity])

    def test_rejects_mismatched_value(self):
        entity = PIIEntity("TEST", "xyz", None, 0, 3)

        with self.assertRaises(ValueError):
            redact_text("abc", [entity])