import { api } from './api'

export const nlpService = {
  async processQuery(query: string, datasetId?: number, dashboardId?: number) {
    const response = await api.post('/query/ask', null, {
      params: { 
        query, 
        dataset_id: datasetId, 
        dashboard_id: dashboardId 
      }
    })
    return response.data
  },

  async getSuggestions(datasetId: number) {
    const response = await api.post('/query/suggest', null, {
      params: { dataset_id: datasetId }
    })
    return response.data
  },

  async explainDataset(datasetId: number, question?: string) {
    const response = await api.post('/query/explain', null, {
      params: { dataset_id: datasetId, question }
    })
    return response.data
  },

  async generateAutoInsights(datasetId: number) {
    const response = await api.post('/query/insights/auto', null, {
      params: { dataset_id: datasetId }
    })
    return response.data
  },
}
