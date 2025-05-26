# LangGraph Flow

A visual flow framework for building multi-agent and RAG applications using LangGraph as the orchestration engine. This framework provides an intuitive drag-and-drop interface for creating complex AI workflows without writing extensive code.

## Features

- **Visual Workflow Builder**: Drag-and-drop interface for creating AI workflows
- **LangGraph Integration**: Powerful orchestration engine for multi-agent systems
- **Real-time Collaboration**: WebSocket-based real-time updates
- **PostgreSQL Persistence**: Reliable storage for workflows and execution history
- **Type-Safe**: Full TypeScript support on frontend with Pydantic models on backend
- **Extensible**: Easy to add new node types and workflow patterns

## Tech Stack

### Backend
- **Python 3.11+**
- **FastAPI** - High-performance async web framework
- **LangGraph** - AI workflow orchestration
- **PostgreSQL** - Database with async support
- **SQLAlchemy** - ORM with async capabilities
- **WebSockets** - Real-time communication

### Frontend
- **React 18** with TypeScript
- **React Flow** - Visual workflow editor
- **Zustand** - State management
- **Tailwind CSS** - Styling
- **Vite** - Build tool

## Prerequisites

- Docker and Docker Compose
- Node.js 20+ (for local development)
- Python 3.11+ (for local development)

## Quick Start

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd visual-ai-framework
   ```

2. **Set up environment variables**
   ```bash
   cp backend/.env.example backend/.env
   # Edit backend/.env with your configuration
   ```

3. **Start the services with Docker**
   ```bash
   docker-compose up -d
   ```

4. **Access the application**
   - Frontend: http://localhost:5173
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

## Development Setup

### Backend Development

1. **Create a virtual environment**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the development server**
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

### Frontend Development

1. **Install dependencies**
   ```bash
   cd frontend
   npm install
   ```

2. **Run the development server**
   ```bash
   npm run dev
   ```

## Project Structure

```
visual-ai-framework/
├── backend/
│   ├── app/
│   │   ├── api/          # API endpoints
│   │   ├── core/         # Core business logic
│   │   ├── models/       # Database models
│   │   ├── schemas/      # Pydantic schemas
│   │   └── main.py       # FastAPI application
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/   # React components
│   │   ├── hooks/        # Custom React hooks
│   │   ├── services/     # API and WebSocket services
│   │   ├── store/        # Zustand state management
│   │   └── types/        # TypeScript types
│   └── package.json
└── docker-compose.yml
```

## Usage

### Creating a Workflow

1. **Drag nodes** from the left panel onto the canvas
2. **Connect nodes** by dragging from output handles to input handles
3. **Configure nodes** by clicking on them (coming in Phase 2)
4. **Save workflow** using the API

### Node Types

- **Agent Node**: Represents an AI agent (LLM-powered)
- **Tool Node**: Represents a tool or function call
- **Conditional Node**: Represents conditional logic with multiple outputs

### Executing a Workflow

```bash
# Using the API
curl -X POST http://localhost:8000/api/workflows/{workflow_id}/execute \
  -H "Content-Type: application/json" \
  -d '{"input_data": {"message": "Hello"}}'
```

## API Documentation

The API documentation is automatically generated and available at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Key Endpoints

- `POST /api/workflows/` - Create a new workflow
- `GET /api/workflows/` - List all workflows
- `GET /api/workflows/{id}` - Get a specific workflow
- `PUT /api/workflows/{id}` - Update a workflow
- `POST /api/workflows/{id}/execute` - Execute a workflow
- `WS /ws/{client_id}` - WebSocket connection for real-time updates

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Roadmap

### Phase 1 (Current)
- ✅ Basic LangGraph integration
- ✅ React Flow visual editor
- ✅ FastAPI backend with WebSocket support
- ✅ PostgreSQL persistence

### Phase 2
- [ ] Multi-agent coordination
- [ ] Enhanced drag-and-drop UI
- [ ] Real-time collaboration with Yjs
- [ ] State management with XState

### Phase 3
- [ ] Kubernetes deployment
- [ ] Distributed tracing
- [ ] Provider-agnostic LLM integration
- [ ] Performance optimization

### Phase 4
- [ ] Advanced debugging features
- [ ] AI-powered workflow suggestions
- [ ] Custom node SDK
- [ ] Enterprise features

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Built on top of [LangGraph](https://github.com/langchain-ai/langgraph)
- Visual editor powered by [React Flow](https://reactflow.dev/)
- Inspired by Langflow and LangGraph Studio