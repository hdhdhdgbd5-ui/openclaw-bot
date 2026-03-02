import React from 'react'
import { AlertTriangle, AlertCircle, Info } from 'lucide-react'

const Risks = ({ risks }) => {
  if (!risks || risks.length === 0) {
    return (
      <div className="text-gray-500 text-center py-4">
        No significant risks identified
      </div>
    )
  }

  const getSeverityIcon = (severity) => {
    switch (severity?.toLowerCase()) {
      case 'critical':
        return <AlertTriangle className="h-5 w-5 text-red-600" />
      case 'high':
        return <AlertTriangle className="h-5 w-5 text-orange-500" />
      case 'medium':
        return <AlertCircle className="h-5 w-5 text-yellow-500" />
      default:
        return <Info className="h-5 w-5 text-blue-500" />
    }
  }

  const getSeverityClass = (severity) => {
    switch (severity?.toLowerCase()) {
      case 'critical':
        return 'border-red-500 bg-red-50'
      case 'high':
        return 'border-orange-400 bg-orange-50'
      case 'medium':
        return 'border-yellow-400 bg-yellow-50'
      default:
        return 'border-blue-300 bg-blue-50'
    }
  }

  const getSeverityBadge = (severity) => {
    switch (severity?.toLowerCase()) {
      case 'critical':
        return 'risk-badge-critical'
      case 'high':
        return 'risk-badge-high'
      case 'medium':
        return 'risk-badge-medium'
      default:
        return 'risk-badge-low'
    }
  }

  return (
    <div className="space-y-4">
      {risks.map((risk, index) => (
        <div
          key={index}
          className={`rounded-lg p-4 border-l-4 ${getSeverityClass(risk.severity)}`}
        >
          <div className="flex items-start justify-between mb-2">
            <div className="flex items-center space-x-2">
              {getSeverityIcon(risk.severity)}
              <h3 className="font-semibold text-gray-900">{risk.risk}</h3>
            </div>
            <span className={getSeverityBadge(risk.severity)}>
              {risk.severity || 'Low'}
            </span>
          </div>
          
          <p className="text-gray-700 mb-3">{risk.explanation}</p>
          
          {risk.recommendation && (
            <div className="bg-white rounded p-3 border border-gray-200">
              <p className="text-sm font-medium text-gray-900 mb-1">Recommendation:</p>
              <p className="text-sm text-gray-700">{risk.recommendation}</p>
            </div>
          )}
        </div>
      ))}
    </div>
  )
}

export default Risks