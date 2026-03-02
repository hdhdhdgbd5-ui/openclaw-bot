import { useEffect, useState } from 'react'
import { useDataStore } from '../stores/dataStore'
import { Link } from 'react-router-dom'
import { 
  PlusIcon, 
  CircleStackIcon, 
  ArrowRightIcon,
  TableCellsIcon,
  SparklesIcon
} from '@heroicons/react/24/outline'
import toast from 'react-hot-toast'

export default function Datasets() {
  const { datasets, fetchDatasets, isLoading } = useDataStore()
  const [showUploadModal, setShowUploadModal] = useState(false)

  useEffect(() => {
    fetchDatasets()
  }, [])

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white">Datasets</h1>
          <p className="text-gray-400">Manage your imported and connected data</p>
        </div>
        
        <button
          onClick={() => setShowUploadModal(true)}
          className="flex items-center gap-2 bg-primary-600 hover:bg-primary-500 text-white px-4 py-2 rounded-lg font-medium"
        >
          <PlusIcon className="w-5 h-5" />
          Import Data
        </button>
      </div>

      {/* Datasets Grid */}
      {isLoading ? (
        <div className="flex justify-center py-12">
          <div className="spinner"></div>
        </div>
      ) : datasets.length === 0 ? (
        <div className="text-center py-16 bg-dark-800 rounded-2xl border border-dark-700">
          <CircleStackIcon className="w-16 h-16 text-gray-600 mx-auto mb-4" />
          <h3 className="text-xl font-semibold text-white mb-2">No datasets yet</h3>
          <p className="text-gray-400 mb-6">Import your data from files or connect to a database</p>
          <button
            onClick={() => setShowUploadModal(true)}
            className="bg-primary-600 hover:bg-primary-500 text-white px-6 py-3 rounded-lg font-medium"
          >
            Import Data
          </button>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {datasets.map((dataset) => (
            <div
              key={dataset.id}
              className="p-6 bg-dark-800 rounded-xl border border-dark-700 card-hover"
            >
              <div className="flex items-start justify-between mb-4">
                <div className="w-12 h-12 rounded-lg bg-gradient-to-br from-accent-cyan/20 to-primary-500/20 flex items-center justify-center">
                  <TableCellsIcon className="w-6 h-6 text-accent-cyan" />
                </div>
                
                <div className="flex items-center gap-2">
                  <button className="p-1 text-gray-400 hover:text-white">
                    <SparklesIcon className="w-4 h-4" />
                  </button>
                  <Link 
                    to={`/datasets/${dataset.id}`}
                    className="p-1 text-gray-400 hover:text-white"
                  >
                    <ArrowRightIcon className="w-4 h-4" />
                  </Link>
                </div>
              </div>
              
              <h3 className="text-lg font-semibold text-white mb-1">{dataset.name}</h3>
              {dataset.description && (
                <p className="text-sm text-gray-400 mb-4 line-clamp-2">{dataset.description}</p>
              )}
              
              <div className="flex items-center gap-4 text-sm text-gray-500">
                <span>{dataset.row_count.toLocaleString()} rows</span>
                <span>•</span>
                <span className="capitalize">{dataset.processing_status}</span>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Upload Modal - Simplified */}
      {showUploadModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-dark-800 rounded-2xl p-6 w-full max-w-md">
            <h2 className="text-xl font-bold text-white mb-4">Import Data</h2>
            
            <div className="space-y-3">
              <button className="w-full p-4 bg-dark-700 hover:bg-dark-600 rounded-xl text-left transition-colors">
                <div className="font-medium text-white">Upload File</div>
                <div className="text-sm text-gray-400">CSV, Excel, or JSON files</div>
              </button>
              
              <button className="w-full p-4 bg-dark-700 hover:bg-dark-600 rounded-xl text-left transition-colors">
                <div className="font-medium text-white">Connect Database</div>
                <div className="text-sm text-gray-400">PostgreSQL, MySQL, Snowflake</div>
              </button>
              
              <button className="w-full p-4 bg-dark-700 hover:bg-dark-600 rounded-xl text-left transition-colors">
                <div className="font-medium text-white">Connect API</div>
                <div className="text-sm text-gray-400">REST or GraphQL endpoints</div>
              </button>
            </div>
            
            <button
              onClick={() => setShowUploadModal(false)}
              className="mt-6 w-full py-2 text-gray-400 hover:text-white"
            >
              Cancel
            </button>
          </div>
        </div>
      )}
    </div>
  )
}
