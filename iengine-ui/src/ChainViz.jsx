import React, { useState, useEffect } from 'react';
import { Play, Pause, SkipBack, SkipForward, RotateCcw } from 'lucide-react';

const ChainViz = ({ type, result }) => {
  const [currentStep, setCurrentStep] = useState(0);
  const [speed, setSpeed] = useState(1000);
  const [isPlaying, setIsPlaying] = useState(false);

  // Enhanced parsing to handle both FC and BC results
  const parseChainData = (resultString) => {
    if (!resultString.includes('YES:')) {
      return [];
    }
  
    const facts = resultString.split('YES:')[1].trim().split(', ');
    const steps = [];
    
    if (type === 'FC') {
      // For Forward Chaining
      let knownFacts = new Set();
      facts.forEach((fact, index) => {
        const currentFact = fact.trim();
        const previousFacts = [...knownFacts];
        
        // Determine reasoning based on whether it's initial fact or derived
        const reasoning = index < 3 
          ? "Initial fact from knowledge base"
          : `Derived using: ${Array.from(previousFacts).join(' AND ')}`;
        
        steps.push({
          fact: currentFact,
          knownFacts: [...previousFacts],
          reasoning,
          type: index < 3 ? 'initial' : 'derived'
        });
        
        knownFacts.add(currentFact);
      });
    } else {
      // For Backward Chaining - work backwards from goal
      facts.reverse().forEach((fact, index) => {
        const currentFact = fact.trim();
        steps.push({
          fact: currentFact,
          subgoals: index < facts.length - 1 ? [facts[index + 1].trim()] : [],
          reasoning: index === 0 
            ? "Goal to prove" 
            : index === facts.length - 1 
              ? "Base fact from knowledge base"
              : `Supporting fact for: ${facts[index - 1].trim()}`,
          type: index === 0 ? 'goal' : index === facts.length - 1 ? 'base' : 'support'
        });
      });
    }
    
    return steps;
  };

  const steps = parseChainData(result);

  useEffect(() => {
    let timer;
    if (isPlaying && currentStep < steps.length - 1) {
      timer = setTimeout(() => {
        setCurrentStep(prev => prev + 1);
      }, speed);
    } else if (currentStep >= steps.length - 1) {
      setIsPlaying(false);
    }
    return () => clearTimeout(timer);
  }, [currentStep, isPlaying, steps.length, speed]);

  const handlePlayPause = () => setIsPlaying(!isPlaying);
  const handleReset = () => {
    setCurrentStep(0);
    setIsPlaying(false);
  };
  const handleStepForward = () => {
    if (currentStep < steps.length - 1) setCurrentStep(currentStep + 1);
  };
  const handleStepBack = () => {
    if (currentStep > 0) setCurrentStep(currentStep - 1);
  };

  if (!steps.length) return null;

  const renderNodes = () => {
    const nodeRadius = 40;
    const svgWidth = 800;
    const svgHeight = 400;
    const centerY = svgHeight / 2;
    const horizontalSpacing = (svgWidth - 100) / (steps.length > 1 ? steps.length - 1 : 1);

    return (
      <svg 
        width="100%" 
        height={svgHeight} 
        viewBox={`0 0 ${svgWidth} ${svgHeight}`}
        className="overflow-visible"
      >
        <defs>
          <marker
            id="arrowhead"
            markerWidth="10"
            markerHeight="7"
            refX="9"
            refY="3.5"
            orient="auto"
          >
            <polygon 
              points="0 0, 10 3.5, 0 7" 
              fill="#3B82F6"
            />
          </marker>
        </defs>

        {/* Connection lines with arrows */}
        {steps.map((step, index) => {
          if (index < steps.length - 1) {
            const x1 = 50 + index * horizontalSpacing + nodeRadius;
            const x2 = 50 + (index + 1) * horizontalSpacing - nodeRadius;
            const y = centerY;
            
            return (
              <line
                key={`line-${index}`}
                x1={x1}
                y1={y}
                x2={x2}
                y2={y}
                stroke={index <= currentStep - 1 ? '#3B82F6' : '#E5E7EB'}
                strokeWidth={3}
                markerEnd="url(#arrowhead)"
                className="transition-all duration-500"
              />
            );
          }
          return null;
        })}

        {/* Nodes with enhanced styling based on type */}
        {steps.map((step, index) => {
          const x = 50 + index * horizontalSpacing;
          const y = centerY;
          const isActive = index === currentStep;
          const isCompleted = index < currentStep;
          const isPending = index > currentStep;

          // Determine node color based on type and state
          let fillColor = 'url(#pendingGradient)';
          let strokeColor = '#D1D5DB';
          
          if (isActive) {
            fillColor = 'url(#activeGradient)';
            strokeColor = '#2563EB';
          } else if (isCompleted) {
            fillColor = 'url(#completedGradient)';
            strokeColor = '#16A34A';
          }

          return (
            <g
              key={`node-${index}`}
              className={`transition-all duration-500 ${
                index <= currentStep ? 'opacity-100' : 'opacity-50'
              }`}
            >
              {/* Node circle */}
              <circle
                cx={x}
                cy={y}
                r={nodeRadius}
                fill={fillColor}
                stroke={strokeColor}
                strokeWidth={2}
                className="transition-all duration-300"
              />

              {/* Step number */}
              <text
                x={x}
                y={y - 20}
                textAnchor="middle"
                className={`text-sm font-semibold ${
                  isActive ? 'fill-blue-600' :
                  isCompleted ? 'fill-green-600' :
                  'fill-gray-400'
                }`}
              >
                Step {index + 1}
              </text>

              {/* Fact text */}
              <text
                x={x}
                y={y + 5}
                textAnchor="middle"
                className={`text-sm font-mono ${
                  isActive ? 'fill-white' :
                  isCompleted ? 'fill-green-700' :
                  'fill-gray-500'
                }`}
              >
                {step.fact}
              </text>

              {/* Type indicator */}
              <text
                x={x}
                y={y + 25}
                textAnchor="middle"
                className="text-xs fill-gray-500"
              >
                {step.type}
              </text>
            </g>
          );
        })}
      </svg>
    );
  };

  return (
    <div className="mt-8 bg-white rounded-lg p-6 shadow-lg">
      <div className="mb-6">
        <h2 className="text-2xl font-semibold text-gray-800 mb-2">
          {type === 'FC' ? 'Forward' : 'Backward'} Chaining Visualization
        </h2>
        <p className="text-gray-600">
          {type === 'FC' 
            ? 'Starting from known facts, deriving new facts until the goal is reached'
            : 'Starting from the goal, working backwards to find supporting facts'}
        </p>
      </div>

      {/* Current Step Details */}
      <div className="bg-blue-50 rounded-lg p-4 mb-4">
        <h3 className="font-semibold text-blue-800 mb-2">Current Step Details</h3>
        {currentStep < steps.length && (
          <div className="space-y-2">
            <p className="text-sm text-blue-700">
              <span className="font-medium">Current Fact:</span> {steps[currentStep].fact}
            </p>
            <p className="text-sm text-blue-700">
              <span className="font-medium">Reasoning:</span> {steps[currentStep].reasoning}
            </p>
            {type === 'FC' && steps[currentStep].knownFacts.length > 0 && (
              <p className="text-sm text-blue-700">
                <span className="font-medium">Known Facts:</span> {steps[currentStep].knownFacts.join(', ')}
              </p>
            )}
            {type === 'BC' && steps[currentStep].subgoals.length > 0 && (
              <p className="text-sm text-blue-700">
                <span className="font-medium">Supporting:</span> {steps[currentStep].subgoals.join(', ')}
              </p>
            )}
          </div>
        )}
      </div>

      {/* Visualization Area */}
      <div className="relative bg-white rounded-lg mb-6">
        {renderNodes()}
      </div>

      {/* Controls */}
      <div className="flex items-center justify-between bg-gray-50 rounded-lg p-4">
        <div className="flex items-center gap-4">
          <button
            onClick={handleStepBack}
            disabled={currentStep === 0}
            className="p-2 rounded-lg bg-white shadow hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <SkipBack className="w-5 h-5" />
          </button>
          <button
            onClick={handlePlayPause}
            className="p-2 rounded-lg bg-white shadow hover:bg-gray-50"
          >
            {isPlaying ? <Pause className="w-5 h-5" /> : <Play className="w-5 h-5" />}
          </button>
          <button
            onClick={handleStepForward}
            disabled={currentStep === steps.length - 1}
            className="p-2 rounded-lg bg-white shadow hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <SkipForward className="w-5 h-5" />
          </button>
          <button
            onClick={handleReset}
            className="p-2 rounded-lg bg-white shadow hover:bg-gray-50"
          >
            <RotateCcw className="w-5 h-5" />
          </button>
        </div>
        
        <div className="flex items-center gap-2">
          <span className="text-sm text-gray-600">Speed:</span>
          <input
            type="range"
            min="200"
            max="2000"
            step="200"
            value={speed}
            onChange={(e) => setSpeed(Number(e.target.value))}
            className="w-32"
          />
        </div>

        <div className="text-sm text-gray-600">
          Step {currentStep + 1} of {steps.length}
        </div>
      </div>
    </div>
  );
};

export default ChainViz;