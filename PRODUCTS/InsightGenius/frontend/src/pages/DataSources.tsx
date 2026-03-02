import { useEffect } from 'react'
import { useDataStore } from '../stores/dataStore'
import { Link } from 'react-router-dom'
import { PlusIcon, CloudArrowUpIcon, CheckCircleIcon, XCircleIcon, ArrowPathIcon } from '@heroicons/react/24/outline'
import toast from 'react-hot-toast'

const sourceTypeIcons: Record<string, string> = {
  csv: '📄',
  excel: '📊',
  postgresql: '🐘',
  mysql: '🐬',
  api_rest: '🌐',
  snowflake: '❄️',
  bigquery: '🔍',
}

const sourceTypeNames: Record<string, string> = {
  csv: 'CSV File',
  excel: 'Excel File',
  postgresql: 'PostgreSQL',
  mysql: 'MySQL',
  api_rest: 'REST API',
  snowflake: 'Snowflake',
  bigquery: 'BigQuery',
}

const statusIcons: Record<string, JSX.Element> = {
  success: <CheckCircleIcon className="w-5 h-5 text-green-500" />,
  error: <XCircleIcon className="w-5 h-5 text-red-500" />,
  pending: <ArrowPathIcon className="w-5 h-5 text-yellow-500 animate-spin" />,
  syncing: <ArrowPathIcon className="w-5 h-5 text-blue-500 animate-spin" />,
}

export default function DataSources() {
  const { dataSources, fetchDataSources, isLoading } = useDataStore()

  useEffect(() => {
    fetchDataSources()
  }, [])

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white">Data Sources</h1>
          <p className="text-gray-400">Connect to databases, APIs, and file storage</p>
        </div>
        
        <Link
          to="/data-sources/new"
          className="flex items-center gap-2 bg-primary-600 hover:bg-primary-500 text-white px-4 py-2 rounded-lg font-medium"
        >
          <PlusIcon className="w-5 h-5" />
          Add Source
        </Link>
      </div>

      {/* Data Sources List */}
      {isLoading ? (
        <div className="flex justify-center py-12">
          <div className="spinner"></div>
        </div>
      ) : dataSources.length === 0 ? (
        <div className="text-center py-16 bg-dark-800 rounded-2xl border border-dark-700">
          <CloudArrowUpIcon className="w-16 h-16 text-gray-600 mx-auto mb-4" />
          <h3 className="text-xl font-semibold text-white mb-2">No data sources</h3>
          <p className="text-gray-400 mb-6">Connect to your data to start visualizing</p>
          <Link
            to="/data-sources/new"
            className="bg-primary-600 hover:bg-primary-500 text-white px-6 py-3 rounded-lg font-medium"
          >
            Connect Data Source
          </Link>
        </div>
      ) : (
        <div className="space-y-4">
          {dataSources.map((source) => (
            <div
              key={source.id}
              className="flex items-center p-4 bg-dark-800 rounded-xl border border-dark-700"
            >
              <div className="text-3xl mr-4">
                {sourceTypeIcons[source.source_type] || '📦'}
              </div>
              
              <div className="flex-1">
                <h3 className="font-semibold text-white">{source.name}</h3>
                <p className="text-sm text-gray-400">
                  {sourceTypeNames[source.source_type] || source.source_type}
                </p>
              </div>
              
              <div className="flex items-center gap-4">
                <div className="flex items-center gap-2">
                  {statusIcons[source.sync_status] || statusIcons.pending}
                  <span className="text-sm text-gray-400 capitalize">{source.sync_status}</span>
                </div>
                
                {source.last_sync_at && (
                  <span className="text-sm text-gray-500">
                    Last sync: {new Date(source.last_sync_at).toLocaleString()}
                  </span>
                )}
                
                <button className="p-2 text-gray-400 hover:text-white">
                  <ArrowPathIcon className="w-5 h-5" />
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
