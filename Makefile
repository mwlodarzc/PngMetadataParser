.DEFAULT_GOAL := run
.PHONY: run clean

setup: requirements.txt
	pip3 install -r "requirements.txt"

run: setup
	python parser/parser.py

clean:
	rm -rf parser/__pycache__

