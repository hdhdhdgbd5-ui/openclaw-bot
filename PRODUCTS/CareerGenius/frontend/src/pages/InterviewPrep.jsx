import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { 
  MessageSquare, Sparkles, Target, Clock, Star,
  ChevronDown, ChevronUp, Copy, RefreshCw, Lightbulb
} from 'lucide-react';
import toast from 'react-hot-toast';
import axios from 'axios';
import useAppStore from '../stores/appStore';
import { copyToClipboard } from '../utils/helpers';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:3001/api';

const interviewTypes = [
  { value: 'phone', label: 'Phone Screen', desc: 'Initial recruiter call' },
  { value: 'technical', label: 'Technical', desc: 'Coding/system design' },
  { value: 'behavioral', label: 'Behavioral', desc: 'STAR format questions' },
  { value: 'final', label: 'Final Round', desc: 'Senior leadership' },
];

function InterviewPrep() {
  const { resumeText, setResumeText } = useAppStore();
  const [jobDescription, setJobDescription] = useState('');
  const [interviewType, setInterviewType] = useState('behavioral');
  const [predicting, setPredicting] = useState(false);
  const [result, setResult] = useState(null);
  const [expandedQuestions, setExpandedQuestions] = useState({});

  const predictQuestions = async () => {
    if (!resumeText || !jobDescription) {
      toast.error('Please provide both resume and job description');
      return;
    }

    setPredicting(true);
    try {
      const response = await axios.post(`${API_URL}/interview/predict`, {
        resumeText,
        jobDescription,
        interviewType
      });
      setResult(response.data);
      toast.success('Questions predicted!');
    } catch (error) {
      toast.error('Failed to predict questions');
    } finally {
      setPredicting(false);
    }
  };

  const toggleQuestion = (id) => {
    setExpandedQuestions(prev => ({ ...prev, [id]: !prev[id] }));
  };

  const getDifficultyColor = (difficulty) => {
    switch (difficulty) {
      case 'easy': return 'bg-emerald-100 text-emerald-700';
      case 'medium': return 'bg-amber-100 text-amber-700';
      case 'hard': return 'bg-red-100 text-red-700';
      default: return 'bg-slate-100 text-slate-700';
    }
  };

  return (
    <div className="max-w-5xl mx-auto">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-slate-900 mb-2">Interview Prep</h1>
        <p className="text-slate-600">AI-predicted questions with STAR format answers tailored to your experience</p>
      </div>

      {!result ? (
        <div className="space-y-6">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="bg-white rounded-2xl border border-slate-200 p-6"
          >
            <label className="block font-semibold text-slate-900 mb-2">Your Resume</label>
            
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
            className="bg-white rounded-2xl border border-slate-200 p-6"
          >
            <label className="block font-semibold text-slate-900 mb-2">Job Description</label>
            
            <textarea
              value={jobDescription}
              onChange={(e) => setJobDescription(e.target.value)}
              placeholder="Paste the job description here..."
              className="w-full h-32 p-4 border border-slate-300 rounded-xl resize-none focus:ring-2 focus:ring-primary-500"
            />
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            className="bg-white rounded-2xl border border-slate-200 p-6"
          >
            <label className="block font-semibold text-slate-900 mb-4">Interview Type</label>
            
            <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
              {interviewTypes.map((type) => (
                <button
                  key={type.value}
                  onClick={() => setInterviewType(type.value)}
                  className={`p-4 rounded-xl border text-left transition-all
                    ${interviewType === type.value 
                      ? 'border-primary-500 bg-primary-50 ring-2 ring-primary-500' 
                      : 'border-slate-200 hover:border-primary-300'}
                  `}
                >
                  <div className="font-medium">{type.label}</div>
                  <div className="text-sm text-slate-500">{type.desc}</div>
                </button>
              ))}
            </div>
          </motion.div>

          <button
            onClick={predictQuestions}
            disabled={predicting || !resumeText || !jobDescription}
            className="w-full py-4 bg-gradient-to-r from-primary-600 to-purple-600 text-white rounded-xl font-semibold hover:opacity-90 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
          >
            {predicting ? (
              <>
                <RefreshCw className="w-5 h-5 animate-spin" />
                Predicting questions...
              </>
            ) : (
              <>
                <Sparkles className="w-5 h-5" />
                Predict Interview Questions
              </>
            )}
          </button>
        </div>
      ) : (
        <>
          <div className="space-y-6">
            {/* Behavioral Questions */}
            <{result.predictedQuestions?.behavioral?.length > 0 && (
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="bg-white rounded-2xl border border-slate-200 overflow-hidden"
              >
                <div className="p-6 border-b border-slate-200">
                  <div className="flex items-center gap-2">
                    <MessageSquare className="w-5 h-5 text-primary-600" />
                    <h3 className="font-semibold">Behavioral Questions</h3>
                  </div>
                </div>

                <div className="divide-y divide-slate-200">
                  {result.predictedQuestions.behavioral.map((q, index) => (
                    <div key={index} className="p-6">
                      <button
                        onClick={() => toggleQuestion(`b-${index}`)}
                        className="w-full flex items-start justify-between gap-4 text-left"
                      >
                        <div>
                          <p className="font-medium text-slate-900 mb-2">{q.question}</p>
                          <p className="text-sm text-slate-500">{q.whatTheyWant}</p>
                        </div>
                        
                        <{expandedQuestions[`b-${index}`] ? (
                          <ChevronUp className="w-5 h-5 text-slate-400 flex-shrink-0" />
                        ) : (
                          <ChevronDown className="w-5 h-5 text-slate-400 flex-shrink-0" />
                        )}
                      </button>

                      <{expandedQuestions[`b-${index}`] && (
                        <motion.div
                          initial={{ opacity: 0, height: 0 }}
                          animate={{ opacity: 1, height: 'auto' }}
                          className="mt-4 pt-4 border-t border-slate-200"
                        >
                          <div className="bg-emerald-50 rounded-xl p-4">
                            <h4 className="font-medium text-emerald-900 mb-3 flex items-center gap-2">
                              <Star className="w-4 h-4" />
                              STAR Answer
                            </h4>
                            
                            <div className="space-y-2 text-sm">
                              <div>
                                <span className="font-medium text-emerald-700">Situation: </span>
                                <span className="text-emerald-800">{q.starFormat.situation}</span>
                              </div>
                              
                              <div>
                                <span className="font-medium text-emerald-700">Task: </span>
                                <span className="text-emerald-800">{q.starFormat.task}</span>
                              </div>
                              
                              <div>
                                <span className="font-medium text-emerald-700">Action: </span>
                                <span className="text-emerald-800">{q.starFormat.action}</span>
                              </div>
                              
                              <div>
                                <span className="font-medium text-emerald-700">Result: </span>
                                <span className="text-emerald-800">{q.starFormat.result}</span>
                              </div>
                            </div>
                          </div>
                        </motion.div>
                      )}
                    </div>
                  ))}
                </div>
              </motion.div>
            )}

            {/* Technical Questions */}
            <{result.predictedQuestions?.technical?.length > 0 && (
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.1 }}
                className="bg-white rounded-2xl border border-slate-200 overflow-hidden"
              >
                <div className="p-6 border-b border-slate-200">
                  <div className="flex items-center gap-2">
                    <Target className="w-5 h-5 text-primary-600" />
                    <h3 className="font-semibold">Technical Questions</h3>
                  </div>
                </div>

                <div className="divide-y divide-slate-200">
                  {result.predictedQuestions.technical.map((q, index) => (
                    <div key={index} className="p-6">
                      <div className="flex items-start justify-between gap-4 mb-2">
                        <p className="font-medium text-slate-900">{q.question}</p>
                        
                        <span className={`px-2 py-1 rounded text-xs font-medium ${getDifficultyColor(q.difficulty)}`}>
                          {q.difficulty}
                        </span>
                      </div>
                      
                      <p className="text-sm text-slate-500 mb-3">{q.whyAsked}</p>
                      
                      <div className="bg-blue-50 rounded-lg p-4">
                        <p className="text-sm text-blue-800 mb-2">
                          <span className="font-medium">Preparation: </span>
                          {q.preparationTips?.join(', ')}
                        </p>
                      </div>
                    </div>
                  ))}
                </div>
              </motion.div>
            )}

            {/* Questions to Ask */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.2 }}
              className="bg-amber-50 rounded-2xl border border-amber-200 p-6"
            >
              <div className="flex items-center gap-2 mb-4">
                <Lightbulb className="w-5 h-5 text-amber-600" />
                <h3 className="font-semibold text-amber-900">Questions to Ask Them</h3>
              </div>
              
              <ul className="space-y-3">
                {result.questionsToAsk?.map((q, i) => (
                  <li key={i} className="text-amber-800">
                    <p className="font-medium">{q.question}</p>
                    <p className="text-sm text-amber-600">Shows: {q.whatItShows}</p>
                  </li>
                ))}
              </ul>
            </motion.div>

            <div className="flex gap-4">
              <button
                onClick={() => setResult(null)}
                className="px-6 py-3 bg-slate-200 text-slate-700 rounded-xl font-medium hover:bg-slate-300"
              >
                Prep for Another Role
              </button>
            </div>
          </>
        )}
    </div>
  );
}

export default InterviewPrep;
