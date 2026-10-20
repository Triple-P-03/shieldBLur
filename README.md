# ShieldBlur

## Current status: Stage 1 ready

ShieldBlur is a Windows-focused, local-first desktop privacy guard. The current
build is **Stage 1**: it provides a working PySide6 desktop shell and a local
clipboard guard that detects several recognizable secret-shaped values and
replaces them before the clipboard can be shared by another application.

This is **not yet the complete roadmap application**. Protected-folder learning,
screenshot OCR/blur, Ollama analysis, file watching, the persistent event log,
the live overlay, and the installer are planned for later stages.

## Quick answer: do I need a Gemma key?

**No. Stage 1 does not use Gemma, Ollama, Tesseract, or any cloud API.** You do
not need an API key, account, cloud service, or internet connection while the
installed application is running.

The current `requirements.txt` installs only the PySide6 package family from the
exact pins in `requirements.lock`. A later local-AI stage may call Ollama at
`http://localhost:11434`; that integration is not present yet and would not
require a paid API key. An Ollama model download would require internet access
once, unless the model was already available locally.

## What works now

When ShieldBlur is running:

1. A user copies text in any desktop application.
2. ShieldBlur receives the local clipboard change.
3. The text is checked locally using format, context, and entropy detection.
4. Recognized secret spans are replaced in the clipboard with a marker such as:

   ```text
   [REDACTED: AWS ACCESS KEY]
   ```

5. The Dashboard counters and recent activity update.
6. A small local toast explains what category was masked. The Details action
   shows the category and detection evidence, never the original value.

Implemented Stage 1 detection includes:

- AWS-style access keys
- GitHub-style tokens
- Slack-style tokens
- Stripe-style secret keys
- Google API keys
- JWT-shaped values
- PEM private-key blocks
- Context-labelled high-entropy values near names such as `token`, `password`,
  `secret`, `credential`, `api_key`, and `access_key`
- Obvious placeholders such as `your-api-key` and `changeme` are not treated as
  secrets by the context detector

The guard preserves ordinary copied text byte-for-byte and handles multiple
recognized values in one clipboard item.

## What is not implemented yet

These features belong to later stages and should not be represented as active
protection in the current build:

- Protected folders, protected files, and protected process-name policy
- Scanning `.env`, configuration, and text files
- SHA-256 learning and hash-only protected secret storage
- SQLite event history and source-app attribution
- Screenshot capture with `mss`
- OCR with Tesseract and positional blur with OpenCV/Pillow
- Screenshot-folder watching with `watchdog`
- Ollama text classification or local vision review
- Live click-through screen-share overlay
- First-run Ollama/Tesseract setup wizard
- System tray pause/resume controls
- PyInstaller executable and Inno Setup installer

The Dashboard navigation already includes placeholder pages for these future
areas so the UI shape is ready for subsequent work.

## Reproducibility inputs

The repository keeps the inputs needed to reproduce the Stage 1 development and
smoke-test environment:

- `.python-version` pins the development runtime to Python 3.11.2.
- `requirements.lock` pins the PySide6 package family to 6.8.2.1.
- `Makefile` exposes the offline unit-test command on Linux and macOS.
- `Dockerfile` pins the Python 3.11.2 Bookworm base image, installs the locked
  dependencies, and defaults to a finite offscreen test run.
- `.dockerignore` excludes local virtual environments, generated files, and
  local environment values from the Docker build context.
- `.env.example` contains placeholders only. A real `.env` is ignored by Git.

The container is a Linux/offscreen verification environment. Native Windows is
the supported environment for real clipboard protection.

## Setup

### Windows desktop setup

Prerequisites are Windows 10/11, Python 3.11 installed with the `py` launcher,
and a normal interactive desktop session. The first setup needs internet access
to download the pinned PySide6 wheels. Later application runs and tests do not
need network access once the virtual environment is populated.

The repository includes a bootstrap launcher. Open PowerShell in the project
folder and run:

```powershell
.\run.bat
```

The launcher creates the project-local `.venv`, installs the exact versions from
`requirements.lock` when needed, and starts the desktop application. It does
not install anything globally.

You can also invoke the PowerShell launcher directly:

```powershell
powershell -ExecutionPolicy Bypass -File .\run.ps1
```

