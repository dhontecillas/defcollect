init:
	pip install pipenv
	pipenv install --dev

test:
	python -m unittest discover -s tests

.PHONY: init test
