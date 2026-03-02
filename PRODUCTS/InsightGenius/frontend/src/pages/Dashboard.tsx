import { useEffect, useState } from 'react'
import { useParams } from 'react-router-dom'
import { useDashboardStore } from '../stores/dashboardStore'
import { Responsive, WidthProvider } from 'react-grid-layout'
import { PlusIcon, Cog6ToothIcon, ShareIcon, SparklesIcon } from '@heroicons/react/24/outline'
import 'react-grid-layout/css/styles.css'
import 'react-resizable/css/styles.css'

const ResponsiveGridLayout = WidthProvider(Responsive)

export default function Dashboard() {
  const { id } = useParams<{ id: string }>()
  const { currentDashboard, fetchDashboard, isLoading } = useDashboardStore()
  const [layouts, setLayouts] = useState({})
  const [showAddWidget, setShowAddWidget] = useState(false)

  useEffect(() => {
    if (id) {
      fetchDashboard(Number(id))
    }
  }, [id])

  if (isLoading) {
    return (
      <div className="flex justify-center py-12">
        <div className="spinner"></div>
      </div>
    )
  }

  if (!currentDashboard) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-400">Dashboard not found</p>
      </div>
    )
  }

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white">{currentDashboard.name}</h1>
          {currentDashboard.description && (
            <p className="text-gray-400">{currentDashboard.description}</p>
          )}
        </div>
        
        <div className="flex items-center gap-2">
          <button
            onClick={() => setShowAddWidget(true)}
            className="flex items-center gap-2 bg-primary-600 hover:bg-primary-500 text-white px-4 py-2 rounded-lg font-medium"
          >
            <PlusIcon className="w-5 h-5" />
            Add Widget
          </button>
          
          <button className="p-2 text-gray-400 hover:text-white">
            <SparklesIcon className="w-5 h-5" />
          </button>
          
          <button className="p-2 text-gray-400 hover:text-white">
            <ShareIcon className="w-5 h-5" />
          </button>
          
          <button className="p-2 text-gray-400 hover:text-white">
            <Cog6ToothIcon className="w-5 h-5" />
          </button>
        </div>
      </div>

      {/* Grid Layout */}
      <div className="bg-dark-800/50 rounded-xl p-4 min-h-[600px]">
        {currentDashboard.widgets?.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-96 text-center">
            <div className="w-16 h-16 rounded-xl bg-dark-700 flex items-center justify-center mb-4">
              <PlusIcon className="w-8 h-8 text-gray-500" />
            </div>
            <h3 className="text-lg font-semibold text-white mb-2">Start building your dashboard</h3>
            <p className="text-gray-400 mb-4">Add charts, metrics, and tables to visualize your data</p>
            <button
              onClick={() => setShowAddWidget(true)}
              className="bg-primary-600 hover:bg-primary-500 text-white px-4 py-2 rounded-lg font-medium"
            >
              Add Your First Widget
            </button>
          </div>
        ) : (
          <ResponsiveGridLayout
            className="layout"
            layouts={layouts}
            breakpoints={{ lg: 1200, md: 996, sm: 768, xs: 480, xxs: 0 }}
            cols={{ lg: 12, md: 10, sm: 6, xs: 4, xxs: 2 }}
            rowHeight={80}
            isDraggable
            isResizable
          >
            {currentDashboard.widgets?.map((widget) => (
              <div 
                key={widget.id}
                className="bg-dark-800 rounded-lg border border-dark-700 p-4"
              >
                <div className="flex items-center justify-between mb-3">
                  <h4 className="font-medium text-white">{widget.title}</h4>
                  <span className="text-xs text-gray-500 uppercase">{widget.type}</span>
                </div>
                <div className="text-gray-400 text-sm">
                  Widget content will render here
                </div>
              </div>
            ))}
          </ResponsiveGridLayout>
        )}
      </div>
    </div>
  )
}
