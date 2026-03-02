import React from 'react'
import { RotateCcw, AlertTriangle, Clock, Ban } from 'lucide-react'

const AutoRenewals = ({ renewals }) => {
  if (!renewals || renewals.length === 0) {
    return (
      <div className="bg-green-50 rounded-lg p-6 text-center">
        <RotateCcw className="h-12 w-12 text-green-500 mx-auto mb-3" />
        <p className="text-green-800 font-medium">No auto-renewal clauses detected</p>
        <p className="text-green-600 text-sm mt-1">Contract requires explicit renewal</p>
      </div>
    )
  }

  return (
    <div className="space-y-4">
      {renewals.map((renewal, index) => (
        <div
          key={index}
          className="bg-orange-50 rounded-lg p-4 border border-orange-200"
        >
          <div className="flex items-start space-x-3">
            <div className="bg-orange-100 p-2 rounded-lg">
              <RotateCcw className="h-5 w-5 text-orange-600" />
            </div>
            
            <div className="flex-grow">
              <div className="flex items-center justify-between mb-2">
                <h3 className="font-semibold text-orange-900">Auto-Renewal Detected</h3>
                <span className="px-2 py-1 bg-orange-200 text-orange-800 text-xs font-semibold rounded-full">
                  ⚠️ Watch Out
                </span>
              </div>
              
              {renewal.clause_location && (
                <p className="text-sm text-orange-700 mb-3">
                  <b>Location:</b> {renewal.clause_location}
                </p>
              )}
              
              <div className="grid gap-3">
                {renewal.renewal_terms && (
                  <div className="flex items-start space-x-2 bg-white rounded p-2">
                    <Clock className="h-4 w-4 text-orange-500 mt-0.5" />
                    <div>
                      <p className="text-sm font-medium text-gray-900">Renewal Terms:</p>
                      <p className="text-sm text-gray-700">{renewal.renewal_terms}</p>
                    </div>
                  </div>
                )}
                
                {renewal.cancellation_terms && (
                  <div className="flex items-start space-x-2 bg-white rounded p-2">
                    <Ban className="h-4 w-4 text-red-500 mt-0.5" />
                    <div>
                      <p className="text-sm font-medium text-gray-900">Cancellation Terms:</p>
                      <p className="text-sm text-gray-700">{renewal.cancellation_terms}</p>
                    </div>
                  </div>
                )}
              </div>
              
              {renewal.warning && (
                <div className="mt-3 p-3 bg-red-100 rounded border border-red-200 flex items-start space-x-2">
                  <AlertTriangle className="h-4 w-4 text-red-600 flex-shrink-0 mt-0.5" />
                  <p className="text-sm text-red-800">{renewal.warning}</p>
                </div>
              )}
            </div>
          </div>
        </div>
      ))}
    </div>
  )
}

export default AutoRenewals