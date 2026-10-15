"""Run ShieldBlur with ``python -m app``."""

from __future__ import annotations

import sys

from PySide6.QtWidgets import QApplication

from app.core.guard import ClipboardGuardService
from app.ui.clipboard_bridge import QtClipboardGuard
from app.ui.main_window import MainWindow


def main() -> int:
    app = QApplication(sys.argv)
    app.setApplicationName("ShieldBlur")
    app.setOrganizationName("ShieldBlur")

    service = ClipboardGuardService()
    window = MainWindow(service)
    clipboard_guard = QtClipboardGuard(app.clipboard(), service)
    clipboard_guard.redacted.connect(window.show_redaction_toast)
    window.clipboard_guard = clipboard_guard
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
