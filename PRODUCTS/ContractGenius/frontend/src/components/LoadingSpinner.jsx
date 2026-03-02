import React from 'react'
import { Loader2, FileText, Brain, Search, CheckCircle } from 'lucide-react'

const LoadingSpinner = ({ stage = 0 }) => {
  const stages = [
    { icon: FileText, text: 'Reading document...' },
    { icon: Brain, text: 'Analyzing with AI...' },
    { icon: Search, text: 'Identifying risks...' },
    { icon: CheckCircle, text: 'Finalizing report...' },
  ]

  return (
    <div className="flex flex-col items-center justify-center py-12">
      <div className="relative">
        <div className="w-20 h-20 border-4 border-primary-200 border-t-primary-600 rounded-full animate-spin"></div>
        <div className="absolute inset-0 flex items-center justify-center">
          {React.createElement(stages[stage]?.icon || FileText, {
            className: 'h-8 w-8 text-primary-600'
          })}
        </div>
      </div>
      
      <p className="mt-4 text-lg font-medium text-gray-700 animate-pulse">
        {stages[stage]?.text || 'Processing...'}
      </p>
      
      <div className="mt-6 flex space-x-2">
        {stages.map((_, index) => (
          <div
            key={index}
            className={`w-2 h-2 rounded-full transition-all duration-300 ${
              index <= stage ? 'bg-primary-600 w-6' : 'bg-gray-300'
            }`}
          />
        ))}
      </div>
    </div>
  )
}

export default LoadingSpinner