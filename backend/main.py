"""
Main FastAPI application with Airflow integration
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import os
import logging
from typing import Dict, Any

# Import routers
from backend.api.workflow_triggers import router as workflow_triggers_router
from backend.api.workflow_status import router as workflow_status_router
from backend.api.monitoring import router as monitoring_router

# Import existing routers from langgraph_flow
from langgraph_flow.api import router as langgraph_router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Application metadata
APP_VERSION = "2.0.0"
APP_TITLE = "LangGraph Flow Visual AI with Airflow"
APP_DESCRIPTION = """
Visual AI Framework combining LangGraph agents with Apache Airflow orchestration.

## Features

* 🚀 **Workflow Orchestration**: Apache Airflow integration for complex AI workflows
* 🤖 **Multi-Agent Support**: Coordinate multiple LangGraph agents
* 📊 **Real-time Monitoring**: SSE-based workflow status updates
* 🔍 **Comprehensive Observability**: LangFuse integration for LLM tracing
* 🛡️ **Production Ready**: Error handling, retry logic, and scalability

## API Sections

* **Workflows**: Trigger and manage Airflow DAGs
* **Status**: Real-time workflow status monitoring
* **Monitoring**: System metrics and analytics
* **LangGraph**: Direct LangGraph agent execution
"""

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager for startup and shutdown tasks
    """
    # Startup
    logger.info(f"Starting {APP_TITLE} v{APP_VERSION}")
    
    # Initialize database connections
    await initialize_database()
    
    # Verify Airflow connection
    airflow_healthy = await check_airflow_connection()
    if not airflow_healthy:
        logger.warning("Airflow connection failed - some features may be unavailable")
    
    # Initialize LangFuse
    initialize_langfuse()
    
    yield
    
    # Shutdown
    logger.info("Shutting down application")
    await cleanup_connections()

# Create FastAPI application
app = FastAPI(
    title=APP_TITLE,
    description=APP_DESCRIPTION,
    version=APP_VERSION,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # React development server
        "http://localhost:8080",  # Airflow webserver
        os.getenv("FRONTEND_URL", "*")
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)

# Mount static files
if os.path.exists("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")

# Include routers
app.include_router(workflow_triggers_router, prefix="/api/v1")
app.include_router(workflow_status_router, prefix="/api/v1")
app.include_router(monitoring_router, prefix="/api/v1")
app.include_router(langgraph_router, prefix="/api/v1/langgraph")

# Health check endpoint
@app.get("/health", tags=["Health"])
async def health_check() -> Dict[str, Any]:
    """
    Health check endpoint for load balancers and monitoring
    """
    # Check various components
    checks = {
        "database": await check_database_health(),
        "airflow": await check_airflow_connection(),
        "redis": await check_redis_health(),
        "langfuse": check_langfuse_health()
    }
    
    # Calculate overall health
    all_healthy = all(checks.values())
    
    return {
        "status": "healthy" if all_healthy else "degraded",
        "version": APP_VERSION,
        "components": checks,
        "mode": os.getenv("EXECUTION_MODE", "hybrid")
    }

# Root endpoint
@app.get("/", tags=["Root"])
async def root():
    """
    Root endpoint with API information
    """
    return {
        "name": APP_TITLE,
        "version": APP_VERSION,
        "status": "operational",
        "documentation": "/docs",
        "health": "/health",
        "features": {
            "airflow_integration": True,
            "langgraph_agents": True,
            "real_time_monitoring": True,
            "langfuse_observability": True
        }
    }

# Configuration endpoint
@app.get("/config", tags=["Configuration"])
async def get_configuration():
    """
    Get current application configuration (non-sensitive)
    """
    return {
        "airflow": {
            "url": os.getenv("AIRFLOW_URL", "http://localhost:8080"),
            "enabled": os.getenv("AIRFLOW_ENABLED", "true") == "true"
        },
        "langfuse": {
            "enabled": os.getenv("LANGFUSE_ENABLED", "true") == "true",
            "host": os.getenv("LANGFUSE_HOST", "https://cloud.langfuse.com")
        },
        "execution_mode": os.getenv("EXECUTION_MODE", "hybrid"),
        "supported_workflows": [
            "visual_ai_workflow",
            "visual_ai_multi_agent_pipeline"
        ]
    }

