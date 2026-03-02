import React, { useState, useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Upload, FileText, CheckCircle2, AlertCircle, 
  ChevronDown, ChevronUp, Download, Copy, RefreshCw,
  Sparkles, Target, Layout, Award, Zap
} from 'lucide-react';
import toast from 'react-hot-toast';
import axios from 'axios';
import useAppStore from '../stores/appStore';
import { getScoreColor, getScoreBg, copyToClipboard, downloadText } from '../utils/helpers';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:3001/api';

function ResumeAnalyzer() {
  const { resumeText, resumeAnalysis, setResumeText, setResumeAnalysis } = useAppStore();
  const [uploading, setUploading] = useState(false);
  const [analyzing, setAnalyzing] = useState(false);
  const [activeTab, setActiveTab] = useState('overview');
  const [expandedSections, setExpandedSections] = useState({});

  const onDrop = useCallback(async (acceptedFiles) => {
    const file = acceptedFiles[0];
    if (!file) return;

    setUploading(true);
    const formData = new FormData();
    formData.append('resume', file);

    try {
      const response = await axios.post(`${API_URL}/resume/upload`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      
      setResumeAnalysis(response.data.analysis);
      toast.success('Resume analyzed successfully!');
    } catch (error) {
      toast.error(error.response?.data?.error || 'Failed to analyze resume');
    } finally {
      setUploading(false);
    }
  }, [setResumeAnalysis]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'application/msword': ['.doc'],
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
      'text/plain': ['.txt']
    },
    maxFiles: 1
  });

  const analyzeText = async () => {
    if (!resumeText || resumeText.length < 50) {
      toast.error('Please enter at least 50 characters of resume text');
      return;
    }

    setAnalyzing(true);
    try {
      const response = await axios.post(`${API_URL}/resume/analyze-text`, { text: resumeText });
      setResumeAnalysis(response.data);
      toast.success('Analysis complete!');
    } catch (error) {
      toast.error('Failed to analyze resume text');
    } finally {
      setAnalyzing(false);
    }
  };

  const toggleSection = (section) => {
    setExpandedSections(prev => ({ ...prev, [section]: !prev[section] }));
  };

  const ScoreRing = ({ score, size = 120, strokeWidth = 8 }) => {
    const radius = (size - strokeWidth) / 2;
    const circumference = radius * 2 * Math.PI;
    const offset = circumference - (score / 100) * circumference;

    return (
      <div className="relative" style={{ width: size, height: size }}>
        <svg width={size} height={size} className="transform -rotate-90">
          <circle
            cx={size / 2}
            cy={size / 2}
            r={radius}
            stroke="#e2e8f0"
            strokeWidth={strokeWidth}
            fill="none"
          />
          <circle
            cx={size / 2}
            cy={size / 2}
            r={radius}
            stroke={score >= 70 ? '#10b981' : score >= 50 ? '#f59e0b' : '#ef4444'}
            strokeWidth={strokeWidth}
            fill="none"
            strokeDasharray={circumference}
            strokeDashoffset={offset}
            strokeLinecap="round"
            className="transition-all duration-1000 ease-out"
          />
        </svg>
        <div className="absolute inset-0 flex items-center justify-center">
          <span className={`text-3xl font-bold ${getScoreColor(score)}`}>{score}</span>
        </div>
      </div>
    );
  };

  return (
    <div className="max-w-5xl mx-auto">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-slate-900 mb-2">Resume Analyzer</h1>
        <p className="text-slate-600">Upload your resume for AI-powered ATS scoring and optimization</p>
      </div>

      {!resumeAnalysis ? (
        <div className="space-y-6">
          {/* Upload Zone */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
          >
            <div
              {...getRootProps()}
              className={`
                border-2 border-dashed rounded-2xl p-12 text-center cursor-pointer
                transition-all duration-300
                ${isDragActive 
                  ? 'border-primary-500 bg-primary-50' 
                  : 'border-slate-300 hover:border-primary-400 hover:bg-slate-50'}
              `}
            >
              <input {...getInputProps()} />
              
              {uploading ? (
                <div className="flex flex-col items-center">
                  <div className="w-12 h-12 border-4 border-primary-200 border-t-primary-600 rounded-full animate-spin mb-4" />
                  <p className="text-slate-600">Analyzing your resume...</p>
                </div>
              ) : (
                <>
                  <div className="w-16 h-16 bg-primary-100 rounded-2xl flex items-center justify-center mx-auto mb-4">
                    <Upload className="w-8 h-8 text-primary-600" />
                  </div>
                  <p className="text-lg font-medium text-slate-900 mb-2">
                    {isDragActive ? 'Drop your resume here' : 'Drag & drop your resume'}
                  </p>
                  <p className="text-slate-500 mb-4">Support PDF, DOCX, DOC, TXT (max 10MB)</p>
                  <button className="px-6 py-2 bg-primary-600 text-white rounded-lg font-medium hover:bg-primary-700 transition-colors">
                    Browse Files
                  </button>
                </>
              )}
            </div>
          </motion.div>

          {/* Or paste text */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
            className="bg-white rounded-2xl border border-slate-200 p-6"
          >
            <div className="flex items-center gap-2 mb-4">
              <FileText className="w-5 h-5 text-slate-500" />
              <span className="font-medium text-slate-900">Or paste your resume text</span>
            </div>
            
            <textarea
              value={resumeText}
              onChange={(e) => setResumeText(e.target.value)}
              placeholder="Paste your resume content here..."
              className="w-full h-48 p-4 border border-slate-300 rounded-xl resize-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
            />
            
            <button
              onClick={analyzeText}
              disabled={analyzing || resumeText.length < 50}
              className="mt-4 w-full py-3 bg-slate-900 text-white rounded-xl font-medium hover:bg-slate-800 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
            >
              {analyzing ? (
                <>
                  <RefreshCw className="w-5 h-5 animate-spin" />
                  Analyzing...
                </>
              ) : (
                <>
                  <Sparkles className="w-5 h-5" />
                  Analyze Resume
                </>
              )}
            </button>
          </motion.div>
        </div>
      ) : (
        <>
          {/* Analysis Results */}
          <div className="space-y-6">
            {/* Score Cards */}
            <div className="grid md:grid-cols-2 gap-6">
              <motion.div
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                className="bg-white rounded-2xl border border-slate-200 p-6 flex items-center justify-between"
              >
                <div>
                  <p className="text-sm font-medium text-slate-500 mb-1">ATS Compatibility</p>
                  <p className="text-2xl font-bold text-slate-900">{resumeAnalysis.atsScore}% Match</p>
                  <p className="text-sm text-slate-500 mt-1">
                    {resumeAnalysis.atsScore >= 80 ? 'Excellent for ATS systems' : 
                     resumeAnalysis.atsScore >= 60 ? 'Good with room for improvement' : 
                     'Needs optimization'}
                  </p>
                </div>
                <ScoreRing score={resumeAnalysis.atsScore} size={100} />
              </motion.div>

              <motion.div
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ delay: 0.1 }}
                className="bg-white rounded-2xl border border-slate-200 p-6 flex items-center justify-between"
              >
                <div>
                  <p className="text-sm font-medium text-slate-500 mb-1">Overall Quality</p>
                  <p className="text-2xl font-bold text-slate-900">{resumeAnalysis.overallScore}/100</p>
                  <p className="text-sm text-slate-500 mt-1">
                    Based on content, formatting, and impact
                  </p>
                </div>
                <ScoreRing score={resumeAnalysis.overallScore} size={100} />
              </motion.div>
            </div>

            {/* Tabs */}
            <div className="bg-white rounded-2xl border border-slate-200 overflow-hidden">
              <div className="flex border-b border-slate-200">
                {['overview', 'sections', 'keywords', 'improvements'].map((tab) => (
                  <button
                    key={tab}
                    onClick={() => setActiveTab(tab)}
                    className={`px-6 py-4 font-medium capitalize transition-colors
                      ${activeTab === tab 
                        ? 'text-primary-600 border-b-2 border-primary-600' 
                        : 'text-slate-500 hover:text-slate-700'}
                    `}
                  >
                    {tab}
                  </button>
                ))}
              </div>

              <div className="p-6">
                {activeTab === 'overview' && (
                  <div className="space-y-6">
                    {/* Section Scores */}
                    <div className="grid sm:grid-cols-2 lg:grid-cols-5 gap-4">
                      {Object.entries(resumeAnalysis.sections || {}).map(([key, section]) => (
                        <div 
                          key={key}
                          className={`p-4 rounded-xl border ${section.present ? 'border-slate-200' : 'border-red-200 bg-red-50'}`}
                        >
                          <div className="flex items-center gap-2 mb-2">
                            {section.present ? (
                              <CheckCircle2 className="w-4 h-4 text-emerald-500" />
                            ) : (
                              <AlertCircle className="w-4 h-4 text-red-500" />
                            )}
                            <span className="font-medium capitalize">{key.replace(/([A-Z])/g, ' $1').trim()}</span>
                          </div>
                          <div className="text-2xl font-bold">{section.score}%</div>
                          <p className="text-sm text-slate-500 mt-1">{section.feedback}</p>
                        </div>
                      ))}
                    </div>

                    {/* Keyword Optimization */}
                    <div className="bg-slate-50 rounded-xl p-6">
                      <div className="flex items-center gap-2 mb-4">
                        <Target className="w-5 h-5 text-primary-600" />
                        <h3 className="font-semibold">Keyword Optimization</h3>
                      </div>
                      
                      <div className="mb-4">
                        <div className="flex justify-between text-sm mb-1">
                          <span>Keyword Score</span>
                          <span className="font-medium">{resumeAnalysis.keywordOptimization?.score}%</span>
                        </div>
                        <div className="h-2 bg-slate-200 rounded-full overflow-hidden">
                          <div 
                            className={`h-full rounded-full ${getScoreBg(resumeAnalysis.keywordOptimization?.score)}`}
                            style={{ width: `${resumeAnalysis.keywordOptimization?.score}%` }}
                          />
                        </div>
                      </div>

                      <div className="grid md:grid-cols-2 gap-4">
                        <div>
                          <p className="text-sm font-medium mb-2">Strengths</p>
                          <ul className="space-y-1">
                            {resumeAnalysis.keywordOptimization?.strengths?.map((strength, i) => (
                              <li key={i} className="text-sm text-slate-600 flex items-start gap-2">
                                <CheckCircle2 className="w-4 h-4 text-emerald-500 mt-0.5 flex-shrink-0" />
                                {strength}
                              </li>
                            ))}
                          </ul>
                        </div>
                        
                        <div>
                          <p className="text-sm font-medium mb-2">Missing Keywords</p>
                          <ul className="space-y-1">
                            {resumeAnalysis.keywordOptimization?.missingKeywords?.map((keyword, i) => (
                              <li key={i} className="text-sm text-slate-600 flex items-start gap-2">
                                <Zap className="w-4 h-4 text-amber-500 mt-0.5 flex-shrink-0" />
                                {keyword}
                              </li>
                            ))}
                          </ul>
                        </div>
                      </div>
                    </div>
                  </div>
                )}

                {activeTab === 'improvements' && (
                  <div className="space-y-4">
                    {resumeAnalysis.improvements?.map((improvement, index) => (
                      <div 
                        key={index}
                        className={`
                          p-4 rounded-xl border
                          ${improvement.priority === 'high' ? 'border-red-200 bg-red-50' : 
                            improvement.priority === 'medium' ? 'border-amber-200 bg-amber-50' : 
                            'border-blue-200 bg-blue-50'}
                        `}
                      >
                        <div className="flex items-center gap-2 mb-2">
                          <span className={`
                            px-2 py-0.5 text-xs font-medium rounded-full uppercase
                            ${improvement.priority === 'high' ? 'bg-red-200 text-red-800' : 
                              improvement.priority === 'medium' ? 'bg-amber-200 text-amber-800' : 
                              'bg-blue-200 text-blue-800'}
                          `}>
                            {improvement.priority}
                          </span>
                          <span className="font-medium capitalize">{improvement.section}</span>
                        </div>
                        <p className="text-slate-700">{improvement.suggestion}</p>
                      </div>
                    ))}
                  </div>
                )}

                {activeTab === 'sections' && (
                  <div className="space-y-4">
                    {Object.entries(resumeAnalysis.sections || {}).map(([key, section]) => (
                      <div key={key} className="border border-slate-200 rounded-xl overflow-hidden">
                        <button
                          onClick={() => toggleSection(key)}
                          className="w-full flex items-center justify-between p-4 hover:bg-slate-50 transition-colors"
                        >
                          <div className="flex items-center gap-3">
                            {section.present ? (
                              <CheckCircle2 className="w-5 h-5 text-emerald-500" />
                            ) : (
                              <AlertCircle className="w-5 h-5 text-red-500" />
                            )}
                            <span className="font-medium capitalize">{key.replace(/([A-Z])/g, ' $1').trim()}</span>
                          </div>
                          <div className="flex items-center gap-3">
                            <span className={`font-bold ${getScoreColor(section.score)}`}>{section.score}%</span>
                            {expandedSections[key] ? <ChevronUp className="w-5 h-5" /> : <ChevronDown className="w-5 h-5" />}
                          </div>
                        </button>
                        
                        <AnimatePresence>
                          {expandedSections[key] && (
                            <motion.div
                              initial={{ height: 0, opacity: 0 }}
                              animate={{ height: 'auto', opacity: 1 }}
                              exit={{ height: 0, opacity: 0 }}
                              className="border-t border-slate-200"
                            >
                              <div className="p-4">
                                <p className="text-slate-700">{section.feedback}</p>
                              </div>
                            </motion.div>
                          )}
                        </AnimatePresence>
                      </div>
                    ))}
                  </div>
                )}

                {activeTab === 'keywords' && (
                  <div className="space-y-6">
                    <div>
                      <h3 className="font-semibold mb-3">Action Verbs Used</h3>
                      <div className="flex flex-wrap gap-2">
                        {resumeAnalysis.keywordOptimization?.actionVerbs?.map((verb, i) => (
                          <span key={i} className="px-3 py-1 bg-emerald-100 text-emerald-700 rounded-full text-sm">
                            {verb}
                          </span>
                        ))}
                      </div>
                    </div>

                    <div>
                      <h3 className="font-semibold mb-3">Formatting Issues</h3>
                      <ul className="space-y-2">
                        {resumeAnalysis.formatting?.issues?.map((issue, i) => (
                          <li key={i} className="flex items-start gap-2 text-slate-600">
                            <AlertCircle className="w-4 h-4 text-amber-500 mt-0.5" />
                            {issue}
                          </li>
                        ))}
                      </ul>
                    </div>
                  </div>
                )}
              </div>
            </div>

            {/* Actions */}
            <div className="flex gap-4">
              <button
                onClick={() => setResumeAnalysis(null)}
                className="px-6 py-3 bg-slate-200 text-slate-700 rounded-xl font-medium hover:bg-slate-300 transition-colors"
              >
                Analyze Another Resume
              </button>
              
              <Link
                to="/job-matcher"
                className="px-6 py-3 bg-primary-600 text-white rounded-xl font-medium hover:bg-primary-700 transition-colors"
              >
                Match to Jobs →
              </Link>
            </div>
          </>
        )}
    </div>
  );
}

export default ResumeAnalyzer;
