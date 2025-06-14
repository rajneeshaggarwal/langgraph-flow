import React, { useEffect, useState, useCallback } from 'react';
import { Card, Progress, Tag, Timeline, Alert, Button, Space, Spin, Statistic, Row, Col } from 'antd';
import { 
  CheckCircleOutlined, 
  ClockCircleOutlined, 
  ExclamationCircleOutlined, 
  SyncOutlined,
  PlayCircleOutlined,
  PauseCircleOutlined,
  StopOutlined,
  ReloadOutlined
} from '@ant-design/icons';
import { useParams, useNavigate } from 'react-router-dom';
import axios from 'axios';

interface TaskInstance {
  task_id: string;
  state: string;
  start_date: string;
  end_date?: string;
  duration?: number;
  try_number?: number;
  logs?: string;
}

interface WorkflowStatus {
  dag_id: string;
  dag_run_id: string;
  state: string;
  start_date: string;
  end_date?: string;
  execution_date: string;
  tasks: TaskInstance[];
  progress: number;
  duration?: number;
  conf?: any;
}

interface WorkflowUpdate {
  dag_run_id: string;
  state: string;
  start_date: string;
  end_date?: string;
  tasks: TaskInstance[];
  progress: number;
}

const WorkflowMonitor: React.FC = () => {
  const { dagId, dagRunId } = useParams<{ dagId: string; dagRunId: string }>();
  const navigate = useNavigate();
  
  const [workflow, setWorkflow] = useState<WorkflowStatus | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [eventSource, setEventSource] = useState<EventSource | null>(null);
  const [selectedTask, setSelectedTask] = useState<TaskInstance | null>(null);
  const [taskLogs, setTaskLogs] = useState<string>('');
  
  const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

  // Initial fetch of workflow status
  const fetchWorkflowStatus = useCallback(async () => {
    try {
      const response = await axios.get(
        `${API_URL}/workflow-status/${dagId}/${dagRunId}`,
        {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`
          }
        }
      );
      setWorkflow(response.data);
      setLoading(false);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to fetch workflow status');
      setLoading(false);
    }
  }, [API_URL, dagId, dagRunId]);

  // Setup SSE connection for real-time updates
  useEffect(() => {
    const token = localStorage.getItem('token');
    const sse = new EventSource(
      `${API_URL}/workflow-status/stream/${dagId}/${dagRunId}?token=${token}`
    );

    sse.addEventListener('workflow_update', (event) => {
      const data: WorkflowUpdate = JSON.parse(event.data);
      setWorkflow(prev => ({
        ...prev!,
        ...data
      }));
    });

    sse.addEventListener('task_update', (event) => {
      const taskUpdate = JSON.parse(event.data);
      setWorkflow(prev => {
        if (!prev) return prev;
        
        const updatedTasks = prev.tasks.map(task => 
          task.task_id === taskUpdate.task.task_id ? taskUpdate.task : task
        );
        
        return {
          ...prev,
          tasks: updatedTasks
        };
      });
    });

    sse.addEventListener('workflow_complete', (event) => {
      const data: WorkflowUpdate = JSON.parse(event.data);
      setWorkflow(prev => ({
        ...prev!,
        ...data
      }));
      sse.close();
    });

    sse.addEventListener('error', (event) => {
      const errorData = JSON.parse(event.data);
      setError(errorData.error);
      sse.close();
    });

    sse.onerror = () => {
      setError('Connection to workflow status stream lost');
      sse.close();
    };

    setEventSource(sse);

    // Initial fetch
    fetchWorkflowStatus();

    return () => {
      if (sse.readyState !== sse.CLOSED) {
        sse.close();
      }
    };
  }, [API_URL, dagId, dagRunId, fetchWorkflowStatus]);

  const getStateIcon = (state: string) => {
    switch (state) {
      case 'success':
        return <CheckCircleOutlined style={{ color: '#52c41a' }} />;
      case 'running':
        return <SyncOutlined spin style={{ color: '#1890ff' }} />;
      case 'failed':
        return <ExclamationCircleOutlined style={{ color: '#ff4d4f' }} />;
      case 'queued':
        return <ClockCircleOutlined style={{ color: '#faad14' }} />;
      default:
        return <ClockCircleOutlined style={{ color: '#8c8c8c' }} />;
    }
  };

  const getStateColor = (state: string) => {
    switch (state) {
      case 'success':
        return 'green';
      case 'running':
        return 'blue';
      case 'failed':
        return 'red';
      case 'queued':
        return 'orange';
      default:
        return 'default';
    }
  };

  const fetchTaskLogs = async (task: TaskInstance) => {
    try {
      const response = await axios.get(
        `${API_URL}/workflow-status/${dagId}/${dagRunId}/logs/${task.task_id}`,
        {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`
          }
        }
      );
      setTaskLogs(response.data.logs);
      setSelectedTask(task);
    } catch (err) {
      console.error('Failed to fetch task logs:', err);
    }
  };

  const cancelWorkflow = async () => {
    try {
      await axios.delete(
        `${API_URL}/workflows/${dagId}/runs/${dagRunId}`,
        {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`
          }
        }
      );
      fetchWorkflowStatus();
    } catch (err) {
      console.error('Failed to cancel workflow:', err);
    }
  };

  const formatDuration = (seconds: number) => {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const secs = Math.floor(seconds % 60);
    
    if (hours > 0) {
      return `${hours}h ${minutes}m ${secs}s`;
    } else if (minutes > 0) {
      return `${minutes}m ${secs}s`;
    } else {
      return `${secs}s`;
    }
  };

  if (loading) {
    return (
      <div style={{ textAlign: 'center', padding: '50px' }}>
        <Spin size="large" />
        <p style={{ marginTop: '20px' }}>Loading workflow status...</p>
      </div>
    );
  }

  if (error) {
    return (
      <Alert
        message="Error"
        description={error}
        type="error"
        showIcon
        action={
          <Button size="small" onClick={fetchWorkflowStatus}>
            Retry
          </Button>
        }
      />
    );
  }

  if (!workflow) {
    return <Alert message="No workflow data available" type="warning" showIcon />;
  }

  return (
    <div style={{ padding: '24px' }}>
      <Card
        title={
          <Space>
            <span>Workflow: {dagId}</span>
            <Tag color={getStateColor(workflow.state)}>
              {workflow.state.toUpperCase()}
            </Tag>
          </Space>
        }
        extra={
          <Space>
            {workflow.state === 'running' && (
              <Button
                danger
                icon={<StopOutlined />}
                onClick={cancelWorkflow}
              >
                Cancel
              </Button>
            )}
            <Button
              icon={<ReloadOutlined />}
              onClick={fetchWorkflowStatus}
            >
              Refresh
            </Button>
            <Button
              type="link"
              onClick={() => navigate('/workflows')}
            >
              Back to Workflows
            </Button>
          </Space>
        }
      >
        <Row gutter={16} style={{ marginBottom: '24px' }}>
          <Col span={6}>
            <Statistic
              title="Progress"
              value={workflow.progress}
              suffix="%"
              valueStyle={{ color: workflow.state === 'failed' ? '#ff4d4f' : '#3f8600' }}
            />
          </Col>
          <Col span={6}>
            <Statistic
              title="Duration"
              value={workflow.duration ? formatDuration(workflow.duration) : 'Running...'}
              prefix={<ClockCircleOutlined />}
            />
          </Col>
          <Col span={6}>
            <Statistic
              title="Tasks"
              value={workflow.tasks.filter(t => t.state === 'success').length}
              suffix={`/ ${workflow.tasks.length}`}
            />
          </Col>
          <Col span={6}>
            <Statistic
              title="Execution Date"
              value={new Date(workflow.execution_date).toLocaleString()}
            />
          </Col>
        </Row>

        <Progress
          percent={workflow.progress}
          status={
            workflow.state === 'failed' ? 'exception' :
            workflow.state === 'success' ? 'success' : 'active'
          }
          strokeWidth={15}
        />

        <div style={{ marginTop: '24px' }}>
          <h3>Task Execution Timeline</h3>
          <Timeline style={{ marginTop: '16px' }}>
            {workflow.tasks.map((task, index) => (
              <Timeline.Item
                key={task.task_id}
                dot={getStateIcon(task.state)}
                color={task.state === 'success' ? 'green' : 
                       task.state === 'failed' ? 'red' : 'gray'}
              >
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <div>
                    <strong>{task.task_id}</strong>
                    <Tag color={getStateColor(task.state)} style={{ marginLeft: '8px' }}>
                      {task.state}
                    </Tag>
                    {task.try_number && task.try_number > 1 && (
                      <Tag color="orange">Retry {task.try_number - 1}</Tag>
                    )}
                  </div>
                  <Space>
                    {task.duration && <span>{task.duration}s</span>}
                    {task.state === 'failed' && (
                      <Button
                        size="small"
                        type="link"
                        onClick={() => fetchTaskLogs(task)}
                      >
                        View Logs
                      </Button>
                    )}
                  </Space>
                </div>
                {task.start_date && (
                  <div style={{ fontSize: '12px', color: '#666', marginTop: '4px' }}>
                    Started: {new Date(task.start_date).toLocaleString()}
                    {task.end_date && ` | Ended: ${new Date(task.end_date).toLocaleString()}`}
                  </div>
                )}
              </Timeline.Item>
            ))}
          </Timeline>
        </div>

        {workflow.conf && (
          <Card
            title="Workflow Configuration"
            style={{ marginTop: '24px' }}
            type="inner"
          >
            <pre style={{ overflow: 'auto' }}>
              {JSON.stringify(workflow.conf, null, 2)}
            </pre>
          </Card>
        )}

        {selectedTask && taskLogs && (
          <Card
            title={`Logs for ${selectedTask.task_id}`}
            style={{ marginTop: '24px' }}
            type="inner"
            extra={
              <Button
                size="small"
                onClick={() => {
                  setSelectedTask(null);
                  setTaskLogs('');
                }}
              >
                Close
              </Button>
            }
          >
            <pre style={{ 
              overflow: 'auto', 
              maxHeight: '400px',
              backgroundColor: '#f5f5f5',
              padding: '12px',
              borderRadius: '4px'
            }}>
              {taskLogs}
            </pre>
          </Card>
        )}
      </Card>
    </div>
  );
};

export default WorkflowMonitor;