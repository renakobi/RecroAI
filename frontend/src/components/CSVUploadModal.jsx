import { useState, useRef } from 'react'
import './CSVUploadModal.css'

function CSVUploadModal({ isOpen, onClose, onUpload }) {
  const [file, setFile] = useState(null)
  const [loading, setLoading] = useState(false)
  const fileInputRef = useRef(null)

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

  const handleQuickCandidate = async (candidate) => {
    setLoading(true)
    try {
      const csvContent = `name,education,experience,skills,summary\n"${candidate.name}","${candidate.education}","${candidate.experience}","${candidate.skills}","${candidate.summary}"`
      const blob = new Blob([csvContent], { type: 'text/csv' })
      const file = new File([blob], 'quick-candidate.csv', { type: 'text/csv' })
      await onUpload(file)
      onClose()
    } catch (error) {
      console.error('Error creating candidate:', error)
      alert(error.response?.data?.detail || 'Failed to create candidate')
    } finally {
      setLoading(false)
    }
  }

  if (!isOpen) return null

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0]
    if (selectedFile) {
      if (!selectedFile.name.endsWith('.csv')) {
        alert('Please select a CSV file')
        return
      }
      setFile(selectedFile)
    }
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!file) {
      alert('Please select a CSV file')
      return
    }

    setLoading(true)
    try {
      await onUpload(file)
      setFile(null)
      if (fileInputRef.current) {
        fileInputRef.current.value = ''
      }
      onClose()
    } catch (error) {
      console.error('Error uploading CSV:', error)
      alert(error.response?.data?.detail || 'Failed to upload CSV file')
    } finally {
      setLoading(false)
    }
  }

  const handleDrop = (e) => {
    e.preventDefault()
    const droppedFile = e.dataTransfer.files[0]
    if (droppedFile && droppedFile.name.endsWith('.csv')) {
      setFile(droppedFile)
    } else {
      alert('Please drop a CSV file')
    }
  }

  const handleDragOver = (e) => {
    e.preventDefault()
  }

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h2>Upload Candidates CSV</h2>
          <button className="modal-close" onClick={onClose}>×</button>
        </div>
        <div style={{ marginBottom: '20px', paddingBottom: '20px', borderBottom: '1px solid #333' }}>
          <div style={{ fontSize: '12px', color: '#8a8a8a', marginBottom: '8px' }}>Quick Test Candidates:</div>
          <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
            {quickCandidates.map((candidate, idx) => (
              <button
                key={idx}
                type="button"
                onClick={() => handleQuickCandidate(candidate)}
                disabled={loading}
                style={{ padding: '6px 12px', fontSize: '11px', background: '#2a2a2a', border: '1px solid #3a3a3a', borderRadius: '4px', color: '#fff', cursor: 'pointer', maxWidth: '200px' }}
              >
                {candidate.name.split(' - ')[0]}
              </button>
            ))}
          </div>
        </div>
        <form onSubmit={handleSubmit} className="csv-upload-form">
          <div className="upload-info">
            <p>Upload a CSV file with candidate information.</p>
            <p className="info-text">Required columns: <strong>name</strong>, <strong>education</strong>, <strong>experience</strong>, <strong>skills</strong>, <strong>summary</strong></p>
          </div>

          <div
            className="file-drop-zone"
            onDrop={handleDrop}
            onDragOver={handleDragOver}
          >
            <input
              ref={fileInputRef}
              type="file"
              accept=".csv"
              onChange={handleFileChange}
              className="file-input"
              id="csv-file-input"
            />
            <label htmlFor="csv-file-input" className="file-label">
              {file ? (
                <div className="file-selected">
                  <span className="file-icon">File</span>
                  <span className="file-name">{file.name}</span>
                  <button
                    type="button"
                    onClick={(e) => {
                      e.stopPropagation()
                      setFile(null)
                      if (fileInputRef.current) {
                        fileInputRef.current.value = ''
                      }
                    }}
                    className="file-remove"
                  >
                    ×
                  </button>
                </div>
              ) : (
                <div className="file-placeholder">
                  <span className="upload-icon">Upload</span>
                  <span>Click to select or drag and drop CSV file</span>
                </div>
              )}
            </label>
          </div>

          <div className="form-actions">
            <button type="button" onClick={onClose} disabled={loading}>
              Cancel
            </button>
            <button type="submit" disabled={loading || !file}>
              {loading ? 'Uploading...' : 'Upload CSV'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}

export default CSVUploadModal





