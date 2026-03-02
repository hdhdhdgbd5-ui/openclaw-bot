import { api } from './api'

export interface MLModel {
  id: number
  name: string
  model_type: string
  status: 'pending' | 'training' | 'ready' | 'failed'
  training_metrics?: any
  validation_metrics?: any
  feature_importance?: any
  last_trained_at?: string
}

export interface Prediction {
  prediction: number
  confidence?: number
  prediction_interval?: {
    lower: number
    upper: number
  }
}

export const mlService = {
  async getModelTypes() {
    const response = await api.get('/ml-models/types')
    return response.data
  },

  async getModels() {
    const response = await api.get('/ml-models/')
    return response.data
  },

  async getModel(id: number) {
    const response = await api.get(`/ml-models/${id}`)
    return response.data
  },

  async createModel(data: any) {
    const response = await api.post('/ml-models/', data)
    return response.data
  },

  async trainModel(id: number) {
    const response = await api.post(`/ml-models/${id}/train`)
    return response.data
  },

  async getTrainingStatus(id: number) {
    const response = await api.get(`/ml-models/${id}/status`)
    return response.data
  },

  async predict(modelId: number, inputData: any) {
    const response = await api.post(`/ml-models/${modelId}/predict`, inputData)
    return response.data
  },

  async batchPredict(modelId: number, inputDataList: any[]) {
    const response = await api.post(`/ml-models/${modelId}/batch-predict`, inputDataList)
    return response.data
  },

  async detectAnomalies(data: any) {
    const response = await api.post('/ml-models/anomaly/detect', data)
    return response.data
  },

  async getAnomalyHistory(datasetId: number) {
    const response = await api.get(`/ml-models/anomaly/history/${datasetId}`)
    return response.data
  },

  async autoRecommendModel(datasetId: number) {
    const response = await api.post('/ml-models/auto-recommend', { dataset_id: datasetId })
    return response.data
  },
}
