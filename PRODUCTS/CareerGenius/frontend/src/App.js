import React from 'react';
import { Routes, Route } from 'react-router-dom';
import Layout from './components/Layout';
import Home from './pages/Home';
import ResumeAnalyzer from './pages/ResumeAnalyzer';
import JobMatcher from './pages/JobMatcher';
import CoverLetter from './pages/CoverLetter';
import LinkedInOptimizer from './pages/LinkedInOptimizer';
import InterviewPrep from './pages/InterviewPrep';
import SalaryNegotiation from './pages/SalaryNegotiation';
import ApplicationTracker from './pages/ApplicationTracker';
import Pricing from './pages/Pricing';
import './index.css';

function App() {
  return (
    <div className="min-h-screen bg-slate-50">
      <Routes>
        <Route path="/" element={<Layout />}>
          <Route index element={<Home />} />
          <Route path="resume-analyzer" element={<ResumeAnalyzer />} />
          <Route path="job-matcher" element={<JobMatcher />} />
          <Route path="cover-letter" element={<CoverLetter />} />
          <Route path="linkedin-optimizer" element={<LinkedInOptimizer />} />
          <Route path="interview-prep" element={<InterviewPrep />} />
          <Route path="salary-negotiation" element={<SalaryNegotiation />} />
          <Route path="application-tracker" element={<ApplicationTracker />} />
          <Route path="pricing" element={<Pricing />} />
        </Route>
      </Routes>
    </div>
  );
}

export default App;
