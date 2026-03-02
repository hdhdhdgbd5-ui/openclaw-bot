import React from 'react'
import { AlertTriangle, CheckCircle, AlertCircle } from 'lucide-react'

const RiskScore = ({ score }) => {
  const getRiskColor = () => {
    if (score <= 30) return 'text-green-500'
    if (score <= 50) return 'text-yellow-500'
    if (score <= 70) return 'text-orange-500'
    return 'text-red-500'
  }

  const getRiskBg = () => {
    if (score <= 30) return 'bg-green-500'
    if (score <= 50) return 'bg-yellow-500'
    if (score <= 70) return 'bg-orange-500'
    return 'bg-red-500'
  }

  const getRiskLabel = () => {
    if (score <= 30) return { text: 'Low Risk', color: 'text-green-700', bg: 'bg-green-100' }
    if (score <= 50) return { text: 'Moderate Risk', color: 'text-yellow-700', bg: 'bg-yellow-100' }
    if (score <= 70) return { text: 'High Risk', color: 'text-orange-700', bg: 'bg-orange-100' }
    return { text: 'Critical Risk', color: 'text-red-700', bg: 'bg-red-100' }
  }

  const getRiskIcon = () => {
    if (score <= 30) return <CheckCircle className="h-6 w-6 text-green-500" />
    if (score <= 50) return <AlertCircle className="h-6 w-6 text-yellow-500" />
    return <AlertTriangle className="h-6 w-6 text-red-500" />
  }

  const riskLabel = getRiskLabel()
  const circumference = 2 * Math.PI * 40
  const strokeDashoffset = circumference - (score / 100) * circumference

  return (
    <div className="card">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-gray-900">Risk Assessment</h3>
        {getRiskIcon()}
      </div>

      <div className="flex items-center justify-center mb-6">
        <div className="relative">
          {/* Circular Progress */}
          <svg className="transform -rotate-90 w-32 h-32">
            {/* Background circle */}
            <circle
              cx="64"
              cy="64"
              r="40"
              stroke="currentColor"
              strokeWidth="8"
              fill="transparent"
              className="text-gray-200"
            />
            {/* Progress circle */}
            <circle
              cx="64"
              cy="64"
              r="40"
              stroke="currentColor"
              strokeWidth="8"
              fill="transparent"
              strokeDasharray={circumference}
              strokeDashoffset={strokeDashoffset}
              strokeLinecap="round"
              className={`${getRiskColor()} transition-all duration-1000 ease-out`}
            />
          </svg>
          
          {/* Score in center */}
          <div className="absolute inset-0 flex flex-col items-center justify-center">
            <span className={`text-3xl font-bold ${getRiskColor()}`}>{score}</span>
            <span className="text-xs text-gray-500">/100</span>
          </div>
        </div>
      </div>

      <div className="text-center">
        <span className={`inline-flex items-center px-4 py-2 rounded-full text-sm font-semibold ${riskLabel.bg} ${riskLabel.color}`}>
          {riskLabel.text}
        </span>
      </div>

      <div className="mt-4 text-center">
        <p className="text-sm text-gray-600">
          {score <= 30 && "This contract appears to be relatively safe with standard terms."}
          {score > 30 && score <= 50 && "Some clauses warrant careful review. Consider negotiating."}
          {score > 50 && score <= 70 && "Multiple concerning elements found. Professional review recommended."}
          {score > 70 && "Significant risks detected. Legal counsel strongly advised before signing."}
        </p>
      </div>
    </div>
  )
}

export default RiskScore