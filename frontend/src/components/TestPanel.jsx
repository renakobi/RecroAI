import { useState } from 'react'
import { candidatesAPI, scoringAPI, jobsAPI } from '../services/api'
import './TestPanel.css'

function TestPanel({ isOpen, onClose, selectedJob, onCandidateAdded, onScoringComplete, onJobCreated, addToast }) {
  const [activeTab, setActiveTab] = useState('job')
  const [loading, setLoading] = useState(false)
  
  // Candidate form state
  const [candidateForm, setCandidateForm] = useState({
    name: '',
    education: '',
    experience: '',
    skills: '',
    summary: ''
  })

  // Quick test candidate templates
  const quickCandidates = [
    {
      name: 'John Doe - Senior Developer',
      education: 'BS Computer Science, MIT, 2015',
      experience: '5 years at Google, 3 years at Microsoft. Full-stack development with Python, React, and AWS.',
      skills: 'Python, React, JavaScript, AWS, Docker, Kubernetes, SQL',
      summary: 'Experienced full-stack developer with strong background in cloud infrastructure and modern web frameworks.'
    },
    {
      name: 'Jane Smith - Data Scientist',
      education: 'MS Data Science, Stanford University, 2018',
      experience: '4 years at Amazon as Data Scientist. Built ML models for recommendation systems.',
      skills: 'Python, TensorFlow, PyTorch, SQL, Spark, Machine Learning, Statistics',
      summary: 'Data scientist specializing in machine learning and recommendation systems with production experience.'
    },
    {
      name: 'Bob Johnson - Junior Developer',
      education: 'BS Software Engineering, State University, 2022',
      experience: '1 year internship at startup. Worked on React frontend and Node.js backend.',
      skills: 'JavaScript, React, Node.js, HTML, CSS, Git',
      summary: 'Recent graduate with internship experience, eager to learn and contribute to development teams.'
    }
  ]

  const handleCreateCandidate = async () => {
    if (!candidateForm.name.trim()) {
      addToast('Please enter at least a name', 'error')
      return
    }

    setLoading(true)
    try {
      // Create a CSV-like structure and upload it
      const csvContent = `name,education,experience,skills,summary\n"${candidateForm.name}","${candidateForm.education}","${candidateForm.experience}","${candidateForm.skills}","${candidateForm.summary}"`
      const blob = new Blob([csvContent], { type: 'text/csv' })
      const file = new File([blob], 'test-candidate.csv', { type: 'text/csv' })
      
      const response = await candidatesAPI.uploadCSV(file)
      addToast(`Created candidate: ${candidateForm.name}`, 'success')
      
      // Reset form
      setCandidateForm({ name: '', education: '', experience: '', skills: '', summary: '' })
      
      // Refresh candidates
      if (onCandidateAdded) {
        onCandidateAdded()
      }
    } catch (error) {
      addToast(error.response?.data?.detail || 'Failed to create candidate', 'error')
    } finally {
      setLoading(false)
    }
  }

  const handleQuickCandidate = async (candidate) => {
    setLoading(true)
    try {
      const csvContent = `name,education,experience,skills,summary\n"${candidate.name}","${candidate.education}","${candidate.experience}","${candidate.skills}","${candidate.summary}"`
      const blob = new Blob([csvContent], { type: 'text/csv' })
      const file = new File([blob], 'quick-candidate.csv', { type: 'text/csv' })
      
      const response = await candidatesAPI.uploadCSV(file)
      addToast(`Created candidate: ${candidate.name}`, 'success')
      
      if (onCandidateAdded) {
        onCandidateAdded()
      }
    } catch (error) {
      addToast(error.response?.data?.detail || 'Failed to create candidate', 'error')
    } finally {
      setLoading(false)
    }
  }

  const handleScoreAll = async () => {
    if (!selectedJob) {
      addToast('Please select a job first', 'error')
      return
    }

    setLoading(true)
    addToast('Scoring candidates... This may take a minute for multiple candidates.', 'info', 10000)
    try {
      console.log('🧪 Starting scoring for job:', selectedJob.id)
      const startTime = Date.now()
      const response = await scoringAPI.scoreAll(selectedJob.id)
      const duration = ((Date.now() - startTime) / 1000).toFixed(1)
      console.log(`🧪 Scoring completed in ${duration} seconds`)
      
      // After scoring, refresh candidates (but don't score again)
      if (onScoringComplete) {
        setTimeout(() => {
          onScoringComplete(false) // false = don't force scoring
        }, 500)
      }
      console.log('🧪 Scoring response:', response)
      console.log('🧪 Response keys:', Object.keys(response))
      console.log('🧪 Candidates count:', response.candidates?.length)
      console.log('🧪 Candidates scored:', response.candidates_scored)
      console.log('🧪 Message:', response.message)
      
      // Log first few candidates to see their structure
      if (response.candidates && response.candidates.length > 0) {
        console.log('🧪 First candidate raw:', response.candidates[0])
        console.log('🧪 First candidate total_score:', response.candidates[0]?.total_score)
        console.log('🧪 First candidate category_scores:', response.candidates[0]?.category_scores)
        
        const withScores = response.candidates.filter(c => c.total_score !== null && c.total_score !== undefined)
        console.log(`🧪 ${withScores.length} candidates have scores out of ${response.candidates.length}`)
        
        if (withScores.length > 0) {
          console.log('🧪 Sample scored candidate:', withScores[0])
        } else {
          // Show why they don't have scores
          console.log('🧪 All candidates missing scores. First candidate:', JSON.stringify(response.candidates[0], null, 2))
        }
      }
      
      const message = response.message || `Scored ${response.candidates_scored || 0} candidates`
      addToast(message, 'success', 5000)
      
      if (onScoringComplete) {
        // Small delay to ensure backend has committed
        setTimeout(() => {
          onScoringComplete()
        }, 500)
      }
    } catch (error) {
      console.error('🧪 Scoring error:', error)
      const errorMsg = error.response?.data?.detail || error.message || 'Failed to score candidates'
      addToast(`Scoring failed: ${errorMsg}`, 'error', 8000)
      
      // If it's a config error, provide helpful message
      if (errorMsg.includes('OPENAI') || errorMsg.includes('LLM') || errorMsg.includes('API_KEY')) {
        addToast('Check your OpenRouter/OpenAI API key configuration', 'info', 8000)
      }
    } finally {
      setLoading(false)
    }
  }

  if (!isOpen) return null

  return (
    <div className="test-panel-overlay" onClick={onClose}>
      <div className="test-panel-content" onClick={(e) => e.stopPropagation()}>
        <div className="test-panel-header">
          <h2>Quick Test Actions</h2>
          <button className="test-panel-close" onClick={onClose}>×</button>
        </div>

        <div className="test-panel-tabs">
          <button
            className={`test-panel-tab ${activeTab === 'job' ? 'active' : ''}`}
            onClick={() => setActiveTab('job')}
          >
            Create Job
          </button>
          <button
            className={`test-panel-tab ${activeTab === 'candidate' ? 'active' : ''}`}
            onClick={() => setActiveTab('candidate')}
          >
            Create Candidate
          </button>
          <button
            className={`test-panel-tab ${activeTab === 'scoring' ? 'active' : ''}`}
            onClick={() => setActiveTab('scoring')}
          >
            Scoring
          </button>
        </div>

        <div className="test-panel-body">
          {activeTab === 'job' && (
            <div className="test-panel-section">
              <h3>Quick Test Jobs</h3>
              <div className="quick-jobs">
                <button
                  className="quick-job-btn"
                  onClick={async () => {
                    setLoading(true)
                    try {
                      await jobsAPI.createJob('Software Engineer', {
                        education: "Bachelor's degree in Computer Science or related field",
                        experience: '3+ years of software development experience',
                        skills: 'Python, React, JavaScript, SQL, AWS',
                        other: 'Experience with cloud infrastructure and modern web frameworks'
                      })
                      addToast('Job "Software Engineer" created', 'success')
                      if (onJobCreated) onJobCreated()
                    } catch (error) {
                      addToast(error.response?.data?.detail || 'Failed to create job', 'error')
                    } finally {
                      setLoading(false)
                    }
                  }}
                  disabled={loading}
                >
                  <strong>Software Engineer</strong>
                  <span>3+ years, Python, React, AWS</span>
                </button>
                <button
                  className="quick-job-btn"
                  onClick={async () => {
                    setLoading(true)
                    try {
                      await jobsAPI.createJob('Data Scientist', {
                        education: "Master's degree in Data Science, Statistics, or related field",
                        experience: '2+ years of data science experience',
                        skills: 'Python, TensorFlow, PyTorch, SQL, Machine Learning',
                        other: 'Experience with recommendation systems and production ML models'
                      })
                      addToast('Job "Data Scientist" created', 'success')
                      if (onJobCreated) onJobCreated()
                    } catch (error) {
                      addToast(error.response?.data?.detail || 'Failed to create job', 'error')
                    } finally {
                      setLoading(false)
                    }
                  }}
                  disabled={loading}
                >
                  <strong>Data Scientist</strong>
                  <span>2+ years, Python, ML, TensorFlow</span>
                </button>
                <button
                  className="quick-job-btn"
                  onClick={async () => {
                    setLoading(true)
                    try {
                      await jobsAPI.createJob('Junior Developer', {
                        education: "Bachelor's degree in Computer Science or related field",
                        experience: '0-2 years of development experience',
                        skills: 'JavaScript, React, Node.js, HTML, CSS',
                        other: 'Recent graduates welcome, strong learning ability required'
                      })
                      addToast('Job "Junior Developer" created', 'success')
                      if (onJobCreated) onJobCreated()
                    } catch (error) {
                      addToast(error.response?.data?.detail || 'Failed to create job', 'error')
                    } finally {
                      setLoading(false)
                    }
                  }}
                  disabled={loading}
                >
                  <strong>Junior Developer</strong>
                  <span>0-2 years, JavaScript, React</span>
                </button>
              </div>
            </div>
          )}

          {activeTab === 'candidate' && (
            <div className="test-panel-section">
              <h3>Quick Test Candidates</h3>
              <div className="quick-candidates">
                {quickCandidates.map((candidate, idx) => (
                  <button
                    key={idx}
                    className="quick-candidate-btn"
                    onClick={() => handleQuickCandidate(candidate)}
                    disabled={loading}
                  >
                    <strong>{candidate.name}</strong>
                    <span className="quick-candidate-desc">{candidate.summary.substring(0, 60)}...</span>
                  </button>
                ))}
              </div>

              <h3 style={{ marginTop: '20px' }}>Custom Candidate</h3>
              <div className="test-form">
                <div className="test-form-group">
                  <label>Name *</label>
                  <input
                    type="text"
                    value={candidateForm.name}
                    onChange={(e) => setCandidateForm({ ...candidateForm, name: e.target.value })}
                    placeholder="Candidate name"
                    disabled={loading}
                  />
                </div>
                <div className="test-form-group">
                  <label>Education</label>
                  <textarea
                    value={candidateForm.education}
                    onChange={(e) => setCandidateForm({ ...candidateForm, education: e.target.value })}
                    placeholder="e.g., BS Computer Science, MIT, 2015"
                    rows="2"
                    disabled={loading}
                  />
                </div>
                <div className="test-form-group">
                  <label>Experience</label>
                  <textarea
                    value={candidateForm.experience}
                    onChange={(e) => setCandidateForm({ ...candidateForm, experience: e.target.value })}
                    placeholder="e.g., 5 years at Google, 3 years at Microsoft"
                    rows="2"
                    disabled={loading}
                  />
                </div>
                <div className="test-form-group">
                  <label>Skills</label>
                  <input
                    type="text"
                    value={candidateForm.skills}
                    onChange={(e) => setCandidateForm({ ...candidateForm, skills: e.target.value })}
                    placeholder="e.g., Python, React, AWS"
                    disabled={loading}
                  />
                </div>
                <div className="test-form-group">
                  <label>Summary</label>
                  <textarea
                    value={candidateForm.summary}
                    onChange={(e) => setCandidateForm({ ...candidateForm, summary: e.target.value })}
                    placeholder="Brief profile summary"
                    rows="2"
                    disabled={loading}
                  />
                </div>
                <button
                  className="test-form-submit"
                  onClick={handleCreateCandidate}
                  disabled={loading || !candidateForm.name.trim()}
                >
                  {loading ? 'Creating...' : 'Create Candidate'}
                </button>
              </div>
            </div>
          )}

          {activeTab === 'scoring' && (
            <div className="test-panel-section">
              <h3>Manual Scoring Actions</h3>
              {!selectedJob ? (
                <p className="test-panel-info">Please select a job first to score candidates</p>
              ) : (
                <>
                  <div className="scoring-actions">
                    <button
                      className="scoring-action-btn primary"
                      onClick={handleScoreAll}
                      disabled={loading}
                    >
                      {loading ? 'Scoring...' : 'Score All Candidates'}
                    </button>
                    <p className="scoring-hint">
                      This will score all candidates for the selected job: <strong>{selectedJob.title}</strong>
                    </p>
                  </div>
                </>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default TestPanel

