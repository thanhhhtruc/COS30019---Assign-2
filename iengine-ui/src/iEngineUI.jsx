import React, { useState, useEffect } from 'react';
import { ArrowRight, Play, Pause, SkipBack, SkipForward, Upload, Terminal, AlertCircle, Loader, Table, RotateCcw, ZoomIn, ZoomOut } from 'lucide-react';
import ChainViz from './ChainViz';
import DPLLViz from './DPLLViz';


// const DPLLViz = ({ result, knowledgeBase }) => {
//   console.log('DPLLViz props:', { result, knowledgeBase });
//   const [currentStep, setCurrentStep] = useState(0);
//   const [isPlaying, setIsPlaying] = useState(false);
//   const [speed, setSpeed] = useState(1000);
//   const [zoomLevel, setZoomLevel] = useState(1);

//   const parseDPLLData = (resultString) => {
//     if (!resultString) return [];

//     const steps = resultString.split('\n').filter(step => step.trim());

//     return steps.map((step, index) => ({
//       step: index + 1,
//       detail: step.trim()
//     }));
//   };

//   const steps = parseDPLLData(result);
//   console.log('Parsed DPLL steps:', steps);

//   useEffect(() => {
//     let timer;
//     if (isPlaying && currentStep < steps.length - 1) {
//       timer = setTimeout(() => {
//         setCurrentStep(prev => prev + 1);
//       }, speed);
//     } else if (currentStep >= steps.length - 1) {
//       setIsPlaying(false);
//     }
//     return () => clearTimeout(timer);
//   }, [currentStep, isPlaying, steps.length, speed]);

//   const handlePlayPause = () => setIsPlaying(!isPlaying);
//   const handleReset = () => {
//     setCurrentStep(0);
//     setIsPlaying(false);
//   };
//   const handleStepForward = () => {
//     if (currentStep < steps.length - 1) setCurrentStep(currentStep + 1);
//   };
//   const handleStepBack = () => {
//     if (currentStep > 0) setCurrentStep(currentStep - 1);
//   };

//   const handleZoomIn = () => setZoomLevel(prev => Math.min(prev + 0.1, 2));
//   const handleZoomOut = () => setZoomLevel(prev => Math.max(prev - 0.1, 0.5));

//   if (!steps.length) {
//     console.log('No steps to display');
//     return null;
//   }

//   const renderTreeNodes = (steps) => {
//     const nodeWidth = 200;
//     const nodeHeight = 80;
//     const horizontalSpacing = 400;
//     const verticalSpacing = 150;
//     const totalLevels = Math.ceil(Math.log2(steps.length + 1));
//     const svgWidth = (2 ** (totalLevels - 1)) * horizontalSpacing;  // Calculate width based on the number of levels
//     const svgHeight = totalLevels * verticalSpacing + nodeHeight;

//     const nodes = steps.map((step, index) => {
//       const level = Math.floor(Math.log2(index + 1));
//       const position = index - (2 ** level - 1);
//       const x = (svgWidth / (2 ** (level + 1))) + position * (svgWidth / (2 ** level));
//       const y = level * verticalSpacing + nodeHeight / 2;
//       return { step, x, y };
//     });

//     return (
//       <svg width={svgWidth} height={svgHeight} className="overflow-visible" style={{ transform: `scale(${zoomLevel})` }}>
//         <defs>
//           <marker id="arrowhead" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto">
//             <polygon points="0 0, 10 3.5, 0 7" fill="#3B82F6" />
//           </marker>
//         </defs>
//         {nodes.map((node, index) => {
//           if (index > 0) {
//             const parentIndex = Math.floor((index - 1) / 2);
//             const parent = nodes[parentIndex];

