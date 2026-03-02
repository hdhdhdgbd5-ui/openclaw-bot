import React from 'react';
import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { 
  FileText, Briefcase, PenTool, Linkedin, 
  MessageSquare, DollarSign, LayoutDashboard,
  ArrowRight, CheckCircle2, Star
} from 'lucide-react';

const features = [
  {
    icon: FileText,
    title: 'Resume Analyzer',
    description: 'AI-powered ATS scoring and optimization suggestions',
    path: '/resume-analyzer',
    color: 'from-blue-500 to-cyan-500'
  },
  {
    icon: Briefcase,
    title: 'Job Matcher',
    description: 'Calculate your fit score for any job description',
    path: '/job-matcher',
    color: 'from-purple-500 to-pink-500'
  },
  {
    icon: PenTool,
    title: 'Cover Letters',
    description: 'Auto-generate tailored cover letters in seconds',
    path: '/cover-letter',
    color: 'from-amber-500 to-orange-500'
  },
  {
    icon: Linkedin,
    title: 'LinkedIn Optimizer',
    description: 'Optimize your profile for recruiters',
    path: '/linkedin-optimizer',
    color: 'from-blue-600 to-indigo-600'
  },
  {
    icon: MessageSquare,
    title: 'Interview Prep',
    description: 'AI-predicted questions with STAR format answers',
    path: '/interview-prep',
    color: 'from-emerald-500 to-teal-500'
  },
  {
    icon: DollarSign,
    title: 'Salary Negotiation',
    description: 'Scripts and strategies to maximize your offer',
    path: '/salary-negotiation',
    color: 'from-green-500 to-emerald-600'
  },
];

const testimonials = [
  {
    name: 'Sarah M.',
    role: 'Software Engineer',
    quote: 'Got 3 interviews in my first week using the optimized resume!',
    rating: 5
  },
  {
    name: 'James K.',
    role: 'Product Manager',
    quote: 'The salary negotiation scripts helped me get a 20% increase.',
    rating: 5
  },
  {
    name: 'Emily R.',
    role: 'Marketing Director',
    quote: 'Finally a tool that understands what recruiters want to see.',
    rating: 5
  }
];

const stats = [
  { value: '50K+', label: 'Resumes Optimized' },
  { value: '85%', label: 'Interview Rate' },
  { value: '$12K', label: 'Avg. Salary Increase' },
  { value: '4.9★', label: 'User Rating' }
];

function Home() {
  return (
    <div className="max-w-6xl mx-auto">
      {/* Hero Section */}
      <motion.div 
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="text-center py-12 lg:py-20"
      >
        <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-primary-50 text-primary-700 text-sm font-medium mb-6">
          <Star className="w-4 h-4 fill-current" />
          <span>Trusted by 50,000+ job seekers</span>
        </div>
        
        <h1 className="text-4xl lg:text-6xl font-bold text-slate-900 mb-6">
          Land Your Dream Job with{' '}
          <span className="text-transparent bg-clip-text bg-gradient-to-r from-primary-600 to-purple-600">
            AI-Powered Tools
          </span>
        </h1>
        
        <p className="text-xl text-slate-600 mb-8 max-w-2xl mx-auto">
          Upload your resume, match with jobs, generate cover letters, and prepare for interviews. 
          Everything you need to accelerate your career.
        </p>
        
        <div className="flex flex-col sm:flex-row gap-4 justify-center">
          <Link
            to="/resume-analyzer"
            className="inline-flex items-center justify-center gap-2 px-8 py-4 bg-primary-600 text-white rounded-xl font-semibold hover:bg-primary-700 transition-colors"
          >
            Analyze Your Resume
            <ArrowRight className="w-5 h-5" />
          </Link>
          <Link
            to="/job-matcher"
            className="inline-flex items-center justify-center gap-2 px-8 py-4 bg-white text-slate-700 border border-slate-300 rounded-xl font-semibold hover:bg-slate-50 transition-colors"
          >
            Check Job Fit
          </Link>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-8 mt-16">
          {stats.map((stat, index) => (
            <motion.div
              key={stat.label}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.1 }}
              className="text-center"
            >
              <div className="text-3xl lg:text-4xl font-bold text-slate-900">{stat.value}</div>
              <div className="text-sm text-slate-500">{stat.label}</div>
            </motion.div>
          ))}
        </div>
      </motion.div>

      {/* Features Grid */}
      <div className="py-12">
        <h2 className="text-2xl font-bold text-slate-900 text-center mb-12">
          All the Tools You Need
        </h2>
        
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
          {features.map((feature, index) => {
            const Icon = feature.icon;
            return (
              <motion.div
                key={feature.path}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.1 }}
              >
                <Link
                  to={feature.path}
                  className="group block p-6 bg-white rounded-2xl border border-slate-200 hover:border-primary-300 hover:shadow-lg transition-all duration-300"
                >
                  <div className={`w-12 h-12 rounded-xl bg-gradient-to-r ${feature.color} flex items-center justify-center mb-4 group-hover:scale-110 transition-transform`}>
                    <Icon className="w-6 h-6 text-white" />
                  </div>
                  <h3 className="text-lg font-semibold text-slate-900 mb-2">{feature.title}</h3>
                  <p className="text-slate-600">{feature.description}</p>
                  <div className="mt-4 flex items-center text-primary-600 font-medium">
                    Get Started
                    <ArrowRight className="w-4 h-4 ml-2 group-hover:translate-x-1 transition-transform" />
                  </div>
                </Link>
              </motion.div>
            );
          })}
        </div>
      </div>

      {/* Application Tracker CTA */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.5 }}
        className="py-12"
      >
        <Link
          to="/application-tracker"
          className="block p-8 bg-gradient-to-r from-slate-900 to-slate-800 rounded-2xl text-white"
        >
          <div className="flex flex-col md:flex-row items-center justify-between gap-6">
            <div className="flex items-center gap-4">
              <div className="w-16 h-16 rounded-xl bg-white/10 flex items-center justify-center">
                <LayoutDashboard className="w-8 h-8" />
              </div>
              <div>
                <h3 className="text-2xl font-bold mb-1">Application Tracker</h3>
                <p className="text-slate-300">Track all your job applications in one place with reminders and analytics</p>
              </div>
            </div>
            <button className="px-6 py-3 bg-white text-slate-900 rounded-xl font-semibold hover:bg-slate-100 transition-colors">
              Open Tracker
            </button>
          </div>
        </Link>
      </motion.div>

      {/* Testimonials */}
      <div className="py-12">
        <h2 className="text-2xl font-bold text-slate-900 text-center mb-12">
          Success Stories
        </h2>
        
        <div className="grid md:grid-cols-3 gap-6">
          {testimonials.map((testimonial, index) => (
            <motion.div
              key={testimonial.name}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.6 + index * 0.1 }}
              className="p-6 bg-white rounded-2xl border border-slate-200"
            >
              <div className="flex gap-1 mb-4">
                {[...Array(testimonial.rating)].map((_, i) => (
                  <Star key={i} className="w-5 h-5 text-amber-400 fill-current" />
                ))}
              </div>
              <p className="text-slate-700 mb-4 italic">"{testimonial.quote}"</p>
              <div>
                <p className="font-semibold text-slate-900">{testimonial.name}</p>
                <p className="text-sm text-slate-500">{testimonial.role}</p>
              </div>
            </motion.div>
          ))}
        </div>
      </div>
    </div>
  );
}

export default Home;
