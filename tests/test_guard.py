import unittest

from app.core.guard import ClipboardGuardService


class ClipboardGuardServiceTests(unittest.TestCase):
    def test_redacts_and_returns_metadata_without_qt(self):
        guard = ClipboardGuardService()
        result = guard.process_text("note: AKIA1234567890ABCDEF")
        self.assertTrue(result.redacted)
        self.assertEqual(result.output_text, "note: [REDACTED: AWS ACCESS KEY]")
        self.assertEqual(result.secret_types, ("AWS ACCESS KEY",))
        self.assertEqual(guard.stats.scanned, 1)
        self.assertEqual(guard.stats.redacted, 1)
        self.assertEqual(guard.stats.secrets_found, 1)

    def test_plain_text_is_returned_byte_for_byte(self):
        guard = ClipboardGuardService()
        text = "a normal copied sentence with punctuation."
        result = guard.scan(text)
        self.assertFalse(result.redacted)
        self.assertEqual(result.output_text, text)
        self.assertEqual(guard.stats.scanned, 1)
        self.assertEqual(guard.stats.redacted, 0)

    def test_multiple_values_are_replaced_and_counted(self):
        guard = ClipboardGuardService()
        text = "first=AKIA1234567890ABCDEF second=sk_test_1234567890ABCDEF"
        result = guard.process_text(text)
        self.assertEqual(len(result.matches), 2)
        self.assertIn("[REDACTED: AWS ACCESS KEY]", result.output_text)
        self.assertIn("[REDACTED: STRIPE SECRET KEY]", result.output_text)
        self.assertEqual(guard.stats.secrets_found, 2)


if __name__ == "__main__":
    unittest.main()
