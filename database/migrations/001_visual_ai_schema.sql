-- Create schema for Visual AI Framework
CREATE SCHEMA IF NOT EXISTS visual_ai;

-- Workflow execution history with Visual AI specific metadata
CREATE TABLE visual_ai.workflow_executions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    dag_id VARCHAR(250) NOT NULL,
    dag_run_id VARCHAR(250) NOT NULL,
    user_id VARCHAR(100),
    input_data JSONB,
    output_data JSONB,
    langfuse_trace_id VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(50),
    error_message TEXT,
    metadata JSONB,
    UNIQUE(dag_run_id)
);

-- Agent execution traces
CREATE TABLE visual_ai.agent_traces (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workflow_execution_id UUID REFERENCES visual_ai.workflow_executions(id) ON DELETE CASCADE,
    agent_name VARCHAR(100),
    input_tokens INTEGER,
    output_tokens INTEGER,
    cost DECIMAL(10, 6),
    duration_ms INTEGER,
    success BOOLEAN,
    error_details JSONB,
    langfuse_observation_id VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Workflow errors for debugging
CREATE TABLE visual_ai.workflow_errors (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workflow_execution_id UUID REFERENCES visual_ai.workflow_executions(id) ON DELETE CASCADE,
    task_id VARCHAR(250),
    error_type VARCHAR(50),
    error_message TEXT,
    stack_trace TEXT,
    context JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- User workflow preferences
CREATE TABLE visual_ai.user_preferences (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id VARCHAR(100) UNIQUE NOT NULL,
    default_model VARCHAR(50),
    notification_settings JSONB,
    workflow_defaults JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Workflow templates
CREATE TABLE visual_ai.workflow_templates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    template_config JSONB NOT NULL,
    category VARCHAR(100),
    tags TEXT[],
    created_by VARCHAR(100),
    is_public BOOLEAN DEFAULT false,
    usage_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for performance
CREATE INDEX idx_workflow_user_id ON visual_ai.workflow_executions(user_id);
CREATE INDEX idx_workflow_dag_run_id ON visual_ai.workflow_executions(dag_run_id);
CREATE INDEX idx_workflow_status ON visual_ai.workflow_executions(status);
CREATE INDEX idx_workflow_created_at ON visual_ai.workflow_executions(created_at DESC);
CREATE INDEX idx_agent_traces_workflow ON visual_ai.agent_traces(workflow_execution_id);
CREATE INDEX idx_agent_traces_name ON visual_ai.agent_traces(agent_name);
CREATE INDEX idx_workflow_errors_execution ON visual_ai.workflow_errors(workflow_execution_id);
CREATE INDEX idx_workflow_errors_type ON visual_ai.workflow_errors(error_type);
CREATE INDEX idx_templates_category ON visual_ai.workflow_templates(category);
CREATE INDEX idx_templates_tags ON visual_ai.workflow_templates USING gin(tags);

-- Create views for monitoring
CREATE VIEW visual_ai.workflow_stats AS
SELECT 
    dag_id,
    COUNT(*) as total_runs,
    COUNT(CASE WHEN status = 'success' THEN 1 END) as successful_runs,
    COUNT(CASE WHEN status = 'failed' THEN 1 END) as failed_runs,
    AVG(EXTRACT(EPOCH FROM (updated_at - created_at))) as avg_duration_seconds,
    MAX(created_at) as last_run_at
FROM visual_ai.workflow_executions
GROUP BY dag_id;

CREATE VIEW visual_ai.agent_performance AS
SELECT 
    agent_name,
    COUNT(*) as total_executions,
    AVG(duration_ms) as avg_duration_ms,
    SUM(input_tokens + output_tokens) as total_tokens,
    SUM(cost) as total_cost,
    AVG(CASE WHEN success THEN 1 ELSE 0 END) * 100 as success_rate
FROM visual_ai.agent_traces
WHERE created_at > CURRENT_TIMESTAMP - INTERVAL '7 days'
GROUP BY agent_name;

-- Create functions for updating timestamps
CREATE OR REPLACE FUNCTION visual_ai.update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create triggers
CREATE TRIGGER update_workflow_executions_updated_at BEFORE UPDATE ON visual_ai.workflow_executions
    FOR EACH ROW EXECUTE FUNCTION visual_ai.update_updated_at_column();

CREATE TRIGGER update_user_preferences_updated_at BEFORE UPDATE ON visual_ai.user_preferences
    FOR EACH ROW EXECUTE FUNCTION visual_ai.update_updated_at_column();

CREATE TRIGGER update_workflow_templates_updated_at BEFORE UPDATE ON visual_ai.workflow_templates
    FOR EACH ROW EXECUTE FUNCTION visual_ai.update_updated_at_column();