# Utility functions

async def initialize_database():
    """Initialize database connections and run migrations"""
    import asyncpg
    
    try:
        # Create connection pool
        pool = await asyncpg.create_pool(
            host=os.getenv("POSTGRES_HOST", "localhost"),
            database=os.getenv("POSTGRES_DB", "airflow"),
            user=os.getenv("POSTGRES_USER", "airflow"),
            password=os.getenv("POSTGRES_PASSWORD", "airflow"),
            min_size=5,
            max_size=20
        )
        
        # Store pool in app state
        app.state.db_pool = pool
        
        logger.info("Database connection pool created")
        
        # Run migrations if needed
        # await run_migrations(pool)
        
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        raise

async def check_database_health() -> bool:
    """Check database health"""
    try:
        if hasattr(app.state, 'db_pool'):
            async with app.state.db_pool.acquire() as conn:
                await conn.fetchval("SELECT 1")
            return True
    except Exception:
        pass
    return False

async def check_airflow_connection() -> bool:
    """Check Airflow connection"""
    import httpx
    
    airflow_url = os.getenv("AIRFLOW_URL", "http://localhost:8080")
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{airflow_url}/health",
                timeout=5.0
            )
            return response.status_code == 200
    except Exception:
        return False

async def check_redis_health() -> bool:
    """Check Redis health"""
    import redis.asyncio as redis
    
    try:
        r = redis.from_url(os.getenv("REDIS_URL", "redis://localhost:6379"))
        await r.ping()
        await r.close()
        return True
    except Exception:
        return False

def check_langfuse_health() -> bool:
    """Check LangFuse health"""
    try:
        from langfuse import Langfuse
        
        langfuse = Langfuse(
            secret_key=os.getenv("LANGFUSE_SECRET_KEY"),
            public_key=os.getenv("LANGFUSE_PUBLIC_KEY"),
            host=os.getenv("LANGFUSE_HOST", "https://cloud.langfuse.com")
        )
        
        # Simple check - if initialization succeeds, consider it healthy
        return True
    except Exception:
        return False

def initialize_langfuse():
    """Initialize LangFuse for observability"""
    try:
        from langfuse import Langfuse
        
        langfuse = Langfuse(
            secret_key=os.getenv("LANGFUSE_SECRET_KEY"),
            public_key=os.getenv("LANGFUSE_PUBLIC_KEY"),
            host=os.getenv("LANGFUSE_HOST", "https://cloud.langfuse.com")
        )
        
        # Store in app state
        app.state.langfuse = langfuse
        
        logger.info("LangFuse initialized successfully")
    except Exception as e:
        logger.warning(f"LangFuse initialization failed: {e}")

async def cleanup_connections():
    """Cleanup connections on shutdown"""
    # Close database pool
    if hasattr(app.state, 'db_pool'):
        await app.state.db_pool.close()
        logger.info("Database connection pool closed")
    
    # Flush LangFuse
    if hasattr(app.state, 'langfuse'):
        app.state.langfuse.flush()
        logger.info("LangFuse flushed")

# Error handlers

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Custom HTTP exception handler"""
    return {
        "error": {
            "status_code": exc.status_code,
            "message": exc.detail,
            "type": "http_error"
        }
    }

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """General exception handler"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    
    return {
        "error": {
            "status_code": 500,
            "message": "Internal server error",
            "type": "internal_error"
        }
    }

# CLI entry point
if __name__ == "__main__":
    import uvicorn
    
    # Get configuration from environment
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))
    reload = os.getenv("RELOAD", "false").lower() == "true"
    
    # Run the application
    uvicorn.run(
        "backend.main:app",
        host=host,
        port=port,
        reload=reload,
        log_level="info"
    )