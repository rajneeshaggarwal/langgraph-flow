#!/bin/bash

# Main entry point for setting up and starting Airflow integration

echo "======================================================================"
echo "      LangGraph Flow - Apache Airflow Integration Setup"
echo "======================================================================"
echo ""

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Step 1: Check if we're in the right directory
echo -e "${BLUE}Step 1: Checking repository...${NC}"
if [ -f "README.md" ] || [ -f "setup.py" ] || [ -f "pyproject.toml" ] || [ -d ".git" ]; then
    echo -e "${GREEN}✅ Found langgraph-flow repository${NC}"
else
    echo -e "${RED}❌ Not in langgraph-flow repository${NC}"
    echo "Please run this script from the root of your langgraph-flow repository"
    exit 1
fi
echo ""

# Step 2: Check for initialization
echo -e "${BLUE}Step 2: Checking initialization...${NC}"
if [ ! -d "airflow" ] || [ ! -d "backend" ] || [ ! -d "docker" ]; then
    echo -e "${YELLOW}⚠️  Directory structure not found. Running initialization...${NC}"
    
    # Make init script executable and run it
    if [ -f "init_airflow_integration.sh" ]; then
        chmod +x init_airflow_integration.sh
        ./init_airflow_integration.sh
    else
        echo -e "${RED}❌ init_airflow_integration.sh not found${NC}"
        echo "Creating basic directory structure..."
        mkdir -p airflow/{dags,logs,plugins,config}
        mkdir -p backend/{api,core}
        mkdir -p docker
        mkdir -p database/migrations
        mkdir -p frontend/src/components
        mkdir -p scripts
        mkdir -p uploads static
    fi
else
    echo -e "${GREEN}✅ Directory structure exists${NC}"
fi
echo ""

# Step 3: Check for integration files
echo -e "${BLUE}Step 3: Checking for Airflow integration files...${NC}"

# Check for critical files
critical_files=(
    "docker/docker-compose.airflow.yml"
    "airflow/dags/visual_ai_workflow_dag.py"
)

missing_critical=0
for file in "${critical_files[@]}"; do
    if [ ! -f "$file" ]; then
        echo -e "${RED}❌ Missing critical file: $file${NC}"
        ((missing_critical++))
    fi
done

if [ $missing_critical -gt 0 ]; then
    echo ""
    echo -e "${RED}Critical files are missing!${NC}"
    echo ""
    echo "The Airflow integration requires specific files to be added to your project."
    echo ""
    echo "You have two options:"
    echo ""
    echo "1. If you have the integration files:"
    echo "   - Copy all files from the integration package to their respective directories"
    echo "   - The complete file list is in AIRFLOW_INTEGRATION_SUMMARY.md"
    echo ""
    echo "2. If you need the integration files:"
    echo "   - They should be provided in the documentation"
    echo "   - Each file's content is documented in the integration guide"
    echo ""
    echo "After adding the files, run this script again."
    exit 1
fi

echo -e "${GREEN}✅ Critical files found${NC}"
echo ""

# Step 4: Check Docker
echo -e "${BLUE}Step 4: Checking Docker...${NC}"
if ! command -v docker >/dev/null 2>&1; then
    echo -e "${RED}❌ Docker is not installed${NC}"
    echo "Please install Docker from https://www.docker.com/"
    exit 1
fi

if ! docker info >/dev/null 2>&1; then
    echo -e "${RED}❌ Docker is not running${NC}"
    echo "Please start Docker Desktop or the Docker service"
    exit 1
fi

echo -e "${GREEN}✅ Docker is running${NC}"
echo ""

# Step 5: Check environment
echo -e "${BLUE}Step 5: Checking environment configuration...${NC}"
if [ ! -f ".env" ]; then
    if [ -f ".env.example" ]; then
        echo -e "${YELLOW}Creating .env from .env.example...${NC}"
        cp .env.example .env
        echo -e "${GREEN}✅ Created .env file${NC}"
        echo -e "${YELLOW}⚠️  Please edit .env and add your API keys!${NC}"
    else
        echo -e "${RED}❌ No .env or .env.example found${NC}"
        exit 1
    fi
else
    echo -e "${GREEN}✅ .env file exists${NC}"
fi

# Set AIRFLOW_UID
export AIRFLOW_UID=$(id -u)
if ! grep -q "AIRFLOW_UID" .env; then
    echo "AIRFLOW_UID=$AIRFLOW_UID" >> .env
fi
echo ""

# Step 6: Confirm before starting
echo -e "${BLUE}Ready to start services!${NC}"
echo ""
echo "This will:"
echo "  - Build Docker images (may take several minutes on first run)"
echo "  - Start PostgreSQL, Redis, Airflow, and the application"
echo "  - Initialize the Airflow database"
echo ""
read -p "Continue? (y/N) " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Cancelled."
    exit 0
fi

# Step 7: Start services
echo ""
echo -e "${BLUE}Starting services...${NC}"

# Run quickstart if it exists, otherwise use docker-compose directly
if [ -f "quickstart.sh" ]; then
    chmod +x quickstart.sh
    ./quickstart.sh
else
    echo "Building and starting Docker services..."
    docker-compose -f docker/docker-compose.airflow.yml build
    docker-compose -f docker/docker-compose.airflow.yml up -d
    
    echo ""
    echo "⏳ Waiting for services to initialize (30 seconds)..."
    sleep 30
    
    echo ""
    echo "======================================================================"
    echo "✅ Services should now be running!"
    echo "======================================================================"
    echo ""
    echo "📊 Airflow UI:        http://localhost:8080"
    echo "   Username: airflow"
    echo "   Password: airflow"
    echo ""
    echo "🚀 FastAPI Backend:   http://localhost:8000/docs"
    echo "🎨 Frontend:          http://localhost:3000"
    echo "🌺 Flower (Celery):   http://localhost:5555"
    echo ""
    echo "======================================================================"
    echo ""
    echo "To check service health: docker-compose -f docker/docker-compose.airflow.yml ps"
    echo "To view logs: docker-compose -f docker/docker-compose.airflow.yml logs -f"
    echo "To stop services: docker-compose -f docker/docker-compose.airflow.yml down"
fi