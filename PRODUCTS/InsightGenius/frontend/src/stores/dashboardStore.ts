import { create } from 'zustand'
import { api } from '../services/api'

interface Widget {
  id: string
  type: string
  title: string
  x: number
  y: number
  w: number
  h: number
  config: any
  datasetId?: number
  visualizationId?: number
}

interface Dashboard {
  id: number
  name: string
  description?: string
  layout: any
  theme: string
  widgets: Widget[]
  globalFilters: any[]
}

interface DashboardState {
  dashboards: Dashboard[]
  currentDashboard: Dashboard | null
  isLoading: boolean
  
  fetchDashboards: () => Promise<void>
  fetchDashboard: (id: number) => Promise<void>
  createDashboard: (data: Partial<Dashboard>) => Promise<Dashboard>
  updateDashboard: (id: number, data: Partial<Dashboard>) => Promise<void>
  deleteDashboard: (id: number) => Promise<void>
  addWidget: (dashboardId: number, widget: Partial<Widget>) => Promise<void>
  updateWidget: (dashboardId: number, widgetId: string, data: Partial<Widget>) => Promise<void>
  removeWidget: (dashboardId: number, widgetId: string) => Promise<void>
  setCurrentDashboard: (dashboard: Dashboard | null) => void
}

export const useDashboardStore = create<DashboardState>((set, get) => ({
  dashboards: [],
  currentDashboard: null,
  isLoading: false,

  fetchDashboards: async () => {
    set({ isLoading: true })
    try {
      const response = await api.get('/dashboards/')
      set({ dashboards: response.data })
    } finally {
      set({ isLoading: false })
    }
  },

  fetchDashboard: async (id: number) => {
    set({ isLoading: true })
    try {
      const response = await api.get(`/dashboards/${id}`)
      set({ currentDashboard: response.data })
    } finally {
      set({ isLoading: false })
    }
  },

  createDashboard: async (data) => {
    const response = await api.post('/dashboards/', data)
    const newDashboard = response.data
    set({ dashboards: [...get().dashboards, newDashboard] })
    return newDashboard
  },

  updateDashboard: async (id, data) => {
    await api.patch(`/dashboards/${id}`, data)
    await get().fetchDashboards()
    if (get().currentDashboard?.id === id) {
      await get().fetchDashboard(id)
    }
  },

  deleteDashboard: async (id) => {
    await api.delete(`/dashboards/${id}`)
    set({ 
      dashboards: get().dashboards.filter(d => d.id !== id),
      currentDashboard: get().currentDashboard?.id === id ? null : get().currentDashboard
    })
  },

  addWidget: async (dashboardId, widget) => {
    await api.post(`/dashboards/${dashboardId}/widgets`, widget)
    await get().fetchDashboard(dashboardId)
  },

  updateWidget: async (dashboardId, widgetId, data) => {
    await api.patch(`/dashboards/${dashboardId}/widgets/${widgetId}`, data)
    await get().fetchDashboard(dashboardId)
  },

  removeWidget: async (dashboardId, widgetId) => {
    await api.delete(`/dashboards/${dashboardId}/widgets/${widgetId}`)
    await get().fetchDashboard(dashboardId)
  },

  setCurrentDashboard: (dashboard) => {
    set({ currentDashboard: dashboard })
  },
}))
