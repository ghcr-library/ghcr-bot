PYTHON=./venv/bin/python
PIP=./venv/bin/pip


venv: requirements.txt
	python3 -m venv venv
	$(PIP) install -r requirements.txt
	touch venv


pull_and_push: venv
	$(PYTHON) ghcr_bot/run.py
	@echo 'Pull-and-Push Job is Finished'


build_sources: venv
	$(PYTHON) ghcr_bot/gen_sources.py $(shell cat all_images)
