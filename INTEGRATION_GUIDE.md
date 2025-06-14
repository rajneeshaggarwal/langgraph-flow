# Complete Airflow Integration Guide for LangGraph Flow

This guide provides step-by-step instructions for integrating Apache Airflow with your LangGraph Flow Visual AI Framework.

## 📋 Table of Contents

1. [Overview](#overview)
2. [File Structure](#file-structure)
3. [Installation Steps](#installation-steps)
4. [Configuration](#configuration)
5. [Running the System](#running-the-system)
6. [Using the Integration](#using-the-integration)
7. [Monitoring and Debugging](#monitoring-and-debugging)
8. [Production Deployment](#production-deployment)
9. [Troubleshooting](#troubleshooting)

## Overview

The Airflow integration adds enterprise-grade workflow orchestration to your LangGraph Flow application, enabling:

- **Scalable Execution**: Run complex AI workflows across distributed workers
- **Retry Logic**: Automatic retry with exponential backoff for transient failures
- **Monitoring**: Real-time workflow status and comprehensive metrics
- **Multi-Agent Coordination**: Orchestrate multiple LangGraph agents with dependencies
- **Production Ready**: Full observability, error handling, and security

## File Structure

Add these files to your existing LangGraph Flow project:

```
langgraph-flow/
├── airflow/
│   ├── dags/
│   │   ├── visual_ai_workflow_dag.py        # Basic workflow DAG
│   │   └── multi_agent_dag.py               # Multi-agent orchestration DAG
│   ├── plugins/
│   │   └── visual_ai_operators.py           # Custom Airflow operators
│   └── logs/                                 # Auto-created log directory
├── backend/
│   ├── api/
│   │   ├── workflow_triggers.py             # API for triggering workflows
│   │   ├── workflow_status.py               # Real-time status endpoints
│   │   └── monitoring.py                    # Monitoring and metrics
│   ├── core/
│   │   └── workflow_error_handler.py        # Error handling logic
│   └── main.py                              # Updated main application
├── frontend/
│   └── src/
│       └── components/
│           ├── WorkflowMonitor.tsx          # Workflow monitoring UI
│           └── WorkflowTrigger.tsx          # Workflow trigger UI
├── database/
│   └── migrations/
│       └── 001_visual_ai_schema.sql         # Database schema
├── docker/
│   ├── Dockerfile.airflow                   # Airflow Docker image
│   └── docker-compose.airflow.yml           # Docker Compose configuration
├── scripts/
│   ├── setup_airflow.sh                     # Setup script
│   └── test_airflow_integration.py          # Integration tests
├── langgraph_flow/
│   ├── agents/
│   │   └── airflow_integration.py           # Airflow integration module
│   └── app_with_airflow.py                  # Modified app with Airflow support
├── .env.example                             # Environment variables template
├── requirements-airflow.txt                 # Python dependencies
├── AIRFLOW_INTEGRATION.md                   # Integration documentation
└── INTEGRATION_GUIDE.md                     # This file
```

## Installation Steps

### 1. Prerequisites

Ensure you have:
- Docker and Docker Compose installed
- Python 3.11+
- At least 4GB RAM available
- The base LangGraph Flow project from the `airflow-support` branch

### 2. Clone and Setup

```bash
# Clone the repository with airflow-support branch
git clone -b airflow-support https://github.com/rajneeshaggarwal/langgraph-flow.git
cd langgraph-flow

# Make setup script executable
chmod +x scripts/setup_airflow.sh

# Run the setup script
./scripts/setup_airflow.sh
```

### 3. Configure Environment

```bash
# Copy environment template
cp .env.example .env

# Edit .env file with your configuration
nano .env
```

Required configuration:
- `OPENAI_API_KEY`: Your OpenAI API key
- `LANGFUSE_SECRET_KEY` and `LANGFUSE_PUBLIC_KEY`: LangFuse credentials
- Database and Redis settings (defaults work for local development)

### 4. Initialize Services

The setup script automatically:
- Creates necessary directories
- Builds Docker images
- Initializes databases
- Creates admin user
- Starts all services

## Configuration

### Environment Variables

Key environment variables in `.env`:

```env
# Airflow Configuration
AIRFLOW_URL=http://localhost:8080
AIRFLOW_USERNAME=airflow
AIRFLOW_PASSWORD=airflow

# LangFuse Configuration
LANGFUSE_SECRET_KEY=your_secret_key
LANGFUSE_PUBLIC_KEY=your_public_key

# OpenAI Configuration
OPENAI_API_KEY=your_api_key

# Execution Mode
EXECUTION_MODE=hybrid  # Options: standalone, airflow, hybrid
```

### Airflow DAG Configuration

DAGs are automatically loaded from `airflow/dags/`. The default DAGs include:
- `visual_ai_workflow`: Basic single-agent workflow
- `visual_ai_multi_agent_pipeline`: Multi-agent orchestration

## Running the System

### Start All Services

```bash
# Start with Docker Compose
docker-compose -f docker/docker-compose.airflow.yml up -d

# Check service status
docker-compose -f docker/docker-compose.airflow.yml ps
```

### Access Services

- **Airflow UI**: http://localhost:8080 (Username: airflow, Password: airflow)
- **FastAPI Backend**: http://localhost:8000/docs
- **Frontend**: http://localhost:3000
- **Flower (Celery Monitor)**: http://localhost:5555

### Run Integration Tests

```bash
# Run the test script
python scripts/test_airflow_integration.py
```

## Using the Integration

### 1. Via Frontend UI

Navigate to http://localhost:3000 and:

1. Go to "Trigger Workflow" section
2. Select a workflow template or create custom configuration
3. Click "Trigger Workflow"
4. Monitor real-time progress in the workflow monitor

### 2. Via API

```python
import httpx

# Trigger a workflow
response = httpx.post(
    "http://localhost:8000/api/v1/workflows/trigger",
    json={
        "dag_id": "visual_ai_workflow",
        "input_data": {
            "query": "Analyze this image",
            "image_url": "https://example.com/image.jpg"
        }
    },
    headers={"Authorization": "Bearer your_token"}
)

dag_run_id = response.json()["dag_run_id"]
print(f"Workflow triggered: {dag_run_id}")
```

### 3. Via Airflow UI

1. Navigate to http://localhost:8080
2. Find your DAG (e.g., `visual_ai_workflow`)
3. Click "Trigger DAG"
4. Provide configuration JSON
5. Monitor execution in the Graph view

## Monitoring and Debugging

### Real-time Monitoring

```javascript
// Subscribe to workflow updates
const eventSource = new EventSource(
    `/api/v1/workflow-status/stream/${dagId}/${dagRunId}`
);

eventSource.addEventListener('workflow_update', (event) => {
    const status = JSON.parse(event.data);
    console.log('Status:', status.state, 'Progress:', status.progress);
});
```

### Metrics and Analytics

Access monitoring endpoints:

```bash
# Workflow metrics
curl http://localhost:8000/api/v1/monitoring/workflow-metrics

# Agent performance
curl http://localhost:8000/api/v1/monitoring/agent-performance

# Error distribution
curl http://localhost:8000/api/v1/monitoring/error-distribution
```

### Debugging

1. **Check Airflow Logs**:
   ```bash
   docker-compose -f docker/docker-compose.airflow.yml logs -f airflow-scheduler
   ```

2. **View Task Logs in Airflow UI**:
   - Navigate to DAG → Graph View
   - Click on failed task
   - View logs

3. **Check LangFuse Traces**:
   - Go to your LangFuse dashboard
   - Filter by `dag_run_id`
   - Analyze LLM calls and errors

## Production Deployment

### 1. Use Kubernetes Executor

Update `docker-compose.airflow.yml`:

```yaml
environment:
  AIRFLOW__CORE__EXECUTOR: KubernetesExecutor
```

### 2. Configure External Databases

```env
# Production PostgreSQL
POSTGRES_HOST=your-rds-instance.amazonaws.com
POSTGRES_DB=airflow_prod
POSTGRES_USER=airflow_prod
POSTGRES_PASSWORD=secure_password

# Production Redis
REDIS_URL=redis://your-elasticache-instance:6379
```

### 3. Enable Authentication

```python
# In backend/main.py
from fastapi_users import FastAPIUsers
# Add proper authentication
```

### 4. Set Resource Limits

In `docker-compose.airflow.yml`:

```yaml
services:
  airflow-worker:
    deploy:
      resources:
        limits:
          cpus: '2.0'
          memory: 4G
```

## Troubleshooting

### Common Issues

1. **Airflow webserver not starting**
   ```bash
   # Check logs
   docker-compose -f docker/docker-compose.airflow.yml logs airflow-webserver
   
   # Restart service
   docker-compose -f docker/docker-compose.airflow.yml restart airflow-webserver
   ```

2. **DAGs not appearing**
   ```bash
   # Check DAG syntax
   docker-compose -f docker/docker-compose.airflow.yml exec airflow-webserver python -m py_compile /opt/airflow/dags/*.py
   
   # Reload DAGs
   docker-compose -f docker/docker-compose.airflow.yml exec airflow-webserver airflow dags reserialize
   ```

3. **Workflow execution fails**
   - Check task logs in Airflow UI
   - Verify API keys in `.env`
   - Check LangFuse traces
   - Review `visual_ai.workflow_errors` table

4. **Real-time updates not working**
   - Ensure CORS is configured correctly
   - Check WebSocket connection
   - Verify authentication tokens

### Reset Everything

```bash
# Stop all services
docker-compose -f docker/docker-compose.airflow.yml down

# Remove all data
docker-compose -f docker/docker-compose.airflow.yml down -v

# Start fresh
./scripts/setup_airflow.sh
```

## Next Steps

1. **Customize DAGs**: Create your own DAGs in `airflow/dags/`
2. **Add Tools**: Extend LangGraph agents with custom tools
3. **Configure Alerts**: Set up email/Slack notifications
4. **Scale Workers**: Add more Airflow workers for parallel execution
5. **Implement CI/CD**: Automate DAG deployment

## Support

- Check logs first: `docker-compose logs [service-name]`
- Review LangFuse traces for LLM debugging
- Query monitoring endpoints for system health
- Open an issue on GitHub with relevant logs

---

This integration brings enterprise-grade workflow orchestration to your Visual AI Framework. Happy orchestrating! 🚀