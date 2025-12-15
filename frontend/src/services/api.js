import axios from 'axios'

const API_BASE_URL = '/api'

// Create axios instance
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Add token to requests if available
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('auth_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Handle auth errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Clear token and redirect to login if needed
      localStorage.removeItem('auth_token')
    }
    return Promise.reject(error)
  }
)

export const authAPI = {
  login: async (username, password) => {
    const formData = new FormData()
    formData.append('username', username)
    formData.append('password', password)
    
    const response = await api.post('/auth/login', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })
    
    if (response.data.access_token) {
      localStorage.setItem('auth_token', response.data.access_token)
    }
    
    return response.data
  },
  
  register: async (email, username, password) => {
    const response = await api.post('/auth/register', {
      email,
      username,
      password,
    })
    return response.data
  },
  
  getCurrentUser: async () => {
    const response = await api.get('/auth/me')
    return response.data
  },
}

export const jobsAPI = {
  getJobs: async () => {
    const response = await api.get('/jobs/')
    return response.data
  },
  
  getJob: async (jobId) => {
    const response = await api.get(`/jobs/${jobId}`)
    return response.data
  },
}

export const candidatesAPI = {
  getCandidates: async () => {
    const response = await api.get('/candidates/')
    return response.data
  },
  
  getCandidate: async (candidateId) => {
    const response = await api.get(`/candidates/${candidateId}`)
    return response.data
  },
}

export const scoringAPI = {
  scoreAll: async (jobId) => {
    const response = await api.post('/scoring/score-all', {
      job_id: jobId,
    })
    return response.data
  },
  
  scoreCandidate: async (candidateId, jobId) => {
    const response = await api.post('/scoring/score', {
      candidate_id: candidateId,
      job_id: jobId,
    })
    return response.data
  },
}

export default api

