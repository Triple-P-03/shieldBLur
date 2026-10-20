PYTHON_VERSION := $(strip $(shell if [ -r .python-version ]; then tr -d '\r\n' < .python-version; fi))
PYTHON ?= $(if $(wildcard .venv/bin/python),.venv/bin/python,$(if $(wildcard .venv/Scripts/python.exe),.venv/Scripts/python.exe,python3.11))

.PHONY: check-python test run demo

check-python:
	@if [ "$(PYTHON_VERSION)" = "3.11.2" ]; then :; else \
		printf 'This project requires the pinned Python 3.11.2 runtime; found pin: %s\n' "$(PYTHON_VERSION)" >&2; \
		exit 1; \
	fi
	@command -v "$(PYTHON)" >/dev/null 2>&1 || { \
		printf 'Python %s is required; install it or set PYTHON to that compatible interpreter.\n' "$(PYTHON_VERSION)" >&2; \
		exit 1; \
	}
	@"$(PYTHON)" -c 'import sys; expected=(3, 11, 2); actual=sys.version_info[:3]; sys.exit("Python 3.11.2 is required (found %s.%s.%s)." % actual) if actual != expected else None'

test: check-python
	@QT_QPA_PLATFORM=offscreen "$(PYTHON)" -m unittest discover -s tests -v

run: check-python
	$(PYTHON) -m app

demo: check-python
	$(PYTHON) -m demo.redaction_demo
