# Makefile
.PHONY: help build up down logs shell test lint format clean

help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Targets:'
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  %-15s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

build: ## Build all Docker containers
	docker-compose build

up: ## Start all services
	docker-compose up -d

down: ## Stop all services
	docker-compose down

logs: ## Show logs from all services
	docker-compose logs -f

backend-logs: ## Show backend logs
	docker-compose logs -f backend

frontend-logs: ## Show frontend logs
	docker-compose logs -f frontend

db-logs: ## Show database logs
	docker-compose logs -f postgres

shell-backend: ## Open a shell in the backend container
	docker-compose exec backend bash

shell-frontend: ## Open a shell in the frontend container
	docker-compose exec frontend sh

shell-db: ## Open a PostgreSQL shell
	docker-compose exec postgres psql -U user -d visual_ai

migrate: ## Run database migrations
	docker-compose exec backend alembic upgrade head

test-backend: ## Run backend tests
	docker-compose exec backend pytest

test-frontend: ## Run frontend tests
	docker-compose exec frontend npm test

lint-backend: ## Lint backend code
	docker-compose exec backend flake8 app/

lint-frontend: ## Lint frontend code
	docker-compose exec frontend npm run lint

format-backend: ## Format backend code
	docker-compose exec backend black app/

format-frontend: ## Format frontend code
	docker-compose exec frontend npm run format

clean: ## Clean up containers, volumes, and build artifacts
	docker-compose down -v
	rm -rf frontend/node_modules
	rm -rf frontend/dist
	rm -rf backend/__pycache__
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

restart: down up ## Restart all services

install-local: ## Install dependencies for local development
	cd backend && pip install -r requirements.txt
	cd frontend && npm install

dev-backend: ## Run backend in development mode (local)
	cd backend && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

dev-frontend: ## Run frontend in development mode (local)
	cd frontend && npm run dev

dev: ## Run both frontend and backend in development mode
	make -j2 dev-backend dev-frontend