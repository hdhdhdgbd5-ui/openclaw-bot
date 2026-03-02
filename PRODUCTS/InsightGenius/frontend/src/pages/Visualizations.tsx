import { useState } from 'react'
import { Link } from 'react-router-dom'
import { 
  PlusIcon, 
  ChartBarIcon, 
  SparklesIcon,
  ArrowRightIcon,
  FunnelIcon
} from '@heroicons/react/24/outline'

const chartTypes = [
  { type: 'line', name: 'Line Chart', icon: '📈' },
  { type: 'bar', name: 'Bar Chart', icon: '📊' },
  { type: 'pie', name: 'Pie Chart', icon: '🥧' },
  { type: 'scatter', name: 'Scatter Plot', icon: '⚫' },
  { type: 'area', name: 'Area Chart', icon: '📉' },
  { type: 'heatmap', name: 'Heatmap', icon: '🔥' },
]

export default function Visualizations() {
  const [filter, setFilter] = useState('all')

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white">Visualizations</h1>
          <p className="text-gray-400">Create and manage charts, graphs, and visual representations</p>
        </div>
        
        <div className="flex items-center gap-2">
          <button className="flex items-center gap-2 px-4 py-2 text-gray-300 hover:text-white">
            <FunnelIcon className="w-5 h-5" />
            Filter
          </button>
          
          <button className="flex items-center gap-2 bg-accent-purple/20 hover:bg-accent-purple/30 text-accent-purple px-4 py-2 rounded-lg font-medium">
            <SparklesIcon className="w-5 h-5" />
            AI Generate
          </button>
          
          <button className="flex items-center gap-2 bg-primary-600 hover:bg-primary-500 text-white px-4 py-2 rounded-lg font-medium">
            <PlusIcon className="w-5 h-5" />
            New Chart
          </button>
        </div>
      </div>

      {/* Chart Types */}
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
        {chartTypes.map((chart) => (
          <button
            key={chart.type}
            className="p-4 bg-dark-800 rounded-xl border border-dark-700 hover:border-primary-500/50 transition-all text-center group"
          >
            <div className="text-4xl mb-2 group-hover:scale-110 transition-transform">{chart.icon}</div>
            <div className="text-sm font-medium text-white">{chart.name}</div>
          </button>
        ))}
      </div>

      {/* Recent Visualizations */}
      <div>
        <h2 className="text-lg font-semibold text-white mb-4">Recent Visualizations</h2>
        
        <div className="text-center py-16 bg-dark-800 rounded-2xl border border-dark-700 border-dashed">
          <ChartBarIcon className="w-16 h-16 text-gray-600 mx-auto mb-4" />
          <h3 className="text-lg font-semibold text-white mb-2">No visualizations yet</h3>
          <p className="text-gray-400 mb-6">Create your first chart or let AI generate them for you</p>
          
          <div className="flex gap-3 justify-center">
            <button className="flex items-center gap-2 bg-accent-purple/20 hover:bg-accent-purple/30 text-accent-purple px-4 py-2 rounded-lg font-medium">
              <SparklesIcon className="w-5 h-5" />
              Auto-Generate
            </button>
            
            <button className="flex items-center gap-2 bg-primary-600 hover:bg-primary-500 text-white px-4 py-2 rounded-lg font-medium">
              <PlusIcon className="w-5 h-5" />
              Create Manually
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}
