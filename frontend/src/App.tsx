import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { 
  Monitor, 
  Smartphone, 
  Battery, 
  HardDrive, 
  Cpu, 
  Wifi, 
  Eye, 
  Zap,
  CheckCircle,
  AlertTriangle,
  XCircle,
  Loader2,
  Play
} from 'lucide-react';

interface DeviceInfo {
  id: string;
  device_class: string;
  make?: string;
  model?: string;
  os: string;
  os_version: string;
  capabilities: string[];
  connected_at: string;
}

interface TestResult {
  test_id: string;
  category: string;
  status: string;
  metrics: Record<string, any>;
  explanation: string;
  confidence: number;
  advisories: string[];
  timestamp: string;
}

interface DiagnosticResponse {
  device: DeviceInfo;
  results: TestResult[];
  summary: {
    total_tests: number;
    passed: number;
    warnings: number;
    failed: number;
    errors: number;
    health_score: number;
    overall_status: string;
  };
  report_id: string;
}

interface AvailableTest {
  id: string;
  name: string;
  duration: string;
}

function App() {
  const [device, setDevice] = useState<DeviceInfo | null>(null);
  const [availableTests, setAvailableTests] = useState<AvailableTest[]>([]);
  const [selectedTests, setSelectedTests] = useState<string[]>([]);
  const [isScanning, setIsScanning] = useState(false);
  const [diagnosticResults, setDiagnosticResults] = useState<DiagnosticResponse | null>(null);
  const [error, setError] = useState<string>('');
  const [currentStep, setCurrentStep] = useState<'detect' | 'select' | 'running' | 'results'>('detect');

  const detectDevice = async () => {
    try {
      setIsScanning(true);
      setError('');
      
      const response = await axios.get('/api/device/detect');
      const deviceInfo: DeviceInfo = response.data;
      setDevice(deviceInfo);
      
      // Get available tests
      const testsResponse = await axios.get(`/api/device/${deviceInfo.id}/capabilities`);
      setAvailableTests(testsResponse.data.available_tests);
      
      setCurrentStep('select');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to detect device');
    } finally {
      setIsScanning(false);
    }
  };

  const runDiagnostics = async () => {
    if (!device || selectedTests.length === 0) return;
    
    try {
      setIsScanning(true);
      setCurrentStep('running');
      setError('');
      
      const response = await axios.post('/api/diagnostics/run', {
        device_id: device.id,
        tests: selectedTests,
        options: {}
      });
      
      setDiagnosticResults(response.data);
      setCurrentStep('results');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to run diagnostics');
      setCurrentStep('select');
    } finally {
      setIsScanning(false);
    }
  };

  const getDeviceIcon = (deviceClass: string, os: string) => {
    if (os.toLowerCase().includes('android') || deviceClass === 'phone') {
      return <Smartphone className="w-16 h-16 text-cosmic-400" />;
    }
    return <Monitor className="w-16 h-16 text-cosmic-400" />;
  };

  const getCategoryIcon = (category: string) => {
    const iconMap: Record<string, React.ReactNode> = {
      power: <Battery className="w-5 h-5" />,
      storage: <HardDrive className="w-5 h-5" />,
      performance: <Cpu className="w-5 h-5" />,
      network: <Wifi className="w-5 h-5" />,
      display: <Eye className="w-5 h-5" />,
      sensors: <Zap className="w-5 h-5" />
    };
    return iconMap[category] || <Zap className="w-5 h-5" />;
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'pass':
        return <CheckCircle className="w-5 h-5 text-green-400" />;
      case 'warn':
        return <AlertTriangle className="w-5 h-5 text-yellow-400" />;
      case 'fail':
      case 'error':
        return <XCircle className="w-5 h-5 text-red-400" />;
      default:
        return <Loader2 className="w-5 h-5 text-blue-400 animate-spin" />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'pass': return 'border-green-400 bg-green-400/10';
      case 'warn': return 'border-yellow-400 bg-yellow-400/10';
      case 'fail':
      case 'error': return 'border-red-400 bg-red-400/10';
      default: return 'border-cosmic-400 bg-cosmic-400/10';
    }
  };

  return (
    <div className="min-h-screen cosmic-gradient">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="text-center mb-12">
          <h1 className="text-4xl md:text-6xl font-bold text-white mb-4">
            Universal Device Diagnostics
          </h1>
          <p className="text-xl text-cosmic-300 max-w-2xl mx-auto">
            AI-powered diagnostic and repair assistant for your devices
          </p>
        </div>

        {/* Error Display */}
        {error && (
          <div className="mb-8 p-4 bg-red-900/20 border border-red-400 rounded-lg">
            <div className="flex">
              <XCircle className="w-5 h-5 text-red-400 mr-3 mt-0.5" />
              <p className="text-red-300">{error}</p>
            </div>
          </div>
        )}

        {/* Step 1: Device Detection */}
        {currentStep === 'detect' && (
          <div className="max-w-2xl mx-auto">
            <div className="diagnostic-card rounded-xl p-8 text-center">
              <Monitor className="w-24 h-24 text-cosmic-400 mx-auto mb-6" />
              <h2 className="text-2xl font-bold text-white mb-4">
                Detect Your Device
              </h2>
              <p className="text-cosmic-300 mb-8">
                Click the button below to scan and identify your device's capabilities.
              </p>
              <button
                onClick={detectDevice}
                disabled={isScanning}
                className="bg-cosmic-600 hover:bg-cosmic-700 disabled:opacity-50 text-white px-8 py-3 rounded-lg font-semibold transition-colors flex items-center mx-auto"
              >
                {isScanning ? (
                  <>
                    <Loader2 className="w-5 h-5 mr-2 animate-spin" />
                    Detecting...
                  </>
                ) : (
                  <>
                    <Play className="w-5 h-5 mr-2" />
                    Detect Device
                  </>
                )}
              </button>
            </div>
          </div>
        )}

        {/* Step 2: Test Selection */}
        {currentStep === 'select' && device && (
          <div className="max-w-4xl mx-auto">
            {/* Device Info */}
            <div className="diagnostic-card rounded-xl p-6 mb-8">
              <div className="flex items-center">
                {getDeviceIcon(device.device_class, device.os)}
                <div className="ml-6">
                  <h2 className="text-2xl font-bold text-white">
                    {device.make || 'Unknown'} {device.model || device.device_class}
                  </h2>
                  <p className="text-cosmic-300">
                    {device.os} {device.os_version}
                  </p>
                  <p className="text-sm text-cosmic-400">
                    {device.capabilities.length} diagnostic capabilities available
                  </p>
                </div>
              </div>
            </div>

            {/* Test Selection */}
            <div className="diagnostic-card rounded-xl p-6 mb-8">
              <h3 className="text-xl font-bold text-white mb-6">Select Diagnostic Tests</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {availableTests.map((test) => (
                  <div
                    key={test.id}
                    className={`p-4 rounded-lg border cursor-pointer transition-all ${
                      selectedTests.includes(test.id)
                        ? 'border-cosmic-400 bg-cosmic-400/20'
                        : 'border-cosmic-700 bg-cosmic-900/30 hover:border-cosmic-500'
                    }`}
                    onClick={() => {
                      setSelectedTests(prev => 
                        prev.includes(test.id)
                          ? prev.filter(id => id !== test.id)
                          : [...prev, test.id]
                      );
                    }}
                  >
                    <div className="flex items-center justify-between">
                      <div>
                        <h4 className="font-semibold text-white">{test.name}</h4>
                        <p className="text-sm text-cosmic-400">~{test.duration}</p>
                      </div>
                      {getCategoryIcon(test.id.split('.')[0])}
                    </div>
                  </div>
                ))}
              </div>
              
              <div className="mt-8 flex justify-between items-center">
                <div className="text-cosmic-300">
                  {selectedTests.length} test{selectedTests.length !== 1 ? 's' : ''} selected
                </div>
                <button
                  onClick={runDiagnostics}
                  disabled={selectedTests.length === 0 || isScanning}
                  className="bg-cosmic-600 hover:bg-cosmic-700 disabled:opacity-50 text-white px-6 py-2 rounded-lg font-semibold transition-colors"
                >
                  Run Diagnostics
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Step 3: Running Tests */}
        {currentStep === 'running' && (
          <div className="max-w-2xl mx-auto">
            <div className="diagnostic-card rounded-xl p-8 text-center">
              <Loader2 className="w-24 h-24 text-cosmic-400 mx-auto mb-6 animate-spin" />
              <h2 className="text-2xl font-bold text-white mb-4">
                Running Diagnostics...
              </h2>
              <p className="text-cosmic-300">
                Please wait while we analyze your device. This may take a few minutes.
              </p>
            </div>
          </div>
        )}

        {/* Step 4: Results */}
        {currentStep === 'results' && diagnosticResults && (
          <div className="max-w-6xl mx-auto">
            {/* Summary */}
            <div className="diagnostic-card rounded-xl p-6 mb-8">
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-2xl font-bold text-white">Diagnostic Results</h2>
                <div className="text-right">
                  <div className="text-3xl font-bold text-cosmic-400">
                    {diagnosticResults.summary.health_score}%
                  </div>
                  <div className="text-sm text-cosmic-300">Health Score</div>
                </div>
              </div>
              
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div className="text-center">
                  <div className="text-2xl font-bold text-green-400">
                    {diagnosticResults.summary.passed}
                  </div>
                  <div className="text-sm text-cosmic-300">Passed</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-yellow-400">
                    {diagnosticResults.summary.warnings}
                  </div>
                  <div className="text-sm text-cosmic-300">Warnings</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-red-400">
                    {diagnosticResults.summary.failed}
                  </div>
                  <div className="text-sm text-cosmic-300">Failed</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-gray-400">
                    {diagnosticResults.summary.errors}
                  </div>
                  <div className="text-sm text-cosmic-300">Errors</div>
                </div>
              </div>
            </div>

            {/* Detailed Results */}
            <div className="space-y-4">
              {diagnosticResults.results.map((result, index) => (
                <div
                  key={index}
                  className={`diagnostic-card rounded-xl p-6 border ${getStatusColor(result.status)}`}
                >
                  <div className="flex items-start justify-between">
                    <div className="flex items-start space-x-4">
                      {getStatusIcon(result.status)}
                      <div className="flex-1">
                        <h3 className="text-lg font-semibold text-white mb-2">
                          {availableTests.find(t => t.id === result.test_id)?.name || result.test_id}
                        </h3>
                        <p className="text-cosmic-300 mb-3">{result.explanation}</p>
                        
                        {result.advisories.length > 0 && (
                          <div className="mb-3">
                            <h4 className="text-sm font-semibold text-cosmic-200 mb-2">Recommendations:</h4>
                            <ul className="text-sm text-cosmic-300 space-y-1">
                              {result.advisories.map((advisory, i) => (
                                <li key={i} className="flex items-start">
                                  <span className="text-cosmic-400 mr-2">•</span>
                                  {advisory}
                                </li>
                              ))}
                            </ul>
                          </div>
                        )}
                        
                        {Object.keys(result.metrics).length > 0 && (
                          <details className="text-sm">
                            <summary className="text-cosmic-400 cursor-pointer hover:text-cosmic-300">
                              Technical Details
                            </summary>
                            <div className="mt-2 bg-cosmic-900/50 p-3 rounded">
                              <pre className="text-cosmic-300 text-xs overflow-x-auto">
                                {JSON.stringify(result.metrics, null, 2)}
                              </pre>
                            </div>
                          </details>
                        )}
                      </div>
                    </div>
                    <div className="text-sm text-cosmic-400">
                      {Math.round(result.confidence * 100)}% confidence
                    </div>
                  </div>
                </div>
              ))}
            </div>

            {/* Actions */}
            <div className="mt-8 flex justify-center space-x-4">
              <button
                onClick={() => {
                  setCurrentStep('select');
                  setDiagnosticResults(null);
                  setSelectedTests([]);
                }}
                className="bg-cosmic-700 hover:bg-cosmic-800 text-white px-6 py-2 rounded-lg font-semibold transition-colors"
              >
                Run New Tests
              </button>
              <button
                onClick={() => {
                  setCurrentStep('detect');
                  setDevice(null);
                  setDiagnosticResults(null);
                  setSelectedTests([]);
                  setAvailableTests([]);
                }}
                className="bg-cosmic-600 hover:bg-cosmic-700 text-white px-6 py-2 rounded-lg font-semibold transition-colors"
              >
                Scan New Device
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default App;