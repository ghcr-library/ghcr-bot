PYTHON=./venv/bin/python
PIP=./venv/bin/pip


venv: requirements.txt
	python3 -m venv venv
	$(PIP) install -r requirements.txt


pull_and_push:
	$(PYTHON) ghcr_bot/run.py
	@echo 'Pull-and-Push Job is Finished'
