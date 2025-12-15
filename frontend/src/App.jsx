import { useState, useEffect, useMemo } from 'react'
import Sidebar from './components/Sidebar'
import Dashboard from './components/Dashboard'
import ToastContainer from './components/ToastContainer'
import LoginForm from './components/LoginForm'
import { authAPI, jobsAPI, scoringAPI } from './services/api'
import './App.css'

// Version check - if you see this in console, new code is loaded
console.log('🚀 RecroAI Frontend v2.0 - Connected to Backend API')

function App() {
  const [candidates, setCandidates] = useState([])
  const [jobs, setJobs] = useState([])
  const [selectedJob, setSelectedJob] = useState(null)
  const [loading, setLoading] = useState(true)
  const [filters, setFilters] = useState({
    university: null,
    universityMatchType: 'exact',
    company: null,
    minExperience: null,
  })
  const [toasts, setToasts] = useState([])
  const [isAuthenticated, setIsAuthenticated] = useState(false)
  const [isLoadingAuth, setIsLoadingAuth] = useState(true)

  const addToast = (message, type = 'error', duration = 5000) => {
    const id = Date.now() + Math.random()
    setToasts((prev) => [...prev, { id, message, type, duration }])
  }

  const removeToast = (id) => {
    setToasts((prev) => prev.filter((toast) => toast.id !== id))
  }

  // Check authentication on mount
  useEffect(() => {
    checkAuth()
  }, [])

  const checkAuth = async () => {
    const token = localStorage.getItem('auth_token')
    if (token) {
      try {
        await authAPI.getCurrentUser()
        setIsAuthenticated(true)
      } catch (error) {
        console.error('Auth check failed:', error)
        localStorage.removeItem('auth_token')
        setIsAuthenticated(false)
      }
    } else {
      setIsAuthenticated(false)
    }
    setIsLoadingAuth(false)
  }

  const handleLogin = async (username, password) => {
    try {
      await authAPI.login(username, password)
      setIsAuthenticated(true)
      addToast('Login successful', 'success')
      await fetchJobs()
    } catch (error) {
      addToast(error.response?.data?.detail || 'Login failed. Please check your credentials.', 'error')
      throw error
    }
  }

  useEffect(() => {
    // Fetch jobs when authenticated
    if (isAuthenticated) {
      fetchJobs()
    }
  }, [isAuthenticated])

  useEffect(() => {
    if (selectedJob) {
      fetchCandidatesForJob(selectedJob.id)
    }
  }, [selectedJob])

  const fetchJobs = async () => {
    try {
      setLoading(true)
      console.log('🔵 Fetching jobs from API...')
      const jobsData = await jobsAPI.getJobs()
      console.log('✅ Jobs received:', jobsData)
      setJobs(jobsData)
      if (jobsData.length > 0) {
        setSelectedJob(jobsData[0])
      } else {
        addToast('No jobs found. Create a job first via the API.', 'info', 8000)
      }
      setLoading(false)
    } catch (error) {
      console.error('❌ Error fetching jobs:', error)
      console.error('Error details:', error.response?.data)
      const errorMsg = error.response?.data?.detail || error.message || 'Failed to load jobs. Make sure the backend is running on http://localhost:8000'
      addToast(errorMsg, 'error')
      setLoading(false)
    }
  }

  const fetchCandidatesForJob = async (jobId) => {
    try {
      setLoading(true)
      console.log('🔵 Fetching candidates for job:', jobId)
      
      // Call the score-all endpoint which returns candidates with scores
      const response = await scoringAPI.scoreAll(jobId)
      console.log('✅ Candidates response:', response)
      
      // Transform the response to match our component structure
      const candidatesData = response.candidates.map(c => ({
        candidate_id: c.candidate_id,
        name: c.name,
        email: c.email,
        total_score: c.total_score,
        category_scores: c.category_scores,
        is_suspicious: c.is_suspicious,
        risk_score: c.risk_score,
        raw_profile: c.raw_profile || null, // Include raw_profile for filtering
      }))
      
      setCandidates(candidatesData)
      
      if (candidatesData.length === 0) {
        addToast('No candidates found. Upload candidates via CSV or LinkedIn first.', 'info', 8000)
      } else {
        addToast(`Loaded ${candidatesData.length} candidate(s)`, 'success', 3000)
      }
      
      setLoading(false)
    } catch (error) {
      console.error('❌ Error fetching candidates:', error)
      console.error('Error response:', error.response?.data)
      
      // If scoring fails (e.g., no candidates), try to get candidates without scores
      try {
        const { candidatesAPI } = await import('./services/api')
        const candidatesData = await candidatesAPI.getCandidates()
        
        if (candidatesData.length === 0) {
          addToast('No candidates found. Upload candidates via CSV or LinkedIn first.', 'info', 8000)
          setCandidates([])
        } else {
          // Include raw_profile from candidates
          const candidatesWithProfiles = candidatesData.map(c => ({
            candidate_id: c.id,
            name: c.name,
            email: c.email,
            total_score: null,
            category_scores: null,
            is_suspicious: null,
            risk_score: null,
            raw_profile: c.raw_profile || null,
          }))
          setCandidates(candidatesWithProfiles)
          addToast(`${candidatesData.length} candidate(s) found but not scored. Scoring will happen automatically.`, 'info', 6000)
        }
      } catch (fallbackError) {
        console.error('❌ Fallback error:', fallbackError)
        const errorMsg = error.response?.data?.detail || fallbackError.response?.data?.detail || 'Failed to load candidates. Please try again.'
        addToast(errorMsg, 'error')
        setCandidates([])
      }
      
      setLoading(false)
    }
  }

  const handleJobSelect = (job) => {
    setSelectedJob(job)
  }

  // Extract unique universities and companies from candidates
  const { universities, companies } = useMemo(() => {
    const uniSet = new Set()
    const compSet = new Set()

    candidates.forEach((candidate) => {
      try {
        const profile = typeof candidate.raw_profile === 'string' 
          ? JSON.parse(candidate.raw_profile) 
          : candidate.raw_profile

        // Extract university from education field
        if (profile.education) {
          const educationStr = typeof profile.education === 'string' 
            ? profile.education 
            : JSON.stringify(profile.education)
          
          // Try to extract university names (common patterns)
          const uniMatches = educationStr.match(/\b([A-Z][a-zA-Z\s&]+(?:University|College|Institute|School|Tech|MIT|Stanford|Harvard|Berkeley|CMU|Caltech))\b/g)
          if (uniMatches) {
            uniMatches.forEach(uni => uniSet.add(uni.trim()))
          }
          
          // Also add the full education string as a potential match
          if (educationStr.length < 100) {
            uniSet.add(educationStr.trim())
          }
        }

        // Extract companies from experience field
        if (profile.experience) {
          const experienceStr = typeof profile.experience === 'string' 
            ? profile.experience 
            : JSON.stringify(profile.experience)
          
          // Try to extract company names (common patterns)
          const companyMatches = experienceStr.match(/\bat\s+([A-Z][a-zA-Z0-9\s&.,-]+?)(?:\s|,|;|$)/g)
          if (companyMatches) {
            companyMatches.forEach(match => {
              const company = match.replace(/^at\s+/i, '').trim().replace(/[,;]$/, '')
              if (company.length > 2 && company.length < 50) {
                compSet.add(company)
              }
            })
          }
        }
      } catch (e) {
        // Skip if parsing fails
      }
    })

    return {
      universities: Array.from(uniSet).sort(),
      companies: Array.from(compSet).sort(),
    }
  }, [candidates])

  // Filter candidates based on active filters
  const filteredCandidates = useMemo(() => {
    return candidates.filter((candidate) => {
      try {
        const profile = typeof candidate.raw_profile === 'string' 
          ? JSON.parse(candidate.raw_profile) 
          : candidate.raw_profile

        // University filter
        if (filters.university) {
          const educationStr = typeof profile.education === 'string' 
            ? profile.education.toLowerCase()
            : JSON.stringify(profile.education).toLowerCase()
          
          const filterUni = filters.university.toLowerCase()
          
          if (filters.universityMatchType === 'exact') {
            if (!educationStr.includes(filterUni)) {
              return false
            }
          } else {
            // Close match: check for similar words or partial matches
            const filterWords = filterUni.split(/\s+/)
            const hasCloseMatch = filterWords.some(word => 
              word.length > 3 && educationStr.includes(word)
            )
            if (!hasCloseMatch && !educationStr.includes(filterUni)) {
              return false
            }
          }
        }

        // Company filter
        if (filters.company) {
          const experienceStr = typeof profile.experience === 'string' 
            ? profile.experience.toLowerCase()
            : JSON.stringify(profile.experience).toLowerCase()
          
          if (!experienceStr.includes(filters.company.toLowerCase())) {
            return false
          }
        }

        // Minimum experience filter
        if (filters.minExperience !== null) {
          const experienceStr = typeof profile.experience === 'string' 
            ? profile.experience
            : JSON.stringify(profile.experience)
          
          // Try to extract years of experience
          const yearMatches = experienceStr.match(/(\d+)\s*(?:years?|yrs?|yr)/gi)
          if (!yearMatches) {
            // If no explicit years, try to estimate from dates
            const dateMatches = experienceStr.match(/\d{4}/g)
            if (dateMatches && dateMatches.length >= 2) {
              const years = new Date().getFullYear() - Math.min(...dateMatches.map(d => parseInt(d)))
              if (years < filters.minExperience) {
                return false
              }
            } else {
              // Can't determine experience, exclude if filter is set
              return false
            }
          } else {
            const maxYears = Math.max(...yearMatches.map(m => parseInt(m.match(/\d+/)[0])))
            if (maxYears < filters.minExperience) {
              return false
            }
          }
        }

        return true
      } catch (e) {
        // If parsing fails, include candidate (don't filter out)
        return true
      }
    })
  }, [candidates, filters])

  // Show loading spinner while checking auth
  if (isLoadingAuth) {
    return (
      <div className="app-loading">
        <div className="loading-spinner"></div>
        <p>Checking authentication...</p>
      </div>
    )
  }

  // Show login form if not authenticated
  if (!isAuthenticated) {
    return (
      <>
        <LoginForm onLogin={handleLogin} />
        <ToastContainer toasts={toasts} onRemoveToast={removeToast} />
      </>
    )
  }

  // Show main app if authenticated
  return (
    <div className="app">
      <Sidebar 
        jobs={jobs} 
        selectedJob={selectedJob} 
        onJobSelect={handleJobSelect}
        loading={loading && jobs.length === 0}
      />
      <Dashboard 
        candidates={filteredCandidates} 
        allCandidates={candidates}
        selectedJob={selectedJob} 
        loading={loading}
        filters={filters}
        onFilterChange={setFilters}
        universities={universities}
        companies={companies}
      />
      <ToastContainer toasts={toasts} onRemoveToast={removeToast} />
    </div>
  )
}

export default App
