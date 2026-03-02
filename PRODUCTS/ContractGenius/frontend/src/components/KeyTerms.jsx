import React from 'react'
import { BookOpen } from 'lucide-react'

const KeyTerms = ({ terms }) => {
  if (!terms || terms.length === 0) {
    return (
      <div className="text-gray-500 text-center py-4">
        No key terms identified
      </div>
    )
  }

  const getImportanceColor = (importance) => {
    switch (importance?.toLowerCase()) {
      case 'high':
        return 'bg-red-100 text-red-800'
      case 'medium':
        return 'bg-yellow-100 text-yellow-800'
      case 'low':
        return 'bg-green-100 text-green-800'
      default:
        return 'bg-gray-100 text-gray-800'
    }
  }

  return (
    <div className="space-y-4">
      {terms.map((term, index) => (
        <div
          key={index}
          className="bg-gray-50 rounded-lg p-4 border border-gray-200 hover:shadow-md transition-shadow"
        >
          <div className="flex items-start justify-between mb-2">
            <div className="flex items-center space-x-2">
              <BookOpen className="h-5 w-5 text-primary-500" />
              <h3 className="font-semibold text-gray-900">{term.term}</h3>
            </div>
            <span className={`px-2 py-1 rounded-full text-xs font-medium ${getImportanceColor(term.importance)}`}>
              {term.importance || 'Medium'}
            </span>
          </div>
          
          {term.section && (
            <p className="text-sm text-gray-500 mb-2">
              Section: {term.section}
            </p>
          )}
          
          <p className="text-gray-700">{term.meaning}</p>
        </div>
      ))}
    </div>
  )
}

export default KeyTerms