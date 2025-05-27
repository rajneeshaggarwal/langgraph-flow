import React, { useState } from 'react';
import { v4 as uuidv4 } from 'uuid';

// Type definitions
interface ComponentType {
  type: string;
  label: string;
  icon: string;
  description: string;
}

interface AgentComponentProps {
  agent: ComponentType;
  onDragStart: (event: React.DragEvent, nodeType: string) => void;
  onClick: () => void;
}

// Component types definition
const componentCategories = [
  {
    name: 'Inputs',
    icon: '📥',
    components: [
      { type: 'chatInput', label: 'Chat Input', icon: '💬', description: 'Interactive chat interface for user input' },
      { type: 'textInput', label: 'Text Input', icon: '📝', description: 'Simple text input field' },
    ]
  },
  {
    name: 'Outputs',
    icon: '📤',
    components: [
      { type: 'chatOutput', label: 'Chat Output', icon: '💭', description: 'Display chat responses and conversations' },
      { type: 'textOutput', label: 'Text Output', icon: '📄', description: 'Display formatted text results' },
    ]
  },
  {
    name: 'Prompts',
    icon: '📋',
    components: [
      { type: 'prompt', label: 'Prompt', icon: '📝', description: 'Create prompt templates with variables' },
    ]
  },
  {
    name: 'Agents',
    icon: '🤖',
    components: [
      { type: 'agent', label: 'Agent', icon: '🤖', description: 'AI-powered agent node' },
      { type: 'coordinator', label: 'Coordinator', icon: '👥', description: 'Coordinates multiple agents' },
      { type: 'researcher', label: 'Researcher', icon: '🔍', description: 'Research and data gathering' },
      { type: 'analyzer', label: 'Analyzer', icon: '📊', description: 'Data analysis agent' },
    ]
  },
  {
    name: 'Tools',
    icon: '🔧',
    components: [
      { type: 'tool', label: 'Tool', icon: '🔧', description: 'Custom tool integration' },
      { type: 'api', label: 'API Call', icon: '🌐', description: 'External API integration' },
      { type: 'database', label: 'Database', icon: '💾', description: 'Database operations' },
    ]
  },
  {
    name: 'Logic',
    icon: '🔀',
    components: [
      { type: 'conditional', label: 'Conditional', icon: '🔀', description: 'Conditional branching' },
      { type: 'loop', label: 'Loop', icon: '🔄', description: 'Iterative operations' },
      { type: 'switch', label: 'Switch', icon: '🎛️', description: 'Multi-path branching' },
    ]
  },
  {
    name: 'Data',
    icon: '📄',
    components: [
      { type: 'input', label: 'Input', icon: '📥', description: 'Data input node' },
      { type: 'output', label: 'Output', icon: '📤', description: 'Data output node' },
      { type: 'transform', label: 'Transform', icon: '🔄', description: 'Data transformation' },
    ]
  }
];

// Agent Component
const AgentComponent = ({ agent, onDragStart, onClick }: AgentComponentProps) => {
  const [isHovered, setIsHovered] = useState(false);

  // Get colors based on component type
  const getComponentColors = (type: string) => {
    switch (type) {
      case 'chatInput':
        return 'border-blue-300 bg-blue-50 hover:border-blue-400';
      case 'textInput':
        return 'border-green-300 bg-green-50 hover:border-green-400';
      case 'chatOutput':
        return 'border-purple-300 bg-purple-50 hover:border-purple-400';
      case 'textOutput':
        return 'border-indigo-300 bg-indigo-50 hover:border-indigo-400';
      case 'agent':
        return 'border-blue-300 bg-blue-50 hover:border-blue-400';
      case 'coordinator':
        return 'border-purple-300 bg-purple-50 hover:border-purple-400';
      case 'researcher':
        return 'border-green-300 bg-green-50 hover:border-green-400';
      case 'analyzer':
        return 'border-orange-300 bg-orange-50 hover:border-orange-400';
      default:
        return 'border-gray-300 bg-gray-50 hover:border-gray-400';
    }
  };

  const getIconBackgroundColor = (type: string) => {
    switch (type) {
      case 'chatInput':
        return 'bg-blue-100';
      case 'textInput':
        return 'bg-green-100';
      case 'chatOutput':
        return 'bg-purple-100';
      case 'textOutput':
        return 'bg-indigo-100';
      case 'agent':
        return 'bg-blue-100';
      case 'coordinator':
        return 'bg-purple-100';
      case 'researcher':
        return 'bg-green-100';
      case 'analyzer':
        return 'bg-orange-100';
      default:
        return 'bg-gray-100';
    }
  };

  return (
    <div
      className={`
        relative p-3 rounded-lg border-2 cursor-move transition-all duration-200 mb-2
        ${getComponentColors(agent.type)}
        ${isHovered ? 'shadow-lg transform scale-105' : 'hover:shadow-md'}
      `}
      onDragStart={(e) => onDragStart(e, agent.type)}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
      onClick={onClick}
      draggable
    >
      <div className="flex items-start space-x-3">
        <div className="flex-shrink-0">
          <div className={`w-10 h-10 rounded-full flex items-center justify-center ${getIconBackgroundColor(agent.type)}`}>
            <span className="text-xl">{agent.icon}</span>
          </div>
        </div>
        <div className="flex-1 min-w-0">
          <h4 className="text-sm font-semibold text-gray-900 truncate">
            {agent.label}
          </h4>
          <p className="text-xs text-gray-500 mt-0.5 line-clamp-2">
            {agent.description}
          </p>
        </div>
      </div>
      
      {/* Drag indicator */}
      <div className="absolute right-2 top-1/2 transform -translate-y-1/2 opacity-0 hover:opacity-100 transition-opacity">
        <svg className="w-4 h-4 text-gray-400" fill="currentColor" viewBox="0 0 20 20">
          <path d="M7 2a2 2 0 1 1-4 0 2 2 0 0 1 4 0zM7 6a2 2 0 1 1-4 0 2 2 0 0 1 4 0zM7 10a2 2 0 1 1-4 0 2 2 0 0 1 4 0zM15 2a2 2 0 1 1-4 0 2 2 0 0 1 4 0zM15 6a2 2 0 1 1-4 0 2 2 0 0 1 4 0zM15 10a2 2 0 1 1-4 0 2 2 0 0 1 4 0z"/>
        </svg>
      </div>
    </div>
  );
};

