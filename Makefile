.PHONY: run test lint format install clean

install:
	pip install -r requirements.txt

run:
	streamlit run app.py

test:
	pytest tests/ -v

lint:
	flake8 src/ tests/ app.py
	black --check src/ tests/ app.py
	isort --check-only src/ tests/ app.py

format:
	black src/ tests/ app.py
	isort src/ tests/ app.py

clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	rm -rf .pytest_cache htmlcov .coverage
