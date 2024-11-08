import React, { useState, useEffect } from 'react';
import { Terminal, ChevronRight, ChevronDown, Info, CheckCircle, XCircle, Search } from 'lucide-react';

const Badge = ({ children, variant }) => {
  const variants = {
    success: 'bg-green-100 text-green-800 border-green-200',
    error: 'bg-red-100 text-red-800 border-red-200',
    info: 'bg-blue-100 text-blue-800 border-blue-200',
    neutral: 'bg-gray-100 text-gray-800 border-gray-200'
  };

  return (
    <span className={`px-2 py-1 rounded-md text-sm font-medium border ${variants[variant]}`}>
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

const DPLLVisualization = ({ dpllSteps }) => {
  const [expandedNodes, setExpandedNodes] = useState(new Set());
  const [activeNodeId, setActiveNodeId] = useState(null);
  const [showExplanations, setShowExplanations] = useState(true);
  const [hoveredNode, setHoveredNode] = useState(null);
  
  console.log('Received dpllSteps in DPLLVisualization:', dpllSteps); // Log to check received prop

  if (!dpllSteps || dpllSteps.length === 0) {
    console.warn('dpllSteps is empty or not valid'); // Warn if array is empty or invalid
    return <p>No data available for visualization.</p>;
  }


  if (!dpllSteps) return null;

  const getExplanationForStep = (step) => {
    if (!step.action) return {
      title: "Initial State",
      description: "Starting the DPLL algorithm with the initial set of clauses."
    };
    
    const explanations = {
      'unit_propagation': {
        title: "Unit Propagation Rule",
        description: "When a clause contains only one unassigned literal, that literal must be true to satisfy the clause. This is a forced assignment that simplifies our formula."
      },
      'pure_literal': {
        title: "Pure Literal Elimination",
        description: "A literal is pure if it appears with only one polarity in all remaining clauses. Since making it true can only help satisfy clauses, we can safely assign it true."
      },
      'split': {
        title: "Decision (Split)",
        description: "No more deterministic rules apply. We must choose an unassigned variable and try both true and false values, creating two branches in our search."
      },
      'backtrack': {
        title: "Backtracking",
        description: "Current assignment led to a contradiction. We must undo our last free choice and try the opposite value."
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

  return (
    <div className="mt-8 space-y-4">
      {/* Header section */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <Terminal className="w-6 h-6 text-gray-700" />
          <h2 className="text-2xl font-semibold text-gray-800">DPLL Decision Tree</h2>
        </div>
        <button
          onClick={() => setShowExplanations(!showExplanations)}
          className={`
            px-4 py-2 rounded-lg transition-colors
            ${showExplanations ? 
              'bg-blue-600 text-white hover:bg-blue-700' : 
              'bg-blue-100 text-blue-800 hover:bg-blue-200'
            }
          `}
        >
          {showExplanations ? 'Hide' : 'Show'} Explanations
        </button>
      </div>


      <div>
        <h2>Visualization of DPLL Steps</h2>
        <ul>
            {dpllSteps.steps.map((step, index) => {
            console.log(`Rendering step ${step.id}:`, step);
            return (
                <li key={index}>
                <p><strong>Step {step.id}</strong></p>
                <p>Assignment: {JSON.stringify(step.assignment)}</p>
                <p>Result: {step.result}</p>
                <p>Action: {step.action}</p>
                {step.children.length > 0 && (
                    <div>
                    <p>Children:</p>
                    <ul>
                        {step.children.map((child, childIndex) => (
                        <li key={childIndex}>{JSON.stringify(child)}</li>
                        ))}
                    </ul>
                    </div>
                )}
                </li>
            );
            })}
        </ul>
        </div>

      

      {/* Instructions */}
      <CustomAlert variant="purple" icon={Info}>
        <div className="font-semibold mb-1">Understanding the Decision Tree</div>
        <div className="space-y-2">
          <p>This tree visualizes the DPLL algorithm's search process:</p>
          <ul className="list-disc pl-4 space-y-1">
            <li><span className="text-green-700 font-medium">Green nodes</span> indicate satisfying assignments</li>
            <li><span className="text-red-700 font-medium">Red nodes</span> show contradictions requiring backtracking</li>
            <li><span className="text-blue-700 font-medium">Blue nodes</span> represent paths still being explored</li>
          </ul>
          <p className="text-sm text-gray-600">Click any node to expand/collapse its children and see the detailed reasoning at each step.</p>
        </div>
      </CustomAlert>

      {/* Tree visualization */}
      <div className="bg-white rounded-lg shadow-lg overflow-hidden p-4">
        <div className="overflow-y-auto max-h-[32rem]">
          {buildTreeNodes(dpllSteps.steps)}
        </div>
      </div>

      {/* Result summary */}
      <div className="p-4 bg-gradient-to-r from-blue-900 to-sky-400 text-white mt-4 rounded-lg">
        <h3 className="text-xl font-bold mb-2">Final Result</h3>
        <p className="text-lg">
          Query is {dpllSteps.satisfiable ? 'entailed' : 'not entailed'} by KB
        </p>
      </div>
    </div>
  );
};

export default DPLLVisualization;