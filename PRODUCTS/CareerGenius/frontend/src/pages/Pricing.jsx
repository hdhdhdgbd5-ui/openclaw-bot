import React from 'react';
import { motion } from 'framer-motion';
import { 
  Check, Sparkles, Crown, Zap, ArrowRight
} from 'lucide-react';

const plans = [
  {
    name: 'Free',
    price: '$0',
    period: 'forever',
    description: 'Try CareerGenius with basic features',
    icon: Sparkles,
    features: [
      '3 resume analyses per month',
      'Basic ATS scoring',
      'Job fit calculator (5 jobs)',
      'Basic cover letters',
      'Limited interview prep',
    ],
    cta: 'Get Started Free',
    popular: false,
  },
  {
    name: 'Pro',
    price: '$29',
    period: '/month',
    description: 'Everything you need to land your dream job',
    icon: Zap,
    features: [
      'Unlimited resume analyses',
      'Advanced ATS optimization',
      'Unlimited job matching',
      'AI cover letter generator',
      'LinkedIn profile optimizer',
      'Full interview prep with STAR answers',
      'Salary negotiation scripts',
      'Application tracker',
      'Priority support',
    ],
    cta: 'Start Pro Trial',
    popular: true,
  },
  {
    name: 'Premium',
    price: '$79',
    period: '/month',
    description: 'For serious job seekers and career changers',
    icon: Crown,
    features: [
      'Everything in Pro',
      '1-on-1 career coaching session',
      'Custom resume templates',
      'Executive networking strategies',
      'Recruiter outreach templates',
      'Market research reports',
      'White-glove support',
      'API access',
    ],
    cta: 'Go Premium',
    popular: false,
  },
];

const testimonials = [
  {
    quote: "CareerGenius helped me negotiate a $25K increase. The scripts were gold!",
    author: "Michael T.",
    role: "Senior Engineer",
    plan: "Pro"
  },
  {
    quote: "Went from 0 callbacks to 5 interviews in 2 weeks after using the resume optimizer.",
    author: "Jennifer L.",
    role: "Product Manager",
    plan: "Pro"
  },
  {
    quote: "The Premium coaching session alone was worth the price. Landed my dream role!",
    author: "David K.",
    role: "VP of Sales",
    plan: "Premium"
  }
];

function Pricing() {
  return (
    <div className="max-w-6xl mx-auto">
      <div className="text-center mb-12">
        <h1 className="text-4xl font-bold text-slate-900 mb-4">
          Invest in Your{' '}
          <span className="text-transparent bg-clip-text bg-gradient-to-r from-primary-600 to-purple-600">
            Career Success
          </span>
        </h1>
        <p className="text-xl text-slate-600 max-w-2xl mx-auto">
          Choose the plan that fits your job search needs. All plans include a 7-day free trial.
        </p>
      </div>

      {/* Pricing Cards */}
      <div className="grid md:grid-cols-3 gap-8 mb-16">
        {plans.map((plan, index) => {
          const Icon = plan.icon;
          return (
            <motion.div
              key={plan.name}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.1 }}
              className={`
                rounded-2xl p-8 relative
                ${plan.popular 
                  ? 'bg-gradient-to-b from-primary-600 to-purple-600 text-white scale-105 shadow-2xl' 
                  : 'bg-white border border-slate-200'}
              `}
            >
              <{plan.popular && (
                <div className="absolute -top-4 left-1/2 -translate-x-1/2">
                  <span className="px-4 py-1 bg-amber-400 text-amber-900 rounded-full text-sm font-bold">
                    MOST POPULAR
                  </span>
                </div>
              )}

              <div className="mb-6">
                <div className={`w-12 h-12 rounded-xl flex items-center justify-center mb-4
                  ${plan.popular ? 'bg-white/20' : 'bg-primary-100'}`}
                >
                  <Icon className={`w-6 h-6 ${plan.popular ? 'text-white' : 'text-primary-600'}`} />
                </div>
                
                <h3 className="text-2xl font-bold mb-2">{plan.name}</h3>
                <p className={plan.popular ? 'text-primary-100' : 'text-slate-500'}>
                  {plan.description}
                </p>
              </div>

              <div className="mb-6">
                <span className="text-4xl font-bold">{plan.price}</span>
                <span className={plan.popular ? 'text-primary-200' : 'text-slate-500'}>
                  {plan.period}
                </span>
              </div>

              <ul className="space-y-3 mb-8">
                {plan.features.map((feature, i) => (
                  <li key={i} className="flex items-start gap-3">
                    <Check className={`w-5 h-5 flex-shrink-0 mt-0.5 ${plan.popular ? 'text-primary-200' : 'text-emerald-500'}`} />
                    <span className={plan.popular ? '' : 'text-slate-600'}>{feature}</span>
                  </li>
                ))}
              </ul>

              <button
                className={`
                  w-full py-4 rounded-xl font-semibold flex items-center justify-center gap-2 transition-all
                  ${plan.popular 
                    ? 'bg-white text-primary-600 hover:bg-primary-50' 
                    : 'bg-primary-600 text-white hover:bg-primary-700'}
                `}
              >
                {plan.cta}
                <ArrowRight className="w-5 h-5" />
              </button>
            </motion.div>
          );
        })}
      </div>

      {/* Testimonials */}
      <div className="bg-slate-900 rounded-3xl p-12 text-white mb-16">
        <h2 className="text-3xl font-bold text-center mb-12">Success Stories</h2>
        
        <div className="grid md:grid-cols-3 gap-8">
          {testimonials.map((t, i) => (
            <motion.div
              key={i}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.3 + i * 0.1 }}
              className="bg-white/10 rounded-2xl p-6 backdrop-blur"
            >
              <p className="text-lg mb-4 italic">"{t.quote}"</p>
              
              <div className="flex items-center justify-between">
                <div>
                  <p className="font-semibold">{t.author}</p>
                  <p className="text-slate-400 text-sm">{t.role}</p>
                </div>
                
                <span className="px-3 py-1 bg-primary-500/30 rounded-full text-sm">
                  {t.plan}
                </span>
              </div>
            </motion.div>
          ))}
        </div>
      </div>

      {/* FAQ */}
      <div className="max-w-3xl mx-auto">
        <h2 className="text-2xl font-bold text-center mb-8">Frequently Asked Questions</h2>
        
        <div className="space-y-4">
          {[
            {
              q: "Can I cancel my subscription anytime?",
              a: "Yes, you can cancel at any time. Your access continues until the end of your billing period."
            },
            {
              q: "Is there a free trial?",
              a: "Yes! All paid plans include a 7-day free trial. No credit card required to start."
            },
            {
              q: "What if I'm not satisfied?",
              a: "We offer a 30-day money-back guarantee. If CareerGenius doesn't help, we'll refund you."
            },
            {
              q: "Can I switch plans?",
              a: "Absolutely. You can upgrade or downgrade your plan at any time."
            },
          ].map((faq, i) => (
            <div key={i} className="bg-white rounded-xl border border-slate-200 p-6">
              <h3 className="font-semibold text-slate-900 mb-2">{faq.q}</h3>
              <p className="text-slate-600">{faq.a}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

export default Pricing;
