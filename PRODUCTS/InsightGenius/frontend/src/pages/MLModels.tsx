import { useEffect, useState } from 'react'
import { mlService } from '../services/mlService'
import { 
  PlusIcon, 
  SparklesIcon, 
  PlayIcon,
  CheckCircleIcon,
  XCircleIcon,
  ClockIcon,
  ArrowPathIcon
} from '@heroicons/react/24/outline'
import toast from 'react-hot-toast'

interface MLModel {
  id: number
  name: string
  model_type: string
  status: 'pending' | 'training' | 'ready' | 'failed'
  training_metrics?: any
  last_trained_at?: string
}

const modelTypeColors: Record<string, string> = {
  timeseries_forecast: 'bg-blue-500/20 text-blue-400',
  classification: 'bg-green-500/20 text-green-400',
  regression: 'bg-purple-500/20 text-purple-400',
  anomaly_detection: 'bg-red-500/20 text-red-400',
  clustering: 'bg-yellow-500/20 text-yellow-400',
}

const statusIcons: Record<string, JSX.Element> = {
  ready: <CheckCircleIcon className="w-5 h-5 text-green-500" />,
  failed: <XCircleIcon className="w-5 h-5 text-red-500" />,
  pending: <ClockIcon className="w-5 h-5 text-yellow-500" />,
  training: <ArrowPathIcon className="w-5 h-5 text-blue-500 animate-spin" />,
}

export default function MLModels() {
  const [models, setModels] = useState<MLModel[]>([])
  const [modelTypes, setModelTypes] = useState<any[]>([])
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    loadData()
  }, [])

  const loadData = async () => {
    try {
      const [modelsData, typesData] = await Promise.all([
        mlService.getModels(),
        mlService.getModelTypes()
      ])
      setModels(modelsData)
      setModelTypes(typesData)
    } catch (error) {
      toast.error('Failed to load ML models')
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white">ML Models</h1>
          <p className="text-gray-400">Train and manage machine learning models for predictions and insights</p>
        </div>
        
        <button className="flex items-center gap-2 bg-primary-600 hover:bg-primary-500 text-white px-4 py-2 rounded-lg font-medium"
        >
          <PlusIcon className="w-5 h-5" />
          New Model
        </button>
      </div>

      {/* Model Types */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {modelTypes.map((type) => (
          <div
            key={type.type}
            className="p-4 bg-dark-800 rounded-xl border border-dark-700 hover:border-primary-500/50 transition-all cursor-pointer group"
          >
            <div className="flex items-start justify-between mb-3">
              <div className={`px-3 py-1 rounded-full text-xs font-medium ${
                modelTypeColors[type.type] || 'bg-gray-500/20 text-gray-400'
              }`}>
                {type.type.replace(/_/g, ' ')}
              </div>
              <SparklesIcon className="w-5 h-5 text-gray-500 group-hover:text-primary-400" />
            </div>
            
            <h3 className="font-semibold text-white mb-1">{type.name}</h3>
            <p className="text-sm text-gray-400 mb-3">{type.description}</p>
            
            <div className="flex flex-wrap gap-1">
              {type.algorithms?.slice(0, 3).map((algo: string) => (
                <span key={algo} className="text-xs text-gray-500 bg-dark-700 px-2 py-0.5 rounded">
                  {algo}
                </span>
              ))}
            </div>
          </div>
        ))}
      </div>

      {/* Trained Models */}
      <div>
        <h2 className="text-lg font-semibold text-white mb-4">Your Models</h2>
        
        {isLoading ? (
          <div className="flex justify-center py-12">
            <div className="spinner"></div>
          </div>
        ) : models.length === 0 ? (
          <div className="text-center py-16 bg-dark-800 rounded-2xl border border-dark-700 border-dashed">
            <SparklesIcon className="w-16 h-16 text-gray-600 mx-auto mb-4" />
            <h3 className="text-lg font-semibold text-white mb-2">No models trained yet</h3>
            <p className="text-gray-400 mb-6">Create and train your first ML model</p>
            
            <button className="bg-primary-600 hover:bg-primary-500 text-white px-6 py-3 rounded-lg font-medium">
              Create Model
            </button>
          </div>
        ) : (
          <div className="space-y-3">
            {models.map((model) => (
              <div
                key={model.id}
                className="flex items-center p-4 bg-dark-800 rounded-xl border border-dark-700"
              >
                <div className="flex-1">
                  <div className="flex items-center gap-3">
                    <h3 className="font-semibold text-white">{model.name}</h3>
                    <span className={`px-2 py-0.5 rounded text-xs font-medium ${
                      modelTypeColors[model.model_type] || 'bg-gray-500/20 text-gray-400'
                    }`}>
                      {model.model_type.replace(/_/g, ' ')}
                    </span>
                  </div>
                  
                  <div className="flex items-center gap-4 mt-2 text-sm text-gray-400">
                    <span className="flex items-center gap-1">
                      {statusIcons[model.status]}
                      <span className="capitalize">{model.status}</span>
                    </span>
                    
                    {model.last_trained_at && (
                      <span>
                        Trained: {new Date(model.last_trained_at).toLocaleDateString()}
                      </span>
                    )}
                  </div>
                </div>
                
                <div className="flex items-center gap-2">
                  {model.status === 'ready' && (
                    <button className="flex items-center gap-1 px-3 py-1.5 bg-green-500/20 text-green-400 rounded-lg text-sm font-medium">
                      <PlayIcon className="w-4 h-4" />
                      Predict
                    </button>
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
    </div>
  )
}
