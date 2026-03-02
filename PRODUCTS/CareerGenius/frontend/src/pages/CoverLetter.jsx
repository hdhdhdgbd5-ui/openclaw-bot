import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { 
  PenTool, Sparkles, Copy, Download, RefreshCw, 
  CheckCircle2, FileText, Lightbulb
} from 'lucide-react';
import toast from 'react-hot-toast';
import axios from 'axios';
import useAppStore from '../stores/appStore';
import { downloadText, copyToClipboard } from '../utils/helpers';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:3001/api';

const tones = [
  { value: 'professional', label: 'Professional', desc: 'Standard business tone' },
  { value: 'confident', label: 'Confident', desc: 'Assertive and bold' },
  { value: 'enthusiastic', label: 'Enthusiastic', desc: 'High energy and passionate' },
  { value: 'formal', label: 'Formal', desc: 'Traditional and respectful' },
];

function CoverLetter() {
  const { resumeText, setResumeText } = useAppStore();
  const [jobDescription, setJobDescription] = useState('');
  const [tone, setTone] = useState('professional');
  const [companyResearch, setCompanyResearch] = useState('');
  const [generating, setGenerating] = useState(false);
  const [result, setResult] = useState(null);

  const generateLetter = async () => {
    if (!resumeText || !jobDescription) {
      toast.error('Please provide both resume and job description');
      return;
    }

    setGenerating(true);
    try {
      const response = await axios.post(`${API_URL}/cover-letter/generate`, {
        resumeText,
        jobDescription,
        tone,
        companyResearch
      });
      setResult(response.data);
      toast.success('Cover letter generated!');
    } catch (error) {
      toast.error('Failed to generate cover letter');
    } finally {
      setGenerating(false);
    }
  };

  return (
    <div className="max-w-5xl mx-auto">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-slate-900 mb-2">Cover Letter Generator</h1>
        <p className="text-slate-600">Create tailored cover letters that match your resume to any job</p>
      </div>

      {!result ? (
        <div className="space-y-6">
          {/* Resume */}
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

          {/* Job Description */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
            className="bg-white rounded-2xl border border-slate-200 p-6"
          >
            <label className="flex items-center gap-2 font-semibold text-slate-900 mb-4">
              <PenTool className="w-5 h-5 text-primary-600" />
              Job Description
            </label>
            
            <textarea
              value={jobDescription}
              onChange={(e) => setJobDescription(e.target.value)}
              placeholder="Paste the job description here..."
              className="w-full h-32 p-4 border border-slate-300 rounded-xl resize-none focus:ring-2 focus:ring-primary-500"
            />
          </motion.div>

          {/* Tone Selection */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            className="bg-white rounded-2xl border border-slate-200 p-6"
          >
            <label className="block font-semibold text-slate-900 mb-4">Tone</label>
            
            <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
              {tones.map((t) => (
                <button
                  key={t.value}
                  onClick={() => setTone(t.value)}
                  className={`p-4 rounded-xl border text-left transition-all
                    ${tone === t.value 
                      ? 'border-primary-500 bg-primary-50 ring-2 ring-primary-500' 
                      : 'border-slate-200 hover:border-primary-300'}
                  `}
                >
                  <div className="font-medium">{t.label}</div>
                  <div className="text-sm text-slate-500">{t.desc}</div>
                </button>
              ))}
            </div>
          </motion.div>

          {/* Company Research */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
            className="bg-white rounded-2xl border border-slate-200 p-6"
          >
            <label className="flex items-center gap-2 font-semibold text-slate-900 mb-4">
              <Lightbulb className="w-5 h-5 text-amber-500" />
              Company Research (Optional)
            </label>
            
            <textarea
              value={companyResearch}
              onChange={(e) => setCompanyResearch(e.target.value)}
              placeholder="Add any specific details about the company: recent news, values, projects, why you're excited about them..."
              className="w-full h-24 p-4 border border-slate-300 rounded-xl resize-none focus:ring-2 focus:ring-primary-500"
            />
          </motion.div>

          {/* Generate Button */}
          <button
            onClick={generateLetter}
            disabled={generating || !resumeText || !jobDescription}
            className="w-full py-4 bg-gradient-to-r from-primary-600 to-purple-600 text-white rounded-xl font-semibold hover:opacity-90 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
          >
            {generating ? (
              <>
                <RefreshCw className="w-5 h-5 animate-spin" />
                Crafting your cover letter...
              </>
            ) : (
              <>
                <Sparkles className="w-5 h-5" />
                Generate Cover Letter
              </>
            )}
          </button>
        </div>
      ) : (
        <>
          {/* Results */}
          <div className="space-y-6">
            {/* Cover Letter Display */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="bg-white rounded-2xl border border-slate-200 overflow-hidden"
            >
              <div className="flex items-center justify-between p-4 border-b border-slate-200">
                <h3 className="font-semibold">Your Cover Letter</h3>
                
                <div className="flex gap-2">
                  <button
                    onClick={() => {
                      copyToClipboard(result.coverLetter);
                      toast.success('Copied!');
                    }}
                    className="p-2 text-slate-600 hover:bg-slate-100 rounded-lg"
                    title="Copy"
                  >
                    <Copy className="w-5 h-5" />
                  </button>
                  
                  <button
                    onClick={() => {
                      downloadText(result.coverLetter, 'cover-letter.txt');
                      toast.success('Downloaded!');
                    }}
                    className="p-2 text-slate-600 hover:bg-slate-100 rounded-lg"
                    title="Download"
                  >
                    <Download className="w-5 h-5" />
                  </button>
                </div>
              </div>
              
              <div className="p-8">
                <div className="prose max-w-none whitespace-pre-wrap font-serif text-lg leading-relaxed">
                  {result.coverLetter}
                </div>
              </div>
            </motion.div>

            {/* Key Points */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.1 }}
              className="bg-emerald-50 rounded-2xl border border-emerald-200 p-6"
            >
              <div className="flex items-center gap-2 mb-4">
                <CheckCircle2 className="w-5 h-5 text-emerald-600" />
                <h3 className="font-semibold text-emerald-900">Key Points Covered</h3>
              </div>
              
              <ul className="space-y-2">
                {result.keyPoints?.map((point, i) => (
                  <li key={i} className="flex items-start gap-2 text-emerald-800">
                    <span className="text-emerald-500">•</span>
                    {point}
                  </li>
                ))}
              </ul>
            </motion.div>

            {/* Customization Tips */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.2 }}
              className="bg-amber-50 rounded-2xl border border-amber-200 p-6"
            >
              <div className="flex items-center gap-2 mb-4">
                <Lightbulb className="w-5 h-5 text-amber-600" />
                <h3 className="font-semibold text-amber-900">Personalization Tips</h3>
              </div>
              
              <ul className="space-y-2">
                {result.customizationTips?.map((tip, i) => (
                  <li key={i} className="flex items-start gap-2 text-amber-800">
                    <span className="text-amber-500">→</span>
                    {tip}
                  </li>
                ))}
              </ul>
            </motion.div>

            {/* Actions */}
            <div className="flex gap-4">
              <button
                onClick={() => setResult(null)}
                className="px-6 py-3 bg-slate-200 text-slate-700 rounded-xl font-medium hover:bg-slate-300"
              >
                Generate Another
              </button>
            </div>
          </>
        )}
    </div>
  );
}

export default CoverLetter;
