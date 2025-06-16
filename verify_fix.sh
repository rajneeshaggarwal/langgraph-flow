#!/bin/bash

# Script to verify the fix worked

echo "🔍 Verifying LangGraph Flow Setup"
echo "================================="
echo ""

# 1. Check environment variables
echo "📋 Checking .env file..."
if [ -f ".env" ]; then
    echo "✅ .env exists"
    echo ""
    echo "Key variables:"
    grep -E "^(LANGFUSE_PUBLIC_KEY|LANGFUSE_SECRET_KEY|JWT_SECRET_KEY|OPENAI_API_KEY|AIRFLOW_UID)=" .env | while read line; do
        key=$(echo $line | cut -d'=' -f1)
        value=$(echo $line | cut -d'=' -f2)
        if [[ "$value" == *"change-me"* ]] || [[ "$value" == *"your_"* ]] || [[ -z "$value" ]]; then
            echo "  ❌ $key = $value (needs to be updated)"
        else
            echo "  ✅ $key = ${value:0:20}... (set)"
        fi
    done
else
    echo "❌ No .env file found!"
fi

echo ""

# 2. Check running containers
echo "🐳 Checking Docker containers..."
running_containers=$(docker ps --format "{{.Names}}" | grep -E "(backend|frontend|postgres|redis|langfuse|ollama)" | wc -l)
echo "Running containers: $running_containers"
docker ps --format "table {{.Names}}\t{{.Status}}" | grep -E "(backend|frontend|postgres|redis|langfuse|ollama)"

echo ""

# 3. Test services
echo "🧪 Testing service endpoints..."
echo ""

# Backend
echo -n "Backend API (http://localhost:8000): "
if curl -s -f http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ Running"
else
    echo "❌ Not responding"
fi

# Frontend
echo -n "Frontend (http://localhost:3000): "
if curl -s -f http://localhost:3000 > /dev/null 2>&1; then
    echo "✅ Running"
else
    echo "❌ Not responding"
fi

# LangFuse
echo -n "LangFuse (http://localhost:3001): "
if curl -s -f http://localhost:3001/api/public/health > /dev/null 2>&1; then
    echo "✅ Running"
else
    echo "⏳ Still starting (can take 1-2 minutes)"
fi

# Ollama
echo -n "Ollama (http://localhost:11434): "
if curl -s -f http://localhost:11434/api/tags > /dev/null 2>&1; then
    echo "✅ Running"
else
    echo "❌ Not responding"
fi

echo ""

# 4. Summary
echo "📊 Summary:"
if [ $running_containers -ge 6 ]; then
    echo "✅ All core services appear to be running!"
    echo ""
    echo "🎉 You can now access:"
    echo "  - API Documentation: http://localhost:8000/docs"
    echo "  - Frontend App: http://localhost:3000"
    echo "  - LangFuse Tracing: http://localhost:3001"
    echo ""
    echo "⚠️  Note: Airflow is not running (workflow orchestration disabled)"
else
    echo "⚠️  Some services may still be starting..."
    echo "Run 'docker ps' to check status"
    echo "Run 'docker-compose -f docker/docker-compose.yml logs [service-name]' to check logs"
fi