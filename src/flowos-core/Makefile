.PHONY: all init format lint build test coverage clean help install dev

# Configurations
VERSION=$(shell grep "^version" pyproject.toml | sed 's/.*\"\(.*\)\"$$/\1/')
DOCKER=podman
GREEN=\033[0;32m
RED=\033[0;31m
NC=\033[0m # No Color

all: help

help: ## show this help message
	@echo '----'
	@grep -hE '^\S+:.*##' $(MAKEFILE_LIST) | \
	awk -F ':.*##' '{printf "\033[36mmake %s\033[0m: %s\n", $$1, $$2}' | \
	column -c2 -t -s :
	@echo '----'

# Development setup
init: ## initialize the project
	@echo "$(GREEN)Installing FLOWOS_CORE dependencies...$(NC)"
	@uv sync --dev
	@echo "$(GREEN)FLOWOS_CORE project initialized.$(NC)"

install: ## install the project dependencies
	@echo "$(GREEN)Installing FLOWOS_CORE dependencies...$(NC)"
	@uv sync

dev: ## install development dependencies
	@echo "$(GREEN)Installing FLOWOS_CORE development dependencies...$(NC)"
	@uv sync --dev

# Code quality
format: dev ## format the code
	@echo "$(GREEN)Formatting FLOWOS_CORE code...$(NC)"
	@uv run ruff check . --fix
	@uv run ruff format .

lint: dev ## run linters
	@echo "$(GREEN)Running FLOWOS_CORE linters...$(NC)"
	@uv run ruff check .

# Testing
test: dev ## run tests
	@echo "$(GREEN)Running FLOWOS_CORE tests...$(NC)"
	@uv run --package flowos_core pytest tests -v $(args)

test_verbose: dev ## run tests with verbose output
	@make test args="-v -s"

coverage: dev ## run tests with coverage
	@echo "$(GREEN)Running FLOWOS_CORE tests with coverage...$(NC)"

	@uv run coverage run -m pytest tests/unit
	@uv run coverage report
	@uv run coverage html

# Building and publishing
build: dev ## build the project
	@echo "$(GREEN)Building FLOWOS_CORE...$(NC)"
	@rm -rf dist/
	@uv build --out-dir dist $(args)
	@echo "$(GREEN)FLOWOS_CORE build completed. Artifacts in dist/$(NC)"

build_wheel: dev ## build wheel only
	@make build args="--wheel"

build_sdist: dev ## build source distribution only
	@make build args="--sdist"

# Publishing
publish: dev ## publish to PyPI
	@echo "$(GREEN)Publishing FLOWOS_CORE to PyPI...$(NC)"
	@uv publish

publish_test: dev ## publish to test PyPI
	@echo "$(GREEN)Publishing FLOWOS_CORE to test PyPI...$(NC)"
	@uv publish --repository testpypi

# Installation testing
install_from_build: dev build ## build and install locally
	@echo "$(GREEN)Installing FLOWOS_CORE from build...$(NC)"
	@uv pip install dist/*.whl --force-reinstall

test_cli: install_from_build ## test the CLI after installation
	@echo "$(GREEN)Testing FLOWOS_CORE CLI...$(NC)"
	@uv run flowos_core --help
	@echo "$(GREEN)CLI test completed.$(NC)"

# Cleanup
clean: ## clean build artifacts
	@echo "$(GREEN)Cleaning FLOWOS_CORE build artifacts...$(NC)"
	@rm -rf dist/
	@rm -rf .coverage
	@rm -rf htmlcov/
	@find . -type d -name '__pycache__' -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name '*.pyc' -delete
	@echo "$(GREEN)Cleanup completed.$(NC)"

# Combined operations
build_and_test: build test_cli ## build and test the package
	@echo "$(GREEN)FLOWOS_CORE build and test completed successfully.$(NC)"

release_check: format lint test build test_cli ## run all checks before release
	@echo "$(GREEN)All FLOWOS_CORE release checks passed!$(NC)"

# Docker operations
docker_build: ## build production Docker image
	@echo "$(GREEN)Building FLOWOS_CORE production Docker image...$(NC)"
	@cd ../.. && $(DOCKER) build -f src/flowos-core/docker/Dockerfile -t flowos_core:latest .

docker_build_dev: ## build development Docker image
	@echo "$(GREEN)Building FLOWOS_CORE development Docker image...$(NC)"
	@cd ../.. && $(DOCKER) build -f src/flowos-core/docker/Dockerfile.dev -t flowos_core:dev .

docker_run: docker_build ## run FLOWOS_CORE in production Docker container
	@echo "$(GREEN)Running FLOWOS_CORE in Docker container...$(NC)"
	@$(DOCKER) run --rm -it flowos_core:latest

docker_dev: docker_build_dev ## run FLOWOS_CORE development environment
	@echo "$(GREEN)Starting FLOWOS_CORE development environment...$(NC)"
	@$(DOCKER) run --rm -it flowos_core:dev

docker_test: docker_build_dev ## run tests in Docker
	@echo "$(GREEN)Running FLOWOS_CORE tests in Docker...$(NC)"
	@$(DOCKER) run --rm flowos_core:dev uv run pytest tests/unit -v

docker_clean: ## clean Docker images and containers
	@echo "$(GREEN)Cleaning FLOWOS_CORE Docker images...$(NC)"
	@$(DOCKER) rmi flowos_core:latest flowos_core:dev 2>/dev/null || true

# Release operations
check_version: ## check current version
	@echo "$(GREEN)Current FLOWOS_CORE version: $(VERSION)$(NC)"

prepare_release: release_check ## prepare for release (run all checks)
	@echo "$(GREEN)FLOWOS_CORE $(VERSION) is ready for release!$(NC)"
	@echo "Next steps:"
	@echo "1. Run: ./scripts/release-flowos-core.sh $(VERSION)"
	@echo "2. Push changes and tag"
	@echo "3. Run GitHub Actions release workflow"

bump_version: ## bump version (usage: make bump_version VERSION=0.1.1)
	@if [ -z "$(VERSION)" ]; then \
		echo "$(RED)Please specify VERSION. Usage: make bump_version VERSION=0.1.1$(NC)"; \
		exit 1; \
	fi
	@echo "$(GREEN)Bumping FLOWOS_CORE version to $(VERSION)...$(NC)"
	@sed -i.bak "s/^version = \".*\"/version = \"$(VERSION)\"/" pyproject.toml
	@rm pyproject.toml.bak
	@echo "$(GREEN)Version bumped to $(VERSION)$(NC)"