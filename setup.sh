#!/bin/bash

# LangGraph Flow - Unified Setup and Management Script
# This script combines all setup, initialization, and management functionality

set -e

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Script version
VERSION="1.0.0"

# Default values
COMPOSE_FILE="docker/docker-compose.yml"
ENV_FILE=".env"

# ASCII Art Banner
show_banner() {
    cat << "EOF"
  _                     ____                 _       _____ _               
 | |                   / ___|_ __ __ _ _ __ | |__   |  ___| | _____      __
 | |      ___  _____  | |  _| '__/ _` | '_ \| '_ \  | |_  | |/ _ \ \ /\ / /
 | |___  |___||_____| | |_| | | | (_| | |_) | | | | |  _| | | (_) \ V  V / 
 |_____|               \____|_|  \__,_| .__/|_| |_| |_|   |_|\___/ \_/\_/  
                                      |_|                                    
                        Enterprise AI Workflow Orchestration

EOF
    echo "Version: $VERSION"
    echo ""
}

# Function to check command existence
check_command() {
    if ! command -v $1 &> /dev/null; then
        echo -e "${RED}❌ $1 is required but not installed.${NC}"
        echo "   Please install $1 and try again."
        return 1
    else
        echo -e "${GREEN}✅ $1 found${NC}"
        return 0
    fi
}

# Function to generate secure keys
generate_secure_key() {
    openssl rand -hex 32 2>/dev/null || cat /dev/urandom | tr -dc 'a-zA-Z0-9' | fold -w 32 | head -n 1
}

# Initialize project structure
init_project() {
    echo -e "${BLUE}Initializing LangGraph Flow project structure...${NC}"
    echo ""
    
    # Create directory structure
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
            echo -e "  ${GREEN}✅ Created${NC}: $dir"
        else
            echo -e "  ℹ️  Exists: $dir"
        fi
    done
    
    # Create .gitkeep files
    for dir in "${directories[@]}"; do
        if [ ! -f "$dir/.gitkeep" ]; then
            touch "$dir/.gitkeep"
        fi
    done
    
    # Create .env from template if needed
    if [ ! -f "$ENV_FILE" ]; then
        echo ""
        echo -e "${BLUE}Creating environment configuration...${NC}"
        
        if [ -f ".env.example" ]; then
            cp .env.example "$ENV_FILE"
        else
            create_env_file
        fi
        
        # Generate secure keys
        generate_keys
        
        echo -e "${GREEN}✅ Environment file created${NC}"
        echo -e "${YELLOW}⚠️  Please edit .env and add your API keys!${NC}"
    fi
    
    # Set AIRFLOW_UID
    export AIRFLOW_UID=$(id -u)
    if ! grep -q "AIRFLOW_UID" "$ENV_FILE"; then
        echo "AIRFLOW_UID=$AIRFLOW_UID" >> "$ENV_FILE"
    fi
    
    echo ""
    echo -e "${GREEN}✅ Project structure initialized!${NC}"
}

# Create default .env file
create_env_file() {
    cat > "$ENV_FILE" << 'EOF'
# Application Configuration
HOST=0.0.0.0
PORT=8000
EXECUTION_MODE=hybrid  # standalone, airflow, or hybrid

# LLM Provider Configuration
LLM_PROVIDER=auto  # openai, ollama, or auto
OPENAI_API_KEY=your_openai_api_key
OPENAI_MODEL=gpt-4
OLLAMA_BASE_URL=http://localhost:11434

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
LANGFUSE_ENABLED=true
LANGFUSE_HOST=http://localhost:3001
LANGFUSE_SECRET_KEY=sk-lf-generated
LANGFUSE_PUBLIC_KEY=pk-lf-generated
LANGFUSE_NEXTAUTH_SECRET=generated
LANGFUSE_SALT=generated
LANGFUSE_ENCRYPTION_KEY=0000000000000000000000000000000000000000000000000000000000000000

# LangFuse Admin
LANGFUSE_ADMIN_EMAIL=admin@localhost
LANGFUSE_ADMIN_NAME=Admin
LANGFUSE_ADMIN_PASSWORD=admin123

# Security
JWT_SECRET_KEY=generated
JWT_ALGORITHM=HS256
JWT_EXPIRATION_MINUTES=1440

# Frontend Configuration
FRONTEND_URL=http://localhost:3000
REACT_APP_API_URL=http://localhost:8000
REACT_APP_AIRFLOW_URL=http://localhost:8080
EOF
}

