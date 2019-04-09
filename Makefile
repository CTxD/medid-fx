test:
	pytest -v --cov=source tests/ --cov-report term --cov-report html --show-capture=no

install:
	python install.py

main:
	python main.py