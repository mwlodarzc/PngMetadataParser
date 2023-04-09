.DEFAULT_GOAL := run
.PHONY: run clean

setup: requirements.txt
	pip install -r requirements.txt

run: setup
	python3 parser/parser.py

clean:
	rm -rf parser/__pycache__

