import { Link } from 'react-router-dom'
import { 
  ChartBarIcon, 
  SparklesIcon, 
  BellIcon, 
  DocumentTextIcon,
  CloudArrowUpIcon,
  ChatBubbleBottomCenterTextIcon,
  ArrowRightIcon,
  CheckIcon
} from '@heroicons/react/24/outline'

const features = [
  {
    name: 'Auto-Generated Visualizations',
    description: 'AI analyzes your data and suggests the best charts and graphs automatically.',
    icon: ChartBarIcon,
  },
  {
    name: 'ML-Powered Predictions',
    description: 'Forecast trends, detect anomalies, and get predictive insights with one click.',
    icon: SparklesIcon,
  },
  {
    name: 'Real-Time Alerts',
    description: 'Get notified instantly when metrics change or thresholds are breached.',
    icon: BellIcon,
  },
  {
    name: 'Automated Reports',
    description: 'Schedule and email PDF/PowerPoint reports to your team automatically.',
    icon: DocumentTextIcon,
  },
  {
    name: 'Connect Any Data Source',
    description: 'Import from CSV, Excel, SQL databases, APIs, Snowflake, BigQuery, and more.',
    icon: CloudArrowUpIcon,
  },
  {
    name: 'Natural Language Queries',
    description: 'Ask questions in plain English like "show me sales last quarter".',
    icon: ChatBubbleBottomCenterTextIcon,
  },
]

const pricingPlans = [
  {
    name: 'Starter',
    price: '$79',
    period: '/month',
    description: 'Perfect for small teams getting started',
    features: [
      'Up to 5 dashboards',
      '3 data sources',
      'Basic visualizations',
      'Email reports',
      'Community support',
    ],
    cta: 'Start Free Trial',
    popular: false,
  },
  {
    name: 'Professional',
    price: '$149',
    period: '/month',
    description: 'For growing businesses with advanced needs',
    features: [
      'Unlimited dashboards',
      'Unlimited data sources',
      'AI-powered predictions',
      'Anomaly detection',
      'Real-time alerts',
      'PDF & PowerPoint export',
      'Priority support',
    ],
    cta: 'Start Free Trial',
    popular: true,
  },
  {
    name: 'Enterprise',
    price: '$199',
    period: '/month',
    description: 'Full-featured for large organizations',
    features: [
      'Everything in Pro',
      'Custom ML models',
      'White-label reports',
      'SSO & advanced security',
      'Dedicated success manager',
      'SLA guarantee',
    ],
    cta: 'Contact Sales',
    popular: false,
  },
]

