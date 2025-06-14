import React, { useState, useEffect } from 'react';
import { 
  Form, 
  Input, 
  Button, 
  Select, 
  Card, 
  Alert, 
  Space, 
  Upload, 
  message,
  Tabs,
  Row,
  Col,
  Typography,
  Divider,
  Tag
} from 'antd';
import { 
  PlayCircleOutlined, 
  UploadOutlined, 
  InfoCircleOutlined,
  CodeOutlined,
  EyeOutlined
} from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { tomorrow } from 'react-syntax-highlighter/dist/esm/styles/prism';

const { Option } = Select;
const { TextArea } = Input;
const { Title, Text, Paragraph } = Typography;
const { TabPane } = Tabs;

interface WorkflowTemplate {
  id: string;
  name: string;
  description: string;
  dag_id: string;
  default_config: any;
  category: string;
}

interface TriggerResponse {
  dag_run_id: string;
  dag_id: string;
  status: string;
  execution_date: string;
}

const WorkflowTrigger: React.FC = () => {
  const [form] = Form.useForm();
  const navigate = useNavigate();
  
  const [loading, setLoading] = useState(false);
  const [templates, setTemplates] = useState<WorkflowTemplate[]>([]);
  const [selectedTemplate, setSelectedTemplate] = useState<WorkflowTemplate | null>(null);
  const [triggerResponse, setTriggerResponse] = useState<TriggerResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  
  const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

  // Predefined workflow templates
  const defaultTemplates: WorkflowTemplate[] = [
    {
      id: '1',
      name: 'Image Analysis',
      description: 'Analyze images and extract insights using Vision AI',
      dag_id: 'visual_ai_workflow',
      category: 'vision',
      default_config: {
        input_data: {
          query: 'Analyze this image and provide insights',
          image_url: '',
          parameters: {
            detail_level: 'high',
            include_objects: true,
            include_text: true
          }
        }
      }
    },
    {
      id: '2',
      name: 'Multi-Agent Analysis',
      description: 'Use multiple AI agents to analyze content comprehensively',
      dag_id: 'visual_ai_multi_agent_pipeline',
      category: 'multi-agent',
      default_config: {
        input_data: {
          image_url: '',
          document_url: '',
          requirements: {
            analysis_depth: 'comprehensive',
            output_format: 'detailed_report'
          }
        }
      }
    },
    {
      id: '3',
      name: 'Document Processing',
      description: 'Extract and analyze text from documents',
      dag_id: 'visual_ai_workflow',
      category: 'text',
      default_config: {
        input_data: {
          query: 'Extract and summarize key information',
          document_url: '',
          parameters: {
            extract_tables: true,
            summarize: true,
            language: 'en'
          }
        }
      }
    }
  ];

  useEffect(() => {
    // In a real app, fetch templates from backend
    setTemplates(defaultTemplates);
  }, []);

  const handleTemplateSelect = (templateId: string) => {
    const template = templates.find(t => t.id === templateId);
    if (template) {
      setSelectedTemplate(template);
      form.setFieldsValue({
        dag_id: template.dag_id,
        input_data: JSON.stringify(template.default_config.input_data, null, 2)
      });
    }
  };

  const handleSubmit = async (values: any) => {
    setLoading(true);
    setError(null);
    setTriggerResponse(null);

    try {
      // Parse input data
      let inputData;
      try {
        inputData = JSON.parse(values.input_data);
      } catch (e) {
        throw new Error('Invalid JSON in input data');
      }

      const response = await axios.post(
        `${API_URL}/workflows/trigger`,
        {
          dag_id: values.dag_id,
          input_data: inputData,
          user_id: localStorage.getItem('user_id') || 'anonymous'
        },
        {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`
          }
        }
      );

      setTriggerResponse(response.data);
      message.success('Workflow triggered successfully!');

      // Redirect to monitoring page after 2 seconds
      setTimeout(() => {
        navigate(`/workflows/${response.data.dag_id}/${response.data.dag_run_id}`);
      }, 2000);

    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || 'Failed to trigger workflow');
      message.error('Failed to trigger workflow');
    } finally {
      setLoading(false);
    }
  };

  const handleFileUpload = (info: any) => {
    if (info.file.status === 'done') {
      message.success(`${info.file.name} uploaded successfully`);
      // Update form with file URL
      const currentData = JSON.parse(form.getFieldValue('input_data') || '{}');
      currentData.file_url = info.file.response.url;
      form.setFieldValue('input_data', JSON.stringify(currentData, null, 2));
    } else if (info.file.status === 'error') {
      message.error(`${info.file.name} upload failed.`);
    }
  };

  return (
    <div style={{ padding: '24px' }}>
      <Card>
        <Title level={2}>
          <PlayCircleOutlined /> Trigger AI Workflow
        </Title>
        <Paragraph>
          Select a workflow template or configure a custom workflow to execute with Apache Airflow orchestration.
        </Paragraph>

        <Tabs defaultActiveKey="templates">
          <TabPane tab="Templates" key="templates">
            <Row gutter={[16, 16]} style={{ marginBottom: '24px' }}>
              {templates.map(template => (
                <Col span={8} key={template.id}>
                  <Card
                    hoverable
                    onClick={() => handleTemplateSelect(template.id)}
                    style={{ 
                      border: selectedTemplate?.id === template.id ? '2px solid #1890ff' : undefined 
                    }}
                  >
                    <Title level={4}>{template.name}</Title>
                    <Paragraph>{template.description}</Paragraph>
                    <Space>
                      <Tag color="blue">{template.category}</Tag>
                      <Tag>{template.dag_id}</Tag>
                    </Space>
                  </Card>
                </Col>
              ))}
            </Row>
          </TabPane>

          <TabPane tab="Custom" key="custom">
            <Alert
              message="Custom Workflow"
              description="Configure your own workflow parameters for advanced use cases."
              type="info"
              showIcon
              style={{ marginBottom: '16px' }}
            />
          </TabPane>
        </Tabs>

        <Divider />

        <Form
          form={form}
          layout="vertical"
          onFinish={handleSubmit}
          initialValues={{
            dag_id: 'visual_ai_workflow',
            input_data: JSON.stringify({
              query: 'Analyze this content',
              parameters: {}
            }, null, 2)
          }}
        >
          <Form.Item
            label="Workflow (DAG ID)"
            name="dag_id"
            rules={[{ required: true, message: 'Please select a workflow' }]}
          >
            <Select placeholder="Select a workflow" size="large">
              <Option value="visual_ai_workflow">Visual AI Workflow</Option>
              <Option value="visual_ai_multi_agent_pipeline">Multi-Agent Pipeline</Option>
            </Select>
          </Form.Item>

          <Form.Item
            label={
              <Space>
                <span>Input Data (JSON)</span>
                <CodeOutlined />
              </Space>
            }
            name="input_data"
            rules={[
              { required: true, message: 'Please provide input data' },
              {
                validator: (_, value) => {
                  try {
                    JSON.parse(value);
                    return Promise.resolve();
                  } catch (e) {
                    return Promise.reject(new Error('Invalid JSON format'));
                  }
                }
              }
            ]}
          >
            <TextArea
              rows={10}
              placeholder="Enter workflow input data in JSON format"
              style={{ fontFamily: 'monospace' }}
            />
          </Form.Item>

          <Form.Item label="Upload Files (Optional)">
            <Upload
              name="file"
              action={`${API_URL}/upload`}
              headers={{
                authorization: `Bearer ${localStorage.getItem('token')}`
              }}
              onChange={handleFileUpload}
            >
              <Button icon={<UploadOutlined />}>Upload Image or Document</Button>
            </Upload>
          </Form.Item>

          {error && (
            <Alert
              message="Error"
              description={error}
              type="error"
              showIcon
              closable
              onClose={() => setError(null)}
              style={{ marginBottom: '16px' }}
            />
          )}

          {triggerResponse && (
            <Alert
              message="Workflow Triggered Successfully"
              description={
                <div>
                  <p>DAG Run ID: <code>{triggerResponse.dag_run_id}</code></p>
                  <p>Status: <Tag color="blue">{triggerResponse.status}</Tag></p>
                  <p>Redirecting to monitoring page...</p>
                </div>
              }
              type="success"
              showIcon
              style={{ marginBottom: '16px' }}
            />
          )}

          <Form.Item>
            <Space>
              <Button
                type="primary"
                htmlType="submit"
                loading={loading}
                size="large"
                icon={<PlayCircleOutlined />}
              >
                Trigger Workflow
              </Button>
              <Button
                size="large"
                onClick={() => form.resetFields()}
              >
                Reset
              </Button>
              <Button
                type="link"
                size="large"
                icon={<EyeOutlined />}
                onClick={() => navigate('/workflows')}
              >
                View All Workflows
              </Button>
            </Space>
          </Form.Item>
        </Form>

        {selectedTemplate && (
          <Card
            title="Template Configuration Preview"
            style={{ marginTop: '24px' }}
            type="inner"
          >
            <SyntaxHighlighter language="json" style={tomorrow}>
              {JSON.stringify(selectedTemplate.default_config, null, 2)}
            </SyntaxHighlighter>
          </Card>
        )}
      </Card>
    </div>
  );
};

export default WorkflowTrigger;