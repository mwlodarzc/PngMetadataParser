.DEFAULT_GOAL := run
.PHONY: run clean

setup: requirements.txt
	pip install -r requirements.txt

run: setup
	python3 src/parser.py

clean:
	rm -rf __pycache__

