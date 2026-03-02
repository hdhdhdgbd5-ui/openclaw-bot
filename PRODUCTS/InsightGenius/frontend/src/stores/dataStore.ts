import { create } from 'zustand'
import { api } from '../services/api'

interface Dataset {
  id: number
  name: string
  description?: string
  row_count: number
  columns: any[]
  processing_status: string
  created_at: string
}

interface DataSource {
  id: number
  name: string
  source_type: string
  sync_status: string
  last_sync_at?: string
}

interface DataState {
  datasets: Dataset[]
  dataSources: DataSource[]
  currentDataset: Dataset | null
  isLoading: boolean
  
  fetchDatasets: () => Promise<void>
  fetchDataSources: () => Promise<void>
  fetchDataset: (id: number) => Promise<void>
  createDataSource: (data: any) => Promise<void>
  uploadFile: (file: File, name: string) => Promise<void>
  createDataset: (data: any) => Promise<void>
  queryDataset: (id: number, sql: string) => Promise<any>
  getDatasetData: (id: number, params?: any) => Promise<any>
}

export const useDataStore = create<DataState>((set, get) => ({
  datasets: [],
  dataSources: [],
  currentDataset: null,
  isLoading: false,

  fetchDatasets: async () => {
    set({ isLoading: true })
    try {
      const response = await api.get('/datasets/')
      set({ datasets: response.data })
    } finally {
      set({ isLoading: false })
    }
  },

  fetchDataSources: async () => {
    set({ isLoading: true })
    try {
      const response = await api.get('/data-sources/')
      set({ dataSources: response.data })
    } finally {
      set({ isLoading: false })
    }
  },

  fetchDataset: async (id: number) => {
    set({ isLoading: true })
    try {
      const response = await api.get(`/datasets/${id}`)
      set({ currentDataset: response.data })
    } finally {
      set({ isLoading: false })
    }
  },

  createDataSource: async (data) => {
    await api.post('/data-sources/', data)
    await get().fetchDataSources()
  },

  uploadFile: async (file, name) => {
    const formData = new FormData()
    formData.append('file', file)
    formData.append('name', name)
    
    await api.post('/data-sources/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
    await get().fetchDataSources()
    await get().fetchDatasets()
  },

  createDataset: async (data) => {
    await api.post('/datasets/', data)
    await get().fetchDatasets()
  },

  queryDataset: async (id, sql) => {
    const response = await api.get(`/datasets/${id}/query`, {
      params: { sql }
    })
    return response.data
  },

  getDatasetData: async (id, params = {}) => {
    const response = await api.get(`/datasets/${id}/data`, { params })
    return response.data
  },
}))
