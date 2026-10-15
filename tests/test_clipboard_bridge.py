import os
import unittest

try:
    from PySide6.QtWidgets import QApplication
    from app.core.guard import ClipboardGuardService
    from app.ui.clipboard_bridge import QtClipboardGuard
    PYSIDE_AVAILABLE = True
except ImportError:
    PYSIDE_AVAILABLE = False


@unittest.skipUnless(PYSIDE_AVAILABLE, "PySide6 is not installed")
class QtClipboardGuardTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
        cls.application = QApplication.instance() or QApplication([])

    def test_guard_rewrites_one_clipboard_change_without_looping(self):
        clipboard = self.application.clipboard()
        service = ClipboardGuardService()
        bridge = QtClipboardGuard(clipboard, service)
        redactions = []
        bridge.redacted.connect(redactions.append)
        clipboard.setText("value=AKIA1234567890ABCDEF")
        self.application.processEvents()
        self.assertEqual(clipboard.text(), "value=[REDACTED: AWS ACCESS KEY]")
        self.assertEqual(len(redactions), 1)
        self.assertEqual(service.stats.scanned, 1)
        bridge.deleteLater()


if __name__ == "__main__":
    unittest.main()
