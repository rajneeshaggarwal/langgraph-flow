# Apache Airflow Integration for LangGraph Flow

This document provides comprehensive instructions for integrating Apache Airflow with your LangGraph Flow Visual AI Framework.

## Overview

The integration adds the following capabilities to your Visual AI Framework:

- **Workflow Orchestration**: Use Apache Airflow to schedule and manage complex AI workflows
- **Multi-Agent Coordination**: Orchestrate multiple LangGraph agents with dependencies
- **Production-Ready Infrastructure**: Scalable deployment with Kubernetes executor
- **Comprehensive Observability**: Full tracing with LangFuse integration
- **Real-time Monitoring**: SSE-based status updates and monitoring dashboards
- **Error Handling**: Intelligent retry logic and error recovery

## Quick Start

### 1. Prerequisites

- Docker and Docker Compose installed
- Python 3.11+
- At least 4GB RAM available
- Environment variables configured (see `.env.example`)

### 2. Environment Setup

Create a `.env` file in the project root:

```env
# Airflow Configuration
AIRFLOW_UID=50000
_AIRFLOW_WWW_USER_USERNAME=airflow
_AIRFLOW_WWW_USER_PASSWORD=airflow

# LangFuse Configuration
LANGFUSE_SECRET_KEY=your_langfuse_secret_key
LANGFUSE_PUBLIC_KEY=your_langfuse_public_key
LANGFUSE_HOST=https://cloud.langfuse.com

# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key

# Database Configuration
POSTGRES_HOST=postgres
POSTGRES_DB=airflow
POSTGRES_USER=airflow
POSTGRES_PASSWORD=airflow
```

### 3. Start the Services

```bash
# Start all services
docker-compose -f docker/docker-compose.airflow.yml up -d

# Check service health
docker-compose -f docker/docker-compose.airflow.yml ps

# View logs
docker-compose -f docker/docker-compose.airflow.yml logs -f
```

### 4. Access the Services

- **Airflow UI**: http://localhost:8080 (Username: airflow, Password: airflow)
- **FastAPI Backend**: http://localhost:8000/docs
- **Frontend**: http://localhost:3000

## Project Structure

```
langgraph-flow/
├── airflow/
│   ├── dags/                    # Airflow DAG definitions
│   │   ├── visual_ai_workflow_dag.py
│   │   └── multi_agent_dag.py
│   ├── plugins/                 # Custom Airflow operators
│   │   └── visual_ai_operators.py
│   └── logs/                    # Airflow logs (auto-created)
├── backend/
│   ├── api/
│   │   ├── workflow_triggers.py # API for triggering DAGs
│   │   ├── workflow_status.py   # Real-time status updates
│   │   └── monitoring.py        # Monitoring endpoints
│   └── core/
│       └── workflow_error_handler.py
└── database/
    └── migrations/
        └── 001_visual_ai_schema.sql
```

## Key Features

### 1. Triggering Workflows via API

```python
import httpx

# Trigger a workflow
response = httpx.post(
    "http://localhost:8000/workflows/trigger",
    json={
        "dag_id": "visual_ai_workflow",
        "input_data": {
            "query": "Analyze this image and extract insights",
            "image_url": "https://example.com/image.jpg"
        },
        "user_id": "user123"
    },
    headers={"Authorization": "Bearer your_token"}
)

dag_run_id = response.json()["dag_run_id"]
```

### 2. Real-time Status Monitoring

```javascript
// Subscribe to workflow status updates
const eventSource = new EventSource(
    `/workflow-status/stream/${dagId}/${dagRunId}`
);

eventSource.addEventListener('workflow_update', (event) => {
    const status = JSON.parse(event.data);
    console.log('Workflow status:', status.state);
    console.log('Progress:', status.progress);
});

eventSource.addEventListener('task_update', (event) => {
    const task = JSON.parse(event.data);
    console.log('Task updated:', task.task_id, task.state);
});
```

### 3. Custom Airflow Operators

```python
from airflow import DAG
from visual_ai_operators import LangGraphOperator, MultiAgentOperator

# Single agent execution
single_agent = LangGraphOperator(
    task_id='analyze_image',
    agent_config={'type': 'vision'},
    input_data={'image_url': '{{ dag_run.conf.image_url }}'},
    model='gpt-4-vision-preview'
)

# Multi-agent orchestration
multi_agent = MultiAgentOperator(
    task_id='multi_agent_analysis',
    agents=[
        {'name': 'vision', 'type': 'vision', 'input_data': {...}},
        {'name': 'text', 'type': 'text', 'input_data': {...}}
    ],
    orchestration_mode='parallel'
)
```

