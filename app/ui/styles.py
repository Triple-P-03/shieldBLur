"""Load the single editable QSS theme used by the stage-one shell."""

from pathlib import Path
import sys


def _theme_path() -> Path:
    """Resolve the theme from source checkouts and PyInstaller bundles."""

    bundle_root = getattr(sys, "_MEIPASS", None)
    root = Path(bundle_root) if bundle_root else Path(__file__).resolve().parents[2]
    return root / "assets" / "shieldblur.qss"


APP_STYLE = _theme_path().read_text(encoding="utf-8")
