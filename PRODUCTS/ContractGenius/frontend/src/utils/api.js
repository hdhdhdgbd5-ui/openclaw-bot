import axios from 'axios'

// API base URL - update this with your Render deployment URL
const API_BASE_URL = import.meta.env.VITE_API_URL || 'https://contractgenius-api.onrender.com'

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'multipart/form-data',
  },
})

// Upload and analyze contract
export const analyzeContract = async (file) => {
  const formData = new FormData()
  formData.append('file', file)
  
  const response = await api.post('/api/analyze', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  })
  return response.data
}

// Get contract by ID
export const getContract = async (contractId) => {
  const response = await api.get(`/api/contracts/${contractId}`)
  return response.data
}

// Chat with contract
export const chatWithContract = async (contractId, message, history = []) => {
  const response = await api.post('/api/chat', {
    contract_id: contractId,
    message,
    history,
  })
  return response.data
}

// Export PDF
export const exportPDF = (contractId) => {
  return `${API_BASE_URL}/api/contracts/${contractId}/export/pdf`
}

// Export JSON
export const exportJSON = async (contractId) => {
  const response = await api.get(`/api/contracts/${contractId}/export/json`)
  return response.data
}

// List contracts
export const listContracts = async () => {
  const response = await api.get('/api/contracts')
  return response.data
}

export default api