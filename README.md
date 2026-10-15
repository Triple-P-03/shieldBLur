# ShieldBlur

## Current status: Stage 1 ready

ShieldBlur is a Windows-focused, local-first desktop privacy guard. The current
build is **Stage 1**: it provides a working PySide6 desktop shell and a local
clipboard guard that detects several recognizable secret-shaped values and
replaces them before the clipboard can be shared by another application.

This is **not yet the complete roadmap application**. Protected-folder learning,
screenshot OCR/blur, Ollama/Gemma analysis, file watching, the persistent event
log, the live overlay, and the installer are planned for later stages.

The current implementation is committed at:

```text
53fa819 feat: add clipboard guard and dark UI shell
```

## Quick answer: do I need a Gemma key?

**No. Stage 1 does not use Gemma, Ollama, Tesseract, or any cloud API.** You do
not need an API key, account, cloud service, or internet connection at runtime.

The current `requirements.txt` installs only PySide6 from the exact pins in
`requirements.lock`. The later Gemma stage is designed to call Ollama at
`http://localhost:11434`, which is a local service;
that integration is not present yet and would not require a paid API key. An
Ollama model download would require internet access once, unless the model was
already available locally, but the model would run on the user's computer.

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
- Ollama/Gemma text classification or Gemma vision review
- Live click-through screen-share overlay
- First-run Ollama/Tesseract setup wizard
- System tray pause/resume controls
- PyInstaller executable and Inno Setup installer

The Dashboard navigation already includes placeholder pages for these future
areas so the UI shape is ready for subsequent work.

## Reproducibility checklist

The repository includes all eight buildathon reproducibility requirements:

- [x] Git repository with commits (`git log --oneline`)
- [x] Dependency lockfile (`requirements.lock` with exact PySide6 pins)
- [x] Pinned runtime version (`.python-version`, Python 3.11.2)
- [x] Dockerfile that installs dependencies and runs `python -m app`
- [x] One offline test command (`python -m unittest discover -s tests -v`; also
  available as `make test`)
- [x] README with setup, run, test, privacy, and deployment guidance
- [x] `.env.example` contains only non-secret local configuration placeholders;
  `.env` is ignored by Git
- [x] No machine-specific absolute paths or credentials are stored in tracked
  source files

The Dockerfile is intended for Linux/offscreen smoke runs. Native Windows is
the supported environment for real clipboard protection.

## Start ShieldBlur with one command

Prerequisites: Windows 10/11, Python 3.11+ installed with the `py` launcher, and
a normal interactive desktop session. No administrator access, Gemma key, Ollama
installation, Tesseract installation, or account is required for Stage 1.
Python 3.11.2 is the pinned development version in `.python-version`.

The repository includes a bootstrap launcher. Open PowerShell in the project
folder and run this single command:

```powershell
.\run.bat
```

You can also run the PowerShell launcher directly:

```powershell
powershell -ExecutionPolicy Bypass -File .\run.ps1
```

That command will:

1. Check for Python 3.11+ through the Windows `py` launcher.
2. Create the project-local `.venv` if it does not exist.
3. Install the exact versions from `requirements.lock` when the lockfile has
   changed or dependencies have not been installed yet.
4. Start ShieldBlur with `python -m app`.

The dependency hash is stored only inside the ignored `.venv` directory, so
subsequent launches do not reinstall unchanged dependencies. The first launch
needs internet access only to download the open-source PySide6 wheels. After
that, the application itself makes no network calls.

### One-command Windows actions

```powershell
# Start the desktop app
.\run.bat

# Run the complete offline test suite
.\run.bat -Mode test

# Run the synthetic clipboard-redaction demo without touching the real clipboard
.\run.bat -Mode demo
```

No Gemma key, Ollama installation, Tesseract installation, administrator
rights, or account is required for any of these Stage 1 commands.

### Manual Windows setup

The launcher is the recommended path. If you prefer to manage the environment
manually, open PowerShell in the ShieldBlur project folder:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m app
```

If PowerShell activation is blocked, use the environment's interpreter directly:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m app
```

