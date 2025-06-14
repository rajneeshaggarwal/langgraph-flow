#!/bin/bash

# Script to initialize the Airflow integration structure for LangGraph Flow

echo "🚀 Initializing Airflow Integration for LangGraph Flow"
echo ""

# Create directory structure
echo "📁 Creating directory structure..."

directories=(
    "airflow/dags"
    "airflow/logs"
    "airflow/plugins"
    "airflow/config"
    "backend/api"
    "backend/core"
    "database/migrations"
    "docker"
    "frontend/src/components"
    "frontend/public"
    "scripts"
    "uploads"
    "static"
)

for dir in "${directories[@]}"; do
    if [ ! -d "$dir" ]; then
        mkdir -p "$dir"
        echo "  ✅ Created: $dir"
    else
        echo "  ℹ️  Exists: $dir"
    fi
done

# Create .gitkeep files
echo ""
echo "📄 Creating .gitkeep files..."
for dir in "${directories[@]}"; do
    if [ ! -f "$dir/.gitkeep" ]; then
        touch "$dir/.gitkeep"
    fi
done

# Create basic .env.example if it doesn't exist
if [ ! -f ".env.example" ]; then
    echo ""
    echo "📝 Creating .env.example..."
    cat > .env.example << 'EOF'
# Application Configuration
HOST=0.0.0.0
PORT=8000
RELOAD=false
EXECUTION_MODE=hybrid

# Database Configuration
POSTGRES_HOST=postgres
POSTGRES_DB=airflow
POSTGRES_USER=airflow
POSTGRES_PASSWORD=airflow

# Redis Configuration
REDIS_URL=redis://redis:6379

# Airflow Configuration
AIRFLOW_URL=http://localhost:8080
AIRFLOW_USERNAME=airflow
AIRFLOW_PASSWORD=airflow
AIRFLOW_ENABLED=true
AIRFLOW_UID=50000

# Airflow Admin User
_AIRFLOW_WWW_USER_USERNAME=airflow
_AIRFLOW_WWW_USER_PASSWORD=airflow

# LangFuse Configuration
LANGFUSE_SECRET_KEY=your_langfuse_secret_key
LANGFUSE_PUBLIC_KEY=your_langfuse_public_key
LANGFUSE_HOST=https://cloud.langfuse.com
LANGFUSE_ENABLED=true

# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key
OPENAI_MODEL=gpt-4

# Security
JWT_SECRET_KEY=your_jwt_secret_key_here
JWT_ALGORITHM=HS256
JWT_EXPIRATION_MINUTES=1440

# Frontend Configuration
FRONTEND_URL=http://localhost:3000
REACT_APP_API_URL=http://localhost:8000
REACT_APP_AIRFLOW_URL=http://localhost:8080
EOF
    echo "  ✅ Created .env.example"
fi

# Copy .env.example to .env if .env doesn't exist
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo "  ✅ Created .env from .env.example"
    echo ""
    echo "  ⚠️  IMPORTANT: Edit .env and add your API keys!"
else
    echo "  ℹ️  .env already exists"
fi

# Create requirements-airflow.txt if it doesn't exist
if [ ! -f "requirements-airflow.txt" ]; then
    echo ""
    echo "📦 Creating requirements-airflow.txt..."
    cat > requirements-airflow.txt << 'EOF'
# LangGraph and LangChain
langgraph==0.2.0
langchain==0.1.0
langchain-community==0.1.0
langchain-openai==0.1.0

# LangFuse for observability
langfuse==2.0.0

# OpenAI
openai>=1.0.0

# Database
psycopg2-binary==2.9.9
redis==5.0.0

# HTTP client
httpx==0.25.0
aiohttp==3.9.0

# Data validation
pydantic==2.0.0

# Utils
python-dotenv==1.0.0
tenacity==8.2.3

# Additional Airflow providers
apache-airflow-providers-celery==3.5.0
EOF
    echo "  ✅ Created requirements-airflow.txt"
fi

# Create a basic Makefile if it doesn't exist
if [ ! -f "Makefile" ]; then
    echo ""
    echo "🔧 Creating Makefile..."
    cat > Makefile << 'EOF'
.PHONY: help setup start stop clean

help:
	@echo "Available commands:"
	@echo "  make setup  - Initial setup"
	@echo "  make start  - Start services"
	@echo "  make stop   - Stop services"
	@echo "  make clean  - Clean up"

setup:
	./init_airflow_integration.sh

start:
	docker-compose -f docker/docker-compose.airflow.yml up -d

stop:
	docker-compose -f docker/docker-compose.airflow.yml down

clean:
	docker-compose -f docker/docker-compose.airflow.yml down -v
EOF
    echo "  ✅ Created Makefile"
fi

echo ""
echo "✅ Basic structure initialized!"
echo ""
echo "Next steps:"
echo "1. You need to add the Airflow integration files to the created directories:"
echo "   - DAG files in airflow/dags/"
echo "   - Docker files in docker/"
echo "   - Backend API files in backend/"
echo "   - Frontend components in frontend/"
echo ""
echo "2. Edit .env file with your API keys"
echo ""
echo "3. Run './scripts/check_setup.sh' to verify all files are in place"
echo ""
echo "4. Run './quickstart.sh' to start the services"
echo ""
echo "For the complete list of required files, see AIRFLOW_INTEGRATION_SUMMARY.md"