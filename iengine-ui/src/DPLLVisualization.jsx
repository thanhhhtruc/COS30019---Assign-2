import React, { useState } from 'react';
import { Terminal, ChevronRight, ChevronDown, Info, CheckCircle, XCircle, Search } from 'lucide-react';

const Badge = ({ children, variant }) => {
  const variants = {
    success: 'bg-green-100 text-green-800 border-green-200',
    error: 'bg-red-100 text-red-800 border-red-200',
    info: 'bg-blue-100 text-blue-800 border-blue-200',
    neutral: 'bg-gray-100 text-gray-800 border-gray-200'
  };

  return (
    <span className={`px-2 py-1 rounded-md text-sm font-medium border ${variants[variant] || variants.neutral}`}>
      {children}
    </span>
  );
};

const CustomAlert = ({ children, variant = 'default', icon: Icon }) => {
  const variants = {
    default: 'bg-gray-50 border-gray-200 text-gray-800',
    info: 'bg-blue-50 border-blue-200 text-blue-800',
    success: 'bg-green-50 border-green-200 text-green-800',
    error: 'bg-red-50 border-red-200 text-red-800',
    purple: 'bg-purple-50 border-purple-200 text-purple-800'
  };

  return (
    <div className={`p-4 rounded-lg border ${variants[variant]} flex gap-3`}>
      {Icon && <Icon className="h-5 w-5 mt-0.5 flex-shrink-0" />}
      <div>{children}</div>
    </div>
  );
};

