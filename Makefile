.PHONY: up down lint

up:
	docker compose up --build -d

down:
	docker compose down

lint:
	ansible-lint ansible
	flake8 ui
