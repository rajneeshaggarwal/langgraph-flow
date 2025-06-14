from fastapi import APIRouter, Query, HTTPException
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import asyncpg
import os
from pydantic import BaseModel

router = APIRouter(prefix="/monitoring", tags=["monitoring"])

class WorkflowMetrics(BaseModel):
    total_workflows: int
    successful: int
    failed: int
    running: int
    avg_duration_seconds: float
    total_tokens_used: int
    total_cost: float
    error_rate: float

class AgentMetrics(BaseModel):
    agent_name: str
    executions: int
    avg_duration_ms: float
    total_tokens: int
    total_cost: float
    success_rate: float

class ErrorMetrics(BaseModel):
    error_type: str
    count: int
    percentage: float
    last_occurrence: datetime

async def get_db_connection():
    """Create database connection"""
    return await asyncpg.connect(
        host=os.getenv("POSTGRES_HOST", "localhost"),
        database=os.getenv("POSTGRES_DB", "airflow"),
        user=os.getenv("POSTGRES_USER", "airflow"),
        password=os.getenv("POSTGRES_PASSWORD", "airflow")
    )

@router.get("/workflow-metrics", response_model=WorkflowMetrics)
async def get_workflow_metrics(
    time_range: str = Query("24h", regex="^(1h|6h|24h|7d|30d)$"),
    user_id: Optional[str] = None
):
    """Get aggregated workflow metrics for monitoring dashboard"""
    
    # Convert time range to interval
    time_intervals = {
        "1h": "1 hour",
        "6h": "6 hours",
        "24h": "24 hours",
        "7d": "7 days",
        "30d": "30 days"
    }
    
    conn = await get_db_connection()
    
    try:
        query = """
            SELECT 
                COUNT(*) as total_workflows,
                COUNT(CASE WHEN status = 'success' THEN 1 END) as successful,
                COUNT(CASE WHEN status = 'failed' THEN 1 END) as failed,
                COUNT(CASE WHEN status = 'running' THEN 1 END) as running,
                AVG(EXTRACT(EPOCH FROM (updated_at - created_at))) as avg_duration,
                COALESCE(SUM((output_data->>'total_tokens')::int), 0) as total_tokens_used,
                COALESCE(SUM((output_data->>'total_cost')::float), 0.0) as total_cost
            FROM visual_ai.workflow_executions
            WHERE created_at > CURRENT_TIMESTAMP - INTERVAL $1
        """
        
        params = [time_intervals[time_range]]
        
        if user_id:
            query += " AND user_id = $2"
            params.append(user_id)
        
        result = await conn.fetchrow(query, *params)
        
        total = result['total_workflows'] or 1
        failed = result['failed'] or 0
        
        return WorkflowMetrics(
            total_workflows=result['total_workflows'] or 0,
            successful=result['successful'] or 0,
            failed=failed,
            running=result['running'] or 0,
            avg_duration_seconds=result['avg_duration'] or 0.0,
            total_tokens_used=result['total_tokens_used'] or 0,
            total_cost=result['total_cost'] or 0.0,
            error_rate=(failed / total) * 100 if total > 0 else 0.0
        )
        
    finally:
        await conn.close()

@router.get("/agent-performance", response_model=List[AgentMetrics])
async def get_agent_performance(
    time_range: str = Query("7d", regex="^(1h|6h|24h|7d|30d)$"),
    limit: int = Query(10, ge=1, le=50)
):
    """Get performance metrics for individual agents"""
    
    time_intervals = {
        "1h": "1 hour",
        "6h": "6 hours",
        "24h": "24 hours",
        "7d": "7 days",
        "30d": "30 days"
    }
    
    conn = await get_db_connection()
    
    try:
        query = """
            SELECT 
                agent_name,
                COUNT(*) as executions,
                AVG(duration_ms) as avg_duration,
                SUM(input_tokens + output_tokens) as total_tokens,
                SUM(cost) as total_cost,
                AVG(CASE WHEN success THEN 1 ELSE 0 END) * 100 as success_rate
            FROM visual_ai.agent_traces
            WHERE created_at > CURRENT_TIMESTAMP - INTERVAL $1
            GROUP BY agent_name
            ORDER BY executions DESC
            LIMIT $2
        """
        
        results = await conn.fetch(query, time_intervals[time_range], limit)
        
        return [
            AgentMetrics(
                agent_name=row['agent_name'],
                executions=row['executions'],
                avg_duration_ms=row['avg_duration'] or 0.0,
                total_tokens=row['total_tokens'] or 0,
                total_cost=row['total_cost'] or 0.0,
                success_rate=row['success_rate'] or 0.0
            )
            for row in results
        ]
        
    finally:
        await conn.close()

