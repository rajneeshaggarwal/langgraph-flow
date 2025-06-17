# LangGraph Flow - Airflow Integration Summary

## Overview
This project integrates LangGraph with Apache Airflow for enterprise-grade AI workflow orchestration.

## Architecture
- **Airflow**: Workflow orchestration
- **LangGraph**: AI agent framework
- **LangFuse**: Observability and monitoring
- **FastAPI**: Backend API
- **React**: Frontend UI

## Key Components

### 1. DAGs
- `visual_ai_dag.py`: Main workflow DAG
- `visual_ai_multi_agent_dag.py`: Multi-agent orchestration

### 2. Custom Operators
- `LangGraphOperator`: Execute single agents
- `MultiAgentOperator`: Orchestrate multiple agents
- `VisualAIValidationOperator`: Validate results

### 3. Agents
- Vision Agent: Image analysis
- Text Agent: Document processing
- Synthesis Agent: Result combination

## Quick Start
```bash
# Initialize project
./setup.sh init

# Start services
./setup.sh start

# Check status
./setup.sh status
```

## Access Points
- Airflow UI: http://localhost:8080
- Backend API: http://localhost:8000
- Frontend: http://localhost:3000
- LangFuse: http://localhost:3001

## Configuration
Edit `.env` file to configure:
- LLM providers (OpenAI/Ollama)
- API keys
- Database connections
- Service URLs
