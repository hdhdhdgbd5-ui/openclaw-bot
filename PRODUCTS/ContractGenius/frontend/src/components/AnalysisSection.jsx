import React from 'react'
import { ChevronDown, ChevronUp } from 'lucide-react'

const AnalysisSection = ({ title, children, defaultOpen = true }) => {
  const [isOpen, setIsOpen] = React.useState(defaultOpen)

  return (
    <div className="card mb-6">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="w-full flex items-center justify-between text-left focus:outline-none"
      >
        <h2 className="section-title mb-0">{title}</h2>
        {isOpen ? (
          <ChevronUp className="h-6 w-6 text-gray-400" />
        ) : (
          <ChevronDown className="h-6 w-6 text-gray-400" />
        )}
      </button>
      
      {isOpen && (
        <div className="mt-4 animate-fade-in">
          {children}
        </div>
      )}
    </div>
  )
}

export default AnalysisSection