# Generate security keys
generate_keys() {
    echo -e "${BLUE}Generating security keys...${NC}"
    
    # JWT Secret
    if grep -q "JWT_SECRET_KEY=generated" "$ENV_FILE"; then
        JWT_SECRET=$(generate_secure_key)
        sed -i.bak "s/JWT_SECRET_KEY=generated/JWT_SECRET_KEY=$JWT_SECRET/g" "$ENV_FILE"
    fi
    
    # LangFuse keys
    if grep -q "LANGFUSE_NEXTAUTH_SECRET=generated" "$ENV_FILE"; then
        NEXTAUTH_SECRET=$(generate_secure_key)
        sed -i.bak "s/LANGFUSE_NEXTAUTH_SECRET=generated/LANGFUSE_NEXTAUTH_SECRET=$NEXTAUTH_SECRET/g" "$ENV_FILE"
    fi
    
    if grep -q "LANGFUSE_SALT=generated" "$ENV_FILE"; then
        SALT=$(generate_secure_key)
        sed -i.bak "s/LANGFUSE_SALT=generated/LANGFUSE_SALT=$SALT/g" "$ENV_FILE"
    fi
    
    if grep -q "LANGFUSE_ENCRYPTION_KEY=0000000000000000000000000000000000000000000000000000000000000000" "$ENV_FILE"; then
        ENCRYPTION_KEY=$(generate_secure_key)
        sed -i.bak "s/0000000000000000000000000000000000000000000000000000000000000000/$ENCRYPTION_KEY/g" "$ENV_FILE"
    fi
    
    if grep -q "pk-lf-generated" "$ENV_FILE"; then
        PUBLIC_KEY="pk-lf-$(openssl rand -hex 16)"
        sed -i.bak "s/pk-lf-generated/$PUBLIC_KEY/g" "$ENV_FILE"
    fi
    
    if grep -q "sk-lf-generated" "$ENV_FILE"; then
        SECRET_KEY="sk-lf-$(openssl rand -hex 16)"
        sed -i.bak "s/sk-lf-generated/$SECRET_KEY/g" "$ENV_FILE"
    fi
    
    # Clean up backup files
    rm -f "$ENV_FILE.bak"
}

# Check prerequisites
check_prerequisites() {
    echo -e "${BLUE}Checking prerequisites...${NC}"
    
    local all_good=true
    
    check_command docker || all_good=false
    check_command docker-compose || all_good=false
    check_command python3 || all_good=false
    check_command npm || all_good=false
    
    if [ "$all_good" = false ]; then
        echo ""
        echo -e "${RED}❌ Some prerequisites are missing${NC}"
        return 1
    fi
    
    # Check Docker daemon
    if ! docker info >/dev/null 2>&1; then
        echo -e "${RED}❌ Docker daemon is not running${NC}"
        echo "   Please start Docker Desktop or the Docker service"
        return 1
    fi
    
    echo ""
    echo -e "${GREEN}✅ All prerequisites satisfied${NC}"
    return 0
}

# Build and start services
start_services() {
    echo -e "${BLUE}Starting LangGraph Flow services...${NC}"
    echo ""
    
    # Check if docker-compose file exists
    if [ ! -f "$COMPOSE_FILE" ]; then
        echo -e "${RED}❌ Docker compose file not found at $COMPOSE_FILE${NC}"
        echo "Creating docker directory and compose file..."
        mkdir -p docker
        # You would need to create the docker-compose.yml here
        echo -e "${YELLOW}Please ensure docker/docker-compose.yml exists${NC}"
        return 1
    fi
    
    # Load environment
    export AIRFLOW_UID=$(id -u)
    
    # Build images
    echo "Building Docker images..."
    docker-compose -f "$COMPOSE_FILE" build
    
    # Start services
    echo "Starting services..."
    docker-compose -f "$COMPOSE_FILE" up -d
    
    # Wait for services
    echo ""
    echo "⏳ Waiting for services to initialize (30 seconds)..."
    sleep 30
    
    # Check service health
    echo ""
    echo -e "${BLUE}Service Status:${NC}"
    docker-compose -f "$COMPOSE_FILE" ps
    
    show_access_info
}

# Stop services
stop_services() {
    echo -e "${BLUE}Stopping services...${NC}"
    docker-compose -f "$COMPOSE_FILE" down
    echo -e "${GREEN}✅ Services stopped${NC}"
}

