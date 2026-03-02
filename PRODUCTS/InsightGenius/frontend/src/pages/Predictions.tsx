import { useState } from 'react'
import { mlService } from '../services/mlService'
import { 
  PlayIcon,
  ArrowPathIcon,
  ChartBarIcon,
  LightBulbIcon
} from '@heroicons/react/24/outline'
import toast from 'react-hot-toast'

export default function Predictions() {
  const [selectedModel, setSelectedModel] = useState('')
  const [inputData, setInputData] = useState('')
  const [prediction, setPrediction] = useState<any>(null)
  const [isLoading, setIsLoading] = useState(false)

  const handlePredict = async () => {
    if (!selectedModel || !inputData) {
      toast.error('Please select a model and enter input data')
      return
    }

    setIsLoading(true)
    try {
      const data = JSON.parse(inputData)
      const result = await mlService.predict(Number(selectedModel), data)
      setPrediction(result)
      toast.success('Prediction generated!')
    } catch (error) {
      toast.error('Failed to generate prediction')
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white">Predictions</h1>
          <p className="text-gray-400">Make predictions using your trained ML models</p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Input Section */}
        <div className="p-6 bg-dark-800 rounded-xl border border-dark-700">
          <h2 className="text-lg font-semibold text-white mb-4">New Prediction</h2>
          
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">Select Model</label>
              <select
                value={selectedModel}
                onChange={(e) => setSelectedModel(e.target.value)}
                className="w-full px-4 py-2 bg-dark-900 border border-dark-700 rounded-lg text-white"
              >
                <option value="">Choose a model...</option>
                <option value="1">Sales Forecasting Model</option>
                <option value="2">Customer Churn Predictor</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">Input Data (JSON)</label>
              <textarea
                value={inputData}
                onChange={(e) => setInputData(e.target.value)}
                rows={8}
                className="w-full px-4 py-2 bg-dark-900 border border-dark-700 rounded-lg text-white font-mono text-sm"
                placeholder={`{\n  "feature1": 123,\n  "feature2": 456\n}`}
              />
            </div>

            <button
              onClick={handlePredict}
              disabled={isLoading}
              className="w-full flex items-center justify-center gap-2 bg-primary-600 hover:bg-primary-500 disabled:bg-primary-600/50 text-white py-3 rounded-lg font-medium"
            >
              {isLoading ? (
                <>
                  <ArrowPathIcon className="w-5 h-5 animate-spin" />
                  Processing...
                </>
              ) : (
                <>
                  <PlayIcon className="w-5 h-5" />
                  Generate Prediction
                </>
              )}
            </button>
          </div>
        </div>

        {/* Results Section */}
        <div className="p-6 bg-dark-800 rounded-xl border border-dark-700">
          <h2 className="text-lg font-semibold text-white mb-4">Prediction Result</h2>
          
          {prediction ? (
            <div className="space-y-4">
              <div className="p-4 bg-dark-900 rounded-lg">
                <div className="text-sm text-gray-400 mb-1">Predicted Value</div>
                <div className="text-3xl font-bold text-white">
                  {prediction.prediction?.toFixed(2)}
                </div>
              </div>

              {prediction.prediction_interval && (
                <div className="p-4 bg-dark-900 rounded-lg">
                  <div className="text-sm text-gray-400 mb-2">Confidence Interval</div>
                  <div className="flex items-center gap-4">
                    <div className="flex-1 h-2 bg-dark-700 rounded-full overflow-hidden">
                      <div className="h-full bg-primary-500 rounded-full" style={{ width: '60%' }}></div>
                    </div>
                  </div>
                  <div className="flex justify-between text-sm text-gray-400 mt-1">
                    <span>{prediction.prediction_interval.lower?.toFixed(2)}</span>
                    <span>{prediction.prediction_interval.upper?.toFixed(2)}</span>
                  </div>
                </div>
              )}

              <div className="p-4 bg-dark-900 rounded-lg">
                <div className="text-sm text-gray-400 mb-1">Confidence</div>
                <div className="text-lg text-white">High</div>
              </div>
            </div>
          ) : (
            <div className="flex flex-col items-center justify-center h-64 text-center">
              <LightBulbIcon className="w-12 h-12 text-gray-600 mb-4" />
              <p className="text-gray-400">
                Select a model and enter input data to generate a prediction
              </p>
            </div>
          )}
        </div>
      </div>

      {/* Recent Predictions */}
      <div className="p-6 bg-dark-800 rounded-xl border border-dark-700">
        <h2 className="text-lg font-semibold text-white mb-4">Recent Predictions</h2>
        
        <div className="text-center py-8">
          <ChartBarIcon className="w-12 h-12 text-gray-600 mx-auto mb-4" />
          <p className="text-gray-400">No predictions yet. Start by making your first prediction above.</p>
        </div>
      </div>
    </div>
  )
}
