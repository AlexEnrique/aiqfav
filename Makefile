.DEFAULT_GOAL := help
.PROJECT_NAME := aiqfav
.API_CONTAINER_NAME := api


.PHONY: .uv
.uv:  ## Checks if uv is installed
	@uv --version || echo 'Please install uv: https://docs.astral.sh/uv/getting-started/installation/'

.PHONY: .pre-commit
.pre-commit: ## Check that pre-commit is installed
	@pre-commit -V || echo 'Please install pre-commit: https://pre-commit.com/'

.PHONY: install
install: .uv .pre-commit  ## Install the project's dependencies and pre-commit hooks
	uv sync
	pre-commit install --install-hooks

.PHONY: dev
dev:  ## Runs the development server
	docker compose up -d --build

.PHONY: down
down:  ## Stops the development server
	docker compose down

.PHONY: restart
restart:  ## Restarts the development server
	docker compose down && docker compose up -d --build

.PHONY: logs
logs:  ## Shows the logs of the development server
	docker compose logs -f

.PHONY: shell
shell:  ## Opens a shell in the development server
	docker compose exec $(.API_CONTAINER_NAME) bash

.PHONY: generate-migration
generate-migration:  ## Generates a new migration
	@if [ -z "$$message" ]; then \
		echo "Error: message is required"; \
		exit 1; \
	fi
	docker compose exec $(.API_CONTAINER_NAME) uv run alembic revision --autogenerate -m "$$message"

.PHONY: migrate
migrate:  ## Runs the alembic migrations
	docker compose exec $(.API_CONTAINER_NAME) uv run alembic upgrade head

.PHONY: format
format: ## Format the code
	uv run ruff format $(.PROJECT_NAME) --target-version py312
	uv run ruff check $(.PROJECT_NAME) --fix --fix-only

.PHONY: typecheck
typecheck: ## Typecheck the code
	uv run pyright $(.PROJECT_NAME)

.PHONY: lint
lint: ## Lint the code
	uv run ruff format $(.PROJECT_NAME) --check
	uv run ruff check $(.PROJECT_NAME) --fix

.PHONY: all
all: format lint typecheck ## Run format, lint and typecheck

.PHONY: help
help: ## Show this help message
	@echo "Usage: make [target]"
	@echo "Targets:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf " - \033[36m%-30s\033[0m %s\n", $$1, $$2}'
