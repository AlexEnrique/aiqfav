.DEFAULT_GOAL := help


.PHONY: dev
dev:  ## Runs the development server
	uv run uvicorn src.api.app:app --host=0.0.0.0 --reload


.PHONY: format
format: ## Format the code
	uv run ruff format src --target-version py312
	uv run ruff check src --fix --fix-only

.PHONY: typecheck
typecheck: ## Typecheck the code
	uv run pyright src

.PHONY: lint
lint: ## Lint the code
	uv run ruff format src --check
	uv run ruff check src --fix

.PHONY: all
all: format lint typecheck ## Run format, lint and typecheck 

.PHONY: help
help: ## Show this help message
	@echo "Usage: make [target]"
	@echo "Targets:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf " - \033[36m%-30s\033[0m %s\n", $$1, $$2}'
