#!/bin/bash

echo "🔍 Setting up Local LangFuse for LangGraph Flow"
echo "=============================================="
echo ""

# Color codes
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Function to generate secure keys
generate_secure_key() {
    openssl rand -hex 32
}

# Check if .env exists
if [ ! -f .env ]; then
    echo -e "${RED}❌ .env file not found. Creating from template...${NC}"
    cp .env.example .env
fi

# Generate security keys if using defaults
echo "🔐 Checking security keys..."

if grep -q "your-nextauth-secret-change-in-production" .env; then
    echo "  Generating LANGFUSE_NEXTAUTH_SECRET..."
    NEXTAUTH_SECRET=$(generate_secure_key)
    sed -i.bak "s/your-nextauth-secret-change-in-production/$NEXTAUTH_SECRET/g" .env
fi

if grep -q "your-salt-change-in-production" .env; then
    echo "  Generating LANGFUSE_SALT..."
    SALT=$(generate_secure_key)
    sed -i.bak "s/your-salt-change-in-production/$SALT/g" .env
fi

if grep -q "0000000000000000000000000000000000000000000000000000000000000000" .env; then
    echo "  Generating LANGFUSE_ENCRYPTION_KEY..."
    ENCRYPTION_KEY=$(generate_secure_key)
    sed -i.bak "s/0000000000000000000000000000000000000000000000000000000000000000/$ENCRYPTION_KEY/g" .env
fi

# Generate API keys if using defaults
if grep -q "pk-lf-default-public" .env; then
    echo "  Generating LANGFUSE_PUBLIC_KEY..."
    PUBLIC_KEY="pk-lf-$(openssl rand -hex 16)"
    sed -i.bak "s/pk-lf-default-public/$PUBLIC_KEY/g" .env
fi

if grep -q "sk-lf-default-secret" .env; then
    echo "  Generating LANGFUSE_SECRET_KEY..."
    SECRET_KEY="sk-lf-$(openssl rand -hex 16)"
    sed -i.bak "s/sk-lf-default-secret/$SECRET_KEY/g" .env
fi

# Update LangFuse host
sed -i.bak "s|https://cloud.langfuse.com|http://localhost:3001|g" .env

echo -e "${GREEN}✅ Security keys generated${NC}"
echo ""

# Extract values for display
source .env

echo "📋 LangFuse Configuration:"
echo "========================="
echo "URL:        http://localhost:3001"
echo "Email:      ${LANGFUSE_ADMIN_EMAIL}"
echo "Password:   ${LANGFUSE_ADMIN_PASSWORD}"
echo ""
echo "API Keys for your application:"
echo "Public Key:  ${LANGFUSE_PUBLIC_KEY}"
echo "Secret Key:  ${LANGFUSE_SECRET_KEY}"
echo ""
echo -e "${YELLOW}⚠️  Save these credentials! The secret key won't be shown again.${NC}"
echo ""

# Create data directories
echo "📁 Creating data directories..."
mkdir -p langfuse/data
echo -e "${GREEN}✅ Directories created${NC}"
echo ""

# Start LangFuse services
echo "🚀 Starting LangFuse services..."
docker-compose -f docker/docker-compose.airflow.yml up -d langfuse-postgres langfuse

# Wait for services
echo "⏳ Waiting for LangFuse to initialize (30 seconds)..."
sleep 30

# Check health
echo "🏥 Checking LangFuse health..."
if curl -s http://localhost:3001/api/public/health | grep -q "ok"; then
    echo -e "${GREEN}✅ LangFuse is healthy!${NC}"
else
    echo -e "${RED}❌ LangFuse health check failed${NC}"
    echo "Check logs: docker-compose -f docker/docker-compose.airflow.yml logs langfuse"
fi

echo ""
echo "✨ LangFuse setup complete!"
echo ""
echo "Access LangFuse at: http://localhost:3001"
echo ""
echo "To stop LangFuse: docker-compose -f docker/docker-compose.airflow.yml stop langfuse langfuse-postgres"