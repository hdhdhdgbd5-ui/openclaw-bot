import { useEffect } from 'react'
import { useDashboardStore } from '../stores/dashboardStore'
import { Link } from 'react-router-dom'
import { PlusIcon, ChartBarIcon, ArrowRightIcon } from '@heroicons/react/24/outline'
import toast from 'react-hot-toast'

export default function Dashboards() {
  const { dashboards, fetchDashboards, createDashboard, isLoading } = useDashboardStore()

  useEffect(() => {
    fetchDashboards()
  }, [])

  const handleCreateDashboard = async () => {
    try {
      const newDashboard = await createDashboard({
        name: 'New Dashboard',
        description: '',
        layout: { type: 'grid', columns: 12, rowHeight: 80 },
        theme: 'dark'
      })
      toast.success('Dashboard created!')
      // Navigate to new dashboard
    } catch (error) {
      toast.error('Failed to create dashboard')
    }
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white">Dashboards</h1>
          <p className="text-gray-400">Manage and view your business intelligence dashboards</p>
        </div>
        
        <button
          onClick={handleCreateDashboard}
          className="flex items-center gap-2 bg-primary-600 hover:bg-primary-500 text-white px-4 py-2 rounded-lg font-medium transition-colors"
        >
          <PlusIcon className="w-5 h-5" />
          New Dashboard
        </button>
      </div>

      {/* Dashboards Grid */}
      {isLoading ? (
        <div className="flex justify-center py-12">
          <div className="spinner"></div>
        </div>
      ) : dashboards.length === 0 ? (
        <div className="text-center py-16 bg-dark-800 rounded-2xl border border-dark-700">
          <ChartBarIcon className="w-16 h-16 text-gray-600 mx-auto mb-4" />
          <h3 className="text-xl font-semibold text-white mb-2">No dashboards yet</h3>
          <p className="text-gray-400 mb-6">Create your first dashboard to visualize your data</p>
          <button
            onClick={handleCreateDashboard}
            className="bg-primary-600 hover:bg-primary-500 text-white px-6 py-3 rounded-lg font-medium"
          >
            Create Dashboard
          </button>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {dashboards.map((dashboard) => (
            <Link
              key={dashboard.id}
              to={`/dashboard/${dashboard.id}`}
              className="group p-6 bg-dark-800 rounded-xl border border-dark-700 card-hover"
            >
              <div className="flex items-start justify-between mb-4">
                <div className="w-12 h-12 rounded-lg bg-gradient-to-br from-primary-500/20 to-accent-purple/20 flex items-center justify-center">
                  <ChartBarIcon className="w-6 h-6 text-primary-400" />
                </div>
                <ArrowRightIcon className="w-5 h-5 text-gray-500 group-hover:text-white transition-colors" />
              </div>
              
              <h3 className="text-lg font-semibold text-white mb-1">{dashboard.name}</h3>
              {dashboard.description && (
                <p className="text-sm text-gray-400 mb-4 line-clamp-2">{dashboard.description}</p>
              )}
              
              <div className="flex items-center gap-4 text-sm text-gray-500">
                <span>{dashboard.widgets?.length || 0} widgets</span>
                <span>•</span>
                <span className="capitalize">{dashboard.theme} theme</span>
              </div>
            </Link>
          ))}
        </div>
      )}
    </div>
  )
}
