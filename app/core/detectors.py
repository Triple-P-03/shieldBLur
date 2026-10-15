"""Conservative local secret detection and redaction.

The detector deliberately favors a small set of recognizable formats and a
context-plus-entropy fallback over trying to identify every possible secret.
It never sends clipboard contents anywhere.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
import math
import re
from typing import Iterable


@dataclass(frozen=True, slots=True)
class SecretMatch:
    """A secret-shaped span found in text."""

    secret_type: str
    start: int
    end: int
    confidence: float
    evidence: str = "format"

    @property
    def replacement(self) -> str:
        return f"[REDACTED: {self.secret_type}]"


def calculate_entropy(value: str) -> float:
    """Return Shannon entropy in bits per character."""

    if not value:
        return 0.0
    counts = Counter(value)
    length = len(value)
    return -sum((count / length) * math.log2(count / length) for count in counts.values())


class SecretDetector:
    """Detect common token formats and high-entropy context-labelled values."""

    _FORMATS: tuple[tuple[str, re.Pattern[str], float], ...] = (
        (
            "PRIVATE KEY",
            re.compile(
                r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"
                r"[\s\S]+?-----END (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"
            ),
            0.99,
        ),
        ("AWS ACCESS KEY", re.compile(r"\bAKIA[0-9A-Z]{16}\b"), 0.98),
        ("GITHUB TOKEN", re.compile(r"\bgh[pousr]_[A-Za-z0-9]{30,}\b"), 0.98),
        ("SLACK TOKEN", re.compile(r"\bxox[baprs]-[0-9A-Za-z-]{10,}\b"), 0.97),
        (
            "STRIPE SECRET KEY",
            re.compile(r"\bsk_(?:live|test)_[A-Za-z0-9]{16,}\b"),
            0.97,
        ),
        ("GOOGLE API KEY", re.compile(r"\bAIza[0-9A-Za-z_-]{30,}\b"), 0.96),
        (
            "JWT",
            re.compile(r"\beyJ[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}\b"),
            0.94,
        ),
    )
    _CONTEXT = re.compile(
        r"(?<![A-Za-z0-9])(?:api[_-]?key|access[_-]?key|secret|token|password|passwd|credential)"
        r"\b\s*[:=]\s*[\"']?"
        r"(?P<value>[A-Za-z0-9_./+=:@-]{12,})"
        r"[\"']?",
        re.IGNORECASE,
    )
    _PLACEHOLDERS = {
        "changeme",
        "change-me",
        "example",
        "placeholder",
        "password",
        "secret",
        "token",
        "your-api-key",
        "your_api_key",
        "not-a-secret",
    }

    def detect(self, text: str) -> list[SecretMatch]:
        """Find non-overlapping secret spans in ``text``."""

        if not text:
            return []

        candidates: list[SecretMatch] = []
        for secret_type, pattern, confidence in self._FORMATS:
            for match in pattern.finditer(text):
                candidates.append(
                    SecretMatch(
                        secret_type=secret_type,
                        start=match.start(),
                        end=match.end(),
                        confidence=confidence,
                    )
                )

        for match in self._CONTEXT.finditer(text):
            value = match.group("value")
            entropy = calculate_entropy(value)
            varied = len(set(value)) >= 6 and any(char.isdigit() for char in value)
            if (
                len(value) >= 16
                and entropy >= 3.0
                and varied
                and value.lower() not in self._PLACEHOLDERS
            ):
                candidates.append(
                    SecretMatch(
                        secret_type="GENERIC SECRET",
                        start=match.start("value"),
                        end=match.end("value"),
                        confidence=min(0.93, 0.62 + entropy / 10),
                        evidence="context + entropy",
                    )
                )

        return self._remove_overlaps(candidates)

    @staticmethod
    def _remove_overlaps(candidates: Iterable[SecretMatch]) -> list[SecretMatch]:
        ordered = sorted(candidates, key=lambda item: (item.start, -(item.end - item.start)))
        accepted: list[SecretMatch] = []
        for candidate in ordered:
            if any(
                candidate.start < previous.end and candidate.end > previous.start
                for previous in accepted
            ):
                continue
            accepted.append(candidate)
        return sorted(accepted, key=lambda item: item.start)


def detect_secrets(text: str) -> list[SecretMatch]:
    """Convenience function for callers that do not need a detector object."""

    return SecretDetector().detect(text)


def redact_secrets(text: str, matches: Iterable[SecretMatch] | None = None) -> str:
    """Replace detected spans while preserving all other clipboard text."""

    resolved = list(detect_secrets(text) if matches is None else matches)
    for match in sorted(resolved, key=lambda item: item.start, reverse=True):
        text = text[: match.start] + match.replacement + text[match.end :]
    return text