export default function Landing() {
  return (
    <div className="min-h-screen bg-dark-900">
      {/* Navigation */}
      <nav className="fixed w-full z-50 bg-dark-900/80 backdrop-blur-md border-b border-dark-700">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex items-center">
              <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-primary-500 to-accent-purple flex items-center justify-center">
                <svg className="w-6 h-6 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                </svg>
              </div>
              <span className="ml-3 text-xl font-bold text-white">InsightGenius</span>
            </div>
            <div className="flex items-center gap-4">
              <Link to="/login" className="text-gray-300 hover:text-white transition-colors">
                Sign in
              </Link>
              <Link 
                to="/register" 
                className="bg-primary-600 hover:bg-primary-500 text-white px-4 py-2 rounded-lg font-medium transition-colors"
              >
                Get Started
              </Link>
            </div>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <div className="relative pt-32 pb-20 lg:pt-40 lg:pb-32 overflow-hidden">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative">
          <div className="text-center max-w-3xl mx-auto">
            <h1 className="text-5xl md:text-6xl font-bold text-white mb-6">
              Business Intelligence
              <br />
              <span className="bg-gradient-to-r from-primary-400 to-accent-purple bg-clip-text text-transparent">
                Powered by AI
              </span>
            </h1>
            
            <p className="text-xl text-gray-400 mb-10">
              Connect your data, get instant visualizations, ML predictions, and automated insights. 
              The all-in-one platform that replaces Tableau and PowerBI at a fraction of the cost.
            </p>
            
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Link 
                to="/register"
                className="inline-flex items-center justify-center gap-2 bg-primary-600 hover:bg-primary-500 text-white px-8 py-4 rounded-xl font-semibold text-lg transition-all hover:scale-105"
              >
                Start Free 14-Day Trial
                <ArrowRightIcon className="w-5 h-5" />
              </Link>
              <a 
                href="#features"
                className="inline-flex items-center justify-center gap-2 bg-dark-800 hover:bg-dark-700 text-white px-8 py-4 rounded-xl font-semibold text-lg transition-all border border-dark-700"
              >
                See Features
              </a>
            </div>
            
            <p className="text-sm text-gray-500 mt-6">No credit card required. Cancel anytime.</p>
          </div>
        </div>
        
        {/* Background decoration */}
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[800px] h-[800px] bg-primary-500/10 rounded-full blur-3xl"></div>
      </div>

      {/* Features Section */}
      <div id="features" className="py-24 bg-dark-800/50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold text-white mb-4">
              Everything You Need
            </h2>
            <p className="text-xl text-gray-400">
              Powerful features to turn your data into actionable insights
            </p>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {features.map((feature) => (
              <div 
                key={feature.name}
                className="p-6 rounded-2xl bg-dark-800 border border-dark-700 card-hover"
              >
                <div className="w-12 h-12 rounded-xl bg-primary-500/10 flex items-center justify-center mb-4">
                  <feature.icon className="w-6 h-6 text-primary-400" />
                </div>
                <h3 className="text-lg font-semibold text-white mb-2">{feature.name}</h3>
                <p className="text-gray-400">{feature.description}</p>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Pricing Section */}
      <div className="py-24">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold text-white mb-4">
              Simple, Transparent Pricing
            </h2>
            <p className="text-xl text-gray-400">
              Choose the plan that fits your needs. All plans include a 14-day free trial.
            </p>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {pricingPlans.map((plan) => (
              <div 
                key={plan.name}
                className={`relative p-8 rounded-2xl border ${
                  plan.popular 
                    ? 'border-primary-500 bg-gradient-to-b from-primary-500/10 to-transparent' 
                    : 'border-dark-700 bg-dark-800'
                }`}
              >
                {plan.popular && (
                  <div className="absolute -top-4 left-1/2 -translate-x-1/2">
                    <span className="bg-primary-500 text-white px-4 py-1 rounded-full text-sm font-medium">
                      Most Popular
                    </span>
                  </div>
                )}
                
                <h3 className="text-xl font-semibold text-white mb-2">{plan.name}</h3>
                <p className="text-gray-400 text-sm mb-4">{plan.description}</p>
                
                <div className="mb-6">
                  <span className="text-4xl font-bold text-white">{plan.price}</span>
                  <span className="text-gray-400">{plan.period}</span>
                </div>
                
                <ul className="space-y-3 mb-8">
                  {plan.features.map((feature) => (
                    <li key={feature} className="flex items-center gap-3 text-gray-300">
                      <CheckIcon className="w-5 h-5 text-primary-500 flex-shrink-0" />
                      {feature}
                    </li>
                  ))}
                </ul>
                
                <Link
                  to="/register"
                  className={`block text-center py-3 rounded-xl font-semibold transition-colors ${
                    plan.popular
                      ? 'bg-primary-600 hover:bg-primary-500 text-white'
                      : 'bg-dark-700 hover:bg-dark-600 text-white'
                  }`}
                >
                  {plan.cta}
                </Link>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* CTA Section */}
      <div className="py-24 bg-gradient-to-r from-primary-600 to-accent-purple">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h2 className="text-3xl md:text-4xl font-bold text-white mb-6">
            Ready to Transform Your Data?
          </h2>
          
          <p className="text-xl text-white/90 mb-10">
            Join thousands of businesses using InsightGenius to make data-driven decisions.
          </p>
          
          <Link 
            to="/register"
            className="inline-flex items-center gap-2 bg-white text-primary-600 px-8 py-4 rounded-xl font-bold text-lg hover:bg-gray-100 transition-colors"
          >
            Get Started Free
            <ArrowRightIcon className="w-5 h-5" />
          </Link>
        </div>
      </div>

      {/* Footer */}
      <footer className="bg-dark-900 border-t border-dark-700 py-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex flex-col md:flex-row justify-between items-center">
            <div className="flex items-center mb-4 md:mb-0">
              <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-primary-500 to-accent-purple flex items-center justify-center">
                <svg className="w-4 h-4 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                </svg>
              </div>
              <span className="ml-2 font-semibold text-white">InsightGenius</span>
            </div>
            
            <p className="text-gray-500 text-sm">
              © 2024 InsightGenius. All rights reserved.
            </p>
          </div>
        </div>
      </footer>
    </div>
  )
}