# Clean everything
clean_all() {
    echo -e "${YELLOW}⚠️  This will remove all data and volumes!${NC}"
    read -p "Are you sure? (y/N) " -n 1 -r
    echo ""
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo -e "${BLUE}Cleaning up...${NC}"
        docker-compose -f "$COMPOSE_FILE" down -v
        rm -rf airflow/logs/*
        echo -e "${GREEN}✅ Cleanup complete${NC}"
    else
        echo "Cancelled"
    fi
}

# Setup Ollama
setup_ollama() {
    echo -e "${BLUE}Setting up Ollama for local LLM...${NC}"
    echo ""
    
    # Check if Ollama is installed
    if ! command -v ollama &> /dev/null; then
        echo "📦 Installing Ollama..."
        curl -fsSL https://ollama.ai/install.sh | sh
    else
        echo -e "${GREEN}✅ Ollama is already installed${NC}"
    fi
    
    # Start Ollama service
    echo "Starting Ollama service..."
    ollama serve &
    sleep 5
    
    # Pull models
    echo "📥 Pulling recommended models..."
    models=("llama2" "mistral" "nomic-embed-text")
    
    for model in "${models[@]}"; do
        echo "Pulling $model..."
        ollama pull $model
    done
    
    echo ""
    echo -e "${GREEN}✅ Ollama setup complete!${NC}"
    ollama list
}

# Test integration
test_integration() {
    echo -e "${BLUE}Testing LangGraph Flow integration...${NC}"
    echo ""
    
    # Run Python test script if it exists
    if [ -f "scripts/test_airflow_integration.py" ]; then
        python3 scripts/test_airflow_integration.py
    else
        # Basic health checks
        echo "Checking service health..."
        
        # Backend health
        if curl -s http://localhost:8000/health | grep -q "healthy"; then
            echo -e "${GREEN}✅ Backend is healthy${NC}"
        else
            echo -e "${RED}❌ Backend health check failed${NC}"
        fi
        
        # Airflow health
        if curl -s -u airflow:airflow http://localhost:8080/health | grep -q "healthy"; then
            echo -e "${GREEN}✅ Airflow is healthy${NC}"
        else
            echo -e "${RED}❌ Airflow health check failed${NC}"
        fi
        
        # LangFuse health
        if curl -s http://localhost:3001/api/public/health | grep -q "ok"; then
            echo -e "${GREEN}✅ LangFuse is healthy${NC}"
        else
            echo -e "${RED}❌ LangFuse health check failed${NC}"
        fi
    fi
}

# Show access information
show_access_info() {
    echo ""
    echo "======================================================================"
    echo -e "${GREEN}✅ LangGraph Flow is running!${NC}"
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
    echo "📈 LangFuse:          http://localhost:3001"
    source "$ENV_FILE"
    echo "   Email: ${LANGFUSE_ADMIN_EMAIL}"
    echo "   Password: ${LANGFUSE_ADMIN_PASSWORD}"
    echo ""
    echo "🌺 Flower (Celery):   http://localhost:5555"
    echo ""
    if [ "${LLM_PROVIDER}" = "ollama" ] || [ "${LLM_PROVIDER}" = "auto" ]; then
        echo "🦙 Ollama:           http://localhost:11434"
        echo ""
    fi
    echo "======================================================================"
}

# Show help
show_help() {
    echo "LangGraph Flow Setup Script v$VERSION"
    echo ""
    echo "Usage: $0 [command] [options]"
    echo ""
    echo "Commands:"
    echo "  init           Initialize project structure"
    echo "  start          Start all services"
    echo "  stop           Stop all services"
    echo "  restart        Restart all services"
    echo "  status         Show service status"
    echo "  logs [service] View service logs"
    echo "  test           Run integration tests"
    echo "  clean          Remove all data and volumes"
    echo "  setup-ollama   Setup Ollama for local LLMs"
    echo "  info           Show access information"
    echo "  help           Show this help message"
    echo ""
    echo "Quick start:"
    echo "  $0              # Run complete setup"
    echo "  $0 start        # Start services"
    echo "  $0 logs backend # View backend logs"
}

# Main command handler
main() {
    show_banner
    
    case "${1:-}" in
        init)
            init_project
            ;;
        start)
            check_prerequisites || exit 1
            start_services
            ;;
        stop)
            stop_services
            ;;
        restart)
            stop_services
            sleep 2
            start_services
            ;;
        status)
            docker-compose -f "$COMPOSE_FILE" ps
            ;;
        logs)
            if [ -z "${2:-}" ]; then
                docker-compose -f "$COMPOSE_FILE" logs -f
            else
                docker-compose -f "$COMPOSE_FILE" logs -f "$2"
            fi
            ;;
        test)
            test_integration
            ;;
        clean)
            clean_all
            ;;
        setup-ollama)
            setup_ollama
            ;;
        info)
            show_access_info
            ;;
        help)
            show_help
            ;;
        "")
            # Default: complete setup
            check_prerequisites || exit 1
            init_project
            
            echo ""
            read -p "Start services now? (Y/n) " -n 1 -r
            echo ""
            
            if [[ ! $REPLY =~ ^[Nn]$ ]]; then
                start_services
            fi
            ;;
        *)
            echo -e "${RED}Unknown command: $1${NC}"
            echo ""
            show_help
            exit 1
            ;;
    esac
}

# Run main function
main "$@"