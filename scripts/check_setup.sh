#!/bin/bash

# Check setup script
echo "🔍 Checking LangGraph Flow setup..."

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "❌ .env file not found"
    exit 1
fi

# Check required directories
required_dirs=(
    "airflow/dags"
    "backend"
    "frontend"
    "docker"
)

for dir in "${required_dirs[@]}"; do
    if [ ! -d "$dir" ]; then
        echo "❌ Directory missing: $dir"
        exit 1
    fi
done

# Check Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker not installed"
    exit 1
fi

# Check Docker Compose
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose not installed"
    exit 1
fi

echo "✅ Setup check passed!"
