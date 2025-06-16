#!/bin/bash

# Complete fix for LangGraph Flow setup issues

echo "🔧 Complete Fix for LangGraph Flow"
echo "=================================="
echo ""

# Function to generate secure keys
generate_key() {
    openssl rand -hex 32 2>/dev/null || cat /dev/urandom | tr -dc 'a-zA-Z0-9' | fold -w 32 | head -n 1
}

# 1. First, let's check where we are
echo "📍 Current directory: $(pwd)"
echo ""

# 2. Check if .env exists
if [ -f ".env" ]; then
    echo "✅ Found .env file"
    echo "📋 Current environment variables:"
    grep -E "LANGFUSE_PUBLIC_KEY|LANGFUSE_SECRET_KEY|JWT_SECRET_KEY|OPENAI_API_KEY|AIRFLOW_UID" .env | head -5
    echo ""
else
    echo "❌ No .env file found. Creating one..."
fi

# 3. Create a proper .env file with all required variables
echo "🔄 Creating/updating .env file with all required variables..."
cat > .env << EOF
# LangGraph Flow Environment Configuration
# Generated on $(date)

# Application Settings
HOST=0.0.0.0
PORT=8000
EXECUTION_MODE=hybrid

# LLM Provider Settings
LLM_PROVIDER=auto
OPENAI_API_KEY=sk-YOUR-OPENAI-KEY-HERE
OPENAI_MODEL=gpt-4
OLLAMA_BASE_URL=http://localhost:11434

# Database Configuration
POSTGRES_HOST=postgres
POSTGRES_DB=airflow
POSTGRES_USER=airflow
POSTGRES_PASSWORD=airflow
DATABASE_URL=postgresql://airflow:airflow@postgres/airflow

# Redis Configuration
REDIS_URL=redis://redis:6379

# Airflow Configuration
AIRFLOW_URL=http://localhost:8080
AIRFLOW_USERNAME=airflow
AIRFLOW_PASSWORD=airflow
AIRFLOW_ENABLED=true
AIRFLOW_UID=$(id -u)
_AIRFLOW_WWW_USER_USERNAME=airflow
_AIRFLOW_WWW_USER_PASSWORD=airflow

# LangFuse Configuration
LANGFUSE_ENABLED=true
LANGFUSE_HOST=http://localhost:3001
LANGFUSE_SECRET_KEY=sk-lf-$(openssl rand -hex 16)
LANGFUSE_PUBLIC_KEY=pk-lf-$(openssl rand -hex 16)
LANGFUSE_NEXTAUTH_SECRET=$(generate_key)
LANGFUSE_SALT=$(generate_key)
LANGFUSE_ENCRYPTION_KEY=$(generate_key)
LANGFUSE_ADMIN_EMAIL=admin@localhost
LANGFUSE_ADMIN_NAME=Admin
LANGFUSE_ADMIN_PASSWORD=admin123

# Security Configuration
JWT_SECRET_KEY=$(generate_key)
JWT_ALGORITHM=HS256
JWT_EXPIRATION_MINUTES=1440

# Frontend Configuration
FRONTEND_URL=http://localhost:3000
REACT_APP_API_URL=http://localhost:8000
REACT_APP_AIRFLOW_URL=http://localhost:8080

# Monitoring
ENABLE_MONITORING=true
ENABLE_TRACING=true
LOG_LEVEL=INFO
EOF

echo "✅ Created .env file with secure keys"
echo ""

# 4. Export critical variables for immediate use
export AIRFLOW_UID=$(id -u)
source .env

# 5. Fix Airflow Dockerfile to prevent version conflicts
echo "🔧 Updating Airflow Dockerfile..."
cat > docker/Dockerfile.airflow << 'EOF'
FROM apache/airflow:2.8.0-python3.11

USER root

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    python3-dev \
    git \
    && rm -rf /var/lib/apt/lists/*

USER airflow

# Use constraints file to avoid version conflicts
ARG CONSTRAINT_URL="https://raw.githubusercontent.com/apache/airflow/constraints-2.8.0/constraints-3.11.txt"

# Install Python dependencies with constraints
RUN pip install --no-cache-dir --constraint "${CONSTRAINT_URL}" \
    langgraph \
    langchain \
    langchain-community \
    langchain-openai \
    langfuse \
    psycopg2-binary==2.9.9 \
    redis==5.0.0 \
    httpx \
    aiohttp==3.9.0 \
    pydantic==2.0.0 \
    python-dotenv==1.0.0 \
    tenacity==8.2.3 \
    pillow==10.0.0 \
    pandas==2.0.0 \
    numpy==1.24.0

# Copy DAGs and plugins
COPY --chown=airflow:airflow ./airflow/dags* /opt/airflow/dags/
COPY --chown=airflow:airflow ./airflow/plugins* /opt/airflow/plugins/

# Set environment variables
ENV AIRFLOW__CORE__LOAD_EXAMPLES=False
ENV AIRFLOW__WEBSERVER__EXPOSE_CONFIG=True
ENV AIRFLOW__API__AUTH_BACKENDS='airflow.api.auth.backend.basic_auth'
EOF

echo "✅ Updated Dockerfile.airflow"
echo ""

# 6. Clean up and rebuild
echo "🧹 Cleaning up old containers and volumes..."
docker-compose -f docker/docker-compose.yml down -v

echo ""
echo "🏗️ Rebuilding images with fixed configuration..."
docker-compose -f docker/docker-compose.yml build --no-cache airflow-init

echo ""
echo "🚀 Starting services..."
docker-compose -f docker/docker-compose.yml up -d

echo ""
echo "⏳ Waiting for services to initialize (30 seconds)..."
sleep 30

echo ""
echo "📊 Checking service status..."
docker-compose -f docker/docker-compose.yml ps

echo ""
echo "======================================================================"
echo "✅ Fix applied! Your services should be starting."
echo "======================================================================"
echo ""
echo "🌐 Access points:"
echo "  - Airflow: http://localhost:8080 (airflow/airflow)"
echo "  - Backend API: http://localhost:8000/docs"
echo "  - Frontend: http://localhost:3000"
echo "  - LangFuse: http://localhost:3001"
echo ""
echo "⚠️  IMPORTANT: Edit .env and replace 'sk-YOUR-OPENAI-KEY-HERE' with your actual OpenAI API key"
echo ""
echo "📋 To check logs:"
echo "  docker-compose -f docker/docker-compose.yml logs -f airflow-init"
echo "  docker-compose -f docker/docker-compose.yml logs -f backend"
echo ""