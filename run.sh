#!/usr/bin/env bash
set -euo pipefail

MODE="${1:-run}"
case "$MODE" in
  run|test|demo) ;;
  *) printf 'Usage: ./run.sh [run|test|demo]\n' >&2; exit 2 ;;
esac

ROOT="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
cd "$ROOT"

if [[ -x .venv/bin/python ]]; then
  PYTHON=".venv/bin/python"
else
  PYTHON_BIN="${PYTHON_BIN:-python3.11}"
  if ! command -v "$PYTHON_BIN" >/dev/null 2>&1; then
    PYTHON_BIN="python3"
  fi
  "$PYTHON_BIN" -m venv .venv
  PYTHON=".venv/bin/python"
fi

STAMP_FILE=".venv/.requirements.lock.sha256"
LOCK_HASH="$(sha256sum requirements.lock | cut -d ' ' -f 1)"
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
