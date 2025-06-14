#!/bin/bash

# Setup script for Airflow integration with LangGraph Flow

set -e

echo "🚀 Setting up Airflow integration for LangGraph Flow..."

# Check prerequisites
command -v docker >/dev/null 2>&1 || { echo "❌ Docker is required but not installed. Aborting." >&2; exit 1; }
command -v docker-compose >/dev/null 2>&1 || { echo "❌ Docker Compose is required but not installed. Aborting." >&2; exit 1; }

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p airflow/{dags,logs,plugins,config}
mkdir -p backend/{api,core}
mkdir -p database/migrations
mkdir -p uploads
mkdir -p static

# Set proper permissions for Airflow
echo "🔒 Setting permissions..."
export AIRFLOW_UID=$(id -u)
echo "AIRFLOW_UID=${AIRFLOW_UID}" >> .env

# Copy environment file if not exists
if [ ! -f .env ]; then
    echo "📝 Creating .env file..."
    cp .env.example .env
    echo "⚠️  Please update .env file with your actual configuration values"
fi

# Generate secret keys if not set
if grep -q "your_jwt_secret_key_here" .env; then
    echo "🔐 Generating JWT secret key..."
    JWT_SECRET=$(openssl rand -hex 32)
    sed -i.bak "s/your_jwt_secret_key_here/$JWT_SECRET/g" .env
fi

# Build Docker images
echo "🐳 Building Docker images..."
docker-compose -f docker/docker-compose.airflow.yml build

# Initialize Airflow database
echo "🗄️ Initializing Airflow database..."
docker-compose -f docker/docker-compose.airflow.yml up -d postgres redis
sleep 10  # Wait for PostgreSQL to be ready

# Run database migrations
echo "📊 Running database migrations..."
docker-compose -f docker/docker-compose.airflow.yml run --rm airflow-webserver airflow db init

# Apply Visual AI schema
echo "🎨 Applying Visual AI database schema..."
docker-compose -f docker/docker-compose.airflow.yml exec -T postgres psql -U airflow -d airflow < database/migrations/001_visual_ai_schema.sql

# Create Airflow admin user
echo "👤 Creating Airflow admin user..."
docker-compose -f docker/docker-compose.airflow.yml run --rm airflow-webserver airflow users create \
    --username airflow \
    --password airflow \
    --firstname Admin \
    --lastname User \
    --role Admin \
    --email admin@example.com

# Start all services
echo "🚀 Starting all services..."
docker-compose -f docker/docker-compose.airflow.yml up -d

# Wait for services to be ready
echo "⏳ Waiting for services to be ready..."
sleep 30

# Check service health
echo "🏥 Checking service health..."
docker-compose -f docker/docker-compose.airflow.yml ps

# Display access information
echo ""
echo "✅ Setup complete! Services are running:"
echo ""
echo "📊 Airflow UI: http://localhost:8080 (Username: airflow, Password: airflow)"
echo "🚀 FastAPI Backend: http://localhost:8000/docs"
echo "🎨 Frontend: http://localhost:3000"
echo "🌺 Flower (Celery): http://localhost:5555"
echo ""
echo "📝 Next steps:"
echo "1. Update .env file with your API keys"
echo "2. Access Airflow UI and verify DAGs are loaded"
echo "3. Test workflow trigger via FastAPI docs"
echo "4. Monitor workflows in real-time via the frontend"
echo ""
echo "🛑 To stop all services: docker-compose -f docker/docker-compose.airflow.yml down"
echo "🗑️ To remove all data: docker-compose -f docker/docker-compose.airflow.yml down -v"