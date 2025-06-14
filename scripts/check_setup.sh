#!/bin/bash

# Script to check if the Airflow integration files are properly set up

echo "🔍 Checking LangGraph Flow Airflow Integration Setup..."
echo ""

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if we're in the right directory
if [ -f "README.md" ] || [ -f "setup.py" ] || [ -f "pyproject.toml" ] || [ -d ".git" ]; then
    echo -e "${GREEN}✅ Detected langgraph-flow repository${NC}"
else
    echo -e "${RED}❌ Not in langgraph-flow repository root${NC}"
    echo "   Please run this from the root of the langgraph-flow repository"
    exit 1
fi

echo ""
echo "Checking required files and directories..."
echo ""

# Files and directories to check
declare -A files_to_check=(
    ["airflow/dags/visual_ai_workflow_dag.py"]="Airflow DAG for basic workflows"
    ["airflow/dags/multi_agent_dag.py"]="Airflow DAG for multi-agent workflows"
    ["airflow/plugins/visual_ai_operators.py"]="Custom Airflow operators"
    ["backend/api/workflow_triggers.py"]="API endpoints for triggering workflows"
    ["backend/api/workflow_status.py"]="API endpoints for workflow status"
    ["backend/api/monitoring.py"]="API endpoints for monitoring"
    ["backend/core/workflow_error_handler.py"]="Error handling logic"
    ["docker/Dockerfile.airflow"]="Dockerfile for Airflow"
    ["docker/docker-compose.airflow.yml"]="Docker Compose configuration"
    ["database/migrations/001_visual_ai_schema.sql"]="Database schema"
    [".env.example"]="Environment variables template"
    ["requirements-airflow.txt"]="Python dependencies for Airflow"
)

missing_files=0
existing_files=0

for file in "${!files_to_check[@]}"; do
    if [ -f "$file" ]; then
        echo -e "${GREEN}✅ Found${NC}: $file"
        ((existing_files++))
    else
        echo -e "${RED}❌ Missing${NC}: $file - ${files_to_check[$file]}"
        ((missing_files++))
    fi
done

echo ""
echo "Summary:"
echo "  Files found: $existing_files"
echo "  Files missing: $missing_files"
echo ""

if [ $missing_files -eq 0 ]; then
    echo -e "${GREEN}✅ All required files are present! You can run './quickstart.sh' to start the services.${NC}"
else
    echo -e "${YELLOW}⚠️  Some files are missing. You need to:${NC}"
    echo ""
    echo "1. Ensure you have all the Airflow integration files from the documentation"
    echo "2. Place them in the correct directories as shown above"
    echo "3. Run this check again to verify everything is in place"
    echo ""
    echo "If you need the integration files, they should be provided in the"
    echo "AIRFLOW_INTEGRATION_SUMMARY.md documentation."
fi

# Check for .env file
echo ""
if [ -f ".env" ]; then
    echo -e "${GREEN}✅ .env file exists${NC}"
    echo "   Make sure to update it with your API keys!"
else
    if [ -f ".env.example" ]; then
        echo -e "${YELLOW}⚠️  .env file not found, but .env.example exists${NC}"
        echo "   Run: cp .env.example .env"
        echo "   Then update it with your API keys"
    else
        echo -e "${RED}❌ Neither .env nor .env.example found${NC}"
        echo "   You need to create an .env file with your configuration"
    fi
fi

# Check Docker
echo ""
echo "Checking Docker setup..."
if command -v docker >/dev/null 2>&1; then
    echo -e "${GREEN}✅ Docker is installed${NC}"
    
    # Check if Docker daemon is running
    if docker info >/dev/null 2>&1; then
        echo -e "${GREEN}✅ Docker daemon is running${NC}"
    else
        echo -e "${RED}❌ Docker daemon is not running${NC}"
        echo "   Please start Docker Desktop or the Docker service"
    fi
else
    echo -e "${RED}❌ Docker is not installed${NC}"
    echo "   Please install Docker from https://www.docker.com/"
fi

if command -v docker-compose >/dev/null 2>&1; then
    echo -e "${GREEN}✅ Docker Compose is installed${NC}"
else
    echo -e "${RED}❌ Docker Compose is not installed${NC}"
    echo "   Please install Docker Compose"
fi

echo ""
echo "Check complete!"