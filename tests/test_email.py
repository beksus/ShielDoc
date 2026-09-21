import unittest

from app.detectors.email import detect_emails


class EmailDetectorTests(unittest.TestCase):
    def test_detects_email_with_correct_offsets(self):
        text = "Contact: demo@example.com"

        entities = detect_emails(text, page=1)

        self.assertEqual(len(entities), 1)

        entity = entities[0]

        self.assertEqual(entity.type, "EMAIL")
        self.assertEqual(entity.value, "demo@example.com")
        self.assertEqual(entity.page, 1)
        self.assertEqual(entity.start, 9)
        self.assertEqual(entity.end, 25)
        self.assertEqual(entity.confidence, 1.0)
        self.assertEqual(text[entity.start:entity.end], entity.value)

    def test_returns_empty_list_without_email(self):
        entities = detect_emails("No email address here.")

        self.assertEqual(entities, [])