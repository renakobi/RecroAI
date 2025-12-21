import { useState } from 'react'
import './CreateJobModal.css'

function CreateJobModal({ isOpen, onClose, onCreateJob }) {
  const [title, setTitle] = useState('')
  const [criteria, setCriteria] = useState({
    education: '',
    experience: '',
    skills: '',
    other: ''
  })
  const [loading, setLoading] = useState(false)

  if (!isOpen) return null

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!title.trim()) {
      alert('Please enter a job title')
      return
    }

    setLoading(true)
    try {
      // Build criteria JSON from form fields
      const criteriaJson = {}
      if (criteria.education.trim()) criteriaJson.education = criteria.education.trim()
      if (criteria.experience.trim()) criteriaJson.experience = criteria.experience.trim()
      if (criteria.skills.trim()) criteriaJson.skills = criteria.skills.trim()
      if (criteria.other.trim()) criteriaJson.other = criteria.other.trim()

      await onCreateJob(title.trim(), criteriaJson)
      
      // Reset form
      setTitle('')
      setCriteria({ education: '', experience: '', skills: '', other: '' })
      onClose()
    } catch (error) {
      console.error('Error creating job:', error)
      alert(error.response?.data?.detail || 'Failed to create job')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h2>Create New Job</h2>
          <button className="modal-close" onClick={onClose}>×</button>
        </div>
        <div className="quick-templates" style={{ marginBottom: '20px', paddingBottom: '20px', borderBottom: '1px solid #333' }}>
          <div style={{ fontSize: '12px', color: '#8a8a8a', marginBottom: '8px' }}>Quick Templates:</div>
          <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
            <button
              type="button"
              onClick={() => {
                setTitle('Software Engineer')
                setCriteria({
                  education: "Bachelor's degree in Computer Science or related field",
                  experience: '3+ years of software development experience',
                  skills: 'Python, React, JavaScript, SQL, AWS',
                  other: 'Experience with cloud infrastructure and modern web frameworks'
                })
              }}
              style={{ padding: '6px 12px', fontSize: '11px', background: '#2a2a2a', border: '1px solid #3a3a3a', borderRadius: '4px', color: '#fff', cursor: 'pointer' }}
            >
              Software Engineer
            </button>
            <button
              type="button"
              onClick={() => {
                setTitle('Data Scientist')
                setCriteria({
                  education: "Master's degree in Data Science, Statistics, or related field",
                  experience: '2+ years of data science experience',
                  skills: 'Python, TensorFlow, PyTorch, SQL, Machine Learning',
                  other: 'Experience with recommendation systems and production ML models'
                })
              }}
              style={{ padding: '6px 12px', fontSize: '11px', background: '#2a2a2a', border: '1px solid #3a3a3a', borderRadius: '4px', color: '#fff', cursor: 'pointer' }}
            >
              Data Scientist
            </button>
            <button
              type="button"
              onClick={() => {
                setTitle('Junior Developer')
                setCriteria({
                  education: "Bachelor's degree in Computer Science or related field",
                  experience: '0-2 years of development experience',
                  skills: 'JavaScript, React, Node.js, HTML, CSS',
                  other: 'Recent graduates welcome, strong learning ability required'
                })
              }}
              style={{ padding: '6px 12px', fontSize: '11px', background: '#2a2a2a', border: '1px solid #3a3a3a', borderRadius: '4px', color: '#fff', cursor: 'pointer' }}
            >
              Junior Developer
            </button>
          </div>
        </div>
        <form onSubmit={handleSubmit} className="create-job-form">
          <div className="form-group">
            <label htmlFor="title">Job Title *</label>
            <input
              id="title"
              type="text"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              placeholder="e.g., Software Engineer"
              required
              disabled={loading}
            />
          </div>

          <div className="form-group">
            <label htmlFor="education">Education Requirements</label>
            <textarea
              id="education"
              value={criteria.education}
              onChange={(e) => setCriteria({ ...criteria, education: e.target.value })}
              placeholder="e.g., Bachelor's degree in Computer Science or related field"
              rows="2"
              disabled={loading}
            />
          </div>

          <div className="form-group">
            <label htmlFor="experience">Experience Requirements</label>
            <textarea
              id="experience"
              value={criteria.experience}
              onChange={(e) => setCriteria({ ...criteria, experience: e.target.value })}
              placeholder="e.g., 3+ years of software development experience"
              rows="2"
              disabled={loading}
            />
          </div>

          <div className="form-group">
            <label htmlFor="skills">Required Skills</label>
            <textarea
              id="skills"
              value={criteria.skills}
              onChange={(e) => setCriteria({ ...criteria, skills: e.target.value })}
              placeholder="e.g., Python, React, SQL, AWS"
              rows="2"
              disabled={loading}
            />
          </div>

          <div className="form-group">
            <label htmlFor="other">Other Requirements</label>
            <textarea
              id="other"
              value={criteria.other}
              onChange={(e) => setCriteria({ ...criteria, other: e.target.value })}
              placeholder="Any additional requirements or preferences"
              rows="2"
              disabled={loading}
            />
          </div>

          <div className="form-actions">
            <button type="button" onClick={onClose} disabled={loading}>
              Cancel
            </button>
            <button type="submit" disabled={loading || !title.trim()}>
              {loading ? 'Creating...' : 'Create Job'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}

export default CreateJobModal





