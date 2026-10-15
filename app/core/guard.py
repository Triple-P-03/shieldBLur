"""Clipboard guard service with no Qt dependency."""

from __future__ import annotations

from dataclasses import dataclass, field

from app.core.detectors import SecretDetector, SecretMatch, redact_secrets


@dataclass(frozen=True, slots=True)
class GuardResult:
    """Result of scanning one clipboard text value."""

    original_text: str
    output_text: str
    matches: tuple[SecretMatch, ...] = ()

    @property
    def redacted(self) -> bool:
        return bool(self.matches)

    @property
    def secret_types(self) -> tuple[str, ...]:
        return tuple(dict.fromkeys(match.secret_type for match in self.matches))


@dataclass(slots=True)
class GuardStats:
    """Small in-memory counter set used by the dashboard."""

    scanned: int = 0
    redacted: int = 0
    secrets_found: int = 0
    type_counts: dict[str, int] = field(default_factory=dict)


class ClipboardGuardService:
    """Scan clipboard text and return a safe replacement when needed.

    This service has no clipboard or Qt access. Integrations decide how to
    write ``GuardResult.output_text`` back to a clipboard implementation.
    """

    def __init__(self, detector: SecretDetector | None = None) -> None:
        self.detector = detector or SecretDetector()
        self.stats = GuardStats()

    def process_text(self, text: str) -> GuardResult:
        """Scan text, redacting only recognized secret spans."""

        matches = tuple(self.detector.detect(text))
        output = redact_secrets(text, matches) if matches else text
        self.stats.scanned += 1
        if matches:
            self.stats.redacted += 1
            self.stats.secrets_found += len(matches)
            for secret_type in (match.secret_type for match in matches):
                self.stats.type_counts[secret_type] = self.stats.type_counts.get(secret_type, 0) + 1
        return GuardResult(original_text=text, output_text=output, matches=matches)

    scan = process_text
