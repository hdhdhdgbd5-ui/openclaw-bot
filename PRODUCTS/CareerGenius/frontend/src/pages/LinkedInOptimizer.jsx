import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { 
  Linkedin, Copy, CheckCircle2, Sparkles, RefreshCw,
  TrendingUp, Users, Hash, FileText
} from 'lucide-react';
import toast from 'react-hot-toast';
import axios from 'axios';
import useAppStore from '../stores/appStore';
import { copyToClipboard } from '../utils/helpers';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:3001/api';

function LinkedInOptimizer() {
  const { resumeText, setResumeText } = useAppStore();
  const [currentHeadline, setCurrentHeadline] = useState('');
  const [currentSummary, setCurrentSummary] = useState('');
  const [optimizing, setOptimizing] = useState(false);
  const [result, setResult] = useState(null);
  const [activeTab, setActiveTab] = useState('headline');

  const optimize = async () => {
    if (!resumeText) {
      toast.error('Please provide your resume');
      return;
    }

    setOptimizing(true);
    try {
      const response = await axios.post(`${API_URL}/linkedin/optimize`, {
        resumeText,
        currentHeadline,
        currentSummary
      });
      setResult(response.data);
      toast.success('Profile optimized!');
    } catch (error) {
      toast.error('Failed to optimize profile');
    } finally {
      setOptimizing(false);
    }
  };

  return (
    <div className="max-w-5xl mx-auto">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-slate-900 mb-2">LinkedIn Optimizer</h1>
        <p className="text-slate-600">Optimize your LinkedIn profile to attract recruiters and opportunities</p>
      </div>

      {!result ? (
        <div className="space-y-6">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="bg-white rounded-2xl border border-slate-200 p-6"
          >
            <label className="flex items-center gap-2 font-semibold text-slate-900 mb-4">
              <FileText className="w-5 h-5 text-primary-600" />
              Your Resume
            </label>
            
            <textarea
              value={resumeText}
              onChange={(e) => setResumeText(e.target.value)}
              placeholder="Paste your resume content here..."
              className="w-full h-32 p-4 border border-slate-300 rounded-xl resize-none focus:ring-2 focus:ring-primary-500"
            />
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
            className="grid md:grid-cols-2 gap-6"
          >
            <div className="bg-white rounded-2xl border border-slate-200 p-6">
              <label className="block font-semibold text-slate-900 mb-2">Current Headline (Optional)</label>
              <input
                type="text"
                value={currentHeadline}
                onChange={(e) => setCurrentHeadline(e.target.value)}
                placeholder="e.g., Software Engineer at Tech Co"
                className="w-full p-3 border border-slate-300 rounded-xl focus:ring-2 focus:ring-primary-500"
                maxLength={220}
              />
              <p className="text-sm text-slate-500 mt-1">{currentHeadline.length}/220 characters</p>
            </div>

            <div className="bg-white rounded-2xl border border-slate-200 p-6">
              <label className="block font-semibold text-slate-900 mb-2">Current Summary (Optional)</label>
              <textarea
                value={currentSummary}
                onChange={(e) => setCurrentSummary(e.target.value)}
                placeholder="Paste your current About section..."
                className="w-full h-20 p-3 border border-slate-300 rounded-xl resize-none focus:ring-2 focus:ring-primary-500"
                maxLength={2600}
              />
              <p className="text-sm text-slate-500 mt-1">{currentSummary.length}/2600 characters</p>
            </div>
          </motion.div>

          <button
            onClick={optimize}
            disabled={optimizing || !resumeText}
            className="w-full py-4 bg-[#0077b5] text-white rounded-xl font-semibold hover:bg-[#006396] disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
          >
            {optimizing ? (
              <>
                <RefreshCw className="w-5 h-5 animate-spin" />
                Optimizing...
              </>
            ) : (
              <>
                <Linkedin className="w-5 h-5" />
                Optimize My Profile
              </>
            )}
          </button>
        </div>
      ) : (
        <>
          <div className="bg-[#0077b5] text-white rounded-2xl p-6 mb-6">
            <div className="flex items-center gap-3">
              <Linkedin className="w-8 h-8" />
              <div>
                <h2 className="text-xl font-bold">Your Optimized Profile</h2>
                <p className="text-blue-100">Ready to copy and paste to LinkedIn</p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-2xl border border-slate-200 overflow-hidden">
            <div className="flex border-b border-slate-200">
              {['headline', 'summary', 'skills', 'networking'].map((tab) => (
                <button
                  key={tab}
                  onClick={() => setActiveTab(tab)}
                  className={`px-6 py-4 font-medium capitalize transition-colors
                    ${activeTab === tab 
                      ? 'text-[#0077b5] border-b-2 border-[#0077b5]' 
                      : 'text-slate-500 hover:text-slate-700'}
                  `}
                >
                  {tab}
                </button>
              ))}
            </div>

            <div className="p-6">
              {activeTab === 'headline' && (
                <div className="space-y-6">
                  <div className="bg-emerald-50 rounded-xl p-4 border border-emerald-200">
                    <div className="flex items-center justify-between mb-2">
                      <span className="font-medium text-emerald-900">Optimized Headline</span>
                      <button
                        onClick={() => {
                          copyToClipboard(result.headline?.optimized);
                          toast.success('Copied!');
                        }}
                        className="p-2 text-emerald-600 hover:bg-emerald-100 rounded-lg"
                      >
                        <Copy className="w-4 h-4" />
                      </button>
                    </div>
                    
                    <p className="text-lg text-emerald-800">{result.headline?.optimized}</p>
                  </div>

                  <div>
                    <h4 className="font-medium mb-3">Alternative Options</h4>
                    <div className="space-y-2">
                      {result.headline?.alternatives?.map((alt, i) => (
                        <div key={i} className="flex items-center justify-between p-3 bg-slate-50 rounded-lg">
                          <span className="text-slate-700">{alt}</span>
                          <button
                            onClick={() => {
                              copyToClipboard(alt);
                              toast.success('Copied!');
                            }}
                            className="p-1.5 text-slate-500 hover:bg-slate-200 rounded"
                          >
                            <Copy className="w-4 h-4" />
                          </button>
                        </div>
                      ))}
                    </div>
                  </div>

                  <div className="bg-blue-50 rounded-xl p-4">
                    <h4 className="font-medium text-blue-900 mb-2">Tips</h4>
                    <ul className="space-y-1">
                      {result.headline?.tips?.map((tip, i) => (
                        <li key={i} className="text-sm text-blue-800 flex items-start gap-2">
                          <Sparkles className="w-4 h-4 mt-0.5" />
                          {tip}
                        </li>
                      ))}
                    </ul>
                  </div>
                </div>
              )}

              {activeTab === 'summary' && (
                <div className="space-y-4">
                  <div className="bg-emerald-50 rounded-xl p-4 border border-emerald-200">
                    <div className="flex items-center justify-between mb-2">
                      <span className="font-medium text-emerald-900">Optimized Summary</span>
                      <button
                        onClick={() => {
                          copyToClipboard(result.summary?.optimized);
                          toast.success('Copied!');
                        }}
                        className="p-2 text-emerald-600 hover:bg-emerald-100 rounded-lg"
                      >
                        <Copy className="w-4 h-4" />
                      </button>
                    </div>
                    
                    <div className="prose max-w-none text-emerald-800 whitespace-pre-wrap">
                      {result.summary?.optimized}
                    </div>
                  </div>

                  <div className="grid md:grid-cols-2 gap-4">
                    <div className="bg-slate-50 rounded-xl p-4">
                      <h4 className="font-medium mb-2">Key Elements</h4>
                      <ul className="space-y-1">
                        {result.summary?.keyElements?.map((el, i) => (
                          <li key={i} className="text-sm text-slate-600 flex items-center gap-2">
                            <CheckCircle2 className="w-4 h-4 text-emerald-500" />
                            {el}
                          </li>
                        ))}
                      </ul>
                    </div>

                    <div className="bg-blue-50 rounded-xl p-4">
                      <h4 className="font-medium text-blue-900 mb-2">Call to Action</h4>
                      <p className="text-sm text-blue-800">{result.summary?.callToAction}</p>
                    </div>
                  </div>
                </div>
              )}

              {activeTab === 'skills' && (
                <div className="space-y-6">
                  <div>
                    <h4 className="font-medium mb-3">Top Skills to Feature</h4>
                    <div className="flex flex-wrap gap-2">
                      {result.skills?.topSkills?.map((skill, i) => (
                        <span key={i} className="px-3 py-1.5 bg-[#0077b5] text-white rounded-full text-sm">
                          {skill}
                        </span>
                      ))}
                    </div>
                  </div>

                  <div>
                    <h4 className="font-medium mb-3">Additional Skills to Add</h4>
                    <div className="flex flex-wrap gap-2">
                      {result.skills?.skillsToAdd?.map((skill, i) => (
                        <span key={i} className="px-3 py-1.5 bg-slate-100 text-slate-700 rounded-full text-sm">
                          {skill}
                        </span>
                      ))}
                    </div>
                  </div>

                  <div className="bg-amber-50 rounded-xl p-4 border border-amber-200">
                    <h4 className="font-medium text-amber-900 mb-2">Endorsement Strategy</h4>
                    <p className="text-amber-800">{result.skills?.endorsementStrategy}</p>
                  </div>
                </div>
              )}

              {activeTab === 'networking' && (
                <div className="space-y-6">
                  <div>
                    <h4 className="font-medium mb-3">Connection Request Templates</h4>
                    <div className="space-y-3">
                      {result.networking?.connectionRequests?.map((template, i) => (
                        <div key={i} className="bg-slate-50 rounded-xl p-4">
                          <div className="flex items-center justify-between mb-2">
                            <span className="text-sm font-medium text-slate-500">Template {i + 1}</span>
                            <button
                              onClick={() => {
                                copyToClipboard(template);
                                toast.success('Copied!');
                              }}
                              className="p-1.5 text-slate-500 hover:bg-slate-200 rounded"
                            >
                              <Copy className="w-4 h-4" />
                            </button>
                          </div>
                          
                          <p className="text-slate-700 text-sm">{template}</p>
                        </div>
                      ))}
                    </div>
                  </div>

                  <div className="bg-blue-50 rounded-xl p-4">
                    <h4 className="font-medium text-blue-900 mb-2">Engagement Strategy</h4>
                    <p className="text-blue-800">{result.networking?.engagementStrategy}</p>
                  </div>
                </div>
              )}
            </div>
          </div>

          <div className="mt-6 flex gap-4">
            <button
              onClick={() => setResult(null)}
              className="px-6 py-3 bg-slate-200 text-slate-700 rounded-xl font-medium hover:bg-slate-300"
            >
              Optimize Again
            </button>
          </div>
        </>
      )}
    </div>
  );
}

export default LinkedInOptimizer;