const DPLLVisualization = ({ dpllSteps = [] }) => {
  const [expandedNodes, setExpandedNodes] = useState(new Set());
  const [activeNodeId, setActiveNodeId] = useState(null);
  const [showExplanations, setShowExplanations] = useState(true);
  const [hoveredNode, setHoveredNode] = useState(null);

  const getExplanationForStep = (step) => {
    if (!step || !step.action) return {
      title: "Initial State",
      description: "Starting the DPLL algorithm with the initial set of clauses."
    };

    const explanations = {
      'unit_propagation': {
        title: "Unit Propagation",
        description: "A clause with only one unassigned literal forces that literal to be true to satisfy the clause."
      },
      'pure_literal': {
        title: "Pure Literal Elimination",
        description: "A literal that appears with only one polarity can be safely assigned true."
      },
      'split': {
        title: "Decision (Split)",
        description: "Choosing an unassigned variable to branch on."
      },
      'backtrack': {
        title: "Backtracking",
        description: "Contradiction found, undoing last decision and trying opposite value."
      }
    };

    return explanations[step.action] || {
      title: `Step: ${step.action}`,
      description: "Processing DPLL algorithm step"
    };
  };

  const toggleNode = (nodeId) => {
    const newExpanded = new Set(expandedNodes);
    if (newExpanded.has(nodeId)) {
      newExpanded.delete(nodeId);
    } else {
      newExpanded.add(nodeId);
    }
    setExpandedNodes(newExpanded);
    setActiveNodeId(nodeId);
  };

  const getStatusIcon = (result) => {
    if (result === true) return CheckCircle;
    if (result === false) return XCircle;
    return Search;
  };

  const buildTreeNodes = (steps, depth = 0) => {
      return steps.map((step, index) => {
          const nodeId = `${depth}-${index}`;
          const hasChildren = step.children && step.children.length > 0;
          const isExpanded = expandedNodes.has(nodeId);
          const isActive = activeNodeId === nodeId;
          const isHovered = hoveredNode === nodeId;
          const StatusIcon = getStatusIcon(step.result);

          const explanation = getExplanationForStep(step);

          return (
              <div key={nodeId} className="transition-all duration-300">
                  <div 
                      className={`
                          flex items-start gap-2 p-4 rounded-lg mb-2 transition-all duration-300
                          ${isActive ? 'bg-blue-50 shadow-lg' : 'bg-white'}
                          ${isHovered ? 'shadow-md' : ''}
                          hover:bg-blue-50 cursor-pointer border
                          ${step.result === true ? 'border-green-200' : 
                            step.result === false ? 'border-red-200' : 
                            'border-blue-200'}
                      `}
                      onClick={() => toggleNode(nodeId)}
                      onMouseEnter={() => setHoveredNode(nodeId)}
                      onMouseLeave={() => setHoveredNode(null)}
                  >
                      {/* Expansion control */}
                      <div className="mt-1">
                          {hasChildren && (
                              isExpanded ? 
                              <ChevronDown className="w-5 h-5 text-blue-600" /> :
                              <ChevronRight className="w-5 h-5 text-blue-600" />
                          )}
                      </div>

                      {/* Node content */}
                      <div className="flex-grow space-y-3">
                          {/* Header with status and assignment */}
                          <div className="flex items-center justify-between">
                              <div className="flex items-center gap-3">
                                  <StatusIcon className={`w-5 h-5 ${
                                      step.result === true ? 'text-green-600' :
                                      step.result === false ? 'text-red-600' :
                                      'text-blue-600'
                                  }`} />
                                  <Badge variant={
                                      step.result === true ? 'success' :
                                      step.result === false ? 'error' :
                                      'info'
                                  }>
                                      {step.result === true ? 'Satisfiable' :
                                      step.result === false ? 'Unsatisfiable' :
                                      'Exploring'}
                                  </Badge>
                              </div>
                              
                              {step.action && (
                                  <Badge variant="neutral">
                                      {step.action.replace('_', ' ').toUpperCase()}
                                  </Badge>
                              )}
                          </div>

                          {/* Assignment details */}
                          {step.assignment && (
                              <div className="font-mono text-sm bg-gray-50 p-2 rounded-md">
                                  {Object.entries(step.assignment).map(([var_, val], idx) => (
                                      <span key={var_} className={`
                                          ${val ? 'text-green-700' : 'text-red-700'}
                                          ${idx !== 0 ? 'ml-2' : ''}
                                      `}>
                                          {var_} = {val.toString()}
                                      </span>
                                  ))}
                              </div>
                          )}

                          {/* Explanation section */}
                          {showExplanations && (
                              <CustomAlert 
                                  variant={
                                      step.result === true ? 'success' :
                                      step.result === false ? 'error' :
                                      'info'
                                  }
                                  icon={Info}
                              >
                                  <div className="font-semibold mb-1">{explanation.title}</div>
                                  <div className="text-sm">{explanation.description}</div>
                              </CustomAlert>
                          )}
                      </div>
                  </div>

                  {/* Children nodes with improved connection lines */}
                  {hasChildren && isExpanded && (
                      <div className="pl-8 border-l-2 border-blue-200 ml-4 transition-all duration-300">
                          {buildTreeNodes(step.children, depth + 1)}
                      </div>
                  )}
              </div>
          );
      });
  };

  const renderStep = (step, depth = 0, index = 0) => {
    if (!step) return null;

    const nodeId = `${depth}-${index}`;
    const hasChildren = Array.isArray(step.children) && step.children.length > 0;
    const isExpanded = expandedNodes.has(nodeId);
    const isActive = activeNodeId === nodeId;
    const isHovered = hoveredNode === nodeId;
    const StatusIcon = getStatusIcon(step.result);
    const explanation = getExplanationForStep(step);

    return (
      <div key={nodeId} className="transition-all duration-300">
        <div
          className={`
            flex items-start gap-2 p-4 rounded-lg mb-2 transition-all duration-300
            ${isActive ? 'bg-blue-50 shadow-lg' : 'bg-white'}
            ${isHovered ? 'bg-gray-100' : ''}
          `}
          onMouseEnter={() => setHoveredNode(nodeId)}
          onMouseLeave={() => setHoveredNode(null)}
        >
          <div className="flex-shrink-0">
            <StatusIcon className="h-5 w-5" />
          </div>
          <div className="flex-grow">
            <div className="flex items-center gap-2">
              <Badge variant="info">{explanation.title}</Badge>
              <div className="text-sm text-gray-600">{explanation.description}</div>
            </div>
            {showExplanations && step.assignment && (
              <div className="text-sm mt-2">{step.assignment}</div>
            )}
          </div>
          {hasChildren && (
            <button onClick={() => toggleNode(nodeId)} className="focus:outline-none">
              {isExpanded ? <ChevronDown className="h-5 w-5" /> : <ChevronRight className="h-5 w-5" />}
            </button>
          )}
        </div>
        {hasChildren && isExpanded && (
          <div className="pl-6">
            {step.children.map((child, childIndex) => 
              renderStep(child, depth + 1, childIndex)
            )}
          </div>
        )}
      </div>
    );
  };

  if (!Array.isArray(dpllSteps)) {
    return (
      <CustomAlert variant="error" icon={Info}>
        Invalid data format. Expected an array of DPLL steps.
      </CustomAlert>
    );
  }

  if (dpllSteps.length === 0) {
    return (
      <CustomAlert variant="info" icon={Info}>
        No DPLL steps available for visualization.
      </CustomAlert>
    );
  }

  return (
    <div className="mt-8">
      <div className="flex items-center gap-2 mb-4">
        <Terminal className="w-6 h-6 text-gray-700" />
        <h2 className="text-2xl font-semibold text-gray-800">DPLL Decision Tree</h2>
      </div>
      <div className="bg-white rounded-lg shadow-lg overflow-hidden p-4">
        <div className="overflow-y-auto max-h-96">
          {dpllSteps.map((step, index) => renderStep(step, 0, index))}
        </div>
        <div className="p-4 bg-gradient-to-r from-blue-900 to-sky-400 text-white mt-4 rounded-lg">
          <h3 className="text-xl font-bold mb-2">Final Result</h3>
          <p className="text-lg">
            Query is {dpllSteps[0]?.result ? 'entailed' : 'not entailed'} by KB
          </p>
        </div>
      </div>
    </div>
  );
};

export default DPLLVisualization;