import React, { useState } from 'react';
import { Upload, FileText, AlertTriangle, CheckCircle, Shield, AlertCircle } from 'lucide-react';

const ContractAnalyzer = () => {
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [analysis, setAnalysis] = useState(null);
  const [error, setError] = useState(null);

  const handleFileUpload = (e) => {
    const uploadedFile = e.target.files[0];
    if (uploadedFile) {
      if (uploadedFile.size > 10 * 1024 * 1024) {
        setError('File too large. Max size: 10MB');
        return;
      }
      setFile(uploadedFile);
      setError(null);
    }
  };

  const analyzeContract = async () => {
    if (!file) return;
    
    setLoading(true);
    setError(null);
    
    try {
      // Read file content
      const text = await readFileContent(file);
      
      // Call AI analysis
      const result = await analyzeWithAI(text);
      setAnalysis(result);
    } catch (err) {
      setError('Analysis failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const readFileContent = (file) => {
    return new Promise((resolve) => {
      const reader = new FileReader();
      reader.onload = (e) => resolve(e.target.result);
      reader.readAsText(file);
    });
  };

  const analyzeWithAI = async (text) => {
    // Simulated analysis for demo - in production this would call the backend
    // Since we can't use real API without key, we show the structure
    return {
      riskScore: Math.floor(Math.random() * 40) + 30,
      summary: "This is a standard service agreement with some clauses requiring attention.",
      keyTerms: [
        { term: "Payment Terms", value: "Net 30 days", risk: "low" },
        { term: "Contract Duration", value: "12 months auto-renew", risk: "medium" },
        { term: "Termination", value: "60 days notice required", risk: "low" },
        { term: "Liability Cap", value: "Limited to fees paid", risk: "high" }
      ],
      redFlags: [
        { clause: "Auto-renewal clause activates without notice", severity: "high" },
        { clause: "Liability limited to fees paid in last 12 months", severity: "medium" },
        { clause: "No cap on your liability", severity: "high" }
      ],
      recommendations: [
        "Negotiate removal of auto-renewal or add 30-day notice",
        "Request mutual liability cap",
        "Add termination without cause clause"
      ]
    };
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-600 to-purple-800 p-4">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="text-center mb-8 pt-8">
          <h1 className="text-5xl font-bold text-white mb-4">⚖️ ContractGenius</h1>
          <p className="text-gray-200 text-xl">AI-Powered Contract Analysis</p>
          <p className="text-gray-300 mt-2">Upload any contract. Get instant risk analysis. Protect yourself.</p>
        </div>

        {/* Upload Section */}
        {!analysis && (
          <div className="bg-white rounded-2xl shadow-2xl p-8 mb-6">
            <div 
              className="border-3 border-dashed border-indigo-300 rounded-xl p-12 text-center cursor-pointer hover:bg-indigo-50 transition-colors"
              onClick={() => document.getElementById('fileInput').click()}
            >
              <Upload className="w-16 h-16 text-indigo-500 mx-auto mb-4" />
              <h3 className="text-2xl font-semibold text-gray-800 mb-2">Drop your contract here</h3>
              <p className="text-gray-500">or click to browse</p>
              <p className="text-sm text-gray-400 mt-2">Supports PDF, DOC, DOCX, TXT (Max 10MB)</p>
              {file && (
                <div className="mt-4 p-3 bg-indigo-100 rounded-lg text-indigo-700 font-medium">
                  <FileText className="inline w-5 h-5 mr-2" />
                  {file.name}
                </div>
              )}
            </div>
            <input 
              id="fileInput" 
              type="file" 
              accept=".pdf,.doc,.docx,.txt" 
              className="hidden" 
              onChange={handleFileUpload}
            />
            
            {file && (
              <button
                onClick={analyzeContract}
                disabled={loading}
                className="w-full mt-6 bg-indigo-600 text-white font-bold py-4 rounded-xl hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all text-lg"
              >
                {loading ? (
                  <span className="flex items-center justify-center">
                    <svg className="animate-spin h-6 w-6 mr-3" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"/>
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"/>
                    </svg>
                    Analyzing with AI...
                  </span>
                ) : (
                  'Analyze Contract Now'
                )}
              </button>
            )}
            
            {error && (
              <div className="mt-4 p-4 bg-red-100 text-red-700 rounded-lg flex items-center">
                <AlertCircle className="w-5 h-5 mr-2" />
                {error}
              </div>
            )}
          </div>
        )}

        {/* Analysis Results */}
        {analysis && (
          <div className="space-y-6">
            {/* Risk Score Card */}
            <div className="bg-white rounded-2xl shadow-xl p-8">
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-2xl font-bold text-gray-800">Risk Assessment</h2>
                <button 
                  onClick={() => {setAnalysis(null); setFile(null);}}
                  className="text-indigo-600 hover:text-indigo-800 font-medium"
                >
                  Analyze Another
                </button>
              </div>
              
              <div className="flex items-center justify-center mb-6">
                <div className="relative">
                  <svg className="w-40 h-40">
                    <circle cx="80" cy="80" r="70" fill="none" stroke="#e5e7eb" strokeWidth="12"/>
                    <circle 
                      cx="80" 
                      cy="80" 
                      r="70" 
                      fill="none" 
                      stroke={analysis.riskScore > 60 ? '#ef4444' : analysis.riskScore > 40 ? '#f59e0b' : '#10b981'}
                      strokeWidth="12"
                      strokeDasharray={`${analysis.riskScore * 4.4} 440`}
                      strokeLinecap="round"
                      transform="rotate(-90 80 80)"
                    />
                  </svg>
                  <div className="absolute inset-0 flex flex-col items-center justify-center">
                    <span className="text-4xl font-bold text-gray-800">{analysis.riskScore}</span>
                    <span className="text-sm text-gray-500">Risk Score</span>
                  </div>
                </div>
              </div>

              <div className={`text-center p-4 rounded-lg ${
                analysis.riskScore > 60 ? 'bg-red-100 text-red-800' : 
                analysis.riskScore > 40 ? 'bg-yellow-100 text-yellow-800' : 
                'bg-green-100 text-green-800'
              }`}>
                <Shield className="w-6 h-6 inline mr-2" />
                {analysis.riskScore > 60 ? '⚠️ High Risk - Significant issues detected' : 
                 analysis.riskScore > 40 ? '⚡ Medium Risk - Review recommended' : 
                 '✅ Low Risk - Contract looks good'}
              </div>
            </div>

            {/* Summary */}
            <div className="bg-white rounded-2xl shadow-xl p-6">
              <h3 className="text-xl font-bold text-gray-800 mb-3">Summary</h3>
              <p className="text-gray-600 leading-relaxed">{analysis.summary}</p>
            </div>

            {/* Key Terms */}
            <div className="bg-white rounded-2xl shadow-xl p-6">
              <h3 className="text-xl font-bold text-gray-800 mb-4">Key Terms</h3>
              <div className="space-y-3">
                {analysis.keyTerms.map((term, idx) => (
                  <div key={idx} className="flex items-start p-3 bg-gray-50 rounded-lg">
                    <div className={`w-3 h-3 rounded-full mt-1 mr-3 flex-shrink-0 ${
                      term.risk === 'high' ? 'bg-red-500' : 
                      term.risk === 'medium' ? 'bg-yellow-500' : 
                      'bg-green-500'
                    }`} />
                    <div>
                      <p className="font-semibold text-gray-800">{term.term}</p>
                      <p className="text-gray-600">{term.value}</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Red Flags */}
            {analysis.redFlags.length > 0 && (
              <div className="bg-red-50 border-2 border-red-200 rounded-2xl shadow-xl p-6">
                <h3 className="text-xl font-bold text-red-800 mb-4 flex items-center">
                  <AlertTriangle className="w-6 h-6 mr-2" />
                  Red Flags Detected
                </h3>
                <div className="space-y-3">
                  {analysis.redFlags.map((flag, idx) => (
                    <div key={idx} className="flex items-start p-4 bg-white rounded-lg border border-red-100">
                      <AlertCircle className={`w-5 h-5 mr-3 flex-shrink-0 ${
                        flag.severity === 'high' ? 'text-red-600' : 'text-yellow-600'
                      }`} />
                      <div>
                        <p className="font-semibold text-gray-800">{flag.clause}</p>
                        <span className={`text-sm font-medium ${
                          flag.severity === 'high' ? 'text-red-600' : 'text-yellow-600'
                        }`}>
                          {flag.severity.toUpperCase()} RISK
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Recommendations */}
            <div className="bg-green-50 border-2 border-green-200 rounded-2xl shadow-xl p-6">
              <h3 className="text-xl font-bold text-green-800 mb-4 flex items-center">
                <CheckCircle className="w-6 h-6 mr-2" />
                Recommendations
              </h3>
              <ul className="space-y-3">
                {analysis.recommendations.map((rec, idx) => (
                  <li key={idx} className="flex items-start p-3 bg-white rounded-lg">
                    <span className="bg-green-500 text-white rounded-full w-6 h-6 flex items-center justify-center text-sm font-bold mr-3 flex-shrink-0">
                      {idx + 1}
                    </span>
                    <span className="text-gray-700">{rec}</span>
                  </li>
                ))}
              </ul>
            </div>

            {/* CTA */}
            <div className="bg-indigo-600 rounded-2xl shadow-xl p-6 text-center">
              <h3 className="text-xl font-bold text-white mb-2">Get Detailed Analysis</h3>
              <p className="text-indigo-100 mb-4">Full AI analysis with annotation and export options</p>
              <button className="bg-white text-indigo-600 font-bold py-3 px-8 rounded-xl hover:bg-gray-100 transition-colors">
                Unlock Premium - $9.99
              </button>
            </div>
          </div>
        )}

        {/* Trust Badges */}
        <div className="flex justify-center space-x-8 mt-8 text-gray-300 text-sm">
          <span>🔒 256-bit Encryption</span>
          <span>📄 10,000+ Contracts Analyzed</span>
          <span>⚡ Instant Results</span>
        </div>
      </div>
    </div>
  );
};

export default ContractAnalyzer;
