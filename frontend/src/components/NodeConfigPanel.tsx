// Enhanced NodeConfigPanel.tsx
import React, { useState, useEffect } from 'react';
import { Node } from 'reactflow';
import { useWorkflowStore } from '../store/workflowStore';

interface NodeConfigPanelProps {
  node: Node | null;
  onClose: () => void;
}

interface ModelProvider {
  id: string;
  name: string;
  icon: string;
  models: string[];
  apiKeyLabel: string;
}

const MODEL_PROVIDERS: ModelProvider[] = [
  {
    id: 'openai',
    name: 'OpenAI',
    icon: '🤖',
    models: ['gpt-4o', 'gpt-4-turbo', 'gpt-4', 'gpt-3.5-turbo'],
    apiKeyLabel: 'OpenAI API Key'
  },
  {
    id: 'anthropic',
    name: 'Anthropic',
    icon: '🧠',
    models: ['claude-3-opus', 'claude-3-sonnet', 'claude-3-haiku'],
    apiKeyLabel: 'Anthropic API Key'
  },
  {
    id: 'google',
    name: 'Google',
    icon: '🔍',
    models: ['gemini-pro', 'gemini-pro-vision', 'palm-2'],
    apiKeyLabel: 'Google API Key'
  },
  {
    id: 'azure',
    name: 'Azure OpenAI',
    icon: '☁️',
    models: ['gpt-4', 'gpt-35-turbo', 'text-davinci-003'],
    apiKeyLabel: 'Azure API Key'
  }
];

const AVAILABLE_TOOLS = [
  { id: 'web_search', name: 'Web Search', icon: '🔍', description: 'Search the web for information' },
  { id: 'calculator', name: 'Calculator', icon: '🧮', description: 'Perform mathematical calculations' },
  { id: 'file_reader', name: 'File Reader', icon: '📄', description: 'Read and process files' },
  { id: 'api_caller', name: 'API Caller', icon: '🌐', description: 'Make HTTP API calls' },
  { id: 'database', name: 'Database', icon: '💾', description: 'Query databases' },
  { id: 'email', name: 'Email', icon: '📧', description: 'Send emails' },
  { id: 'code_executor', name: 'Code Executor', icon: '💻', description: 'Execute code snippets' }
];

