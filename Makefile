# Makefile for LangGraph Flow with Airflow Integration

.PHONY: help setup start stop restart clean test logs shell format lint build

# Default target
help:
	@echo "LangGraph Flow with Airflow Integration - Available Commands:"
	@echo ""
	@echo "Setup & Installation:"
	@echo "  make setup          - Complete initial setup (install deps, create dirs, build images)"
	@echo "  make build          - Build Docker images"
	@echo ""
	@echo "Service Management:"
	@echo "  make start          - Start all services"
	@echo "  make stop           - Stop all services"
	@echo "  make restart        - Restart all services"
	@echo "  make clean          - Stop services and remove volumes (WARNING: deletes data)"
	@echo ""
	@echo "Development:"
	@echo "  make test           - Run integration tests"
	@echo "  make logs           - View logs for all services"
	@echo "  make logs-<service> - View logs for specific service (e.g., make logs-airflow)"
	@echo "  make shell-<service>- Open shell in service container"
	@echo "  make format         - Format code (Python with black, JS with prettier)"
	@echo "  make lint           - Run linters"
	@echo ""
	@echo "Utilities:"
	@echo "  make urls           - Display service URLs"
	@echo "  make health         - Check service health"
	@echo "  make backup         - Backup database"
	@echo "  make restore        - Restore database from backup"

# Setup commands
setup: check-deps create-dirs install-deps build
	@echo "✅ Setup complete! Run 'make start' to begin."

check-deps:
	@echo "Checking dependencies..."
	@command -v docker >/dev/null 2>&1 || { echo "❌ Docker is required but not installed."; exit 1; }
	@command -v docker-compose >/dev/null 2>&1 || { echo "❌ Docker Compose is required but not installed."; exit 1; }
	@command -v python3 >/dev/null 2>&1 || { echo "❌ Python 3 is required but not installed."; exit 1; }
	@command -v npm >/dev/null 2>&1 || { echo "❌ npm is required but not installed."; exit 1; }
	@echo "✅ All dependencies found"

create-dirs:
	@echo "Creating directories..."
	@mkdir -p airflow/{dags,logs,plugins,config}
	@mkdir -p backend/{api,core}
	@mkdir -p database/migrations
	@mkdir -p uploads static
	@mkdir -p scripts
	@./scripts/create_gitkeep_files.sh || true
	@echo "✅ Directories created"

install-deps:
	@echo "Installing dependencies..."
	@if [ -f "requirements-airflow.txt" ]; then pip install -r requirements-airflow.txt; fi
	@if [ -d "frontend" ] && [ -f "frontend/package.json" ]; then cd frontend && npm install; fi
	@echo "✅ Dependencies installed"

# Docker commands
build:
	@echo "Building Docker images..."
	@docker-compose -f docker/docker-compose.airflow.yml build

start:
	@echo "Starting services..."
	@docker-compose -f docker/docker-compose.airflow.yml up -d
	@sleep 5
	@make urls

stop:
	@echo "Stopping services..."
	@docker-compose -f docker/docker-compose.airflow.yml down

restart: stop start

