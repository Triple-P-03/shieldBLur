# ShieldBlur — stage 1

ShieldBlur is a local-first desktop shell that protects copied text. Stage 1
includes a dark PySide6 UI, a Qt-free clipboard guard service, and conservative
regex/context/entropy detection for several common fake-secret shapes. It does
not use a network service, Ollama, screenshots, or cloud storage.

## Requirements

- Python 3.11 or newer (the repository pins the development runtime to 3.11.2)
- A desktop environment for normal Qt display, or `QT_QPA_PLATFORM=offscreen` for
  headless smoke checks

## Setup

Create a virtual environment inside the project and install the pinned runtime
dependency:

```bash
python3.11 -m venv .venv
. .venv/bin/activate
python -m pip install -r requirements.txt
```

The application itself performs all inspection locally. No API keys or service
configuration are required.

## Run

```bash
. .venv/bin/activate
python -m app
```

The frameless shell starts on Dashboard. Copying text while it is running makes
the clipboard adapter scan it; recognized spans are replaced with a marker such
as `[REDACTED: TYPE]`. The remaining navigation pages are labelled placeholders
for later stages.

## Test

The test command has no Qt requirement for the detector and guard coverage and
runs offline:

```bash
python -m unittest discover -s tests -v
# or
make test
```

If PySide6 is installed, the suite also runs a headless Qt clipboard integration
check. Without it, that one integration test is skipped while the pure-Python
checks still run.

## Offline demo

This uses only synthetic, visibly fake values and never touches the system
clipboard:

```bash
python -m demo.redaction_demo
# or
make demo
```

## Docker

Build and run the reproducible desktop image (the default offscreen platform is
suitable for a container smoke run):

```bash
docker build -t shieldblur:stage1 .
docker run --rm shieldblur:stage1
```

A host desktop may set `QT_QPA_PLATFORM` as appropriate when using a desktop
container setup.

## Project layout

- `app/core/` — detector and Qt-free clipboard guard service
- `app/ui/` — PySide6 shell and clipboard signal adapter
- `assets/` — local application artwork and the single editable QSS theme (`shieldblur.qss`)
- `demo/` — offline redaction demonstration
- `tests/` — unit and optional Qt integration tests
