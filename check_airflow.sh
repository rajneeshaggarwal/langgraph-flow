#!/bin/bash

# Script to diagnose Airflow initialization issues

echo "🔍 Diagnosing Airflow Issues"
echo "============================"
echo ""

# Check container logs
echo "📋 Checking Airflow init container logs..."
echo "----------------------------------------"
docker logs docker-airflow-init-1 2>&1 | tail -50

echo ""
echo "📋 Checking if database is accessible..."
echo "----------------------------------------"
docker exec docker-postgres-1 psql -U airflow -c "SELECT 1;" 2>&1

echo ""
echo "📋 Checking Airflow directories..."
echo "----------------------------------------"
ls -la airflow/
ls -la airflow/dags/ 2>/dev/null || echo "  No dags directory"
ls -la airflow/plugins/ 2>/dev/null || echo "  No plugins directory"

echo ""
echo "📋 Checking environment variables in .env..."
echo "----------------------------------------"
grep -E "AIRFLOW_UID|_AIRFLOW_WWW_USER" .env

echo ""
echo "💡 Common fixes:"
echo ""
echo "1. Set correct AIRFLOW_UID:"
echo "   echo 'AIRFLOW_UID=$(id -u)' >> .env"
echo ""
echo "2. Create missing directories:"
echo "   mkdir -p airflow/dags airflow/plugins airflow/logs"
echo ""
echo "3. Reset Airflow database:"
echo "   docker-compose -f docker/docker-compose.yml down -v"
echo "   docker-compose -f docker/docker-compose.yml up postgres -d"
echo "   sleep 10"
echo "   docker-compose -f docker/docker-compose.yml up airflow-init"
echo ""
echo "4. Or skip Airflow and use minimal mode:"
echo "   ./start_minimal.sh"