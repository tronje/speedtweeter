NAME = speedtweeter.py

.PHONY: default run deps clean

default: deps

run: venv
	@venv/bin/python $(NAME)

venv:
	python -m venv venv

deps: requirements.txt venv
	venv/bin/pip install --upgrade -r requirements.txt

clean:
	rm -rf venv
