import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { 
  Briefcase, ArrowRight, Target, CheckCircle2, AlertTriangle,
  TrendingUp, Award, Zap, Copy, RefreshCw
} from 'lucide-react';
import toast from 'react-hot-toast';
import axios from 'axios';
import useAppStore from '../stores/appStore';
import { getScoreColor, getScoreBg, copyToClipboard } from '../utils/helpers';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:3001/api';

function JobMatcher() {
  const { resumeText, setResumeText } = useAppStore();
  const [jobDescription, setJobDescription] = useState('');
  const [analyzing, setAnalyzing] = useState(false);
  const [fitResult, setFitResult] = useState(null);

  const analyzeFit = async () => {
    if (!resumeText || !jobDescription) {
      toast.error('Please provide both resume and job description');
      return;
    }

    setAnalyzing(true);
    try {
      const response = await axios.post(`${API_URL}/jobs/fit-score`, {
        resumeText,
        jobDescription
      });
      setFitResult(response.data);
      toast.success('Fit analysis complete!');
    } catch (error) {
      toast.error('Failed to analyze job fit');
    } finally {
      setAnalyzing(false);
    }
  };

  const getCategoryColor = (category) => {
    switch (category) {
      case 'excellent': return 'text-emerald-600 bg-emerald-50';
      case 'good': return 'text-blue-600 bg-blue-50';
      case 'fair': return 'text-amber-600 bg-amber-50';
      default: return 'text-red-600 bg-red-50';
    }
  };

  return (
    <div className="max-w-5xl mx-auto">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-slate-900 mb-2">Job Matcher</h1>
        <p className="text-slate-600">Compare your resume with job descriptions to calculate your fit score</p>
      </div>

      {!fitResult ? (
        <div className="grid lg:grid-cols-2 gap-6">
          {/* Resume Input */}
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            className="bg-white rounded-2xl border border-slate-200 p-6"
          >
            <div className="flex items-center gap-2 mb-4">
              <div className="w-10 h-10 rounded-lg bg-blue-100 flex items-center justify-center">
                <Briefcase className="w-5 h-5 text-blue-600" />
              </div>
              <div>
                <h3 className="font-semibold text-slate-900">Your Resume</h3>
                <p className="text-sm text-slate-500">Paste your resume content</p>
              </div>
            </div>
            
            <textarea
              value={resumeText}
              onChange={(e) => setResumeText(e.target.value)}
              placeholder="Paste your resume here..."
              className="w-full h-64 p-4 border border-slate-300 rounded-xl resize-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
            />
          </motion.div>

          {/* Job Description Input */}
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            className="bg-white rounded-2xl border border-slate-200 p-6"
          >
            <div className="flex items-center gap-2 mb-4">
              <div className="w-10 h-10 rounded-lg bg-purple-100 flex items-center justify-center">
                <Target className="w-5 h-5 text-purple-600" />
              </div>
              <div>
                <h3 className="font-semibold text-slate-900">Job Description</h3>
                <p className="text-sm text-slate-500">Paste the job posting</p>
              </div>
            </div>
            
            <textarea
              value={jobDescription}
              onChange={(e) => setJobDescription(e.target.value)}
              placeholder="Paste the job description here..."
              className="w-full h-64 p-4 border border-slate-300 rounded-xl resize-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
            />
          </motion.div>

          {/* Analyze Button */}
          <div className="lg:col-span-2">
            <button
              onClick={analyzeFit}
              disabled={analyzing || !resumeText || !jobDescription}
              className="w-full py-4 bg-gradient-to-r from-primary-600 to-purple-600 text-white rounded-xl font-semibold hover:opacity-90 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
            >
              {analyzing ? (
                <>
                  <RefreshCw className="w-5 h-5 animate-spin" />
                  Analyzing Fit...
                </>
              ) : (
                <>
                  <Target className="w-5 h-5" />
                  Calculate Fit Score
                  <ArrowRight className="w-5 h-5" />
                </>
              )}
            </button>
          </div>
        </div>
      ) : (
        <>
          {/* Results */}
          <div className="space-y-6">
            {/* Overall Score */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="bg-white rounded-2xl border border-slate-200 p-8"
            >
              <div className="flex flex-col md:flex-row items-center gap-8">
                <div className="relative">
                  <div className="w-40 h-40 rounded-full border-8 border-slate-100 flex items-center justify-center">
                    <span className={`text-5xl font-bold ${getScoreColor(fitResult.overallFitScore)}`}>
                      {fitResult.overallFitScore}%
                    </span>
                  </div>
                </div>
                
                <div className="flex-1 text-center md:text-left">
                  <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full font-medium mb-4">
                    <span className={getCategoryColor(fitResult.category)}>
                      {fitResult.category?.toUpperCase()} MATCH
                    </span>
                  </div>
                  
                  <p className="text-lg text-slate-600 mb-4">
                    {fitResult.overallFitScore >= 80 
                      ? 'Excellent match! You have strong qualifications for this role.' 
                      : fitResult.overallFitScore >= 60 
                      ? 'Good match with some areas to highlight or improve.' 
                      : 'This role may be a stretch. Consider addressing the gaps below.'}
                  </p>
                  
                  <div className="flex flex-wrap gap-3 justify-center md:justify-start">
                    <button
                      onClick={() => setFitResult(null)}
                      className="px-4 py-2 bg-slate-200 text-slate-700 rounded-lg hover:bg-slate-300 transition-colors"
                    >
                      Try Another Job
                    </button>
                    
                    <button
                      onClick={() => {
                        navigator.clipboard.writeText(JSON.stringify(fitResult, null, 2));
                        toast.success('Results copied!');
                      }}
                      className="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors flex items-center gap-2"
                    >
                      <Copy className="w-4 h-4" />
                      Copy Results
                    </button>
                  </div>
                </div>
              </div>
            </motion.div>

            {/* Detailed Breakdown */}
            <div className="grid md:grid-cols-3 gap-6">
              {/* Skills Match */}
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.1 }}
                className="bg-white rounded-2xl border border-slate-200 p-6"
              >
                <div className="flex items-center justify-between mb-4">
                  <div className="flex items-center gap-2">
                    <Award className="w-5 h-5 text-primary-600" />
                    <h3 className="font-semibold">Skills Match</h3>
                  </div>
                  <span className={`text-2xl font-bold ${getScoreColor(fitResult.matching?.skills?.score)}`}>
                    {fitResult.matching?.skills?.score}%
                  </span>
                </div>
                
                <div className="space-y-4">
                  <div>
                    <p className="text-sm font-medium text-emerald-600 mb-2">✓ Matched Skills</p>
                    <div className="flex flex-wrap gap-2">
                      {fitResult.matching?.skills?.matched?.map((skill, i) => (
                        <span key={i} className="px-2 py-1 bg-emerald-100 text-emerald-700 rounded text-sm">
                          {skill}
                        </span>
                      ))}
                    </div>
                  </div>
                  
                  <div>
                    <p className="text-sm font-medium text-red-600 mb-2">✗ Missing Skills</p>
                    <div className="flex flex-wrap gap-2">
                      {fitResult.matching?.skills?.missing?.map((skill, i) => (
                        <span key={i} className="px-2 py-1 bg-red-100 text-red-700 rounded text-sm">
                          {skill}
                        </span>
                      ))}
                    </div>
                  </div>
                </div>
              </motion.div>

              {/* Experience Match */}
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.2 }}
                className="bg-white rounded-2xl border border-slate-200 p-6"
              >
                <div className="flex items-center justify-between mb-4">
                  <div className="flex items-center gap-2">
                    <TrendingUp className="w-5 h-5 text-primary-600" />
                    <h3 className="font-semibold">Experience</h3>
                  </div>
                  <span className={`text-2xl font-bold ${getScoreColor(fitResult.matching?.experience?.score)}`}>
                    {fitResult.matching?.experience?.score}%
                  </span>
                </div>
                
                <div className="space-y-3">
                  <div className="flex justify-between text-sm">
                    <span className="text-slate-600">Required</span>
                    <span className="font-medium">{fitResult.matching?.experience?.yearsRequired} years</span>
                  </div>
                  
                  <div className="flex justify-between text-sm">
                    <span className="text-slate-600">You Have</span>
                    <span className="font-medium">{fitResult.matching?.experience?.yearsCandidate} years</span>
                  </div>
                  
                  <div className="h-2 bg-slate-100 rounded-full overflow-hidden">
                    <div 
                      className={`h-full ${getScoreBg(fitResult.matching?.experience?.score)}`}
                      style={{ width: `${fitResult.matching?.experience?.score}%` }}
                    />
                  </div>
                </div>
              </motion.div>

              {/* Gap Analysis */}
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.3 }}
                className="bg-white rounded-2xl border border-slate-200 p-6"
              >
                <div className="flex items-center gap-2 mb-4">
                  <Zap className="w-5 h-5 text-amber-500" />
                  <h3 className="font-semibold">Quick Wins</h3>
                </div>
                
                <ul className="space-y-2">
                  {fitResult.recommendations?.quickWins?.map((win, i) => (
                    <li key={i} className="flex items-start gap-2 text-sm text-slate-600">
                      <CheckCircle2 className="w-4 h-4 text-emerald-500 mt-0.5 flex-shrink-0" />
                      {win}
                    </li>
                  ))}
                </ul>
              </motion.div>
            </div>

            {/* Critical Gaps */}
            <{fitResult.gapAnalysis?.criticalGaps?.length > 0 && (
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="bg-amber-50 border border-amber-200 rounded-2xl p-6"
              >
                <div className="flex items-center gap-2 mb-4">
                  <AlertTriangle className="w-5 h-5 text-amber-600" />
                  <h3 className="font-semibold text-amber-900">Critical Gaps to Address</h3>
                </div>
                
                <ul className="space-y-2">
                  {fitResult.gapAnalysis.criticalGaps.map((gap, i) => (
                    <li key={i} className="text-amber-800">{gap}</li>
                  ))}
                </ul>
              </motion.div>
            )}
          </>
        )}
    </div>
  );
}

export default JobMatcher;