@router.get("/error-distribution", response_model=List[ErrorMetrics])
async def get_error_distribution(
    time_range: str = Query("24h", regex="^(1h|6h|24h|7d|30d)$")
):
    """Get distribution of errors by type"""
    
    time_intervals = {
        "1h": "1 hour",
        "6h": "6 hours",
        "24h": "24 hours",
        "7d": "7 days",
        "30d": "30 days"
    }
    
    conn = await get_db_connection()
    
    try:
        query = """
            WITH error_counts AS (
                SELECT 
                    error_type,
                    COUNT(*) as count,
                    MAX(created_at) as last_occurrence
                FROM visual_ai.workflow_errors
                WHERE created_at > CURRENT_TIMESTAMP - INTERVAL $1
                GROUP BY error_type
            ),
            total_errors AS (
                SELECT SUM(count) as total FROM error_counts
            )
            SELECT 
                e.error_type,
                e.count,
                (e.count::float / NULLIF(t.total, 0) * 100) as percentage,
                e.last_occurrence
            FROM error_counts e
            CROSS JOIN total_errors t
            ORDER BY e.count DESC
        """
        
        results = await conn.fetch(query, time_intervals[time_range])
        
        return [
            ErrorMetrics(
                error_type=row['error_type'],
                count=row['count'],
                percentage=row['percentage'] or 0.0,
                last_occurrence=row['last_occurrence']
            )
            for row in results
        ]
        
    finally:
        await conn.close()

@router.get("/system-health")
async def get_system_health():
    """Get overall system health status"""
    
    conn = await get_db_connection()
    
    try:
        # Check database connectivity
        await conn.fetchval("SELECT 1")
        db_healthy = True
    except Exception as e:
        db_healthy = False
    finally:
        await conn.close()
    
    # Check Airflow health
    airflow_healthy = await check_airflow_health()
    
    # Check Redis health
    redis_healthy = await check_redis_health()
    
    # Calculate overall health score
    health_score = sum([db_healthy, airflow_healthy, redis_healthy]) / 3 * 100
    
    return {
        "status": "healthy" if health_score >= 66 else "degraded" if health_score >= 33 else "unhealthy",
        "health_score": health_score,
        "components": {
            "database": {"status": "healthy" if db_healthy else "unhealthy"},
            "airflow": {"status": "healthy" if airflow_healthy else "unhealthy"},
            "redis": {"status": "healthy" if redis_healthy else "unhealthy"}
        },
        "timestamp": datetime.utcnow().isoformat()
    }

@router.get("/workflow-trends")
async def get_workflow_trends(
    days: int = Query(7, ge=1, le=30)
):
    """Get workflow execution trends over time"""
    
    conn = await get_db_connection()
    
    try:
        query = """
            SELECT 
                DATE(created_at) as date,
                COUNT(*) as total,
                COUNT(CASE WHEN status = 'success' THEN 1 END) as successful,
                COUNT(CASE WHEN status = 'failed' THEN 1 END) as failed,
                AVG(EXTRACT(EPOCH FROM (updated_at - created_at))) as avg_duration
            FROM visual_ai.workflow_executions
            WHERE created_at > CURRENT_TIMESTAMP - INTERVAL '%s days'
            GROUP BY DATE(created_at)
            ORDER BY date DESC
        """
        
        results = await conn.fetch(query % days)
        
        return {
            "trends": [
                {
                    "date": row['date'].isoformat(),
                    "total": row['total'],
                    "successful": row['successful'],
                    "failed": row['failed'],
                    "avg_duration_seconds": row['avg_duration'] or 0.0,
                    "success_rate": (row['successful'] / row['total'] * 100) if row['total'] > 0 else 0.0
                }
                for row in results
            ]
        }
        
    finally:
        await conn.close()

@router.get("/cost-analysis")
async def get_cost_analysis(
    group_by: str = Query("day", regex="^(hour|day|week|month)$"),
    days: int = Query(7, ge=1, le=90)
):
    """Get cost analysis for workflows"""
    
    conn = await get_db_connection()
    
    try:
        date_trunc_map = {
            "hour": "hour",
            "day": "day",
            "week": "week",
            "month": "month"
        }
        
        query = """
            SELECT 
                DATE_TRUNC($1, at.created_at) as period,
                SUM(at.cost) as total_cost,
                SUM(at.input_tokens + at.output_tokens) as total_tokens,
                COUNT(DISTINCT we.id) as workflow_count,
                AVG(at.cost) as avg_cost_per_execution
            FROM visual_ai.agent_traces at
            JOIN visual_ai.workflow_executions we ON at.workflow_execution_id = we.id
            WHERE at.created_at > CURRENT_TIMESTAMP - INTERVAL '%s days'
            GROUP BY DATE_TRUNC($1, at.created_at)
            ORDER BY period DESC
        """
        
        results = await conn.fetch(query % days, date_trunc_map[group_by])
        
        return {
            "cost_analysis": [
                {
                    "period": row['period'].isoformat(),
                    "total_cost": row['total_cost'] or 0.0,
                    "total_tokens": row['total_tokens'] or 0,
                    "workflow_count": row['workflow_count'],
                    "avg_cost_per_execution": row['avg_cost_per_execution'] or 0.0
                }
                for row in results
            ],
            "summary": {
                "total_cost": sum(row['total_cost'] or 0 for row in results),
                "total_tokens": sum(row['total_tokens'] or 0 for row in results)
            }
        }
        
    finally:
        await conn.close()

async def check_airflow_health() -> bool:
    """Check Airflow health status"""
    try:
        import httpx
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{os.getenv('AIRFLOW_URL', 'http://localhost:8080')}/health",
                timeout=5.0
            )
            return response.status_code == 200
    except Exception:
        return False

async def check_redis_health() -> bool:
    """Check Redis health status"""
    try:
        import redis.asyncio as redis
        r = redis.from_url(os.getenv("REDIS_URL", "redis://localhost:6379"))
        await r.ping()
        await r.close()
        return True
    except Exception:
        return False