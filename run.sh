#!/usr/bin/env bash
set -euo pipefail

MODE="${1:-run}"
case "$MODE" in
  run|test|demo) ;;
  *) printf 'Usage: ./run.sh [run|test|demo]\n' >&2; exit 2 ;;
esac

ROOT="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
cd "$ROOT"

PIN_FILE=".python-version"
if [[ ! -r "$PIN_FILE" ]]; then
  printf 'Missing pinned Python version file: %s\n' "$PIN_FILE" >&2
  exit 1
fi

REQUIRED_PYTHON_VERSION="3.11.2"
PYTHON_VERSION="$(tr -d '[:space:]' < "$PIN_FILE")"
if [[ "$PYTHON_VERSION" != "$REQUIRED_PYTHON_VERSION" ]]; then
  printf 'This project requires the pinned Python %s runtime; found pin in %s: %s\n' \
    "$REQUIRED_PYTHON_VERSION" "$PIN_FILE" "$PYTHON_VERSION" >&2
  exit 1
fi
PYTHON_MAJOR=3
PYTHON_MINOR=11
PYTHON_PATCH=2
PYTHON_BIN="${PYTHON_BIN:-python3.11}"
PYTHON=".venv/bin/python"

check_python() {
  local interpreter="$1"
  if ! "$interpreter" -c 'import sys; expected=tuple(map(int, sys.argv[1:4])); actual=sys.version_info[:3]; sys.exit("expected Python %s.%s.%s, found %s.%s.%s" % (*expected, *actual)) if actual != expected else None' "$PYTHON_MAJOR" "$PYTHON_MINOR" "$PYTHON_PATCH"; then
    printf 'Python %s (from %s) is required; refusing to use an arbitrary interpreter.\n' "$PYTHON_VERSION" "$PIN_FILE" >&2
    exit 1
  fi
}

if [[ ! -x "$PYTHON" ]]; then
  if [[ -e .venv ]]; then
    printf 'The project virtual environment is incomplete: %s\n' "$PYTHON" >&2
    printf 'Remove .venv and rerun this launcher to recreate it with Python %s.\n' "$PYTHON_VERSION" >&2
    exit 1
  fi
  if ! command -v "$PYTHON_BIN" >/dev/null 2>&1; then
    printf 'Python %s is required, but %s was not found. Install that runtime or set PYTHON_BIN to a compatible interpreter.\n' "$PYTHON_VERSION" "$PYTHON_BIN" >&2
    exit 1
  fi
  check_python "$PYTHON_BIN"
  "$PYTHON_BIN" -m venv .venv
fi

if [[ ! -x "$PYTHON" ]]; then
  printf 'Python virtual environment creation failed: %s\n' "$PYTHON" >&2
  exit 1
fi
check_python "$PYTHON"

if [[ ! -r requirements.lock ]]; then
  printf 'Missing dependency lockfile: requirements.lock\n' >&2
  exit 1
fi

STAMP_FILE=".venv/.requirements.lock.sha256"
LOCK_HASH="$("$PYTHON" -c 'import hashlib; from pathlib import Path; print(hashlib.sha256(Path("requirements.lock").read_bytes()).hexdigest())')"
if [[ ! -f "$STAMP_FILE" ]] || [[ "$(tr -d '\r\n' < "$STAMP_FILE")" != "$LOCK_HASH" ]]; then
  "$PYTHON" -m pip install --disable-pip-version-check --requirement requirements.lock
  printf '%s' "$LOCK_HASH" > "$STAMP_FILE"
fi

if [[ -z "${DISPLAY:-}" && -z "${WAYLAND_DISPLAY:-}" ]]; then
  export QT_QPA_PLATFORM="${QT_QPA_PLATFORM:-offscreen}"
fi

case "$MODE" in
  run)  exec "$PYTHON" -m app ;;
  test) exec "$PYTHON" -m unittest discover -s tests -v ;;
  demo) exec "$PYTHON" -m demo.redaction_demo ;;
esac
