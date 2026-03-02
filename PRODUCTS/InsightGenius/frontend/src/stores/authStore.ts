import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import { api } from '../services/api'

interface User {
  id: number
  email: string
  full_name: string
  plan: string
}

interface AuthState {
  token: string | null
  user: User | null
  isAuthenticated: boolean
  isLoading: boolean
  
  login: (email: string, password: string) => Promise<void>
  register: (data: { email: string; password: string; full_name: string }) => Promise<void>
  logout: () => void
  setToken: (token: string) => void
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      token: null,
      user: null,
      isAuthenticated: false,
      isLoading: false,

      login: async (email: string, password: string) => {
        set({ isLoading: true })
        try {
          const response = await api.post('/auth/login', {
            username: email,
            password,
          })
          
          const { access_token, user } = response.data
          set({ token: access_token, user, isAuthenticated: true })
          api.defaults.headers.common['Authorization'] = `Bearer ${access_token}`
        } finally {
          set({ isLoading: false })
        }
      },

      register: async (data) => {
        set({ isLoading: true })
        try {
          const response = await api.post('/auth/register', data)
          const { access_token, user } = response.data
          set({ token: access_token, user, isAuthenticated: true })
          api.defaults.headers.common['Authorization'] = `Bearer ${access_token}`
        } finally {
          set({ isLoading: false })
        }
      },

      logout: () => {
        set({ token: null, user: null, isAuthenticated: false })
        delete api.defaults.headers.common['Authorization']
      },

      setToken: (token: string) => {
        set({ token, isAuthenticated: true })
        api.defaults.headers.common['Authorization'] = `Bearer ${token}`
      },
    }),
    {
      name: 'auth-storage',
    }
  )
)
