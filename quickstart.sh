#!/bin/bash

# Quick start script for LangGraph Flow with Airflow integration

cat << "EOF"
  _                     ____                 _       _____ _               
 | |                   / ___|_ __ __ _ _ __ | |__   |  ___| | _____      __
 | |      ___  _____  | |  _| '__/ _` | '_ \| '_ \  | |_  | |/ _ \ \ /\ / /
 | |___  |___||_____| | |_| | | | (_| | |_) | | | | |  _| | | (_) \ V  V / 
 |_____|               \____|_|  \__,_| .__/|_| |_| |_|   |_|\___/ \_/\_/  
                                      |_|                                    
                        with Apache Airflow Integration

EOF

echo "🚀 Starting LangGraph Flow with Airflow Integration Setup..."
echo ""

# Check if running from correct directory
if [ ! -f "README.md" ] && [ ! -f "setup.py" ] && [ ! -f "pyproject.toml" ]; then
    echo "❌ Error: Please run this script from the root of the langgraph-flow repository"
    exit 1
fi

# Function to check command existence
check_command() {
    if ! command -v $1 &> /dev/null; then
        echo "❌ $1 is required but not installed."
        echo "   Please install $1 and try again."
        exit 1
    else
        echo "✅ $1 found"
    fi
}

# Check prerequisites
echo "📋 Checking prerequisites..."
check_command docker
check_command docker-compose
check_command python3
check_command npm
echo ""

# Create necessary directories
echo "📁 Creating directory structure..."
mkdir -p airflow/{dags,logs,plugins,config}
mkdir -p backend/{api,core}
mkdir -p database/migrations
mkdir -p uploads
mkdir -p static
mkdir -p scripts
echo "✅ Directories created"
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    if [ -f .env.example ]; then
        echo "📝 Creating .env file from template..."
        cp .env.example .env
        echo "⚠️  Please edit .env file and add your API keys!"
        echo ""
    else
        echo "❌ No .env.example file found. Creating minimal .env..."
        cat > .env << 'ENVFILE'
# Minimal environment configuration
AIRFLOW_UID=$(id -u)
POSTGRES_HOST=localhost
POSTGRES_DB=airflow
POSTGRES_USER=airflow
POSTGRES_PASSWORD=airflow
REDIS_URL=redis://localhost:6379
AIRFLOW_URL=http://localhost:8080
AIRFLOW_USERNAME=airflow
AIRFLOW_PASSWORD=airflow
OPENAI_API_KEY=your_openai_api_key_here
LANGFUSE_SECRET_KEY=your_langfuse_secret_key
LANGFUSE_PUBLIC_KEY=your_langfuse_public_key
JWT_SECRET_KEY=$(openssl rand -hex 32)
ENVFILE
        echo "✅ Created .env file - Please update with your actual API keys!"
        echo ""
    fi
else
    echo "✅ .env file already exists"
    echo ""
fi

# Set AIRFLOW_UID
export AIRFLOW_UID=$(id -u)
if ! grep -q "AIRFLOW_UID" .env; then
    echo "AIRFLOW_UID=$AIRFLOW_UID" >> .env
fi

# Install Python dependencies
echo "🐍 Installing Python dependencies..."
if [ -f "requirements-airflow.txt" ]; then
    pip install -r requirements-airflow.txt
    echo "✅ Python dependencies installed"
else
    echo "⚠️  requirements-airflow.txt not found, skipping Python dependencies"
fi
echo ""

# Install frontend dependencies
echo "📦 Installing frontend dependencies..."
if [ -d "frontend" ] && [ -f "frontend/package.json" ]; then
    cd frontend
    npm install
    cd ..
    echo "✅ Frontend dependencies installed"
else
    echo "ℹ️  Frontend directory not found, creating it..."
    mkdir -p frontend/src/components frontend/public
    echo "✅ Frontend directory created - you'll need to add the React app later"
fi
echo ""

# Build and start services
echo "🐳 Building and starting Docker services..."
echo "This may take several minutes on first run..."
echo ""

# Check if docker-compose file exists
if [ ! -f "docker/docker-compose.airflow.yml" ]; then
    echo "⚠️  docker-compose.airflow.yml not found. Creating docker directory..."
    mkdir -p docker
    echo "❌ You need to add the Docker configuration files to the docker/ directory."
    echo "   Please ensure all Airflow integration files are properly installed."
    exit 1
fi

docker-compose -f docker/docker-compose.airflow.yml build
docker-compose -f docker/docker-compose.airflow.yml up -d

# Wait for services to be ready
echo ""
echo "⏳ Waiting for services to initialize..."
sleep 30

# Check service status
echo ""
echo "🏥 Checking service health..."
docker-compose -f docker/docker-compose.airflow.yml ps

# Display access information
echo ""
echo "======================================================================"
echo "✅ Setup Complete! Your services should be running at:"
echo "======================================================================"
echo ""
echo "📊 Airflow UI:        http://localhost:8080"
echo "   Username: airflow"
echo "   Password: airflow"
echo ""
echo "🚀 FastAPI Backend:   http://localhost:8000/docs"
echo ""
echo "🎨 Frontend:          http://localhost:3000"
echo ""
echo "🌺 Flower (Celery):   http://localhost:5555"
echo ""
echo "======================================================================"
echo ""
echo "📝 Next Steps:"
echo ""
echo "1. Edit .env file and add your API keys:"
echo "   - OPENAI_API_KEY"
echo "   - LANGFUSE_SECRET_KEY and LANGFUSE_PUBLIC_KEY"
echo ""
echo "2. Test the integration:"
echo "   python scripts/test_airflow_integration.py"
echo ""
echo "3. Access Airflow UI and verify DAGs are loaded"
echo ""
echo "4. Try triggering a workflow via the Frontend or API"
echo ""
echo "======================================================================"
echo ""
echo "🛑 To stop all services:"
echo "   docker-compose -f docker/docker-compose.airflow.yml down"
echo ""
echo "🗑️  To remove all data and start fresh:"
echo "   docker-compose -f docker/docker-compose.airflow.yml down -v"
echo ""
echo "📚 For more information, see INTEGRATION_GUIDE.md"
echo ""
echo "Happy orchestrating! 🎉"