### Try the Stage 1 flow

Use only synthetic values while testing. For example, copy this visibly fake
sample into a text editor:

```text
build_token=AKIA1234567890ABCDEF
```

The clipboard should become similar to:

```text
build_token=[REDACTED: AWS ACCESS KEY]
```

You can also copy ordinary text such as:

```text
The release review is at 3 PM.
```

That text should remain unchanged. The Dashboard counters should increase only
when clipboard text is scanned, and the redaction counters should increase when
a match is found.

## Run the offline demo

The demo does not touch the system clipboard. It uses only synthetic, fake
values and prints the input/output transformation:

```powershell
.\run.bat -Mode demo
```

The equivalent direct command after installing dependencies is:

```powershell
.\.venv\Scripts\python.exe -m demo.redaction_demo
```

Expected output includes a plain sentence that stays unchanged and fake
secret-shaped values replaced with `[REDACTED: ...]` markers.

## Run tests

The test suite is offline and uses only fake values. The recommended single
command is:

```powershell
.\run.bat -Mode test
```

After manually activating the virtual environment, the direct command is:

```powershell
python -m unittest discover -s tests -v
```

On Linux/macOS, the repository also provides:

```bash
make test
```

The tests cover detector formats, entropy/context behavior, placeholder
handling, redaction output, counters, multiple matches, and the Qt clipboard
bridge's loop protection. PySide6 must be installed for the Qt integration test;
without it, only that optional integration test is skipped.

A compile-only check is also useful:

```powershell
python -m compileall -q app demo tests
```

## Linux/headless development

The target is Windows, but the repository also includes a one-command Linux
launcher. It creates `.venv`, installs the locked dependencies, and starts the
offscreen-compatible application:

```bash
./run.sh
```

Other Linux launcher modes are:

```bash
./run.sh test
./run.sh demo
```

For a visible Linux desktop, run from the desktop session normally. If no
display variables are present, `run.sh` selects Qt's offscreen backend. An
offscreen run verifies startup but cannot provide a normal interactive system
clipboard or visible desktop window.

## Technology stack

### Used in Stage 1

| Area | Technology | Purpose |
| --- | --- | --- |
| Runtime | Python 3.11+ | Application language and runtime |
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
| Local AI | Ollama + Gemma 4 (`gemma4:e2b` default, up to `gemma4:e4b`) | Classify ambiguous values and review screenshot regions locally |
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
├── Dockerfile
├── Makefile
├── run.bat                     # One-command Windows entry point
├── run.ps1                     # Windows bootstrap/run/test/demo implementation
├── run.sh                      # One-command Linux bootstrap/run/test/demo
├── requirements.txt            # Install entry point
├── requirements.lock           # Exact dependency versions
├── .env.example                # Non-secret local settings template
└── .python-version
```

## Docker smoke environment

A stage-one Dockerfile is included for reproducible Linux/offscreen checks:

```bash
docker build -t shieldblur:stage1 .
docker run --rm shieldblur:stage1
```

Docker is not the normal way to use Windows clipboard protection because a
container does not automatically share the host's interactive clipboard or
Windows desktop. Use the native Python setup for the real desktop experience.

## Troubleshooting

### `No module named PySide6`

The app is being started with a Python interpreter that does not have the
project dependencies. Activate the virtual environment or use its interpreter
explicitly:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m app
```

### The app starts but does not modify copied text

Confirm that the ShieldBlur window is still running and that the copy operation
happens after the app starts. Stage 1 watches clipboard changes only while its
process is active; it does not scan clipboard history.

### The window does not appear in a server or CI session

A normal desktop session is required. For a startup smoke check on a headless
Linux machine, use `QT_QPA_PLATFORM=offscreen` as shown above.

## Next stage

The next implementation stage is protected-source policy and folder scanning.
That stage will add editable protected folders/files/process names and hash-only
learning without storing plaintext secret values. No Gemma setup is required
until the later local-AI integration stage.
#   s h i e l d B L u r 
 
 