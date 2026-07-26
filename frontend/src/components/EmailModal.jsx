import { useState } from 'react'
import './EmailModal.css'

function EmailModal({ isOpen, onClose, candidate, job, emailType, onSend }) {
  const [interviewDate, setInterviewDate] = useState('')
  const [interviewTime, setInterviewTime] = useState('')
  const [interviewLocation, setInterviewLocation] = useState('')
  const [loading, setLoading] = useState(false)

  if (!isOpen) return null

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    try {
      await onSend(
        candidate.candidate_id,
        job.id,
        emailType,
        interviewDate || undefined,
        interviewTime || undefined,
        interviewLocation || undefined
      )
      // Reset form
      setInterviewDate('')
      setInterviewTime('')
      setInterviewLocation('')
      onClose()
    } catch (error) {
      console.error('Error sending email:', error)
    } finally {
      setLoading(false)
    }
  }

  const isInterview = emailType === 'interview'

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content email-modal-content" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h2>{isInterview ? 'Send Interview Email' : 'Send Rejection Email'}</h2>
          <button className="modal-close" onClick={onClose}>×</button>
        </div>
        <form onSubmit={handleSubmit} className="email-form">
          <div className="email-info">
            <p><strong>To:</strong> {candidate.name || candidate.email}</p>
            <p><strong>Job:</strong> {job.title}</p>
          </div>

          {isInterview && (
            <>
              <div className="form-group">
                <label htmlFor="interview-date">Interview Date (optional)</label>
                <input
                  id="interview-date"
                  type="date"
                  value={interviewDate}
                  onChange={(e) => setInterviewDate(e.target.value)}
                  disabled={loading}
                />
              </div>

              <div className="form-group">
                <label htmlFor="interview-time">Interview Time (optional)</label>
                <input
                  id="interview-time"
                  type="time"
                  value={interviewTime}
                  onChange={(e) => setInterviewTime(e.target.value)}
                  disabled={loading}
                />
              </div>

              <div className="form-group">
                <label htmlFor="interview-location">Interview Location (optional)</label>
                <input
                  id="interview-location"
                  type="text"
                  value={interviewLocation}
                  onChange={(e) => setInterviewLocation(e.target.value)}
                  placeholder="e.g., Office Address or Video Call"
                  disabled={loading}
                />
              </div>
            </>
          )}

          <div className="form-actions">
            <button type="button" onClick={onClose} disabled={loading}>
              Cancel
            </button>
            <button type="submit" disabled={loading}>
              {loading ? 'Sending...' : `Send ${isInterview ? 'Interview' : 'Rejection'} Email`}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}

export default EmailModal





