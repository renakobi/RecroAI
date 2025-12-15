import { useState, useEffect } from 'react'
import Sidebar from './components/Sidebar'
import Dashboard from './components/Dashboard'
import './App.css'

function App() {
  const [candidates, setCandidates] = useState([])
  const [jobs, setJobs] = useState([])
  const [selectedJob, setSelectedJob] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    // Fetch jobs on mount
    fetchJobs()
  }, [])

  useEffect(() => {
    if (selectedJob) {
      fetchCandidatesForJob(selectedJob.id)
    }
  }, [selectedJob])

  const fetchJobs = async () => {
    try {
      // This would be replaced with actual API call
      // For now, using mock data
      setJobs([
        { id: 1, title: 'Senior Software Engineer', status: 'active' },
        { id: 2, title: 'Frontend Developer', status: 'active' },
      ])
      if (jobs.length > 0) {
        setSelectedJob(jobs[0])
      }
      setLoading(false)
    } catch (error) {
      console.error('Error fetching jobs:', error)
      setLoading(false)
    }
  }

  const fetchCandidatesForJob = async (jobId) => {
    try {
      setLoading(true)
      // This would be replaced with actual API call to /scoring/score-all
      // For now, using mock data
      const mockCandidates = [
        {
          candidate_id: 1,
          name: 'John Doe',
          email: 'john@example.com',
          total_score: 92.5,
          category_scores: {
            'Technical Skills': { score: 95, reasoning: 'Strong Python and FastAPI' },
            'Experience': { score: 90, reasoning: '5 years relevant experience' },
            'Education': { score: 85, reasoning: 'BS Computer Science' },
          },
          is_suspicious: false,
          risk_score: 0.1,
        },
        {
          candidate_id: 2,
          name: 'Jane Smith',
          email: 'jane@example.com',
          total_score: 78.0,
          category_scores: {
            'Technical Skills': { score: 80, reasoning: 'Good React skills' },
            'Experience': { score: 75, reasoning: '3 years experience' },
            'Education': { score: 80, reasoning: 'MS Software Engineering' },
          },
          is_suspicious: true,
          risk_score: 0.65,
        },
        {
          candidate_id: 3,
          name: 'Bob Johnson',
          email: 'bob@example.com',
          total_score: 85.5,
          category_scores: {
            'Technical Skills': { score: 88, reasoning: 'Strong backend skills' },
            'Experience': { score: 85, reasoning: '4 years experience' },
            'Education': { score: 82, reasoning: 'BS Engineering' },
          },
          is_suspicious: false,
          risk_score: 0.2,
        },
      ]
      setCandidates(mockCandidates)
      setLoading(false)
    } catch (error) {
      console.error('Error fetching candidates:', error)
      setLoading(false)
    }
  }

  const handleJobSelect = (job) => {
    setSelectedJob(job)
  }

  return (
    <div className="app">
      <Sidebar jobs={jobs} selectedJob={selectedJob} onJobSelect={handleJobSelect} />
      <Dashboard candidates={candidates} selectedJob={selectedJob} loading={loading} />
    </div>
  )
}

export default App
