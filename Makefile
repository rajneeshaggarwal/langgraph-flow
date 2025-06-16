# LangGraph Flow Makefile
.PHONY: help setup start stop restart status logs clean test

# Default target
help:
	@echo "LangGraph Flow - Available Commands:"
	@echo ""
	@echo "  make setup       - Initialize project and configure environment"
	@echo "  make start       - Start all services"
	@echo "  make stop        - Stop all services"
	@echo "  make restart     - Restart all services"
	@echo "  make status      - Show service status"
	@echo "  make logs        - View all logs (tail)"
	@echo "  make clean       - Remove all data and volumes"
	@echo "  make test        - Run integration tests"
	@echo ""
	@echo "Service-specific commands:"
	@echo "  make logs-backend    - View backend logs"
	@echo "  make logs-airflow    - View Airflow logs"
	@echo "  make logs-langfuse   - View LangFuse logs"
	@echo ""
	@echo "Utility commands:"
	@echo "  make check       - Check setup completeness"
	@echo "  make ollama      - Setup Ollama for local LLMs"

# Setup the project
setup:
	@./setup.sh init

# Start all services
start:
	@./setup.sh start

# Stop all services
stop:
	@./setup.sh stop

# Restart all services
restart:
	@./setup.sh restart

# Show service status
status:
	@./setup.sh status

# View logs (all services)
logs:
	@./setup.sh logs

# Clean everything
clean:
	@./setup.sh clean

# Run tests
test:
	@python3 utilities.py test

# Service-specific logs
logs-backend:
	@./setup.sh logs backend

logs-airflow:
	@./setup.sh logs airflow-scheduler

logs-langfuse:
	@./setup.sh logs langfuse

# Check setup
check:
	@python3 utilities.py check

# Setup Ollama
ollama:
	@./setup.sh setup-ollama

# Quick commands
up: start
down: stop