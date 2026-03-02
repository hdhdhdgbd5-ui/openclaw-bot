import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { 
  DollarSign, TrendingUp, MessageCircle, Copy, RefreshCw,
  CheckCircle2, AlertTriangle, Award, ChevronDown, ChevronUp
} from 'lucide-react';
import toast from 'react-hot-toast';
import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:3001/api';

function SalaryNegotiation() {
  const [jobTitle, setJobTitle] = useState('');
  const [currentSalary, setCurrentSalary] = useState('');
  const [offerAmount, setOfferAmount] = useState('');
  const [location, setLocation] = useState('');
  const [experience, setExperience] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [activeTab, setActiveTab] = useState('scripts');
  const [expandedScenarios, setExpandedScenarios] = useState({});

  const generateScripts = async () => {
    if (!jobTitle) {
      toast.error('Please enter a job title');
      return;
    }

    setLoading(true);
    try {
      const response = await axios.post(`${API_URL}/salary/negotiation-scripts`, {
        jobTitle,
        currentSalary: currentSalary ? parseInt(currentSalary) : null,
        offerDetails: {
          amount: offerAmount ? parseInt(offerAmount) : null,
          location,
          experience: experience ? parseInt(experience) : null
        }
      });
      setResult(response.data);
      toast.success('Negotiation scripts ready!');
    } catch (error) {
      toast.error('Failed to generate scripts');
    } finally {
      setLoading(false);
    }
  };

  const toggleScenario = (scenario) => {
    setExpandedScenarios(prev => ({ ...prev, [scenario]: !prev[scenario] }));
  };

  return (
    <div className="max-w-5xl mx-auto">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-slate-900 mb-2">Salary Negotiation</h1>
        <p className="text-slate-600">Scripts, strategies, and market data to maximize your compensation</p>
      </div>

      {!result ? (
        <div className="space-y-6">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="grid md:grid-cols-2 gap-6"
          >
            <div className="bg-white rounded-2xl border border-slate-200 p-6">
              <label className="block font-semibold text-slate-900 mb-2">Job Title *</label>
              <input
                type="text"
                value={jobTitle}
                onChange={(e) => setJobTitle(e.target.value)}
                placeholder="e.g., Senior Software Engineer"
                className="w-full p-3 border border-slate-300 rounded-xl focus:ring-2 focus:ring-primary-500"
              />
            </div>

            <div className="bg-white rounded-2xl border border-slate-200 p-6">
              <label className="block font-semibold text-slate-900 mb-2">Location</label>
              <input
                type="text"
                value={location}
                onChange={(e) => setLocation(e.target.value)}
                placeholder="e.g., San Francisco, CA"
                className="w-full p-3 border border-slate-300 rounded-xl focus:ring-2 focus:ring-primary-500"
              />
            </div>

            <div className="bg-white rounded-2xl border border-slate-200 p-6">
              <label className="block font-semibold text-slate-900 mb-2">Years of Experience</label>
              <input
                type="number"
                value={experience}
                onChange={(e) => setExperience(e.target.value)}
                placeholder="e.g., 5"
                className="w-full p-3 border border-slate-300 rounded-xl focus:ring-2 focus:ring-primary-500"
              />
            </div>

            <div className="bg-white rounded-2xl border border-slate-200 p-6">
              <label className="block font-semibold text-slate-900 mb-2">Current Salary (optional)</label>
              <input
                type="number"
                value={currentSalary}
                onChange={(e) => setCurrentSalary(e.target.value)}
                placeholder="e.g., 80000"
                className="w-full p-3 border border-slate-300 rounded-xl focus:ring-2 focus:ring-primary-500"
              />
            </div>

            <div className="bg-white rounded-2xl border border-slate-200 p-6">
              <label className="block font-semibold text-slate-900 mb-2">Offer Amount (if received)</label>
              <input
                type="number"
                value={offerAmount}
                onChange={(e) => setOfferAmount(e.target.value)}
                placeholder="e.g., 95000"
                className="w-full p-3 border border-slate-300 rounded-xl focus:ring-2 focus:ring-primary-500"
              />
            </div>
          </motion.div>

          <button
            onClick={generateScripts}
            disabled={loading || !jobTitle}
            className="w-full py-4 bg-gradient-to-r from-emerald-500 to-teal-600 text-white rounded-xl font-semibold hover:opacity-90 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
          >
            {loading ? (
              <>
                <RefreshCw className="w-5 h-5 animate-spin" />
                Generating scripts...
              </>
            ) : (
              <>
                <DollarSign className="w-5 h-5" />
                Generate Negotiation Scripts
              </>
            )}
          </button>
        </div>
      ) : (
        <>
          <div className="space-y-6">
            {/* Market Context */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="bg-gradient-to-r from-emerald-500 to-teal-600 text-white rounded-2xl p-6"
            >
              <div className="flex items-center gap-3 mb-4">
                <TrendingUp className="w-6 h-6" />
                <h2 className="text-xl font-bold">Market Context</h2>
              </div>
              
              <div className="grid md:grid-cols-3 gap-4">
                <div className="bg-white/10 rounded-xl p-4">
                  <p className="text-sm text-emerald-100">25th Percentile</p>
                  <p className="text-2xl font-bold">${result.marketContext?.salaryRange?.low?.toLocaleString()}</p>
                </div>
                
                <div className="bg-white/20 rounded-xl p-4">
                  <p className="text-sm text-emerald-100">Median</p>
                  <p className="text-2xl font-bold">${result.marketContext?.salaryRange?.median?.toLocaleString()}</p>
                </div>
                
                <div className="bg-white/10 rounded-xl p-4">
                  <p className="text-sm text-emerald-100">75th Percentile</p>
                  <p className="text-2xl font-bold">${result.marketContext?.salaryRange?.high?.toLocaleString()}</p>
                </div>
              </div>
            </motion.div>

            {/* Negotiation Scripts */}
            <div className="bg-white rounded-2xl border border-slate-200 overflow-hidden">
              <div className="flex border-b border-slate-200">
                {['scripts', 'scenarios', 'tactics'].map((tab) => (
                  <button
                    key={tab}
                    onClick={() => setActiveTab(tab)}
                    className={`px-6 py-4 font-medium capitalize transition-colors
                      ${activeTab === tab 
                        ? 'text-emerald-600 border-b-2 border-emerald-600' 
                        : 'text-slate-500 hover:text-slate-700'}
                    `}
                  >
                    {tab}
                  </button>
                ))}
              </div>

              <div className="p-6">
                {activeTab === 'scripts' && (
                  <div className="space-y-6">
                    {/* Counter Offer Email */}
                    <div className="bg-slate-50 rounded-xl p-4">
                      <div className="flex items-center justify-between mb-3">
                        <div className="flex items-center gap-2">
                          <MessageCircle className="w-5 h-5 text-primary-600" />
                          <h4 className="font-semibold">Counter Offer Email</h4>
                        </div>
                        
                        <button
                          onClick={() => {
                            navigator.clipboard.writeText(result.scripts?.initialCounter?.email);
                            toast.success('Copied!');
                          }}
                          className="p-2 text-slate-500 hover:bg-slate-200 rounded-lg"
                        >
                          <Copy className="w-4 h-4" />
                        </button>
                      </div>
                      
                      <div className="bg-white rounded-lg p-4 text-slate-700 whitespace-pre-wrap text-sm">
                        {result.scripts?.initialCounter?.email}
                      </div>
                    </div>

                    {/* Phone Script */}
                    <div className="bg-slate-50 rounded-xl p-4">
                      <div className="flex items-center justify-between mb-3">
                        <div className="flex items-center gap-2">
                          <MessageCircle className="w-5 h-5 text-primary-600" />
                          <h4 className="font-semibold">Phone Negotiation Script</h4>
                        </div>
                        
                        <button
                          onClick={() => {
                            navigator.clipboard.writeText(result.scripts?.initialCounter?.phone);
                            toast.success('Copied!');
                          }}
                          className="p-2 text-slate-500 hover:bg-slate-200 rounded-lg"
                        >
                          <Copy className="w-4 h-4" />
                        </button>
                      </div>
                      
                      <div className="bg-white rounded-lg p-4 text-slate-700 whitespace-pre-wrap text-sm">
                        {result.scripts?.initialCounter?.phone}
                      </div>
                    </div>
                  </div>
                )}

                {activeTab === 'scenarios' && (
                  <div className="space-y-4">
                    {Object.entries(result.scripts?.scenarios || {}).map(([key, scenario]) => (
                      <div key={key} className="border border-slate-200 rounded-xl overflow-hidden">
                        <button
                          onClick={() => toggleScenario(key)}
                          className="w-full flex items-center justify-between p-4 hover:bg-slate-50"
                        >
                          <span className="font-semibold capitalize">{key.replace(/([A-Z])/g, ' $1').trim()}</span>
                          
                          <{expandedScenarios[key] ? <ChevronUp className="w-5 h-5" /> : <ChevronDown className="w-5 h-5" />}
                        </button>

                        <{expandedScenarios[key] && (
                          <div className="p-4 border-t border-slate-200 bg-slate-50">
                            <p className="font-medium mb-2">{scenario.approach}</p>
                            
                            <div className="bg-white rounded-lg p-3 text-sm text-slate-700 whitespace-pre-wrap">
                              {scenario.script}
                            </div>
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                )}

                {activeTab === 'tactics' && (
                  <div className="space-y-4">
                    {Object.entries(result.tactics || {}).map(([key, tactic]) => (
                      <div key={key} className="bg-amber-50 rounded-xl p-4 border border-amber-200">
                        <h4 className="font-semibold text-amber-900 capitalize mb-2">{key}</h4>
                        
                        <p className="text-amber-800 mb-2">{tactic.description}</p>
                        
                        <{key === 'anchoring' && tactic.script && (
                          <div className="bg-white rounded-lg p-3 text-sm">
                            {tactic.script}
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>

            <div className="flex gap-4">
              <button
                onClick={() => setResult(null)}
                className="px-6 py-3 bg-slate-200 text-slate-700 rounded-xl font-medium hover:bg-slate-300"
              >
                New Negotiation
              </button>
            </div>
          </>
        )}
    </div>
  );
}

export default SalaryNegotiation;