For a manual setup, use the pinned Python interpreter and the lockfile:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\python.exe -m pip install --requirement requirements.lock
```

If PowerShell activation is permitted, these equivalent commands are shorter:

```powershell
.\.venv\Scripts\Activate.ps1
python -m pip install --requirement requirements.lock
```

### Linux or macOS development setup

Python 3.11 and a virtual-environment module are required. From the repository
root, install the locked dependencies into the project-local environment:

```bash
python3.11 -m venv .venv
.venv/bin/python -m pip install --requirement requirements.lock
```

The existing `run.sh` launcher is also available. Its first invocation may
install the lockfile if `.venv` is absent or its lock hash is stale:

```bash
./run.sh run
```

The desktop command is intentionally long-running. For a headless machine,
`run.sh` selects Qt's offscreen backend, but an offscreen GUI is only a startup
check and cannot provide a normal interactive window or host clipboard.

Stage 1 does not read `.env.example`; it documents future local-AI settings and
must not contain real credentials.

## Run the desktop GUI

The GUI keeps running until its window is closed or the process is interrupted.
Start it separately from finite verification commands:

```powershell
# Windows
.\run.bat
```

```bash
# Linux/macOS, after setup
.venv/bin/python -m app
# or
./run.sh run
```

Docker does not provide the host's Windows clipboard or an interactive desktop,
so the Docker image deliberately does not start this command by default. Use a
native desktop session for the real clipboard-protection flow.

## Offline tests and demo

After the dependencies have been installed, the canonical finite test command
is:

```bash
python -m unittest discover -s tests -v
```

Run it with the virtual environment active, or call its interpreter directly:

```bash
.venv/bin/python -m unittest discover -s tests -v
```

On Linux and macOS, the Makefile provides the same command:

```bash
make test
```

The test suite uses only synthetic values. It covers detector formats,
entropy/context behavior, placeholder handling, redaction output, counters,
multiple matches, and the Qt clipboard bridge's loop protection. The Qt test
uses the offscreen platform in headless environments. No test command makes
HTTP requests or downloads dependencies; install the lockfile once during setup
before running tests offline.

An offline demonstration that does not touch the system clipboard is available:

```bash
.venv/bin/python -m demo.redaction_demo
```

Windows users can use the launcher modes instead:

```powershell
.\run.bat -Mode test
.\run.bat -Mode demo
```

The demo uses clearly fake values and prints the input/output transformation.

A compile-only check is also useful:

```bash
.venv/bin/python -m compileall -q app demo tests
```

## Docker smoke test

The Dockerfile is for reproducible Linux/offscreen checks, not for the native
Windows clipboard experience. Build the image from the repository root:

```bash
docker build --pull=false -t shieldblur:stage1 .
```

The first build needs access to the configured container registry, Debian
package repositories, and Python package index unless those inputs are already
cached locally. `--pull=false` prevents Docker from refreshing an already cached
base image. The Python base version and application dependency versions are
explicitly pinned in the Dockerfile and lockfile.

Run the image with networking disabled to verify that runtime tests do not rely
on network access:

```bash
docker run --rm --network none shieldblur:stage1
```

The default command is finite:
`python -m unittest discover -s tests -v`. It exits with the test result and is
suitable for CI or automated smoke verification. The image sets
`QT_QPA_PLATFORM=offscreen` and includes the Linux Qt runtime libraries needed
by the tests.

The demo can be run without rebuilding the image:

```bash
docker run --rm --network none --entrypoint python shieldblur:stage1 -m demo.redaction_demo
```

Do not use `docker run` as the Windows GUI deployment method. Containers do not
automatically share a Windows host clipboard or desktop session.

## Deployment and packaging guidance

Stage 1 is a local desktop application, not a server and not a hosted service.
The supported deployment path is a source checkout on the target desktop with
Python 3.11, the locked dependencies installed into a project-local virtual
environment, and the native GUI launcher used to start the process.

For a source release, create an archive from the tracked repository state:

```bash
git archive --format=tar.gz --output=shieldblur-stage1.tar.gz HEAD
```

The archive does not include `.venv`, cache files, `.env`, or generated build
artifacts. Install from `requirements.lock` on the target machine rather than
copying a virtual environment between operating systems.

The Docker image is a portable smoke-test artifact. It can be saved and loaded
on another Docker host for verification:

```bash
docker save --output shieldblur-stage1.tar shieldblur:stage1
docker load --input shieldblur-stage1.tar
```

That image remains a headless test artifact; it is not a Windows clipboard
package. A standalone Windows executable and Inno Setup installer are not
implemented in Stage 1, so no `.exe` or installer should be advertised as a
current release artifact. PyInstaller and Inno Setup are planned for a later
packaging stage.

## Technology stack

### Used in Stage 1

| Area | Technology | Purpose |
| --- | --- | --- |
| Runtime | Python 3.11.2 | Application language and runtime |
| Desktop UI | PySide6 6.8.2.1 | Qt window, widgets, signals, and clipboard access |
| UI styling | Qt Style Sheets (QSS) | Single editable dark theme in `assets/shieldblur.qss` |
| Detection | Python `re`, `math`, `collections`, `dataclasses` | Format matching, entropy scoring, and match metadata |
| Clipboard integration | `QClipboard` through PySide6 | Observe changes and replace detected text |
| Tests | Python `unittest` | Offline unit and integration tests |
| Packaging preparation | Dockerfile, Makefile, `.python-version` | Reproducible development and smoke-test setup |

### Planned for later stages

These technologies are part of the requested architecture but are **not yet
installed or active in Stage 1**:

| Area | Technology | Planned purpose |
| --- | --- | --- |
| Screen capture | `mss` | Capture a selected screen or hotkey screenshot |
| Image processing | `opencv-python`, Pillow | Blur, pixelate, and write safe screenshots |
| OCR | Tesseract through `pytesseract` | Locate text and secret spans by word position |
| Local AI | Ollama and a future local model | Classify ambiguous values and review screenshot regions locally |
| File watching | `watchdog` | Detect new images in a protected Screenshots folder |
| Storage | SQLite via Python `sqlite3` | Store policy, hash metadata, and non-secret event records |
| Windows packaging | PyInstaller | Produce a standalone executable |
| Installer | Inno Setup | Produce a Windows installer |

No paid libraries, cloud APIs, accounts, or remote storage are used by the
implemented Stage 1 code.

## Privacy and security behavior

- Stage 1 performs detection in the local Python process.
- No HTTP requests are made by the current application.
- No Ollama or external network connection is attempted.
- No clipboard text is written to a database, file, log, or analytics service.
- The service keeps only in-memory counters while the app is running.
- Toast details contain detection categories and evidence labels, not secret
  values.
- The original clipboard text remains in memory only as part of processing and
  is not intentionally retained after the guard result is handled.
- The application is not a kernel-level Data Loss Prevention product. A source
  application and the operating system may briefly hold the original clipboard
  value before ShieldBlur receives the clipboard-change signal.
- Detection is pattern-based and conservative. It can miss unknown formats or
  produce false positives for high-entropy values near secret-related words.

For production use, users should still rotate exposed credentials and follow
organizational security policy. ShieldBlur is a local sharing safeguard, not a
replacement for secret management, endpoint security, or access revocation.

## Current project layout

```text
Shieldbur/
├── app/
│   ├── __main__.py              # `python -m app` entry point
│   ├── core/
│   │   ├── detectors.py         # Local secret detection and redaction
│   │   ├── guard.py             # Qt-free clipboard guard service
│   │   └── settings.py          # Stage 1 app/page constants
│   └── ui/
│       ├── clipboard_bridge.py  # QClipboard signal adapter
│       ├── main_window.py       # Frameless dashboard shell
│       └── styles.py            # Loads the QSS theme
├── assets/
│   ├── shieldblur-mark.svg      # Local app mark
│   └── shieldblur.qss           # Single editable UI stylesheet
├── demo/
│   └── redaction_demo.py        # Offline demonstration
├── tests/
│   ├── test_detectors.py
│   ├── test_guard.py
│   └── test_clipboard_bridge.py
├── Dockerfile                   # Headless finite smoke-test image
├── .dockerignore                # Build-context exclusions
├── Makefile
├── run.bat                      # One-command Windows entry point
├── run.ps1                      # Windows bootstrap/run/test/demo implementation
├── run.sh                       # One-command Linux bootstrap/run/test/demo
├── requirements.txt             # Install entry point
├── requirements.lock            # Exact dependency versions
├── .env.example                 # Non-secret future settings template
└── .python-version              # Python 3.11.2 pin
```

## Troubleshooting

### `No module named PySide6`

The application is being started with a Python interpreter that does not have
the project dependencies. Install the lockfile into the project-local virtual
environment and use that interpreter explicitly:

```powershell
.\.venv\Scripts\python.exe -m pip install --requirement requirements.lock
.\.venv\Scripts\python.exe -m app
```

On Linux/macOS, use the corresponding `.venv/bin/python` path.

### The app starts but does not modify copied text

Confirm that the ShieldBlur window is still running and that the copy operation
happens after the app starts. Stage 1 watches clipboard changes only while its
process is active; it does not scan clipboard history.

### The window does not appear in a server or CI session

A normal desktop session is required for an interactive GUI. For a finite
headless verification, run the unittest command or the Docker smoke command
above. Setting `QT_QPA_PLATFORM=offscreen` can verify Qt startup, but it cannot
provide a visible window or a normal interactive system clipboard.

## Next stage

The next implementation stage is protected-source policy and folder scanning.
That stage will add editable protected folders/files/process names and hash-only
learning without storing plaintext secret values. No local-AI setup is required
until the later Ollama integration stage.
