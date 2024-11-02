import React, { useState } from 'react';
import { ArrowRight, Upload, Terminal, AlertCircle, Loader } from 'lucide-react';

const iEngineUI = () => {
  const [file, setFile] = useState(null);
  const [method, setMethod] = useState('');
  const [result, setResult] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [fileContent, setFileContent] = useState('');

  const handleFileChange = (event) => {
    const selectedFile = event.target.files[0];
    setFile(selectedFile);
    setError('');

    const reader = new FileReader();
    reader.onload = (e) => {
      setFileContent(e.target.result);
    };
    reader.readAsText(selectedFile);
  };

  const handleMethodSelect = (selectedMethod) => {
    setMethod(selectedMethod);
    setError('');
  };

  const processFile = async () => {
    if (!file || !method) {
      setError('Please select both a file and a method');
      return;
    }

    setIsLoading(true);
    setError('');

    try {
      const formData = new FormData();
      formData.append('file', file);
      formData.append('method', method);

      const response = await fetch('/api/process', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        throw new Error('Failed to process file');
      }

      const data = await response.text();
      setResult(data);
    } catch (err) {
      setError('Error processing file: ' + err.message);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex flex-col">
      {/* Header */}
      <header className="bg-white shadow">
        <div className="container mx-auto px-6 py-4">
          <h1 className="text-3xl font-bold text-gray-800">iEngine</h1>
        </div>
      </header>

      {/* Banner Section */}
      <div className="bg-gradient-to-b from-sky-400 to-blue-900 text-white text-center py-16">
        <h2 className="text-6xl font-extrabold">Inference Engine</h2>
        <p className="text-3xl font-semibold mt-2">for Propositional Logic</p>
      </div>

      {/* Main Content */}
      <div className="flex-grow flex items-center justify-center bg-gray-100 py-12">
        <div className="max-w-4xl w-full mx-4 bg-white p-8 rounded-lg shadow-lg">
          {/* File Upload Section */}
          <div className="mb-8">
            <h2 className="text-3xl font-semibold mb-4 text-gray-800">Upload Your File</h2>
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
            <h2 className="text-3xl font-semibold mb-4 text-gray-800">Select Method</h2>
            <div className="grid grid-cols-2 gap-4 md:grid-cols-3">
              {['TT', 'FC', 'BC'].map((m) => (
                <button
                  key={m}
                  onClick={() => handleMethodSelect(m)}
                  className={`p-4 rounded-xl font-medium transition-all transform hover:scale-105 
                    ${method === m
                      ? 'bg-blue-600 text-white shadow-lg'
                      : 'bg-gray-50 text-gray-700 hover:bg-gray-100'
                    }`}
                >
                  {m}
                </button>
              ))}
            </div>
          </div>

          {/* Process Button */}
          <button
            onClick={processFile}
            disabled={isLoading}
            className="w-full py-4 bg-gradient-to-r from-blue-600 to-indigo-600 text-white rounded-xl 
              font-medium transition-all transform hover:translate-y-[-2px] hover:shadow-lg
              disabled:from-gray-400 disabled:to-gray-500 disabled:cursor-not-allowed flex items-center justify-center gap-2"
          >
            {isLoading ? (
              <>
                <Loader className="w-6 h-6 animate-spin" />
                Processing...
              </>
            ) : (
              <>
                Process File
                <ArrowRight className="w-6 h-6" />
              </>
            )}
          </button>

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

          {/* Results Section - Terminal Style */}
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
        </div>
      </div>

      {/* Footer */}
      <footer className="bg-gray-50">
        <div className="container mx-auto px-6 py-8">
          <p className="text-center text-gray-600">
            Developed by Truong Thien and Thanh Truc
          </p>
        </div>
      </footer>
    </div>
  );
};

export default iEngineUI;