// Navigation Bar Component
const LeftNavigationBar = () => {
  const [searchTerm, setSearchTerm] = useState('');
  const [expandedCategories, setExpandedCategories] = useState(['Inputs', 'Outputs', 'Prompts', 'Agents']);
  const [selectedCategory, setSelectedCategory] = useState('all');

  // Mock addNode function - replace with your actual store function
  const addNode = (type: string, position: { x: number; y: number }) => {
    console.log('Adding node:', type, position);
    // This would be replaced with your actual store action
  };

  const onDragStart = (event: React.DragEvent, nodeType: string) => {
    event.dataTransfer.setData('application/reactflow', nodeType);
    event.dataTransfer.effectAllowed = 'move';
  };

  const toggleCategory = (categoryName: string) => {
    setExpandedCategories(prev => 
      prev.includes(categoryName) 
        ? prev.filter(c => c !== categoryName)
        : [...prev, categoryName]
    );
  };

  const filteredCategories = componentCategories.map(category => ({
    ...category,
    components: category.components.filter(component => 
      component.label.toLowerCase().includes(searchTerm.toLowerCase()) ||
      component.description.toLowerCase().includes(searchTerm.toLowerCase())
    )
  })).filter(category => 
    selectedCategory === 'all' || 
    category.name === selectedCategory ||
    category.components.length > 0
  );

  return (
    <aside className="w-80 bg-gray-50 h-full flex flex-col border-r border-gray-200">
      {/* Header */}
      <div className="p-4 bg-white border-b border-gray-200">
        <h2 className="text-lg font-bold text-gray-800 mb-3">Components</h2>
        
        {/* Search Bar */}
        <div className="relative">
          <input
            type="text"
            placeholder="Search components..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full px-3 py-2 pl-10 text-sm border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
          <svg 
            className="absolute left-3 top-2.5 w-4 h-4 text-gray-400"
            fill="none" 
            stroke="currentColor" 
            viewBox="0 0 24 24"
          >
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
          </svg>
        </div>
      </div>

      {/* Components List */}
      <div className="flex-1 overflow-y-auto p-4">
        {filteredCategories.map((category) => (
          <div key={category.name} className="mb-6">
            <button
              onClick={() => toggleCategory(category.name)}
              className="flex items-center justify-between w-full mb-3 group"
            >
              <div className="flex items-center space-x-2">
                <span className="text-lg">{category.icon}</span>
                <h3 className="text-sm font-semibold text-gray-700 group-hover:text-gray-900">
                  {category.name}
                </h3>
                <span className="text-xs text-gray-500">
                  ({category.components.length})
                </span>
              </div>
              <svg
                className={`w-4 h-4 text-gray-400 transition-transform ${
                  expandedCategories.includes(category.name) ? 'rotate-180' : ''
                }`}
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
              </svg>
            </button>

            {expandedCategories.includes(category.name) && (
              <div className="space-y-2">
                {category.components.map((component) => (
                  <AgentComponent
                    key={component.type}
                    agent={component}
                    onDragStart={onDragStart}
                    onClick={() => addNode(component.type, { x: 250, y: 250 })}
                  />
                ))}
              </div>
            )}
          </div>
        ))}

        {filteredCategories.every(cat => cat.components.length === 0) && (
          <div className="text-center py-8">
            <p className="text-gray-500 text-sm">No components found</p>
          </div>
        )}
      </div>

      {/* Quick Actions */}
      <div className="p-4 bg-white border-t border-gray-200">
        <h4 className="text-xs font-semibold text-gray-600 uppercase tracking-wider mb-2">
          Quick Actions
        </h4>
        <div className="grid grid-cols-2 gap-2">
          <button className="px-3 py-2 text-xs bg-blue-50 text-blue-700 rounded hover:bg-blue-100 transition-colors">
            Import Flow
          </button>
          <button className="px-3 py-2 text-xs bg-green-50 text-green-700 rounded hover:bg-green-100 transition-colors">
            Templates
          </button>
        </div>
      </div>
    </aside>
  );
};

// NodePanel Component
export function NodePanel() {
  return (
    <LeftNavigationBar />
  );
}