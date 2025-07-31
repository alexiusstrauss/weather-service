.PHONY: help create-env install clean devstack run run-dev run-worker test test-all lint format

# Colors
BLUE := \033[36m
GREEN := \033[32m
YELLOW := \033[33m
RED := \033[31m
RESET := \033[0m

# Project info
PROJECT_NAME := Weather Service API
VERSION := 0.1.0
DATABASE := PostgreSQL

help: ## Show available commands
	@echo "$(BLUE)$(PROJECT_NAME) v$(VERSION)$(RESET)"
	@echo "Database: $(DATABASE)"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "$(GREEN)%-15s$(RESET) %s\n", $$1, $$2}'

create-env: ## Create virtual environment with Python version from pyproject.toml
	@echo "$(BLUE)Creating virtual environment...$(RESET)"
	@# Check if pyenv is installed
	@if ! command -v pyenv &> /dev/null; then \
		echo "$(RED)pyenv not found. Please install pyenv first.$(RESET)"; \
		exit 1; \
	fi
	@# Check if poetry is installed
	@if ! command -v poetry &> /dev/null; then \
		echo "$(RED)Poetry not found. Please install poetry first.$(RESET)"; \
		exit 1; \
	fi
	@# Create a temporary script to handle the complex logic
	@echo '#!/bin/bash' > .create_env_script.sh
	@echo 'set -e' >> .create_env_script.sh
	@echo 'BLUE="\033[36m"' >> .create_env_script.sh
	@echo 'GREEN="\033[32m"' >> .create_env_script.sh
	@echo 'YELLOW="\033[33m"' >> .create_env_script.sh
	@echo 'RED="\033[31m"' >> .create_env_script.sh
	@echo 'RESET="\033[0m"' >> .create_env_script.sh
	@echo '' >> .create_env_script.sh
	@echo '# Extract Python version from pyproject.toml' >> .create_env_script.sh
	@echo 'PYTHON_BASE_VERSION=$$(grep "python = " pyproject.toml | cut -d"\"" -f2 | sed "s/\\^//" | sed "s/~//")' >> .create_env_script.sh
	@echo 'echo "$${BLUE}Required Python base version: $$PYTHON_BASE_VERSION$${RESET}"' >> .create_env_script.sh
	@echo '' >> .create_env_script.sh
	@echo '# Check if we have a matching Python version installed' >> .create_env_script.sh
	@echo 'PYTHON_VERSION=$$(pyenv versions --bare | grep "^$$PYTHON_BASE_VERSION" | sort -V | tail -1)' >> .create_env_script.sh
	@echo '' >> .create_env_script.sh
	@echo 'if [ -z "$$PYTHON_VERSION" ]; then' >> .create_env_script.sh
	@echo '    echo "$${YELLOW}No local Python $$PYTHON_BASE_VERSION found. Finding latest available version...$${RESET}"' >> .create_env_script.sh
	@echo '    PYTHON_VERSION=$$(pyenv install --list | grep -E "^\\s*$$PYTHON_BASE_VERSION\\.[0-9]+$$" | tail -1 | tr -d " ")' >> .create_env_script.sh
	@echo '    if [ -z "$$PYTHON_VERSION" ]; then' >> .create_env_script.sh
	@echo '        echo "$${RED}No Python $$PYTHON_BASE_VERSION version available$${RESET}"' >> .create_env_script.sh
	@echo '        exit 1' >> .create_env_script.sh
	@echo '    fi' >> .create_env_script.sh
	@echo '    echo "$${YELLOW}Installing Python $$PYTHON_VERSION...$${RESET}"' >> .create_env_script.sh
	@echo '    pyenv install $$PYTHON_VERSION' >> .create_env_script.sh
	@echo '    echo "$${GREEN}Python $$PYTHON_VERSION installed successfully$${RESET}"' >> .create_env_script.sh
	@echo 'else' >> .create_env_script.sh
	@echo '    echo "$${GREEN}Using existing Python $$PYTHON_VERSION$${RESET}"' >> .create_env_script.sh
	@echo 'fi' >> .create_env_script.sh
	@echo '' >> .create_env_script.sh
	@echo '# Set local Python version' >> .create_env_script.sh
	@echo 'echo "$${BLUE}Setting local Python version to $$PYTHON_VERSION...$${RESET}"' >> .create_env_script.sh
	@echo 'pyenv local $$PYTHON_VERSION' >> .create_env_script.sh
	@echo '' >> .create_env_script.sh
	@echo '# Remove existing virtual environment if it exists' >> .create_env_script.sh
	@echo 'if [ -d ".venv" ]; then' >> .create_env_script.sh
	@echo '    echo "$${YELLOW}Removing existing .venv directory...$${RESET}"' >> .create_env_script.sh
	@echo '    rm -rf .venv' >> .create_env_script.sh
	@echo 'fi' >> .create_env_script.sh
	@echo '' >> .create_env_script.sh
	@echo '# Configure Poetry' >> .create_env_script.sh
	@echo 'echo "$${BLUE}Configuring Poetry...$${RESET}"' >> .create_env_script.sh
	@echo 'poetry config virtualenvs.in-project true' >> .create_env_script.sh
	@echo 'poetry env remove --all 2>/dev/null || true' >> .create_env_script.sh
	@echo '' >> .create_env_script.sh
	@echo '# Create virtual environment' >> .create_env_script.sh
	@echo 'echo "$${BLUE}Creating virtual environment with Python $$PYTHON_VERSION...$${RESET}"' >> .create_env_script.sh
	@echo 'poetry env use $$PYTHON_VERSION' >> .create_env_script.sh
	@echo '' >> .create_env_script.sh
	@echo '# Install dependencies' >> .create_env_script.sh
	@echo 'echo "$${BLUE}Installing dependencies...$${RESET}"' >> .create_env_script.sh
	@echo 'poetry install --no-root' >> .create_env_script.sh
	@echo '' >> .create_env_script.sh
	@echo '# Success message' >> .create_env_script.sh
	@echo 'echo "$${GREEN}╔══════════════════════════════════════════════════════════════════════╗$${RESET}"' >> .create_env_script.sh
	@echo 'echo "$${GREEN}║                    Environment created successfully!                 ║$${RESET}"' >> .create_env_script.sh
	@echo 'echo "$${GREEN}╚══════════════════════════════════════════════════════════════════════╝$${RESET}"' >> .create_env_script.sh
	@echo 'echo "$${YELLOW}Python version: $$PYTHON_VERSION$${RESET}"' >> .create_env_script.sh
	@echo 'echo "$${YELLOW}Virtual environment: .venv$${RESET}"' >> .create_env_script.sh
	@echo 'echo "$${YELLOW}To activate environment, run: poetry shell$${RESET}"' >> .create_env_script.sh
	@chmod +x .create_env_script.sh
	@./.create_env_script.sh
	@rm -f .create_env_script.sh

install: create-env

build: ## Build Docker images
	@echo "$(BLUE)Building Docker images...$(RESET)"
	@docker-compose -f docker/docker-compose.yml build
	@echo "$(GREEN)Docker images built successfully!$(RESET)"

clean:
	@echo "$(BLUE)Cleaning repository...$(RESET)"
	@find . -type f -name "*.pyc" -delete
	@find . -type d -name "__pycache__" -delete
	@find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	@find . -name "*.db" -delete 2>/dev/null || true
	@rm -rf .coverage htmlcov/ .pytest_cache/ celerybeat-schedule.db
	@rm -rf .ruff_cache
	@echo "$(GREEN)Repository cleaned successfully!$(RESET)"

devstack: ## Start development stack (PostgreSQL, Redis, RedisInsight, Prometheus, Grafana)
	@echo "$(BLUE)Starting development stack...$(RESET)"
	@docker-compose -f docker/docker-compose.yml up -d db redis redisinsight prometheus grafana
	@echo "$(GREEN)Development stack started!$(RESET)"

run-dev: ## Run API locally (without Celery)
	@echo "$(BLUE)Starting API server...$(RESET)"
	@poetry run python manage.py migrate --run-syncdb
	@poetry run python manage.py runserver 0.0.0.0:8000

run-worker: ## Run Celery worker and beat scheduler
	@echo "$(BLUE)Starting Celery worker and beat scheduler...$(RESET)"
	@poetry run celery -A weather_service worker -l info --detach
	@poetry run celery -A weather_service beat -l info

run: build ## Run complete stack (devstack + API + Celery)
	@echo "$(BLUE)╔══════════════════════════════════════════════════════════════════════╗$(RESET)"
	@echo "$(BLUE)║                    $(PROJECT_NAME) v$(VERSION)                       ║$(RESET)"
	@echo "$(BLUE)╚══════════════════════════════════════════════════════════════════════╝$(RESET)"
	@echo ""
	@echo "$(YELLOW)🚀 Starting services...$(RESET)"
	@echo "$(BLUE)   ├─ Starting PostgreSQL...$(RESET)"
	@docker-compose -f docker/docker-compose.yml up -d db
	@echo "$(BLUE)   ├─ Starting Redis...$(RESET)"
	@docker-compose -f docker/docker-compose.yml up -d redis
	@echo "$(BLUE)   ├─ Starting RedisInsight...$(RESET)"
	@docker-compose -f docker/docker-compose.yml up -d redisinsight
	@echo "$(BLUE)   ├─ Starting Prometheus...$(RESET)"
	@docker-compose -f docker/docker-compose.yml up -d prometheus
	@echo "$(BLUE)   ├─ Starting Grafana...$(RESET)"
	@docker-compose -f docker/docker-compose.yml up -d grafana
	@echo "$(BLUE)   ├─ Starting API...$(RESET)"
	@docker-compose -f docker/docker-compose.yml up -d api
	@echo "$(BLUE)   ├─ Starting Celery Worker...$(RESET)"
	@docker-compose -f docker/docker-compose.yml up -d celery
	@echo "$(BLUE)   └─ Starting Celery Beat (Scheduler)...$(RESET)"
	@docker-compose -f docker/docker-compose.yml up -d celery-beat
	@echo ""
	@echo "$(GREEN)✅ All services started successfully!$(RESET)"
	@echo ""
	@echo "$(YELLOW)📋 Service Information:$(RESET)"
	@echo "$(BLUE)   Project:$(RESET)     $(PROJECT_NAME) v$(VERSION)"
	@echo "$(BLUE)   Database:$(RESET)    $(DATABASE) (localhost:5432)"
	@echo ""
	@echo "$(YELLOW)🌐 Available Endpoints:$(RESET)"
	@echo "$(BLUE)   API Swagger:$(RESET)     http://localhost:8000/api/docs/"
	@echo "$(BLUE)   API Metrics:$(RESET)     http://localhost:8000/metrics/"
	@echo "$(BLUE)   RedisInsight:$(RESET)    http://localhost:5540/"
	@echo "$(BLUE)   Grafana:$(RESET)         http://localhost:3000/ (admin/admin)"
	@echo "$(BLUE)   Prometheus:$(RESET)      http://localhost:9090/"
	@echo ""

test: ## Run unit tests
	@echo "$(BLUE)Running unit tests...$(RESET)"
	@poetry run pytest tests/unit/ -v --cov=weather_service --cov-report=term

test-bdd: ## Run BDD tests only
	@echo "$(BLUE)Running BDD tests...$(RESET)"
	@DJANGO_SETTINGS_MODULE=weather_service.settings.test DJANGO_LOG_LEVEL=WARNING poetry run python manage.py behave --format progress

test-bdd-quiet: ## Run BDD tests with minimal output (dots + summary only)
	@echo "$(BLUE)Running BDD tests (quiet mode)...$(RESET)"
	@DJANGO_SETTINGS_MODULE=weather_service.settings.test poetry run python manage.py behave --format progress

test-bdd-verbose: ## Run BDD tests showing scenario names
	@echo "$(BLUE)Running BDD tests (verbose mode)...$(RESET)"
	@DJANGO_SETTINGS_MODULE=weather_service.settings.test poetry run python manage.py behave --format plain

test-all: ## Run all tests (unit, integration, BDD)
	@echo "$(BLUE)Running all tests...$(RESET)"
	@poetry run pytest tests/unit/ tests/integration/ -v --cov=weather_service --cov-report=term
	@DJANGO_SETTINGS_MODULE=weather_service.settings.test poetry run python manage.py behave

format: ## Format code
	@echo "$(BLUE)Formatting code...$(RESET)"
	@poetry run black .
	@poetry run isort .
	@poetry run ruff check --fix .

stop: ## Stop all services
	@echo "$(BLUE)Stopping all services...$(RESET)"
	@docker-compose -f docker/docker-compose.yml down
	@echo "$(GREEN)All services stopped!$(RESET)"
