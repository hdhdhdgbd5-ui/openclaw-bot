import React from 'react'
import { DollarSign, Eye, FileText } from 'lucide-react'

const HiddenFees = ({ fees }) => {
  if (!fees || fees.length === 0) {
    return (
      <div className="bg-green-50 rounded-lg p-6 text-center">
        <Eye className="h-12 w-12 text-green-500 mx-auto mb-3" />
        <p className="text-green-800 font-medium">No hidden fees detected</p>
        <p className="text-green-600 text-sm mt-1">All fees appear to be clearly disclosed</p>
      </div>
    )
  }

  return (
    <div className="grid gap-4">
      {fees.map((fee, index) => (
        <div
          key={index}
          className="bg-amber-50 rounded-lg p-4 border border-amber-200"
        >
          <div className="flex items-start justify-between mb-3">
            <div className="flex items-center space-x-2">
              <div className="bg-amber-100 p-2 rounded-lg">
                <DollarSign className="h-5 w-5 text-amber-600" />
              </div>
              <h3 className="font-semibold text-amber-900">{fee.fee}</h3>
            </div>
            <span className="text-lg font-bold text-amber-700">{fee.amount}</span>
          </div>
          
          <div className="space-y-2">
            <div className="flex items-center space-x-2 text-sm">
              <FileText className="h-4 w-4 text-amber-600" />
              <span className="text-amber-800">Location: {fee.location_in_contract}</span>
            </div>
            
            <p className="text-amber-800 text-sm">{fee.impact}</p>
          </div>
        </div>
      ))}
    </div>
  )
}

export default HiddenFees