### 4. Error Handling and Retry Logic

The integration includes intelligent error handling:

- **Rate Limit Errors**: Exponential backoff with up to 5 retries
- **API Timeout**: 3 retries with shorter timeouts
- **Context Length Errors**: Automatic fallback to smaller models
- **All errors**: Stored in database with full context for debugging

### 5. Monitoring Dashboard

Access comprehensive metrics via the monitoring API:

```bash
# Get workflow metrics
curl http://localhost:8000/monitoring/workflow-metrics?time_range=24h

# Get agent performance
curl http://localhost:8000/monitoring/agent-performance

# Get error distribution
curl http://localhost:8000/monitoring/error-distribution

# Check system health
curl http://localhost:8000/monitoring/system-health
```

## Database Schema

The integration creates a `visual_ai` schema with the following tables:

- `workflow_executions`: Tracks all workflow runs
- `agent_traces`: Individual agent execution details
- `workflow_errors`: Error tracking and debugging
- `user_preferences`: User-specific settings
- `workflow_templates`: Reusable workflow templates

## Development Workflow

### 1. Creating New DAGs

Create a new DAG in `airflow/dags/`:

```python
from airflow import DAG
from datetime import datetime, timedelta
from visual_ai_operators import LangGraphOperator

default_args = {
    'owner': 'visual-ai-team',
    'retries': 2,
    'retry_delay': timedelta(minutes=5)
}

dag = DAG(
    'my_custom_workflow',
    default_args=default_args,
    description='Custom Visual AI workflow',
    schedule_interval=None,
    start_date=datetime(2024, 1, 1),
    tags=['visual-ai', 'custom']
)

# Add your tasks here
```

### 2. Testing DAGs Locally

```bash
# Test DAG syntax
docker-compose -f docker/docker-compose.airflow.yml exec airflow-webserver airflow dags test visual_ai_workflow

# Trigger DAG manually
docker-compose -f docker/docker-compose.airflow.yml exec airflow-webserver airflow dags trigger visual_ai_workflow
```

### 3. Debugging

- Check Airflow logs: `airflow/logs/`
- View task logs in Airflow UI
- Monitor LangFuse traces at https://cloud.langfuse.com
- Check PostgreSQL for workflow execution details

## Production Deployment

### 1. Kubernetes Deployment

For production, use the Kubernetes executor:

```yaml
# airflow-values.yaml
executor: KubernetesExecutor

config:
  AIRFLOW__KUBERNETES__NAMESPACE: airflow
  AIRFLOW__KUBERNETES__WORKER_CONTAINER_REPOSITORY: your-registry/airflow-worker
  AIRFLOW__KUBERNETES__WORKER_CONTAINER_TAG: latest
```

### 2. Scaling Considerations

- Use Redis Sentinel for high availability
- Deploy PostgreSQL with replication
- Configure autoscaling for worker pods
- Use persistent volumes for logs

### 3. Security

- Enable RBAC in Airflow
- Use JWT tokens for API authentication
- Configure SSL/TLS for all services
- Implement network policies in Kubernetes

## Troubleshooting

### Common Issues

1. **Airflow webserver not starting**
   - Check logs: `docker-compose logs airflow-webserver`
   - Ensure database migrations completed
   - Verify environment variables

2. **Workflow execution fails**
   - Check task logs in Airflow UI
   - Verify LangFuse traces
   - Check error details in `visual_ai.workflow_errors` table

3. **Real-time updates not working**
   - Ensure WebSocket connection is established
   - Check CORS settings
   - Verify Nginx configuration (if using)

### Getting Help

- Check the logs first
- Review LangFuse traces for agent execution details
- Query the monitoring endpoints for system health
- Open an issue on GitHub with relevant logs

## Next Steps

1. Customize the DAGs for your specific use cases
2. Add more custom operators as needed
3. Configure alerts and notifications
4. Integrate with your existing MLOps infrastructure
5. Set up CI/CD for DAG deployment

For more details, refer to the Apache Airflow documentation and the LangGraph documentation.