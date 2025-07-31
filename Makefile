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
	@echo "$(BLUE)Setting up development environment...$(RESET)"
	@# Check if pyenv is available
	@which pyenv >/dev/null 2>&1 || { \
		echo "$(RED)❌ pyenv not found. Please install pyenv first:$(RESET)"; \
		echo "$(YELLOW)  macOS: brew install pyenv$(RESET)"; \
		echo "$(YELLOW)  Linux: curl https://pyenv.run | bash$(RESET)"; \
		exit 1; \
	}
	@# Check if poetry is available
	@which poetry >/dev/null 2>&1 || { \
		echo "$(RED)❌ poetry not found. Please install poetry first:$(RESET)"; \
		echo "$(YELLOW)  curl -sSL https://install.python-poetry.org | python3 -$(RESET)"; \
		exit 1; \
	}
	@# Extract and validate Python version
	@echo "$(BLUE)📋 Extracting Python version from pyproject.toml...$(RESET)"
	@if [ ! -f pyproject.toml ]; then \
		echo "$(RED)❌ pyproject.toml not found$(RESET)"; \
		exit 1; \
	fi
	@PYTHON_VERSION=$$(grep '^python = ' pyproject.toml | head -1 | cut -d'"' -f2 | sed 's/[\^~]//g' | sed 's/>=//g'); \
	if [ -z "$$PYTHON_VERSION" ]; then \
		echo "$(RED)❌ Could not extract Python version from pyproject.toml$(RESET)"; \
		exit 1; \
	fi; \
	echo "$(BLUE)📋 Required Python: $$PYTHON_VERSION$(RESET)"
	@# Check and install Python version
	@PYTHON_VERSION=$$(grep '^python = ' pyproject.toml | head -1 | cut -d'"' -f2 | sed 's/[\^~]//g' | sed 's/>=//g'); \
	if ! pyenv versions --bare 2>/dev/null | grep -q "^$$PYTHON_VERSION"; then \
		echo "$(YELLOW)📥 Installing Python $$PYTHON_VERSION...$(RESET)"; \
		LATEST_VERSION=$$(pyenv install --list 2>/dev/null | grep -E "^\s*$$PYTHON_VERSION\.[0-9]+$$" | tail -1 | tr -d ' '); \
		if [ -z "$$LATEST_VERSION" ]; then \
			echo "$(RED)❌ Python $$PYTHON_VERSION not available for installation$(RESET)"; \
			echo "$(YELLOW)Available versions:$(RESET)"; \
			pyenv install --list | grep "$$PYTHON_VERSION" | head -5; \
			exit 1; \
		fi; \
		echo "$(BLUE)Installing Python $$LATEST_VERSION...$(RESET)"; \
		pyenv install $$LATEST_VERSION || { \
			echo "$(RED)❌ Failed to install Python $$LATEST_VERSION$(RESET)"; \
			exit 1; \
		}; \
		PYTHON_VERSION=$$LATEST_VERSION; \
	else \
		PYTHON_VERSION=$$(pyenv versions --bare 2>/dev/null | grep "^$$PYTHON_VERSION" | sort -V | tail -1); \
	fi; \
	echo "$(GREEN)✅ Using Python: $$PYTHON_VERSION$(RESET)"
	@# Configure environment
	@PYTHON_VERSION=$$(grep '^python = ' pyproject.toml | head -1 | cut -d'"' -f2 | sed 's/[\^~]//g' | sed 's/>=//g'); \
	if ! pyenv versions --bare 2>/dev/null | grep -q "^$$PYTHON_VERSION"; then \
		PYTHON_VERSION=$$(pyenv versions --bare 2>/dev/null | grep "^$$PYTHON_VERSION" | sort -V | tail -1); \
	fi; \
	echo "$(BLUE)🔧 Configuring environment...$(RESET)"; \
	pyenv local $$PYTHON_VERSION 2>/dev/null || { \
		echo "$(RED)❌ Failed to set local Python version$(RESET)"; \
		exit 1; \
	}; \
	poetry env use $$(pyenv which python 2>/dev/null) >/dev/null 2>&1 || { \
		echo "$(RED)❌ Failed to configure poetry environment$(RESET)"; \
		exit 1; \
	}
	@echo "$(BLUE)📦 Installing dependencies...$(RESET)"
	@poetry install --no-root >/dev/null 2>&1 || { \
		echo "$(RED)❌ Failed to install dependencies$(RESET)"; \
		exit 1; \
	}
	@echo "$(GREEN)🎉 Environment ready!$(RESET)"
	@echo "$(YELLOW)💡 Activate with: poetry shell$(RESET)"


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
	@echo "$(BLUE)   API Metrics:$(RESET)     http://localhost:8000/metrics"
	@echo "$(BLUE)   RedisInsight:$(RESET)    http://localhost:5540/"
	@echo "$(BLUE)   Grafana:$(RESET)         http://localhost:3000/ (admin/admin)"
	@echo "$(BLUE)   Prometheus:$(RESET)      http://localhost:9090/"
	@echo ""

test: ## Run pytest tests
	@echo "$(BLUE)Running pytest tests...$(RESET)"
	@poetry run pytest tests/ -vv --cov=weather_service --cov-report=term
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
	@poetry run pytest tests/ -vv --cov=weather_service --cov-report=term
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