//             return (
//               <line
//                 key={`line-${index}`}
//                 x1={parent.x}
//                 y1={parent.y}
//                 x2={node.x}
//                 y2={node.y}
//                 stroke="#ccc"
//                 strokeWidth={2}
//                 markerEnd="url(#arrowhead)"
//               />
//             );
//           }
//           return null;
//         })}
//         {nodes.map((node, index) => (
//           <g key={`node-${index}`} className="transition-all duration-500">
//             <rect
//               x={node.x - nodeWidth / 2}
//               y={node.y - nodeHeight / 2}
//               width={nodeWidth}
//               height={nodeHeight}
//               rx={15}
//               ry={15}
//               fill="#FFFFFF"
//               stroke={index <= currentStep ? '#10B981' : '#3B82F6'}
//               strokeWidth={index === currentStep ? 3 : 2}
//               className="transition-all duration-300"
//             />
//             <foreignObject
//               x={node.x - nodeWidth / 2}
//               y={node.y - nodeHeight / 2}
//               width={nodeWidth}
//               height={nodeHeight}
//             >
//               <div className="flex items-center justify-center h-full p-2">
//                 <p className="text-sm font-mono text-gray-700 text-center break-words">{node.step.detail}</p>
//               </div>
//             </foreignObject>
//           </g>
//         ))}
//       </svg>
//     );
//   };

//   return (
//     <div className="mt-8 bg-white rounded-lg p-6 shadow-lg">
//       <div className="mb-6">
//         <h2 className="text-2xl font-semibold text-gray-800 mb-2">DPLL Visualization</h2>
//         <p className="text-gray-800">Visualizing the DPLL algorithm steps.</p>
//       </div>

//       {/* Current Step Details */}
//       <div className="bg-gray-50 rounded-lg p-6 mb-4">
//         <h3 className="font-semibold text-gray-800 mb-4 text-lg">Step {currentStep + 1} Details</h3>
//         <p className="text-gray-800">{steps[currentStep].detail}</p>
//       </div>

//       {/* Visualization Area */}
//       <div className="relative bg-white rounded-lg mb-6 p-4 overflow-auto" style={{ width: '100%', height: '600px' }}>
//         {renderTreeNodes(steps)}
//       </div>

//       {/* Controls */}
//       <div className="flex items-center justify-between bg-gray-50 rounded-lg p-4">
//         <div className="flex items-center gap-4">
//           <button onClick={handleStepBack} disabled={currentStep === 0} className="p-2 rounded-lg bg-white shadow hover:bg-gray-200 transition duration-200 disabled:opacity-50 disabled:cursor-not-allowed border-none text-gray-800">
//             <SkipBack />
//           </button>
//           <button onClick={handlePlayPause} className="p-2 rounded-lg bg-white shadow hover:bg-gray-200 transition duration-200 border-none text-gray-800">
//             {isPlaying ? <Pause /> : <Play />}
//           </button>
//           <button onClick={handleStepForward} disabled={currentStep === steps.length - 1} className="p-2 rounded-lg bg-white shadow hover:bg-gray-200 transition duration-200 disabled:opacity-50 disabled:cursor-not-allowed border-none text-gray-800">
//             <SkipForward />
//           </button>
//           <button onClick={handleReset} className="p-2 rounded-lg bg-white shadow hover:bg-gray-200 transition duration-200 border-none text-gray-800">
//             <RotateCcw />
//           </button>
//           <button onClick={handleZoomIn} className="p-2 rounded-lg bg-white shadow hover:bg-gray-200 transition duration-200 border-none text-gray-800">
//             <ZoomIn />
//           </button>
//           <button onClick={handleZoomOut} className="p-2 rounded-lg bg-white shadow hover:bg-gray-200 transition duration-200 border-none text-gray-800">
//             <ZoomOut />
//           </button>
//         </div>
//         <div className="flex items-center gap-2">
//           <span className="text-sm text-gray-800">Speed:</span>
//           <input type="range" min="200" max="2000" step="200" value={2000 - speed + 200} onChange={(e) => setSpeed(2000 - Number(e.target.value) + 200)} className="w-32" />
//         </div>
//         <div className="text-sm text-gray-800">Step {currentStep + 1} of {steps.length}</div>
//       </div>
//     </div>
//   );
// };












