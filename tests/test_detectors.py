import unittest

from app.core.detectors import SecretDetector, calculate_entropy, redact_secrets


class SecretDetectorTests(unittest.TestCase):
    def setUp(self):
        self.detector = SecretDetector()

    def test_detects_synthetic_aws_format(self):
        text = "deploy value: AKIA1234567890ABCDEF"
        matches = self.detector.detect(text)
        self.assertEqual([match.secret_type for match in matches], ["AWS ACCESS KEY"])
        self.assertEqual(redact_secrets(text, matches), "deploy value: [REDACTED: AWS ACCESS KEY]")

    def test_detects_synthetic_context_value_using_entropy(self):
        text = "service_token=v7Nq2Lm9Qx4Rz8TpK3"
        matches = self.detector.detect(text)
        self.assertEqual(len(matches), 1)
        self.assertEqual(matches[0].secret_type, "GENERIC SECRET")
        self.assertEqual(matches[0].evidence, "context + entropy")

    def test_detects_fake_private_key_block(self):
        text = "before\n-----BEGIN PRIVATE KEY-----\nFAKE-DEMO-DATA\n-----END PRIVATE KEY-----\nafter"
        matches = self.detector.detect(text)
        self.assertEqual([match.secret_type for match in matches], ["PRIVATE KEY"])
        self.assertIn("[REDACTED: PRIVATE KEY]", redact_secrets(text, matches))

    def test_preserves_plain_clipboard_text(self):
        text = "meeting notes: bring tea and a notebook"
        self.assertEqual(self.detector.detect(text), [])
        self.assertEqual(redact_secrets(text), text)

    def test_does_not_flag_obvious_context_placeholder(self):
        text = "api_key=your-api-key"
        self.assertEqual(self.detector.detect(text), [])

    def test_entropy_handles_empty_and_repetitive_values(self):
        self.assertEqual(calculate_entropy(""), 0.0)
        self.assertEqual(calculate_entropy("aaaa"), 0.0)
        self.assertGreater(calculate_entropy("aB7x-29Qp"), 2.0)


if __name__ == "__main__":
    unittest.main()
