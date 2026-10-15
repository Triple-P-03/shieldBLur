PYTHON ?= python3

.PHONY: test run demo

test:
	$(PYTHON) -m unittest discover -s tests -v

run:
	$(PYTHON) -m app

demo:
	$(PYTHON) -m demo.redaction_demo