const iEngineUI = () => {
  const [file, setFile] = useState(null);
  const [method, setMethod] = useState('');
  const [result, setResult] = useState('');
  const [chainResult, setChainResult] = useState('');
  const [truthTable, setTruthTable] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [fileContent, setFileContent] = useState('');
  const [dpllData, setDpllData] = useState(null);

  const handleFileChange = (event) => {
    const selectedFile = event.target.files[0];
    setFile(selectedFile);
    setError('');
    setTruthTable(null);

    const reader = new FileReader();
    reader.onload = (e) => {
      setFileContent(e.target.result);
    };
    reader.readAsText(selectedFile);
  };

  const handleMethodSelect = async (selectedMethod) => {
    console.log('Selected method:', selectedMethod);
    setMethod(selectedMethod);
    setError('');
    setTruthTable(null);

    if (!file) {
      setError('Please select a file first');
      return;
    }

    setIsLoading(true);

    try {
      const formData = new FormData();
      formData.append('file', file);
      formData.append('method', selectedMethod);

      const response = await fetch('/api/process', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        throw new Error('Failed to process file');
      }

      const data = await response.json();
      setResult(data.result);

      // Format the chain result for visualization
      if (selectedMethod === 'DPLL') {
        console.log('Processing DPLL result'); // Debug log
        // Ensure we have properly formatted DPLL data
        const dpllSteps = data.steps || [];
        setDpllData(dpllSteps);
        setChainResult(dpllSteps.join('\n'));
        console.log("Rendering DPLLViz with result:", dpllSteps);

        console.log('DPLL Steps:', dpllSteps); // Debug log
      } else if ((selectedMethod === 'FC' || selectedMethod === 'BC') && data.result.includes('YES:')) {
        const facts = data.result.split('YES:')[1].trim();
        setChainResult(`YES:\n${facts}`);  // Format for ChainViz
      } else {
        setChainResult('');
      }

      if (data.truthTable) {
        setTruthTable(data.truthTable);
      }
    } catch (err) {
      setError('Error processing file: ' + err.message);
    } finally {
      setIsLoading(false);
    }
  };

  const renderTruthTable = () => {
    if (!truthTable) return null;

    // Extract symbols from truth table data
    const symbols = truthTable.symbols || [];

    return (
      <div className="mt-8">
        <div className="flex items-center gap-2 mb-4">
          <Table className="w-6 h-6 text-gray-700" />
          <h2 className="text-2xl font-semibold text-gray-800">Truth Table</h2>
        </div>
        <div className="relative overflow-x-auto rounded-lg">
          <div className="max-h-96 overflow-y-auto rounded-lg">
            <table className="w-full border-collapse rounded-lg">
              <thead className="bg-blue-900 text-white sticky top-0 z-10 rounded-t-lg">
                <tr>
                  <th className="p-4 border-b border-blue-700 whitespace-nowrap">Model ID</th>
                  {/* Model columns */}
                  {symbols.map(symbol => (
                    <th
                      key={symbol}
                      className="p-4 border-b border-blue-700 whitespace-nowrap"
                    >
                      {symbol}
                    </th>
                  ))}
                  {/* KB clause columns */}
                  {truthTable.clauses.map((clause, i) => (
                    <th
                      key={`clause-${i}`}
                      className="p-4 border-b border-blue-700 whitespace-nowrap"
                    >
                      {clause}
                    </th>
                  ))}
                  {/* Query column */}
                  <th className="p-4 border-b border-blue-700 whitespace-nowrap bg-purple-700">
                    {truthTable.query}
                  </th>
                </tr>
              </thead>
              <tbody>
                {truthTable.rows.map((row, rowIndex) => (
                  <tr key={rowIndex} className={`hover:bg-blue-100 ${row.proves_query ? 'bg-green-50' : ''}`}>
                    <td className="p-4 border-b border-gray-200 text-center text-black">
                      {rowIndex + 1}
                    </td>
                    {/* Model values */}
                    {symbols.map(symbol => (
                      <td
                        key={symbol}
                        className="p-4 border-b border-gray-200 text-center text-black"
                      >
                        {row.model[symbol] ? 'T' : 'F'}
                      </td>
                    ))}
                    {/* KB results */}
                    {row.kb_results.map((result, i) => (
                      <td
                        key={`result-${i}`}
                        className="p-4 border-b border-gray-200 text-center text-black"
                      >
                        {result ? 'T' : 'F'}
                      </td>
                    ))}
                    {/* Query result */}
                    <td className="p-4 border-b border-gray-200 text-center text-black bg-purple-50">
                      {row.query_result ? 'T' : 'F'}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
        <div className="mt-4 p-4 bg-gradient-to-b from-sky-400 to-blue-900 text-white rounded-lg text-center">
          <h3 className="text-2xl font-extrabold mb-2">Summary</h3>
          <p className="text-lg font-semibold mb-1">Total Models: {truthTable.summary.total_models}</p>
          <p className="text-lg font-semibold mb-1">Models Proving Query: {truthTable.summary.proving_models}</p>
          <p className="text-lg font-semibold">
            Query is {truthTable.summary.is_entailed ? 'entailed' : 'not entailed'} by KB
          </p>
        </div>
      </div>
    );
  };




  return (
    <div className="min-h-screen flex flex-col">
      {/* Loading */}
      {isLoading && (
        <div className="loading-overlay">
          <div className="loading-spinner"></div>
        </div>
      )}
      {/* Header */}
      <header className="bg-white bg-opacity-30 backdrop-blur-md shadow-lg rounded-full w-8/12 mx-auto mt-4 z-20 fixed top-0 left-1/2 transform -translate-x-1/2">
        <div className="container mx-auto px-6 py-2 flex justify-between items-center">
          <h1 className="text-3xl font-bold text-gray-800">iEngine</h1>
          <div className="flex items-center gap-4">
            <span className="symbol animate-spin">¬</span>
            <span className="symbol animate-bounce">∧</span>
            <span className="symbol animate-pulse">∨</span>
            <span className="symbol animate-bounce">⇒</span>
            <span className="symbol animate-spin">⇔</span>
          </div>
        </div>
      </header>

      {/* Banner Section */}
      <div className="text-white text-center py-64" style={{ backgroundImage: 'url(/bg.webp)', backgroundSize: 'cover', backgroundPosition: 'center' }}>
        <h2 className="text-6xl font-extrabold">Inference Engine</h2>
        <p className="text-3xl font-semibold mt-2">for Propositional Logic</p>
      </div>

      {/* Main Content */}
      <div className="flex-grow bg-gray-100 py-12">
        <div className="max-w-7.5xl mx-auto px-4">
          <div className="bg-white p-8 rounded-lg shadow-lg">
            {/* File Upload Section */}
            <div className="mb-8">
              <h2 className="text-3xl font-semibold mb-4 text-gray-800">Upload Test File</h2>
              <div className="border-2 border-dashed border-blue-200 rounded-xl p-6 text-center hover:border-blue-400 transition-colors">
                <input
                  type="file"
                  onChange={handleFileChange}
                  className="hidden"
                  id="file-upload"
                  accept=".txt"
                />
                <label htmlFor="file-upload" className="cursor-pointer">
                  <Upload className="w-16 h-16 text-blue-500 mx-auto mb-4" />
                  <p className="text-gray-600 mb-2">
                    {file ? file.name : 'Drop your .txt file here or click to browse'}
                  </p>
                  <span className="text-lg text-blue-500 hover:text-blue-600">
                    Select File
                  </span>
                </label>
              </div>
            </div>

            {/* Method Selection */}
            <div className="mb-8">
              <h2 className="text-3xl font-semibold mb-4 text-gray-800">Select Algorithms</h2>
              <div className="grid grid-cols-2 gap-4 md:grid-cols-4">
                {[
                  { key: 'TT', name: 'Truth Table', description: 'Exhaustive search through all possible models.' },
                  { key: 'FC', name: 'Forward Chaining', description: 'Inference method using forward chaining.' },
                  { key: 'BC', name: 'Backward Chaining', description: 'Inference method using backward chaining.' },
                  { key: 'DPLL', name: 'DPLL', description: 'Davis-Putnam-Logemann-Loveland algorithm for SAT.' }
                ].map((m) => (
                  <button
                    key={m.key}
                    onClick={() => handleMethodSelect(m.key)}
                    className={`p-4 rounded-xl font-medium transition-all transform hover:scale-105 
                      ${method === m.key
                        ? 'bg-blue-600 text-white shadow-lg'
                        : 'bg-gray-50 text-gray-700 hover:bg-gray-100'
                      }`}
                  >
                    <div className="text-lg font-bold">{m.name}</div>
                    <div className="text-sm">{m.description}</div>
                  </button>
                ))}
              </div>
            </div>

            {/* Error Message */}
            {error && (
              <div className="mt-6 p-4 bg-red-50 text-red-700 rounded-xl flex items-center gap-2">
                <AlertCircle className="w-6 h-6" />
                {error}
              </div>
            )}

            {/* File Content Section */}
            {fileContent && (
              <div className="mt-8">
                <div className="flex items-center gap-2 mb-4">
                  <Terminal className="w-6 h-6 text-gray-700" />
                  <h2 className="text-2xl font-semibold text-gray-800">Input</h2>
                </div>
                <div className="bg-gray-900 p-4 rounded-lg shadow-inner">
                  <pre className="font-mono text-green-400 whitespace-pre-wrap">
                    {fileContent}
                  </pre>
                </div>
              </div>
            )}

            {/* Results Section */}
            {result && (
              <div className="mt-8">
                <div className="flex items-center gap-2 mb-4">
                  <Terminal className="w-6 h-6 text-gray-700" />
                  <h2 className="text-2xl font-semibold text-gray-800">Output</h2>
                </div>
                <div className="bg-gray-900 p-4 rounded-lg shadow-inner">
                  <pre className="font-mono text-green-400 whitespace-pre-wrap">
                    {`${file ? file.name : 'file.txt'} ${method}\n${result}`}
                  </pre>
                </div>
              </div>
            )}

            {/* Chain Visualization */}
            {chainResult && (method === 'FC' || method === 'BC') && (
              <ChainViz
                type={method}
                result={chainResult}
                knowledgeBase={fileContent} // Pass the KB content
              />
            )}

            {/* DPLL Visualization */}
            {chainResult && method === 'DPLL' && (
              <DPLLViz
                result={chainResult}
                knowledgeBase={fileContent}
              />
            )}

            {/* Truth Table Section */}
            {renderTruthTable()}
          </div>
        </div>
      </div>

      {/* Footer */}
      <footer className="bg-white bg-opacity-30 backdrop-blur-md shadow-lg rounded-lg py-8 mt-8">
        <div className="container mx-auto px-6 flex flex-col md:flex-row justify-between items-center">
          <div className="text-center md:text-left mb-4 md:mb-0">
            <h2 className="text-2xl font-bold text-gray-800">iEngine</h2>
            <p className="text-gray-600">Developed by Truong Thien and Thanh Truc</p>
          </div>
          <div className="flex space-x-4">
            <a href="#" className="text-gray-600 hover:text-gray-800 transition-colors">Privacy Policy</a>
            <a href="#" className="text-gray-600 hover:text-gray-800 transition-colors">Terms of Service</a>
            <a href="#" className="text-gray-600 hover:text-gray-800 transition-colors">Contact Us</a>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default iEngineUI;