.PHONY: install lint test run docker

install:
	pip install -r requirements.txt

lint:
	ruff check .

test:
	pytest -q

run:
	uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

docker:
	docker compose up --build