export const NodeConfigPanel: React.FC<NodeConfigPanelProps> = ({ node, onClose }) => {
  const updateNodeData = useWorkflowStore((state) => state.updateNodeData);
  const [config, setConfig] = useState<any>({});
  const [selectedProvider, setSelectedProvider] = useState<ModelProvider>(MODEL_PROVIDERS[0]);
  const [selectedTools, setSelectedTools] = useState<string[]>([]);
  const [showApiKey, setShowApiKey] = useState(false);

  useEffect(() => {
    if (node) {
      const nodeConfig = node.data.config || {};
      setConfig(nodeConfig);
      
      // Set provider based on saved config
      const provider = MODEL_PROVIDERS.find(p => p.id === nodeConfig.provider) || MODEL_PROVIDERS[0];
      setSelectedProvider(provider);
      
      setSelectedTools(nodeConfig.tools || []);
    }
  }, [node]);

  if (!node) return null;

  const handleSave = () => {
    const updatedConfig = {
      ...config,
      provider: selectedProvider.id,
      tools: selectedTools
    };
    updateNodeData(node.id, { config: updatedConfig });
    onClose();
  };

  const handleProviderChange = (providerId: string) => {
    const provider = MODEL_PROVIDERS.find(p => p.id === providerId);
    if (provider) {
      setSelectedProvider(provider);
      // Reset model if it's not available in the new provider
      if (!provider.models.includes(config.model)) {
        setConfig({ ...config, model: provider.models[0] });
      }
    }
  };

  const toggleTool = (toolId: string) => {
    setSelectedTools(prev => 
      prev.includes(toolId) 
        ? prev.filter(id => id !== toolId)
        : [...prev, toolId]
    );
  };

  const renderAgentConfig = () => (
    <div className="space-y-6">
      {/* Model Provider Section */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-3">
          Model Provider
        </label>
        <div className="grid grid-cols-2 gap-2">
          {MODEL_PROVIDERS.map((provider) => (
            <button
              key={provider.id}
              onClick={() => handleProviderChange(provider.id)}
              className={`flex items-center p-3 rounded-lg border-2 transition-all ${
                selectedProvider.id === provider.id
                  ? 'border-blue-500 bg-blue-50'
                  : 'border-gray-200 hover:border-gray-300'
              }`}
            >
              <span className="text-lg mr-2">{provider.icon}</span>
              <span className="text-sm font-medium">{provider.name}</span>
            </button>
          ))}
        </div>
      </div>

      {/* Model Name Section */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Model Name
        </label>
        <select
          value={config.model || selectedProvider.models[0]}
          onChange={(e) => setConfig({ ...config, model: e.target.value })}
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
        >
          {selectedProvider.models.map((model) => (
            <option key={model} value={model}>
              {model}
            </option>
          ))}
        </select>
      </div>

      {/* API Key Section */}
      <div>
        <div className="flex items-center justify-between mb-2">
          <label className="block text-sm font-medium text-gray-700">
            {selectedProvider.apiKeyLabel} <span className="text-red-500">*</span>
          </label>
          <button
            onClick={() => setShowApiKey(!showApiKey)}
            className="text-xs text-gray-500 hover:text-gray-700"
          >
            {showApiKey ? 'Hide' : 'Show'}
          </button>
        </div>
        <div className="relative">
          <input
            type={showApiKey ? 'text' : 'password'}
            value={config.apiKey || ''}
            onChange={(e) => setConfig({ ...config, apiKey: e.target.value })}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 pr-10"
            placeholder="Enter your API key..."
          />
          <div className="absolute right-3 top-2.5">
            <svg className="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
            </svg>
          </div>
        </div>
        <p className="mt-1 text-xs text-gray-500">
          Keep your API keys secure. They will be encrypted when saved.
        </p>
      </div>

      {/* Agent Instructions Section */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Agent Instructions
        </label>
        <textarea
          value={config.instructions || 'You are a helpful assistant that can'}
          onChange={(e) => setConfig({ ...config, instructions: e.target.value })}
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          rows={6}
          placeholder="Describe what this agent should do and how it should behave..."
        />
        <p className="mt-1 text-xs text-gray-500">
          Clear instructions help the agent understand its role and capabilities.
        </p>
      </div>

      {/* Tools Section */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-3">
          Tools
        </label>
        <div className="space-y-2 max-h-48 overflow-y-auto">
          {AVAILABLE_TOOLS.map((tool) => (
            <div
              key={tool.id}
              className={`flex items-center p-3 rounded-lg border cursor-pointer transition-all ${
                selectedTools.includes(tool.id)
                  ? 'border-blue-500 bg-blue-50'
                  : 'border-gray-200 hover:border-gray-300'
              }`}
              onClick={() => toggleTool(tool.id)}
            >
              <div className="flex items-center space-x-3 flex-1">
                <span className="text-lg">{tool.icon}</span>
                <div className="flex-1">
                  <div className="font-medium text-sm">{tool.name}</div>
                  <div className="text-xs text-gray-500">{tool.description}</div>
                </div>
              </div>
              <div className={`w-4 h-4 rounded border-2 flex items-center justify-center ${
                selectedTools.includes(tool.id)
                  ? 'border-blue-500 bg-blue-500'
                  : 'border-gray-300'
              }`}>
                {selectedTools.includes(tool.id) && (
                  <svg className="w-3 h-3 text-white" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                  </svg>
                )}
              </div>
            </div>
          ))}
        </div>
        <p className="mt-2 text-xs text-gray-500">
          Selected tools: {selectedTools.length} / {AVAILABLE_TOOLS.length}
        </p>
      </div>

      {/* Input Configuration Section */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Input
        </label>
        <div className="border border-gray-200 rounded-lg p-3">
          <div className="flex items-center space-x-2 mb-2">
            <svg className="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 12a9 9 0 01-9 9m9-9a9 9 0 00-9-9m9 9H3m9 9v-9m0-9v9" />
            </svg>
            <span className="text-sm font-medium">Web Input</span>
          </div>
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-xs text-gray-600 mb-1">Input Type</label>
              <select
                value={config.inputType || 'text'}
                onChange={(e) => setConfig({ ...config, inputType: e.target.value })}
                className="w-full px-2 py-1 text-sm border border-gray-300 rounded focus:outline-none focus:ring-1 focus:ring-blue-500"
              >
                <option value="text">Text</option>
                <option value="json">JSON</option>
                <option value="file">File</option>
                <option value="url">URL</option>
              </select>
            </div>
            <div>
              <label className="block text-xs text-gray-600 mb-1">Required</label>
              <label className="flex items-center">
                <input
                  type="checkbox"
                  checked={config.inputRequired || false}
                  onChange={(e) => setConfig({ ...config, inputRequired: e.target.checked })}
                  className="mr-2"
                />
                <span className="text-sm">Required</span>
              </label>
            </div>
          </div>
        </div>
      </div>

      {/* Advanced Settings */}
      <div>
        <details className="group">
          <summary className="flex items-center justify-between cursor-pointer list-none">
            <span className="text-sm font-medium text-gray-700">Advanced Settings</span>
            <svg className="w-4 h-4 text-gray-400 group-open:rotate-180 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
            </svg>
          </summary>
          
          <div className="mt-3 space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Temperature: {config.temperature || 0.7}
              </label>
              <input
                type="range"
                min="0"
                max="1"
                step="0.1"
                value={config.temperature || 0.7}
                onChange={(e) => setConfig({ ...config, temperature: parseFloat(e.target.value) })}
                className="w-full"
              />
              <div className="flex justify-between text-xs text-gray-500 mt-1">
                <span>Focused</span>
                <span>Creative</span>
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Max Tokens
              </label>
              <input
                type="number"
                value={config.maxTokens || 1000}
                onChange={(e) => setConfig({ ...config, maxTokens: parseInt(e.target.value) })}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                min="1"
                max="4000"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Timeout (seconds)
              </label>
              <input
                type="number"
                value={config.timeout || 30}
                onChange={(e) => setConfig({ ...config, timeout: parseInt(e.target.value) })}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                min="5"
                max="300"
              />
            </div>
          </div>
        </details>
      </div>
    </div>
  );

  const renderInputConfig = () => (
    <div className="space-y-6">
      {/* Input Type Configuration */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Input Type
        </label>
        <select
          value={config.inputType || 'text'}
          onChange={(e) => setConfig({ ...config, inputType: e.target.value })}
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          <option value="text">Text</option>
          <option value="number">Number</option>
          <option value="email">Email</option>
          <option value="url">URL</option>
          <option value="password">Password</option>
          <option value="textarea">Textarea</option>
        </select>
      </div>

      {/* Placeholder Text */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Placeholder Text
        </label>
        <input
          type="text"
          value={config.placeholder || ''}
          onChange={(e) => setConfig({ ...config, placeholder: e.target.value })}
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          placeholder="Enter placeholder text..."
        />
      </div>

      {/* Default Value */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Default Value
        </label>
        <input
          type="text"
          value={config.defaultValue || ''}
          onChange={(e) => setConfig({ ...config, defaultValue: e.target.value })}
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          placeholder="Enter default value..."
        />
      </div>

      {/* Required Field */}
      <div className="flex items-center">
        <input
          type="checkbox"
          id="required"
          checked={config.required || false}
          onChange={(e) => setConfig({ ...config, required: e.target.checked })}
          className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
        />
        <label htmlFor="required" className="ml-2 block text-sm text-gray-900">
          Required field
        </label>
      </div>

      {/* Validation */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Validation Pattern (Regex)
        </label>
        <input
          type="text"
          value={config.pattern || ''}
          onChange={(e) => setConfig({ ...config, pattern: e.target.value })}
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          placeholder="^[a-zA-Z0-9]+$"
        />
        <p className="mt-1 text-xs text-gray-500">
          Optional regex pattern for input validation
        </p>
      </div>
    </div>
  );

  const renderChatInputConfig = () => (
    <div className="space-y-6">
      {/* Chat Settings */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Chat Interface Style
        </label>
        <select
          value={config.chatStyle || 'bubble'}
          onChange={(e) => setConfig({ ...config, chatStyle: e.target.value })}
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          <option value="bubble">Bubble Style</option>
          <option value="flat">Flat Style</option>
          <option value="minimal">Minimal</option>
        </select>
      </div>

      {/* Welcome Message */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Welcome Message
        </label>
        <textarea
          value={config.welcomeMessage || 'Hello! How can I help you today?'}
          onChange={(e) => setConfig({ ...config, welcomeMessage: e.target.value })}
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          rows={3}
          placeholder="Enter welcome message..."
        />
      </div>

      {/* Input Placeholder */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Input Placeholder
        </label>
        <input
          type="text"
          value={config.inputPlaceholder || 'Type your message...'}
          onChange={(e) => setConfig({ ...config, inputPlaceholder: e.target.value })}
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
      </div>

      {/* Enable File Upload */}
      <div className="flex items-center">
        <input
          type="checkbox"
          id="fileUpload"
          checked={config.enableFileUpload || false}
          onChange={(e) => setConfig({ ...config, enableFileUpload: e.target.checked })}
          className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
        />
        <label htmlFor="fileUpload" className="ml-2 block text-sm text-gray-900">
          Enable file upload
        </label>
      </div>

      {/* Message History Limit */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Message History Limit
        </label>
        <input
          type="number"
          value={config.historyLimit || 50}
          onChange={(e) => setConfig({ ...config, historyLimit: parseInt(e.target.value) })}
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          min="1"
          max="1000"
        />
      </div>
    </div>
  );

  const renderOutputConfig = () => (
    <div className="space-y-6">
      {/* Output Format */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Output Format
        </label>
        <select
          value={config.outputFormat || 'text'}
          onChange={(e) => setConfig({ ...config, outputFormat: e.target.value })}
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          <option value="text">Plain Text</option>
          <option value="markdown">Markdown</option>
          <option value="html">HTML</option>
          <option value="json">JSON</option>
        </select>
      </div>

      {/* Display Options */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Display Style
        </label>
        <div className="space-y-2">
          <label className="flex items-center">
            <input
              type="radio"
              name="displayStyle"
              value="inline"
              checked={config.displayStyle === 'inline'}
              onChange={(e) => setConfig({ ...config, displayStyle: e.target.value })}
              className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300"
            />
            <span className="ml-2 text-sm text-gray-900">Inline</span>
          </label>
          <label className="flex items-center">
            <input
              type="radio"
              name="displayStyle"
              value="block"
              checked={config.displayStyle === 'block'}
              onChange={(e) => setConfig({ ...config, displayStyle: e.target.value })}
              className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300"
            />
            <span className="ml-2 text-sm text-gray-900">Block</span>
          </label>
          <label className="flex items-center">
            <input
              type="radio"
              name="displayStyle"
              value="card"
              checked={config.displayStyle === 'card'}
              onChange={(e) => setConfig({ ...config, displayStyle: e.target.value })}
              className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300"
            />
            <span className="ml-2 text-sm text-gray-900">Card</span>
          </label>
        </div>
      </div>

      {/* Auto-refresh */}
      <div className="flex items-center">
        <input
          type="checkbox"
          id="autoRefresh"
          checked={config.autoRefresh || false}
          onChange={(e) => setConfig({ ...config, autoRefresh: e.target.checked })}
          className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
        />
        <label htmlFor="autoRefresh" className="ml-2 block text-sm text-gray-900">
          Auto-refresh output
        </label>
      </div>

      {config.autoRefresh && (
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Refresh Interval (seconds)
          </label>
          <input
            type="number"
            value={config.refreshInterval || 30}
            onChange={(e) => setConfig({ ...config, refreshInterval: parseInt(e.target.value) })}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            min="1"
            max="3600"
          />
        </div>
      )}

      {/* Max Length */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Maximum Display Length
        </label>
        <input
          type="number"
          value={config.maxLength || 1000}
          onChange={(e) => setConfig({ ...config, maxLength: parseInt(e.target.value) })}
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          min="100"
          max="10000"
        />
        <p className="mt-1 text-xs text-gray-500">
          Maximum characters to display (0 for unlimited)
        </p>
      </div>
    </div>
  );

  const renderChatOutputConfig = () => (
    <div className="space-y-6">
      {/* Chat Display Settings */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Chat Display Mode
        </label>
        <select
          value={config.displayMode || 'conversation'}
          onChange={(e) => setConfig({ ...config, displayMode: e.target.value })}
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          <option value="conversation">Full Conversation</option>
          <option value="latest">Latest Message Only</option>
          <option value="summary">Summary View</option>
        </select>
      </div>

      {/* Message Bubble Style */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Message Bubble Style
        </label>
        <select
          value={config.bubbleStyle || 'modern'}
          onChange={(e) => setConfig({ ...config, bubbleStyle: e.target.value })}
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          <option value="modern">Modern</option>
          <option value="classic">Classic</option>
          <option value="minimal">Minimal</option>
          <option value="bordered">Bordered</option>
        </select>
      </div>

      {/* Show Timestamps */}
      <div className="flex items-center">
        <input
          type="checkbox"
          id="showTimestamps"
          checked={config.showTimestamps || false}
          onChange={(e) => setConfig({ ...config, showTimestamps: e.target.checked })}
          className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
        />
        <label htmlFor="showTimestamps" className="ml-2 block text-sm text-gray-900">
          Show timestamps
        </label>
      </div>

      {/* Show Avatar */}
      <div className="flex items-center">
        <input
          type="checkbox"
          id="showAvatar"
          checked={config.showAvatar || true}
          onChange={(e) => setConfig({ ...config, showAvatar: e.target.checked })}
          className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
        />
        <label htmlFor="showAvatar" className="ml-2 block text-sm text-gray-900">
          Show user avatars
        </label>
      </div>

      {/* Enable Copy */}
      <div className="flex items-center">
        <input
          type="checkbox"
          id="enableCopy"
          checked={config.enableCopy || true}
          onChange={(e) => setConfig({ ...config, enableCopy: e.target.checked })}
          className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
        />
        <label htmlFor="enableCopy" className="ml-2 block text-sm text-gray-900">
          Enable message copying
        </label>
      </div>

      {/* Max Messages */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Maximum Messages to Display
        </label>
        <input
          type="number"
          value={config.maxMessages || 100}
          onChange={(e) => setConfig({ ...config, maxMessages: parseInt(e.target.value) })}
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          min="1"
          max="500"
        />
      </div>
    </div>
  );

  const renderOtherNodeTypes = () => {
    // Configuration for different node types
    switch (node.data.type) {
      case 'chatInput':
        return renderChatInputConfig();
      case 'textInput':
        return renderInputConfig();
      case 'chatOutput':
        return renderChatOutputConfig();
      case 'textOutput':
        return renderOutputConfig();
      case 'tool':
        return (
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Tool Name
              </label>
              <input
                type="text"
                value={config.toolName || ''}
                onChange={(e) => setConfig({ ...config, toolName: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="Enter tool name..."
              />
            </div>
          </div>
        );
      default:
        return null;
    }
  };

  return (
    <div className="fixed right-0 top-0 h-full w-96 bg-white shadow-xl z-50 overflow-y-auto">
      <div className="sticky top-0 bg-white border-b border-gray-200 p-4">
        <div className="flex justify-between items-center">
          <h3 className="text-xl font-bold text-gray-900">Configure {node.data.label}</h3>
          <button
            onClick={onClose}
            className="p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-lg transition-colors"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
      </div>

      <div className="p-4">
        {/* Node Name */}
        <div className="mb-6">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Node Name
          </label>
          <input
            type="text"
            value={node.data.label}
            onChange={(e) => updateNodeData(node.id, { label: e.target.value })}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>

        {/* Node-specific configuration */}
        {node.data.type === 'agent' ? renderAgentConfig() : renderOtherNodeTypes()}

        {/* Action Buttons */}
        <div className="sticky bottom-0 bg-white border-t border-gray-200 p-4 flex justify-end space-x-3 mt-8">
          <button
            onClick={onClose}
            className="px-4 py-2 text-gray-700 bg-gray-200 rounded-md hover:bg-gray-300 transition-colors"
          >
            Cancel
          </button>
          <button
            onClick={handleSave}
            className="px-4 py-2 text-white bg-blue-600 rounded-md hover:bg-blue-700 transition-colors"
          >
            Save Changes
          </button>
        </div>
      </div>
    </div>
  );
};