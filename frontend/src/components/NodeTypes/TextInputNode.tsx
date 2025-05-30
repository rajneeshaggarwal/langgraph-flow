// frontend/src/components/NodeTypes/TextInputNode.tsx
import React, { memo, useState, useEffect, useRef } from 'react';
import { Handle, Position, NodeProps } from 'reactflow';
import { useWorkflowStore } from '../../store/workflowStore';
import ReactDOM from 'react-dom';

export const TextInputNode = memo(({ data, selected, id }: NodeProps) => {
  const [showEditModal, setShowEditModal] = useState(false);
  const [editValue, setEditValue] = useState(data.config?.defaultValue || '');
  const [isEditingTitle, setIsEditingTitle] = useState(false);
  const [isEditingDescription, setIsEditingDescription] = useState(false);
  const [titleValue, setTitleValue] = useState(data.label || 'Text Input');
  const [descriptionValue, setDescriptionValue] = useState(data.description || 'Get text inputs from the Playground.');
  const [isOutputHidden, setIsOutputHidden] = useState(false); // Controls hidden eye icon state
  const [isOutputExpanded, setIsOutputExpanded] = useState(true); // Controls expand/collapse state
  const updateNodeData = useWorkflowStore((state) => state.updateNodeData);
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const titleInputRef = useRef<HTMLInputElement>(null);
  const descriptionTextareaRef = useRef<HTMLTextAreaElement>(null);

  const handleSaveEdit = () => {
    updateNodeData(id, {
      config: {
        ...data.config,
        defaultValue: editValue
      }
    });
    setShowEditModal(false);
  };

  const handleConfigClick = (e: React.MouseEvent) => {
    e.stopPropagation();
    const event = new CustomEvent('nodeConfigClick', { 
      detail: { nodeId: id }
    });
    window.dispatchEvent(event);
  };

  const handleTitleSave = () => {
    updateNodeData(id, {
      label: titleValue
    });
    setIsEditingTitle(false);
  };

  const handleDescriptionSave = () => {
    updateNodeData(id, {
      description: descriptionValue
    });
    setIsEditingDescription(false);
  };

  const toggleOutputVisibility = (e: React.MouseEvent) => {
    e.stopPropagation();
    setIsOutputHidden(!isOutputHidden);
    if (!isOutputHidden) {
      // When hiding output (eye icon -> hidden eye icon), collapse the footer
      setIsOutputExpanded(false);
    } else {
      // When showing output (hidden eye icon -> eye icon), expand the footer
      setIsOutputExpanded(true);
    }
  };

  const toggleOutputExpansion = (e: React.MouseEvent) => {
    e.stopPropagation();
    setIsOutputExpanded(!isOutputExpanded);
  };

  useEffect(() => {
    if (isEditingTitle && titleInputRef.current) {
      titleInputRef.current.focus();
      titleInputRef.current.select();
    }
  }, [isEditingTitle]);

  useEffect(() => {
    if (isEditingDescription && descriptionTextareaRef.current) {
      descriptionTextareaRef.current.focus();
      descriptionTextareaRef.current.select();
    }
  }, [isEditingDescription]);

  // Main Edit Modal (existing)
  const EditModal = () => {
    useEffect(() => {
      if (showEditModal && textareaRef.current) {
        textareaRef.current.focus();
        const length = textareaRef.current.value.length;
        textareaRef.current.setSelectionRange(length, length);
        
        const handleKeyDown = (e: KeyboardEvent) => {
          if (e.key === 'Delete' || e.key === 'Backspace') {
            e.stopPropagation();
          }
        };

        document.addEventListener('keydown', handleKeyDown, true);
        return () => {
          document.removeEventListener('keydown', handleKeyDown, true);
        };
      }
    }, [showEditModal]);

    if (!showEditModal) return null;

    return ReactDOM.createPortal(
      <div className="fixed inset-0 z-[999999] p-8" style={{ backgroundColor: 'rgba(0, 0, 0, 0.5)' }}>
        <div className="w-full h-full bg-white rounded-lg shadow-2xl flex flex-col">
          <div className="flex items-center justify-between px-6 py-4 border-b border-gray-200">
            <div className="flex items-center space-x-2">
              <svg className="w-5 h-5 text-gray-700" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
              <h2 className="text-lg font-semibold text-gray-900">Edit text content</h2>
            </div>
            <button
              onClick={() => setShowEditModal(false)}
              className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
            >
              <svg className="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>

          <div className="flex-1 p-6 overflow-hidden">
            <textarea
              ref={textareaRef}
              value={editValue}
              onChange={(e) => {
                setEditValue(e.target.value);
              }}
              onKeyDown={(e) => {
                if (e.key === 'Delete' || e.key === 'Backspace') {
                  e.stopPropagation();
                }
              }}
              placeholder="Type message here."
              className="w-full h-full px-4 py-3 border border-gray-300 rounded-lg resize-none focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-gray-700"
              style={{ 
                textAlign: 'left',
                direction: 'ltr',
                unicodeBidi: 'normal',
                writingMode: 'horizontal-tb'
              }}
              lang="en"
              dir="ltr"
            />
          </div>

          <div className="px-6 py-4 flex justify-end border-t border-gray-200">
            <button
              onClick={handleSaveEdit}
              className="px-6 py-2.5 bg-gray-900 text-white rounded-lg hover:bg-gray-800 transition-colors font-medium"
            >
              Finish Editing
            </button>
          </div>
        </div>
      </div>,
      document.body
    );
  };

  return (
    <>
      <div
        className={`shadow-md rounded-lg bg-white border-2 min-w-[350px] relative ${
          selected ? 'border-blue-500' : 'border-gray-200'
        }`}
      >
        <Handle
          type="target"
          position={Position.Left}
          className="w-3 h-3 bg-blue-500"
          style={{ left: -6 }}
        />
        
        {/* Header */}
        <div className="px-4 py-3 border-b border-gray-200">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3 flex-1">
              <div className="w-8 h-8 bg-gray-100 rounded flex items-center justify-center">
                <span className="text-lg font-bold text-gray-700">T</span>
              </div>
              <div className="flex-1">
                {/* Inline Title Edit */}
                <div className="relative group">
                  {isEditingTitle ? (
                    <input
                      ref={titleInputRef}
                      type="text"
                      value={titleValue}
                      onChange={(e) => setTitleValue(e.target.value)}
                      onBlur={handleTitleSave}
                      onKeyDown={(e) => {
                        if (e.key === 'Enter') {
                          handleTitleSave();
                        } else if (e.key === 'Escape') {
                          setTitleValue(data.label || 'Text Input');
                          setIsEditingTitle(false);
                        } else if (e.key === 'Delete' || e.key === 'Backspace') {
                          e.stopPropagation();
                        }
                      }}
                      className="text-sm font-semibold text-gray-900 bg-blue-100 border border-blue-400 rounded px-2 py-0.5 outline-none"
                    />
                  ) : (
                    <div 
                      className="inline-flex items-center relative"
                      onDoubleClick={() => setIsEditingTitle(true)}
                    >
                      <h3 className="text-sm font-semibold text-gray-900 pr-6">
                        {data.label || 'Text Input'}
                      </h3>
                      <button 
                        onClick={(e) => {
                          e.stopPropagation();
                          setIsEditingTitle(true);
                        }}
                        className="absolute right-0 p-0.5 opacity-0 group-hover:opacity-100 transition-opacity"
                      >
                        <svg className="w-3 h-3 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z" />
                        </svg>
                      </button>
                    </div>
                  )}
                </div>
                
                {/* Inline Description Edit */}
                <div className="relative group mt-1">
                  {isEditingDescription ? (
                    <textarea
                      ref={descriptionTextareaRef}
                      value={descriptionValue}
                      onChange={(e) => setDescriptionValue(e.target.value)}
                      onBlur={handleDescriptionSave}
                      onKeyDown={(e) => {
                        if (e.key === 'Enter' && !e.shiftKey) {
                          e.preventDefault();
                          handleDescriptionSave();
                        } else if (e.key === 'Escape') {
                          setDescriptionValue(data.description || 'Get text inputs from the Playground.');
                          setIsEditingDescription(false);
                        } else if (e.key === 'Delete' || e.key === 'Backspace') {
                          e.stopPropagation();
                        }
                      }}
                      className="text-xs text-gray-500 bg-gray-100 border border-gray-300 rounded px-2 py-0.5 outline-none w-full resize-none"
                      rows={1}
                    />
                  ) : (
                    <div 
                      className="flex items-start justify-between"
                      onDoubleClick={() => setIsEditingDescription(true)}
                    >
                      <p className="text-xs text-gray-500 pr-6">
                        {data.description || 'Get text inputs from the Playground.'}
                      </p>
                      <button 
                        onClick={(e) => {
                          e.stopPropagation();
                          setIsEditingDescription(true);
                        }}
                        className="p-0.5 opacity-0 group-hover:opacity-100 transition-opacity flex-shrink-0"
                      >
                        <svg className="w-3 h-3 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z" />
                        </svg>
                      </button>
                    </div>
                  )}
                </div>
              </div>
            </div>
            <div className="flex items-center space-x-1 ml-2">
              {/* Configure Button */}
              <button 
                onClick={handleConfigClick}
                className="p-1 hover:bg-gray-100 rounded"
                title="Configure"
              >
                <svg className="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                </svg>
              </button>
              {/* Play Button */}
              <button className="p-1 hover:bg-gray-100 rounded">
                <svg className="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z" />
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </button>
            </div>
          </div>
        </div>

        {/* Content */}
        <div className="p-4">
          <div className="mb-3">
            <div className="flex items-center space-x-1 mb-2">
              <label className="text-sm font-medium text-gray-700">Text</label>
              <svg className="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <div className="relative">
              <input
                type="text"
                placeholder="Type something..."
                className="w-full px-3 py-2 pr-10 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                value={data.config?.defaultValue || ''}
                disabled
                style={{ textAlign: 'left', direction: 'ltr' }}
              />
              <button 
                onClick={(e) => {
                  e.stopPropagation();
                  setEditValue(data.config?.defaultValue || '');
                  setShowEditModal(true);
                }}
                className="absolute right-2 top-1/2 transform -translate-y-1/2 p-1 hover:bg-gray-100 rounded"
              >
                <svg className="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 8V4m0 0h4M4 4l5 5m11-5h-4m4 0v4m0-4l-5 5M4 16v4m0 0h4m-4 0l5-5m11 5l-5-5m5 5h-4m4 0v-4" />
                </svg>
              </button>
            </div>
          </div>
        </div>

        {/* Floating Expand/Collapse Button */}
        {isOutputHidden && (
          <div className="absolute -bottom-3 left-1/2 transform -translate-x-1/2">
            <button
              onClick={toggleOutputExpansion}
              className="group flex h-7 w-7 items-center justify-center rounded-full border bg-gray-100 hover:text-gray-900 hover:bg-gray-200 transition-colors relative"
              type="button"
              title={isOutputExpanded ? "Collapse outputs" : "Expand hidden outputs (1)"}
            >
              {/* Tooltip */}
              <span className="absolute bottom-full mb-2 px-2 py-1 text-xs text-white bg-gray-900 rounded opacity-0 group-hover:opacity-100 transition-opacity whitespace-nowrap pointer-events-none">
                {isOutputExpanded ? "Collapse outputs" : "Expand hidden outputs (1)"}
              </span>
              <svg 
                xmlns="http://www.w3.org/2000/svg" 
                width="24" 
                height="24" 
                viewBox="0 0 24 24" 
                fill="none" 
                stroke="currentColor" 
                strokeWidth="1.5" 
                strokeLinecap="round" 
                strokeLinejoin="round" 
                className={`w-4 h-4 text-gray-600 group-hover:text-gray-900 transform transition-transform ${isOutputExpanded ? 'rotate-180' : ''}`}
              >
                <path d="m7 20 5-5 5 5"></path>
                <path d="m7 4 5 5 5-5"></path>
              </svg>
            </button>
          </div>
        )}

        {/* Footer - Collapsible */}
        {isOutputExpanded && (
          <div className="px-4 py-2 bg-gray-50 border-t border-gray-200 rounded-b-lg">
            <div className="flex items-center justify-between">
              <button
                onClick={toggleOutputVisibility}
                className="p-1 hover:bg-gray-200 rounded transition-colors group relative"
                title={isOutputHidden ? "Show output" : "Hide output"}
              >
                {/* Tooltip */}
                <span className="absolute left-0 bottom-full mb-1 px-2 py-1 text-xs text-white bg-gray-800 rounded opacity-0 group-hover:opacity-100 transition-opacity whitespace-nowrap pointer-events-none">
                  {isOutputHidden ? "Show output" : "Hide output"}
                </span>
                {/* Eye icon - changes based on isOutputHidden state */}
                {isOutputHidden ? (
                  // Hidden eye icon
                  <svg className="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l3.59 3.59m0 0A9.953 9.953 0 0112 5c4.478 0 8.268 2.943 9.543 7a10.025 10.025 0 01-4.132 5.411m0 0L21 21" />
                  </svg>
                ) : (
                  // Normal eye icon
                  <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" className="w-4 h-4 text-gray-400" aria-hidden="true" style={{strokeWidth: '1.5'}}>
                    <path d="M2.062 12.348a1 1 0 0 1 0-.696 10.75 10.75 0 0 1 19.876 0 1 1 0 0 1 0 .696 10.75 10.75 0 0 1-19.876 0"></path>
                    <circle cx="12" cy="12" r="3"></circle>
                  </svg>
                )}
              </button>
              <div className="flex items-center space-x-2">
                <span className="text-sm text-gray-600">Message</span>
                <svg className="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6V4m0 2a2 2 0 100 4m0-4a2 2 0 110 4m-6 8a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4m6 6v10m6-2a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4" />
                </svg>
              </div>
            </div>
          </div>
        )}

        <Handle
          type="source"
          position={Position.Right}
          className="w-3 h-3 bg-blue-500"
          style={{ right: -6 }}
        />
      </div>

      {/* Render modal via portal */}
      <EditModal />
    </>
  );
});

TextInputNode.displayName = 'TextInputNode';