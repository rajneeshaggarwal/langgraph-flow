# Troubleshooting Guide for LangGraph Flow Airflow Integration

## Common Issues and Solutions

### 1. Quickstart Script Fails with "Not in repository root" Error

**Problem:**
```bash
❌ Error: Please run this script from the root of the langgraph-flow repository
```

**Solution:**
1. Make sure you're in the correct directory:
   ```bash
   pwd  # Should show path to langgraph-flow directory
   ls   # Should show files like README.md, setup.py, etc.
   ```

2. Run the initialization script first:
   ```bash
   chmod +x init_airflow_integration.sh
   ./init_airflow_integration.sh
   ```

3. Check if all required files are present:
   ```bash
   chmod +x scripts/check_setup.sh
   ./scripts/check_setup.sh
   ```

### 2. Missing Airflow Integration Files

**Problem:**
The integration files (DAGs, Docker configs, etc.) are not present.

**Solution:**
1. The integration files need to be added to your project. You have two options:

   **Option A: Manual Setup**
   - Create the files manually from the documentation
   - Place them in the correct directories as shown in the check_setup.sh output

   **Option B: Use the provided files**
   - All required files are documented in `AIRFLOW_INTEGRATION_SUMMARY.md`
   - Copy each file content to the appropriate location

2. Directory structure should look like:
   ```
   langgraph-flow/
   ├── airflow/
   │   ├── dags/
   │   │   ├── visual_ai_workflow_dag.py
   │   │   └── multi_agent_dag.py
   │   └── plugins/
   │       └── visual_ai_operators.py
   ├── backend/
   │   ├── api/
   │   │   ├── workflow_triggers.py
   │   │   ├── workflow_status.py
   │   │   └── monitoring.py
   │   └── core/
   │       └── workflow_error_handler.py
   ├── docker/
   │   ├── Dockerfile.airflow
   │   └── docker-compose.airflow.yml
   └── database/
       └── migrations/
           └── 001_visual_ai_schema.sql
   ```

### 3. Docker Compose File Not Found

**Problem:**
```bash
docker-compose: docker/docker-compose.airflow.yml: no such file or directory
```

**Solution:**
1. Ensure the docker directory exists:
   ```bash
   mkdir -p docker
   ```

2. Add the `docker-compose.airflow.yml` file from the integration documentation

3. Verify the file exists:
   ```bash
   ls -la docker/docker-compose.airflow.yml
   ```

### 4. Environment Variables Not Set

**Problem:**
Services fail to start due to missing environment variables.

**Solution:**
1. Copy the example environment file:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` and add your API keys:
   ```bash
   nano .env  # or use your preferred editor
   ```

3. Required keys to update:
   - `OPENAI_API_KEY`
   - `LANGFUSE_SECRET_KEY`
   - `LANGFUSE_PUBLIC_KEY`

### 5. Docker Not Running

**Problem:**
```bash
Cannot connect to the Docker daemon
```

**Solution:**
1. Start Docker Desktop (on macOS/Windows) or Docker service (on Linux)

2. Verify Docker is running:
   ```bash
   docker info
   ```

3. Check Docker Compose is installed:
   ```bash
   docker-compose --version
   ```

### 6. Port Already in Use

**Problem:**
```bash
bind: address already in use
```

**Solution:**
1. Check which ports are in use:
   ```bash
   # Check port 8080 (Airflow)
   lsof -i :8080
   
   # Check port 8000 (FastAPI)
   lsof -i :8000
   
   # Check port 3000 (Frontend)
   lsof -i :3000
   ```

2. Stop conflicting services or change ports in `.env` and `docker-compose.airflow.yml`

### 7. Airflow DAGs Not Showing Up

**Problem:**
DAGs don't appear in Airflow UI.

**Solution:**
1. Check DAG syntax:
   ```bash
   docker-compose -f docker/docker-compose.airflow.yml exec airflow-webserver python -m py_compile /opt/airflow/dags/*.py
   ```

2. Check Airflow logs:
   ```bash
   docker-compose -f docker/docker-compose.airflow.yml logs airflow-scheduler
   ```

3. Reload DAGs:
   ```bash
   docker-compose -f docker/docker-compose.airflow.yml exec airflow-webserver airflow dags reserialize
   ```

## Getting Help

If you're still having issues:

1. Run the diagnostic script:
   ```bash
   ./scripts/check_setup.sh > setup_diagnostic.txt
   ```

2. Check all service logs:
   ```bash
   docker-compose -f docker/docker-compose.airflow.yml logs > services.log
   ```

3. Open an issue on GitHub with:
   - The error message
   - Output of the diagnostic script
   - Relevant log files
   - Steps you've already tried

## Quick Recovery

To start fresh:

```bash
# Stop all services and remove data
docker-compose -f docker/docker-compose.airflow.yml down -v

# Remove directories
rm -rf airflow/logs/*

# Re-initialize
./init_airflow_integration.sh

# Add the integration files again

# Start services
./quickstart.sh
```