# LangGraph Flow - Complete Documentation

## Table of Contents

1. [Overview](#overview)
2. [Quick Start](#quick-start)
3. [Installation Guide](#installation-guide)
4. [Configuration](#configuration)
5. [Apache Airflow Integration](#apache-airflow-integration)
6. [Local Services Setup](#local-services-setup)
7. [Usage](#usage)
8. [API Reference](#api-reference)
9. [Troubleshooting](#troubleshooting)
10. [File Structure](#file-structure)

## Overview

LangGraph Flow is a visual flow framework for building multi-agent and RAG applications using LangGraph as the orchestration engine. This framework provides an intuitive drag-and-drop interface for creating complex AI workflows without writing extensive code.

### Key Features

- **Visual Workflow Builder**: Drag-and-drop interface for creating AI workflows
- **Apache Airflow Integration**: Enterprise-grade workflow orchestration
- **Multi-LLM Support**: OpenAI, Ollama, and auto-selection
- **Real-time Monitoring**: WebSocket-based updates and LangFuse tracing
- **Production Ready**: Kubernetes support, error handling, and security

### Tech Stack

**Backend**: Python 3.11+, FastAPI, LangGraph, PostgreSQL, SQLAlchemy
**Frontend**: React 18, TypeScript, React Flow, Tailwind CSS
**Orchestration**: Apache Airflow, Celery, Redis
**Observability**: LangFuse, OpenTelemetry

## Quick Start

```bash
# 1. Clone the repository
git clone -b airflow-support https://github.com/rajneeshaggarwal/langgraph-flow.git
cd langgraph-flow

# 2. Run the setup script
chmod +x setup.sh
./setup.sh

# 3. Access the services
# Airflow UI: http://localhost:8080 (airflow/airflow)
# Backend API: http://localhost:8000/docs
# Frontend: http://localhost:3000
# LangFuse: http://localhost:3001
```

## Installation Guide

### Prerequisites

- Docker and Docker Compose
- Python 3.11+
- Node.js 20+
- 4GB+ RAM available

### Step-by-Step Installation

1. **Initialize the project structure**
   ```bash
   ./setup.sh init
   ```

2. **Configure environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys:
   # - OPENAI_API_KEY
   # - LANGFUSE_SECRET_KEY
   # - LANGFUSE_PUBLIC_KEY
   ```

3. **Start all services**
   ```bash
   ./setup.sh start
   ```

4. **Verify installation**
   ```bash
   ./setup.sh test
   ```

## Configuration

### Environment Variables

```env
# Application Mode
EXECUTION_MODE=hybrid  # standalone, airflow, or hybrid

# LLM Provider
LLM_PROVIDER=auto  # openai, ollama, or auto
OPENAI_API_KEY=your_key
OLLAMA_BASE_URL=http://localhost:11434

# Airflow
AIRFLOW_URL=http://localhost:8080
AIRFLOW_USERNAME=airflow
AIRFLOW_PASSWORD=airflow

# LangFuse
LANGFUSE_HOST=http://localhost:3001
LANGFUSE_SECRET_KEY=auto_generated
LANGFUSE_PUBLIC_KEY=auto_generated

# Database
DATABASE_URL=postgresql://airflow:airflow@postgres/airflow
```

### Security Configuration

The setup script automatically generates:
- JWT secret keys
- LangFuse encryption keys
- Database passwords

For production, ensure all keys are properly secured.

## Apache Airflow Integration

### Overview

The Airflow integration adds:
- **Workflow Orchestration**: Schedule and manage complex AI workflows
- **Multi-Agent Coordination**: Orchestrate multiple LangGraph agents
- **Production Infrastructure**: Scalable deployment with Kubernetes support
- **Comprehensive Observability**: Full tracing with LangFuse
- **Error Handling**: Intelligent retry logic and recovery

### Key Components

#### Custom Operators

```python
# LangGraphOperator - Execute single agents
single_agent = LangGraphOperator(
    task_id='analyze_image',
    agent_config={'type': 'vision'},
    input_data={'image_url': '{{ dag_run.conf.image_url }}'}
)

# MultiAgentOperator - Orchestrate multiple agents
multi_agent = MultiAgentOperator(
    task_id='multi_agent_analysis',
    agents=[
        {'name': 'vision', 'type': 'vision'},
        {'name': 'text', 'type': 'text'}
    ],
    orchestration_mode='parallel'
)
```

#### Workflow Triggers

```python
# Trigger via API
response = httpx.post(
    "http://localhost:8000/api/v1/workflows/trigger",
    json={
        "dag_id": "visual_ai_workflow",
        "input_data": {"query": "Analyze this image"},
        "user_id": "user123"
    }
)
```

#### Real-time Monitoring

```javascript
// Subscribe to updates
const eventSource = new EventSource(
    `/api/v1/workflow-status/stream/${dagId}/${dagRunId}`
);

eventSource.addEventListener('workflow_update', (event) => {
    const status = JSON.parse(event.data);
    console.log('Status:', status.state, 'Progress:', status.progress);
});
```

### Creating Custom DAGs

Create new DAGs in `airflow/dags/`:

```python
from airflow import DAG
from visual_ai_operators import LangGraphOperator

dag = DAG(
    'my_custom_workflow',
    description='Custom Visual AI workflow',
    schedule_interval=None,
    tags=['visual-ai']
)

task = LangGraphOperator(
    task_id='my_task',
    agent_config={'type': 'custom'},
    dag=dag
)
```

## Local Services Setup

### LangFuse (Observability)

LangFuse provides LLM tracing and monitoring:

```bash
# Setup is automatic with main script
./setup.sh start

# Access at http://localhost:3001
# API keys are in .env file
```

### Ollama (Local LLM)

For private, local LLM execution:

```bash
# Install and setup Ollama
./setup.sh setup-ollama

# Pull models
ollama pull llama2
ollama pull mistral
```

## Usage

### Creating Workflows

1. **Via UI**: Drag nodes from the left panel, connect them, and save
2. **Via API**: POST to `/api/workflows/` with workflow definition
3. **Via Airflow**: Create DAG files in `airflow/dags/`

### Node Types

- **Agent Node**: LLM-powered agents
- **Tool Node**: Function calls and integrations
- **Conditional Node**: Branching logic
- **Human Node**: Human-in-the-loop interactions

### Executing Workflows

```bash
# Via API
curl -X POST http://localhost:8000/api/workflows/{id}/execute \
  -H "Content-Type: application/json" \
  -d '{"input_data": {"message": "Hello"}}'

# Via Airflow UI
# Navigate to DAG and click "Trigger"
```

## API Reference

### Workflow Management

- `POST /api/v1/workflows/trigger` - Trigger a workflow
- `GET /api/v1/workflows/list` - List available workflows
- `GET /api/v1/workflows/{dag_id}/runs` - Get workflow runs
- `DELETE /api/v1/workflows/{dag_id}/runs/{run_id}` - Cancel workflow

### Status Monitoring

- `GET /api/v1/workflow-status/stream/{dag_id}/{run_id}` - SSE stream
- `GET /api/v1/workflow-status/{dag_id}/{run_id}` - Current status
- `GET /api/v1/workflow-status/{dag_id}/{run_id}/logs/{task_id}` - Logs

### Monitoring & Analytics

- `GET /api/v1/monitoring/workflow-metrics` - Workflow metrics
- `GET /api/v1/monitoring/agent-performance` - Agent performance
- `GET /api/v1/monitoring/error-distribution` - Error analysis
- `GET /api/v1/monitoring/system-health` - System health

## Troubleshooting

### Common Issues

#### Services Not Starting

```bash
# Check Docker
docker info

# Check logs
docker-compose -f docker/docker-compose.yml logs -f [service-name]

# Restart services
./setup.sh restart
```

#### DAGs Not Appearing

```bash
# Check DAG syntax
docker-compose exec airflow-webserver python -m py_compile /opt/airflow/dags/*.py

# Reload DAGs
docker-compose exec airflow-webserver airflow dags reserialize
```

#### Port Conflicts

```bash
# Check ports
lsof -i :8080  # Airflow
lsof -i :8000  # Backend
lsof -i :3000  # Frontend

# Change ports in .env file
```

#### API Key Issues

- Ensure all keys in `.env` are properly set
- Check LangFuse traces for detailed error messages
- Verify Ollama is running if using local LLMs

### Reset Everything

```bash
# Stop and remove all data
./setup.sh clean

# Start fresh
./setup.sh init
./setup.sh start
```

## File Structure

```
langgraph-flow/
├── airflow/
│   ├── dags/                    # Airflow DAG definitions
│   ├── plugins/                 # Custom operators
│   └── logs/                    # Airflow logs
├── backend/
│   ├── api/                     # API endpoints
│   ├── core/                    # Business logic
│   └── main.py                  # FastAPI app
├── frontend/
│   ├── src/                     # React source
│   └── package.json
├── database/
│   └── migrations/              # SQL migrations
├── docker/
│   └── docker-compose.yml       # All services
├── scripts/                     # Utility scripts
├── .env                         # Configuration
├── setup.sh                     # Main setup script
└── requirements.txt             # Python dependencies
```

## Production Deployment

### Kubernetes Deployment

```yaml
# Use Kubernetes executor
executor: KubernetesExecutor
config:
  AIRFLOW__KUBERNETES__NAMESPACE: airflow
  AIRFLOW__KUBERNETES__WORKER_CONTAINER_REPOSITORY: your-registry/airflow
```

### Scaling Considerations

- Use Redis Sentinel for HA
- Deploy PostgreSQL with replication
- Configure autoscaling for workers
- Use persistent volumes for logs

### Security

- Enable RBAC in Airflow
- Use JWT tokens for API auth
- Configure SSL/TLS
- Implement network policies

## Git Configuration

### .gitignore

The project includes comprehensive .gitignore for:
- Environment files (except .env.example)
- Python artifacts (__pycache__, venv)
- Node modules and build files
- Docker volumes
- IDE configurations
- Temporary files and logs

### Best Practices

- Never commit .env files
- Use Git LFS for large models
- Review commits for sensitive data
- Set up branch protection

---

For support, check logs first, then open an issue with relevant diagnostics.