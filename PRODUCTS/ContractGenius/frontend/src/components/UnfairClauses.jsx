import React from 'react'
import { ShieldAlert, Lightbulb } from 'lucide-react'

const UnfairClauses = ({ clauses }) => {
  if (!clauses || clauses.length === 0) {
    return (
      <div className="bg-green-50 rounded-lg p-6 text-center">
        <ShieldAlert className="h-12 w-12 text-green-500 mx-auto mb-3" />
        <p className="text-green-800 font-medium">No unfair clauses detected</p>
        <p className="text-green-600 text-sm mt-1">This contract appears to have balanced terms</p>
      </div>
    )
  }

  return (
    <div className="space-y-4">
      {clauses.map((clause, index) => (
        <div
          key={index}
          className="bg-red-50 rounded-lg p-4 border border-red-200"
        >
          <div className="flex items-start space-x-3">
            <ShieldAlert className="h-5 w-5 text-red-500 flex-shrink-0 mt-0.5" />
            <div className="flex-grow">
              <h3 className="font-semibold text-red-900 mb-2">{clause.clause}</h3>
              
              <div className="bg-white rounded p-3 mb-3">
                <p className="text-sm text-gray-600 mb-1"><b>Why it's concerning:</b></p>
                <p className="text-gray-800">{clause.why_unfair}</p>
              </div>
              
              {clause.suggested_alternative && (
                <div className="bg-green-50 rounded p-3 border border-green-200">
                  <div className="flex items-start space-x-2">
                    <Lightbulb className="h-4 w-4 text-green-600 flex-shrink-0 mt-0.5" />
                    <div>
                      <p className="text-sm font-medium text-green-800 mb-1">Suggested Alternative:</p>
                      <p className="text-sm text-green-700">{clause.suggested_alternative}</p>
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      ))}
    </div>
  )
}

export default UnfairClauses