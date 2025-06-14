from typing import Optional, Dict, Any, List
import traceback
from datetime import datetime
import asyncio
import json
import logging
from enum import Enum
import psycopg2
from psycopg2.extras import Json

logger = logging.getLogger(__name__)

class ErrorType(Enum):
    RATE_LIMIT = "rate_limit"
    API_TIMEOUT = "api_timeout"
    CONTEXT_LENGTH = "context_length"
    AUTHENTICATION = "authentication"
    VALIDATION = "validation"
    SYSTEM = "system"
    UNKNOWN = "unknown"

class RetryStrategy:
    def __init__(self, max_retries: int = 3, base_delay: float = 1.0):
        self.max_retries = max_retries
        self.base_delay = base_delay
    
    def get_delay(self, retry_count: int) -> float:
        """Calculate exponential backoff delay"""
        return self.base_delay * (2 ** retry_count)

class WorkflowErrorHandler:
    """Centralized error handling for Visual AI workflows"""
    
    def __init__(self, langfuse_client, db_connection):
        self.langfuse = langfuse_client
        self.db = db_connection
        self.retry_strategies = {
            ErrorType.RATE_LIMIT: RetryStrategy(max_retries=5, base_delay=2.0),
            ErrorType.API_TIMEOUT: RetryStrategy(max_retries=3, base_delay=1.0),
            ErrorType.CONTEXT_LENGTH: RetryStrategy(max_retries=1, base_delay=0),
        }
    
    async def handle_agent_failure(
        self,
        error: Exception,
        context: Dict[str, Any],
        retry_count: int = 0
    ) -> Optional[Dict[str, Any]]:
        """Handle LangGraph agent failures with intelligent retry logic"""
        
        error_type = self.classify_error(error)
        
        # Log to LangFuse
        self.langfuse.create_score(
            trace_id=context.get('trace_id'),
            name="error-occurred",
            value=1,
            data_type="NUMERIC",
            comment=f"{error_type.value}: {str(error)}"
        )
        
        # Store error in database
        await self.store_error_details(error, context, error_type)
        
        # Determine retry strategy
        strategy = self.retry_strategies.get(error_type)
        
        if strategy and retry_count < strategy.max_retries:
            wait_time = strategy.get_delay(retry_count)
            
            logger.warning(
                f"Retrying after {error_type.value} error "
                f"(attempt {retry_count + 1}/{strategy.max_retries}): {str(error)}"
            )
            
            await asyncio.sleep(wait_time)
            
            return {
                "retry": True,
                "wait_time": wait_time,
                "retry_count": retry_count + 1
            }
        
        # Handle specific error types
        if error_type == ErrorType.CONTEXT_LENGTH:
            return {
                "fallback_model": "gpt-3.5-turbo-16k",
                "retry": True,
                "strategy": "use_smaller_model"
            }
        
        # For non-retryable errors
        return {
            "retry": False,
            "fatal": True,
            "error_type": error_type.value,
            "message": str(error)
        }
    
    def classify_error(self, error: Exception) -> ErrorType:
        """Classify error type for appropriate handling"""
        error_str = str(error).lower()
        error_type_name = type(error).__name__
        
        if "rate limit" in error_str or "429" in error_str:
            return ErrorType.RATE_LIMIT
        elif "timeout" in error_str or "timed out" in error_str:
            return ErrorType.API_TIMEOUT
        elif "context length" in error_str or "token limit" in error_str:
            return ErrorType.CONTEXT_LENGTH
        elif "unauthorized" in error_str or "401" in error_str:
            return ErrorType.AUTHENTICATION
        elif "validation" in error_str or "invalid" in error_str:
            return ErrorType.VALIDATION
        elif error_type_name in ["OSError", "ConnectionError", "IOError"]:
            return ErrorType.SYSTEM
        else:
            return ErrorType.UNKNOWN
    
    async def store_error_details(
        self,
        error: Exception,
        context: Dict[str, Any],
        error_type: ErrorType
    ):
        """Store detailed error information for debugging"""
        
        query = """
            INSERT INTO visual_ai.workflow_errors 
            (workflow_execution_id, task_id, error_type, error_message, 
             stack_trace, context, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        
        try:
            with self.db.cursor() as cur:
                cur.execute(
                    query,
                    (
                        context.get('workflow_execution_id'),
                        context.get('task_id'),
                        error_type.value,
                        str(error),
                        traceback.format_exc(),
                        Json(context),
                        datetime.utcnow()
                    )
                )
                self.db.commit()
        except Exception as e:
            logger.error(f"Failed to store error details: {e}")
    
    def create_error_notification(
        self,
        error: Exception,
        context: Dict[str, Any],
        error_type: ErrorType
    ) -> Dict[str, Any]:
        """Create error notification for alerting systems"""
        
        return {
            "severity": self.get_error_severity(error_type),
            "error_type": error_type.value,
            "message": str(error),
            "workflow_id": context.get('workflow_execution_id'),
            "task_id": context.get('task_id'),
            "timestamp": datetime.utcnow().isoformat(),
            "context": {
                "dag_id": context.get('dag_id'),
                "dag_run_id": context.get('dag_run_id'),
                "user_id": context.get('user_id')
            },
            "suggested_action": self.get_suggested_action(error_type)
        }
    
    def get_error_severity(self, error_type: ErrorType) -> str:
        """Determine error severity for alerting"""
        severity_map = {
            ErrorType.RATE_LIMIT: "warning",
            ErrorType.API_TIMEOUT: "warning",
            ErrorType.CONTEXT_LENGTH: "info",
            ErrorType.AUTHENTICATION: "critical",
            ErrorType.VALIDATION: "error",
            ErrorType.SYSTEM: "critical",
            ErrorType.UNKNOWN: "error"
        }
        return severity_map.get(error_type, "error")
    
    def get_suggested_action(self, error_type: ErrorType) -> str:
        """Get suggested action for error type"""
        action_map = {
            ErrorType.RATE_LIMIT: "Wait and retry with exponential backoff",
            ErrorType.API_TIMEOUT: "Retry with shorter timeout or simpler request",
            ErrorType.CONTEXT_LENGTH: "Use a model with larger context window or reduce input size",
            ErrorType.AUTHENTICATION: "Check API credentials and permissions",
            ErrorType.VALIDATION: "Review input data format and requirements",
            ErrorType.SYSTEM: "Check system resources and connectivity",
            ErrorType.UNKNOWN: "Review logs and contact support if persistent"
        }
        return action_map.get(error_type, "Review error details")

# Usage in Airflow task
def robust_langgraph_execution(**context):
    """Execute LangGraph with comprehensive error handling"""
    
    from langfuse import Langfuse
    import psycopg2
    
    # Initialize connections
    langfuse_client = Langfuse(
        secret_key=os.getenv("LANGFUSE_SECRET_KEY"),
        public_key=os.getenv("LANGFUSE_PUBLIC_KEY")
    )
    
    db_connection = psycopg2.connect(
        host=os.getenv("POSTGRES_HOST", "localhost"),
        database=os.getenv("POSTGRES_DB", "airflow"),
        user=os.getenv("POSTGRES_USER", "airflow"),
        password=os.getenv("POSTGRES_PASSWORD", "airflow")
    )
    
    error_handler = WorkflowErrorHandler(langfuse_client, db_connection)
    max_retries = 3
    retry_count = 0
    
    while retry_count < max_retries:
        try:
            # Import and create agent
            from langgraph_flow.agents import create_visual_ai_agent
            
            agent = create_visual_ai_agent(
                model=context.get('model', 'gpt-4'),
                tools=get_visual_ai_tools()
            )
            
            # Execute agent
            result = agent.invoke(
                context['input_data'],
                config={
                    'timeout': 300,
                    'callbacks': [langfuse_handler],
                    'metadata': {
                        'dag_run_id': context['dag_run'].run_id,
                        'task_id': context['task_instance'].task_id
                    }
                }
            )
            
            # Validate result
            if validate_agent_output(result):
                return result
            else:
                raise ValueError("Agent output validation failed")
            
        except Exception as e:
            retry_count += 1
            
            # Handle error
            error_response = asyncio.run(
                error_handler.handle_agent_failure(
                    error=e,
                    context={
                        'workflow_execution_id': context['dag_run'].run_id,
                        'task_id': context['task_instance'].task_id,
                        'trace_id': langfuse_handler.get_current_trace_id(),
                        'retry_count': retry_count,
                        'dag_id': context['dag'].dag_id,
                        'user_id': context['dag_run'].conf.get('user_id')
                    },
                    retry_count=retry_count
                )
            )
            
            if error_response.get('retry'):
                if error_response.get('fallback_model'):
                    context['model'] = error_response['fallback_model']
                    logger.info(f"Switching to fallback model: {context['model']}")
                continue
            else:
                # Create error notification
                notification = error_handler.create_error_notification(
                    e, context, error_handler.classify_error(e)
                )
                
                # Log final error
                logger.error(f"Fatal error in workflow: {notification}")
                
                # Raise the error
                raise e
    
    raise Exception(f"Max retries ({max_retries}) exceeded")

def validate_agent_output(result: Dict[str, Any]) -> bool:
    """Validate agent output structure and content"""
    
    # Check required fields
    required_fields = ['messages', 'usage']
    for field in required_fields:
        if field not in result:
            logger.error(f"Missing required field in agent output: {field}")
            return False
    
    # Check for error indicators
    if 'error' in result:
        logger.error(f"Agent returned error: {result['error']}")
        return False
    
    # Validate message structure
    messages = result.get('messages', [])
    if not messages:
        logger.error("Agent returned no messages")
        return False
    
    # Additional validation logic here
    
    return True