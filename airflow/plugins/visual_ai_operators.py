from airflow.models import BaseOperator
from airflow.utils.decorators import apply_defaults
from typing import Any, Dict, List, Optional
from langfuse.callback import CallbackHandler
from langgraph.prebuilt import create_react_agent
import os
import json
import asyncio

class LangGraphOperator(BaseOperator):
    """
    Custom Airflow operator for executing LangGraph agents
    
    :param agent_config: Configuration for the LangGraph agent
    :param input_data: Input data for the agent
    :param tools: List of tools to provide to the agent
    :param model: LLM model to use
    :param langfuse_config: LangFuse configuration for observability
    """
    
    template_fields = ['input_data', 'agent_config']
    ui_color = '#358140'
    
    @apply_defaults
    def __init__(
        self,
        agent_config: Dict[str, Any],
        input_data: Dict[str, Any],
        tools: Optional[List[Any]] = None,
        model: str = "gpt-4",
        langfuse_config: Optional[Dict[str, str]] = None,
        *args,
        **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.agent_config = agent_config
        self.input_data = input_data
        self.tools = tools or []
        self.model = model
        self.langfuse_config = langfuse_config or {}
    
    def execute(self, context):
        """Execute the LangGraph agent"""
        
        # Initialize LangFuse handler
        langfuse_handler = CallbackHandler(
            secret_key=self.langfuse_config.get('secret_key') or os.getenv("LANGFUSE_SECRET_KEY"),
            public_key=self.langfuse_config.get('public_key') or os.getenv("LANGFUSE_PUBLIC_KEY"),
            host=self.langfuse_config.get('host') or os.getenv("LANGFUSE_HOST", "https://cloud.langfuse.com")
        )
        
        # Create trace metadata
        trace_metadata = {
            "dag_id": context['dag'].dag_id,
            "dag_run_id": context['dag_run'].run_id,
            "task_id": context['task_instance'].task_id,
            "execution_date": context['execution_date'].isoformat()
        }
        
        # Create agent
        agent = create_react_agent(
            model=self.model,
            tools=self.tools,
            **self.agent_config
        )
        
        # Execute agent
        try:
            result = agent.invoke(
                self.input_data,
                config={
                    "callbacks": [langfuse_handler],
                    "metadata": trace_metadata
                }
            )
            
            # Log success
            self.log.info(f"Agent execution successful: {json.dumps(result, indent=2)}")
            
            # Store result in XCom
            return result
            
        except Exception as e:
            self.log.error(f"Agent execution failed: {str(e)}")
            raise

class MultiAgentOperator(BaseOperator):
    """
    Custom operator for orchestrating multiple LangGraph agents
    
    :param agents: List of agent configurations
    :param orchestration_mode: How to orchestrate agents (parallel, sequential, supervisor)
    :param synthesis_config: Configuration for synthesizing results
    """
    
    template_fields = ['agents', 'synthesis_config']
    ui_color = '#00a1df'
    
    @apply_defaults
    def __init__(
        self,
        agents: List[Dict[str, Any]],
        orchestration_mode: str = "parallel",
        synthesis_config: Optional[Dict[str, Any]] = None,
        *args,
        **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.agents = agents
        self.orchestration_mode = orchestration_mode
        self.synthesis_config = synthesis_config or {}
    
    def execute(self, context):
        """Execute multiple agents based on orchestration mode"""
        
        if self.orchestration_mode == "parallel":
            return self._execute_parallel(context)
        elif self.orchestration_mode == "sequential":
            return self._execute_sequential(context)
        elif self.orchestration_mode == "supervisor":
            return self._execute_supervisor(context)
        else:
            raise ValueError(f"Unknown orchestration mode: {self.orchestration_mode}")
    
    def _execute_parallel(self, context):
        """Execute agents in parallel"""
        import concurrent.futures
        
        results = {}
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=len(self.agents)) as executor:
            future_to_agent = {
                executor.submit(self._execute_single_agent, agent, context): agent['name']
                for agent in self.agents
            }
            
            for future in concurrent.futures.as_completed(future_to_agent):
                agent_name = future_to_agent[future]
                try:
                    result = future.result()
                    results[agent_name] = result
                    self.log.info(f"Agent {agent_name} completed successfully")
                except Exception as e:
                    self.log.error(f"Agent {agent_name} failed: {str(e)}")
                    results[agent_name] = {"error": str(e)}
        
        # Synthesize results if configured
        if self.synthesis_config:
            return self._synthesize_results(results, context)
        
        return results
    
    def _execute_sequential(self, context):
        """Execute agents sequentially, passing output to next agent"""
        results = {}
        previous_output = None
        
        for agent_config in self.agents:
            # Add previous output to agent input if available
            if previous_output:
                agent_config['input_data'] = {
                    **agent_config.get('input_data', {}),
                    'previous_output': previous_output
                }
            
            try:
                result = self._execute_single_agent(agent_config, context)
                results[agent_config['name']] = result
                previous_output = result
                self.log.info(f"Agent {agent_config['name']} completed successfully")
            except Exception as e:
                self.log.error(f"Agent {agent_config['name']} failed: {str(e)}")
                raise
        
        return results
    
    def _execute_supervisor(self, context):
        """Execute agents with supervisor pattern"""
        from langgraph.graph import StateGraph, END
        
        # Create supervisor graph
        workflow = StateGraph(dict)
        
        # Add nodes for each agent
        for agent_config in self.agents:
            workflow.add_node(
                agent_config['name'],
                lambda state, config=agent_config: self._execute_single_agent(config, context)
            )
        
        # Add supervisor node
        workflow.add_node("supervisor", self._supervisor_logic)
        
        # Define edges based on supervisor decisions
        workflow.set_entry_point("supervisor")
        
        for agent_config in self.agents:
            workflow.add_edge("supervisor", agent_config['name'])
            workflow.add_edge(agent_config['name'], "supervisor")
        
        workflow.add_edge("supervisor", END)
        
        # Execute workflow
        app = workflow.compile()
        return app.invoke({})
    
    def _execute_single_agent(self, agent_config: Dict[str, Any], context):
        """Execute a single agent"""
        
        # Initialize LangFuse handler
        langfuse_handler = CallbackHandler(
            secret_key=os.getenv("LANGFUSE_SECRET_KEY"),
            public_key=os.getenv("LANGFUSE_PUBLIC_KEY")
        )
        
        # Import the appropriate agent based on type
        agent_type = agent_config.get('type', 'generic')
        
        if agent_type == 'vision':
            from langgraph_flow.agents.vision import create_vision_agent
            agent = create_vision_agent()
        elif agent_type == 'text':
            from langgraph_flow.agents.text import create_text_extraction_agent
            agent = create_text_extraction_agent()
        elif agent_type == 'synthesis':
            from langgraph_flow.agents.synthesis import create_synthesis_agent
            agent = create_synthesis_agent()
        else:
            agent = create_react_agent(
                model=agent_config.get('model', 'gpt-4'),
                tools=agent_config.get('tools', [])
            )
        
        # Execute agent
        return agent.invoke(
            agent_config.get('input_data', {}),
            config={
                "callbacks": [langfuse_handler],
                "metadata": {
                    "agent_name": agent_config['name'],
                    "dag_run_id": context['dag_run'].run_id
                }
            }
        )
    
    def _supervisor_logic(self, state):
        """Supervisor logic for coordinating agents"""
        # Implement supervisor decision logic
        # This is a placeholder - implement based on your specific needs
        return state
    
    def _synthesize_results(self, results: Dict[str, Any], context):
        """Synthesize results from multiple agents"""
        from langgraph_flow.agents.synthesis import create_synthesis_agent
        
        synthesis_agent = create_synthesis_agent()
        
        return synthesis_agent.invoke({
            "agent_results": results,
            "synthesis_instructions": self.synthesis_config.get('instructions', '')
        })

class VisualAIValidationOperator(BaseOperator):
    """
    Custom operator for validating Visual AI workflow results
    
    :param validation_rules: Rules for validating the output
    :param fail_on_validation_error: Whether to fail the task on validation error
    """
    
    template_fields = ['validation_rules']
    ui_color = '#ffdb58'
    
    @apply_defaults
    def __init__(
        self,
        validation_rules: Dict[str, Any],
        fail_on_validation_error: bool = True,
        *args,
        **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.validation_rules = validation_rules
        self.fail_on_validation_error = fail_on_validation_error
    
    def execute(self, context):
        """Validate workflow results"""
        
        # Get results from upstream task
        ti = context['task_instance']
        upstream_task_ids = list(self.upstream_task_ids)
        
        results_to_validate = {}
        for task_id in upstream_task_ids:
            result = ti.xcom_pull(task_ids=task_id)
            if result:
                results_to_validate[task_id] = result
        
        # Perform validation
        validation_results = {
            "passed": True,
            "failures": []
        }
        
        for rule_name, rule_config in self.validation_rules.items():
            try:
                if not self._validate_rule(rule_config, results_to_validate):
                    validation_results["passed"] = False
                    validation_results["failures"].append({
                        "rule": rule_name,
                        "message": rule_config.get("error_message", f"Validation failed for {rule_name}")
                    })
            except Exception as e:
                validation_results["passed"] = False
                validation_results["failures"].append({
                    "rule": rule_name,
                    "message": f"Validation error: {str(e)}"
                })
        
        # Log results
        if validation_results["passed"]:
            self.log.info("All validation rules passed")
        else:
            self.log.warning(f"Validation failures: {json.dumps(validation_results['failures'], indent=2)}")
            
            if self.fail_on_validation_error:
                raise ValueError(f"Validation failed: {validation_results['failures']}")
        
        return validation_results
    
    def _validate_rule(self, rule_config: Dict[str, Any], results: Dict[str, Any]) -> bool:
        """Validate a single rule"""
        
        rule_type = rule_config.get('type')
        
        if rule_type == 'required_fields':
            return self._validate_required_fields(rule_config, results)
        elif rule_type == 'value_range':
            return self._validate_value_range(rule_config, results)
        elif rule_type == 'custom':
            return self._validate_custom(rule_config, results)
        else:
            raise ValueError(f"Unknown rule type: {rule_type}")
    
    def _validate_required_fields(self, rule_config: Dict[str, Any], results: Dict[str, Any]) -> bool:
        """Validate that required fields are present"""
        required_fields = rule_config.get('fields', [])
        target_task = rule_config.get('target_task')
        
        if target_task not in results:
            return False
        
        task_result = results[target_task]
        for field in required_fields:
            if field not in task_result:
                return False
        
        return True
    
    def _validate_value_range(self, rule_config: Dict[str, Any], results: Dict[str, Any]) -> bool:
        """Validate that values are within expected range"""
        target_task = rule_config.get('target_task')
        field = rule_config.get('field')
        min_value = rule_config.get('min')
        max_value = rule_config.get('max')
        
        if target_task not in results:
            return False
        
        value = results[target_task].get(field)
        if value is None:
            return False
        
        if min_value is not None and value < min_value:
            return False
        
        if max_value is not None and value > max_value:
            return False
        
        return True
    
    def _validate_custom(self, rule_config: Dict[str, Any], results: Dict[str, Any]) -> bool:
        """Execute custom validation function"""
        validation_code = rule_config.get('code', '')
        
        # Create a safe execution environment
        safe_globals = {
            'results': results,
            'len': len,
            'str': str,
            'int': int,
            'float': float,
            'bool': bool,
            'list': list,
            'dict': dict
        }
        
        try:
            exec(validation_code, safe_globals)
            return safe_globals.get('validation_result', False)
        except Exception as e:
            self.log.error(f"Custom validation error: {str(e)}")
            return False