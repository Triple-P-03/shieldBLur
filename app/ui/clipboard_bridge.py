"""Qt adapter for the Qt-free clipboard guard service."""

from __future__ import annotations

from PySide6.QtCore import QObject, Signal
from PySide6.QtGui import QClipboard

from app.core.guard import ClipboardGuardService, GuardResult


class QtClipboardGuard(QObject):
    """Watch a QClipboard and replace detected secrets once per change."""

    redacted = Signal(object)

    def __init__(self, clipboard: QClipboard, service: ClipboardGuardService) -> None:
        super().__init__(clipboard)
        self.clipboard = clipboard
        self.service = service
        self._writing = False
        self._last_written: str | None = None
        clipboard.dataChanged.connect(self._on_data_changed)

    def _on_data_changed(self) -> None:
        # setText can emit dataChanged immediately on some platforms and later
        # on others. Both guards are needed to avoid a write/process loop.
        if self._writing:
            return
        text = self.clipboard.text()
        if self._last_written is not None and text == self._last_written:
            self._last_written = None
            return
        self._last_written = None
        if not text:
            return

        result = self.service.process_text(text)
        if not result.redacted:
            return

        self._last_written = result.output_text
        self._writing = True
        try:
            self.clipboard.setText(result.output_text)
        finally:
            self._writing = False
        self.redacted.emit(result)
