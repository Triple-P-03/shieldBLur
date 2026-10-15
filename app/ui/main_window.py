"""Frameless ShieldBlur desktop shell."""

from __future__ import annotations

from PySide6.QtCore import QEvent, QPoint, QTimer, Qt
from PySide6.QtGui import QMouseEvent
from PySide6.QtWidgets import (
    QApplication,
    QFrame,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QSizePolicy,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from app.core.guard import ClipboardGuardService, GuardResult
from app.core.settings import SUPPORTED_PAGES
from app.ui.styles import APP_STYLE


class MainWindow(QMainWindow):
    """Dark shell for stage one, with a functional dashboard and placeholders."""

    def __init__(self, service: ClipboardGuardService) -> None:
        super().__init__()
        self.service = service
        self._drag_position: QPoint | None = None
        self._last_result: GuardResult | None = None
        self._nav_buttons: list[QPushButton] = []
        self.setWindowTitle("ShieldBlur")
        self.setMinimumSize(1040, 680)
        self.resize(1180, 760)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Window)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setStyleSheet(APP_STYLE)
        self._build()

    def _build(self) -> None:
        root = QWidget(objectName="root")
        outer = QVBoxLayout(root)
        outer.setContentsMargins(8, 8, 8, 8)
        outer.setSpacing(0)
        frame = QFrame(objectName="windowFrame")
        outer.addWidget(frame)
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(self._title_bar())

        body = QHBoxLayout()
        body.setContentsMargins(12, 0, 12, 12)
        body.setSpacing(14)
        self.sidebar = self._sidebar()
        body.addWidget(self.sidebar)

        self.content = QWidget()
        content_layout = QVBoxLayout(self.content)
        content_layout.setContentsMargins(12, 4, 12, 8)
        content_layout.setSpacing(18)
        content_layout.addWidget(self._content_header())
        self.pages = QStackedWidget()
        self.pages.addWidget(self._dashboard_page())
        for page_name in SUPPORTED_PAGES[1:]:
            self.pages.addWidget(self._placeholder_page(page_name))
        content_layout.addWidget(self.pages, 1)
        body.addWidget(self.content, 1)
        layout.addLayout(body, 1)
        self.setCentralWidget(root)
        self._toast = self._make_toast()
        self._toast.hide()

    def _title_bar(self) -> QWidget:
        bar = QFrame(objectName="titleBar")
        bar.setFixedHeight(52)
        layout = QHBoxLayout(bar)
        layout.setContentsMargins(20, 0, 12, 0)
        layout.setSpacing(8)
        mark = QLabel("S", objectName="brandMark")
        mark.setFixedWidth(22)
        layout.addWidget(mark)
        brand = QLabel("ShieldBlur", objectName="brand")
        layout.addWidget(brand)
        layout.addStretch(1)
        minimize = QPushButton("—", objectName="windowButton")
        minimize.setFixedSize(30, 28)
        minimize.clicked.connect(self.showMinimized)
        close = QPushButton("×", objectName="windowButton")
        close.setFixedSize(30, 28)
        close.clicked.connect(self.close)
        layout.addWidget(minimize)
        layout.addWidget(close)
        bar.installEventFilter(self)
        return bar

    def _sidebar(self) -> QFrame:
        sidebar = QFrame(objectName="sidebar")
        sidebar.setFixedWidth(214)
        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(12, 20, 12, 16)
        layout.setSpacing(5)
        intro = QLabel("LOCAL GUARD", objectName="eyebrow")
        intro.setContentsMargins(10, 0, 0, 14)
        layout.addWidget(intro)
        for index, page_name in enumerate(SUPPORTED_PAGES):
            button = QPushButton(self._page_label(index, page_name), objectName="navButton")
            button.setCheckable(True)
            button.clicked.connect(lambda checked, page=index: self._select_page(page))
            self._nav_buttons.append(button)
            layout.addWidget(button)
        layout.addStretch(1)
        hint = QLabel("Nothing leaves this device.\nClipboard protection is local.", objectName="sidebarHint")
        hint.setWordWrap(True)
        hint.setContentsMargins(10, 0, 8, 8)
        layout.addWidget(hint)
        self._nav_buttons[0].setChecked(True)
        return sidebar

    @staticmethod
    def _page_label(index: int, name: str) -> str:
        icons = ("⌂", "◈", "◌", "≡", "⚙")
        return f"  {icons[index]}   {name}"

    def _content_header(self) -> QWidget:
        header = QWidget()
        layout = QHBoxLayout(header)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)
        self.page_title = QLabel("Dashboard", objectName="pageTitle")
        layout.addWidget(self.page_title)
        layout.addStretch(1)
        self.status_pill = QLabel("●  Protection active", objectName="statusPill")
        layout.addWidget(self.status_pill)
        return header

    def _dashboard_page(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(18)
        intro = QHBoxLayout()
        intro.setSpacing(8)
        copy = QVBoxLayout()
        copy.setSpacing(5)
        greeting = QLabel("Your local safety layer is ready", objectName="subtitle")
        greeting.setStyleSheet("font-size: 16px; color: #d8eeee; font-weight: 600;")
        copy.addWidget(greeting)
        copy.addWidget(QLabel("ShieldBlur watches copied text and removes recognizable secrets before they travel.", objectName="muted"))
        intro.addLayout(copy)
        intro.addStretch(1)
        layout.addLayout(intro)

        cards = QHBoxLayout()
        cards.setSpacing(12)
        self._scanned_value = self._add_stat_card(cards, "◷", "CLIPBOARD CHECKS", "0")
        self._redacted_value = self._add_stat_card(cards, "✦", "ITEMS REDACTED", "0", accent=True)
        self._found_value = self._add_stat_card(cards, "◈", "SECRETS FOUND", "0")
        layout.addLayout(cards)

        activity_card = QFrame(objectName="card")
        activity_layout = QVBoxLayout(activity_card)
        activity_layout.setContentsMargins(18, 16, 18, 16)
        activity_layout.setSpacing(12)
        activity_header = QHBoxLayout()
        activity_header.addWidget(QLabel("Recent activity", objectName="cardLabel"))
        activity_header.addStretch(1)
        activity_header.addWidget(QLabel("LIVE", objectName="badge"))
        activity_layout.addLayout(activity_header)
        self._activity_empty = QLabel("No clipboard events yet. Copy some text to test the local guard.", objectName="muted")
        self._activity_empty.setContentsMargins(4, 10, 4, 10)
        activity_layout.addWidget(self._activity_empty)
        self._activity_rows = QVBoxLayout()
        self._activity_rows.setSpacing(8)
        activity_layout.addLayout(self._activity_rows)
        layout.addWidget(activity_card, 1)
        layout.addStretch(1)
        return page

    @staticmethod
    def _add_stat_card(parent: QHBoxLayout, icon: str, label: str, value: str, accent: bool = False) -> QLabel:
        card = QFrame(objectName="cardAccent" if accent else "card")
        card.setMinimumHeight(112)
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(16, 13, 16, 13)
        top = QHBoxLayout()
        top.addWidget(QLabel(icon, objectName="cardIcon"))
        top.addStretch(1)
        card_layout.addLayout(top)
        card_layout.addWidget(QLabel(label, objectName="cardLabel"))
        value_label = QLabel(value, objectName="cardValue")
        card_layout.addWidget(value_label)
        parent.addWidget(card, 1)
        return value_label

    def _placeholder_page(self, title: str) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 16, 0, 0)
        layout.setSpacing(12)
        label = QLabel(title, objectName="pageTitle")
        layout.addWidget(label)
        description = {
            "Protected Sources": "Choose which local clipboard sources should be watched in a later stage.",
            "Detection Rules": "Pattern controls and custom rules will be available in a later stage.",
            "Event Log": "A searchable local event history is planned for a later stage.",
            "Settings": "Preferences and startup controls will be added in a later stage.",
        }[title]
        layout.addWidget(QLabel(description, objectName="subtitle"))
        card = QFrame(objectName="card")
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(24, 24, 24, 24)
        card_layout.addWidget(QLabel("Stage-one placeholder", objectName="cardLabel"))
        card_layout.addWidget(QLabel("The navigation is ready while this page is intentionally not implemented yet.", objectName="muted"))
        card_layout.addStretch(1)
        layout.addWidget(card, 1)
        return page

    def _make_toast(self) -> QFrame:
        toast = QFrame(self, objectName="toast")
        toast.setFixedSize(360, 76)
        layout = QHBoxLayout(toast)
        layout.setContentsMargins(14, 10, 10, 10)
        layout.setSpacing(10)
        icon = QLabel("✓", objectName="cardIcon")
        icon.setFixedWidth(20)
        layout.addWidget(icon)
        text_layout = QVBoxLayout()
        text_layout.setSpacing(2)
        self._toast_title = QLabel("Clipboard secured", objectName="toastTitle")
        self._toast_text = QLabel("Sensitive text was replaced locally.", objectName="toastText")
        text_layout.addWidget(self._toast_title)
        text_layout.addWidget(self._toast_text)
        layout.addLayout(text_layout, 1)
        details = QPushButton("Details", objectName="toastDetails")
        details.clicked.connect(self._show_last_details)
        layout.addWidget(details)
        return toast

    def _select_page(self, index: int) -> None:
        self.pages.setCurrentIndex(index)
        self.page_title.setText(SUPPORTED_PAGES[index])
        for position, button in enumerate(self._nav_buttons):
            button.setChecked(position == index)

    def show_redaction_toast(self, result: GuardResult) -> None:
        """Update dashboard counters and show a non-sensitive notification."""

        self._last_result = result
        stats = self.service.stats
        self._scanned_value.setText(str(stats.scanned))
        self._redacted_value.setText(str(stats.redacted))
        self._found_value.setText(str(stats.secrets_found))
        types = ", ".join(result.secret_types)
        self._toast_text.setText(f"Redacted {types} locally")
        self._toast.adjustSize()
        self._toast.setFixedSize(360, 76)
        self._toast.move(self.width() - self._toast.width() - 24, self.height() - self._toast.height() - 24)
        self._toast.show()
        QTimer.singleShot(6500, self._toast.hide)
        self._add_activity(result)

    def _add_activity(self, result: GuardResult) -> None:
        self._activity_empty.hide()
        row = QFrame(objectName="activityRow")
        row_layout = QHBoxLayout(row)
        row_layout.setContentsMargins(12, 8, 12, 8)
        copy = QVBoxLayout()
        copy.setSpacing(2)
        copy.addWidget(QLabel("Clipboard protected", objectName="activityType"))
        copy.addWidget(QLabel(f"{len(result.matches)} item(s) replaced · local only", objectName="activityMeta"))
        row_layout.addLayout(copy, 1)
        row_layout.addWidget(QLabel("REDACTED", objectName="badge"))
        self._activity_rows.insertWidget(0, row)
        while self._activity_rows.count() > 4:
            old = self._activity_rows.takeAt(4)
            if old.widget():
                old.widget().deleteLater()

    def _show_last_details(self) -> None:
        if not self._last_result:
            return
        details = "\n".join(f"• {match.secret_type} ({match.evidence})" for match in self._last_result.matches)
        QMessageBox.information(
            self,
            "Redaction details",
            f"Detected locally:\n{details}\n\nThe original value was processed locally and is not persisted.",
        )

    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)
        if hasattr(self, "_toast") and self._toast.isVisible():
            self._toast.move(self.width() - self._toast.width() - 24, self.height() - self._toast.height() - 24)

    def eventFilter(self, watched, event) -> bool:
        if watched.objectName() == "titleBar":
            if event.type() == QEvent.Type.MouseButtonPress and isinstance(event, QMouseEvent):
                if event.button() == Qt.MouseButton.LeftButton:
                    self._drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
                    return True
            if event.type() == QEvent.Type.MouseMove and self._drag_position and isinstance(event, QMouseEvent):
                if event.buttons() & Qt.MouseButton.LeftButton:
                    self.move(event.globalPosition().toPoint() - self._drag_position)
                    return True
            if event.type() == QEvent.Type.MouseButtonRelease:
                self._drag_position = None
        return super().eventFilter(watched, event)