clean:
	@echo "⚠️  WARNING: This will delete all data!"
	@echo "Press Ctrl+C to cancel, or Enter to continue..."
	@read confirm
	@docker-compose -f docker/docker-compose.airflow.yml down -v
	@rm -rf airflow/logs/*
	@echo "✅ Cleaned up services and data"

# Development commands
test:
	@echo "Running integration tests..."
	@python scripts/test_airflow_integration.py

logs:
	@docker-compose -f docker/docker-compose.airflow.yml logs -f

logs-airflow:
	@docker-compose -f docker/docker-compose.airflow.yml logs -f airflow-webserver airflow-scheduler

logs-backend:
	@docker-compose -f docker/docker-compose.airflow.yml logs -f backend

logs-frontend:
	@docker-compose -f docker/docker-compose.airflow.yml logs -f frontend

logs-postgres:
	@docker-compose -f docker/docker-compose.airflow.yml logs -f postgres

logs-redis:
	@docker-compose -f docker/docker-compose.airflow.yml logs -f redis

shell-airflow:
	@docker-compose -f docker/docker-compose.airflow.yml exec airflow-webserver /bin/bash

shell-backend:
	@docker-compose -f docker/docker-compose.airflow.yml exec backend /bin/bash

shell-postgres:
	@docker-compose -f docker/docker-compose.airflow.yml exec postgres psql -U airflow

format:
	@echo "Formatting code..."
	@if command -v black >/dev/null 2>&1; then \
		black backend/ airflow/dags/ airflow/plugins/ scripts/; \
	else \
		echo "⚠️  Black not installed, skipping Python formatting"; \
	fi
	@if [ -d "frontend" ]; then \
		cd frontend && npm run format || true; \
	fi
	@echo "✅ Code formatted"

lint:
	@echo "Running linters..."
	@if command -v flake8 >/dev/null 2>&1; then \
		flake8 backend/ airflow/dags/ airflow/plugins/ --max-line-length=100; \
	else \
		echo "⚠️  Flake8 not installed, skipping Python linting"; \
	fi
	@if [ -d "frontend" ]; then \
		cd frontend && npm run lint || true; \
	fi

# Utility commands
urls:
	@echo ""
	@echo "🌐 Service URLs:"
	@echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
	@echo "📊 Airflow UI:        http://localhost:8080"
	@echo "   Username: airflow"
	@echo "   Password: airflow"
	@echo ""
	@echo "🚀 FastAPI Backend:   http://localhost:8000/docs"
	@echo "🎨 Frontend:          http://localhost:3000"
	@echo "🌺 Flower (Celery):   http://localhost:5555"
	@echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
	@echo ""

health:
	@echo "Checking service health..."
	@echo -n "Airflow: "
	@curl -s http://localhost:8080/health >/dev/null 2>&1 && echo "✅ Healthy" || echo "❌ Unhealthy"
	@echo -n "Backend: "
	@curl -s http://localhost:8000/health >/dev/null 2>&1 && echo "✅ Healthy" || echo "❌ Unhealthy"
	@echo -n "Frontend: "
	@curl -s http://localhost:3000 >/dev/null 2>&1 && echo "✅ Healthy" || echo "❌ Unhealthy"
	@echo -n "PostgreSQL: "
	@docker-compose -f docker/docker-compose.airflow.yml exec -T postgres pg_isready >/dev/null 2>&1 && echo "✅ Healthy" || echo "❌ Unhealthy"
	@echo -n "Redis: "
	@docker-compose -f docker/docker-compose.airflow.yml exec -T redis redis-cli ping >/dev/null 2>&1 && echo "✅ Healthy" || echo "❌ Unhealthy"

backup:
	@echo "Backing up database..."
	@mkdir -p backups
	@docker-compose -f docker/docker-compose.airflow.yml exec -T postgres pg_dump -U airflow airflow > backups/airflow_backup_$(shell date +%Y%m%d_%H%M%S).sql
	@echo "✅ Database backed up to backups/"

restore:
	@echo "Available backups:"
	@ls -la backups/*.sql 2>/dev/null || echo "No backups found"
	@echo ""
	@echo "To restore, run: docker-compose exec -T postgres psql -U airflow airflow < backups/[filename]"

# Environment setup
env-setup:
	@if [ ! -f .env ]; then \
		cp .env.example .env; \
		echo "✅ Created .env file. Please update with your API keys."; \
	else \
		echo "✅ .env file already exists"; \
	fi

# Quick commands for common tasks
trigger-workflow:
	@echo "Triggering test workflow..."
	@curl -X POST http://localhost:8000/api/v1/workflows/trigger \
		-H "Content-Type: application/json" \
		-H "Authorization: Bearer test_token" \
		-d '{"dag_id": "visual_ai_workflow", "input_data": {"query": "Test from Makefile"}}'

monitor-workflows:
	@echo "Opening workflow monitor in browser..."
	@open http://localhost:3000/workflows || xdg-open http://localhost:3000/workflows || echo "Please open http://localhost:3000/workflows in your browser"

airflow-ui:
	@echo "Opening Airflow UI in browser..."
	@open http://localhost:8080 || xdg-open http://localhost:8080 || echo "Please open http://localhost:8080 in your browser"

# Docker compose shortcuts
ps:
	@docker-compose -f docker/docker-compose.airflow.yml ps

top:
	@docker-compose -f docker/docker-compose.airflow.yml top