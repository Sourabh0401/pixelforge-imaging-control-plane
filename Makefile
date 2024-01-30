PYTHON := python
PYTHONPATH := src:tests

.PHONY: test coverage lint examples clean

test:
	PYTHONPATH=$(PYTHONPATH) $(PYTHON) -m unittest discover -s tests -q

coverage:
	PYTHONPATH=$(PYTHONPATH) $(PYTHON) -m coverage run --source=src -m unittest discover -s tests -q
	$(PYTHON) -m coverage report --fail-under=85

lint:
	PYTHONPATH=$(PYTHONPATH) $(PYTHON) -m compileall -q src tests scripts

examples:
	PYTHONPATH=$(PYTHONPATH) $(PYTHON) scripts/bootstrap_examples.py

clean:
	rm -rf .pytest_cache .coverage htmlcov .mypy_cache .ruff_cache runtime
	find . -type d -name "__pycache__" -prune -exec rm -rf {} +
	find . -name "*.pyc" -delete
