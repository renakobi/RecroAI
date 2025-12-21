import { useState } from 'react'
import './SenderEmailModal.css'

function SenderEmailModal({ isOpen, onClose, onSave, currentSenderEmail }) {
  const [email, setEmail] = useState(currentSenderEmail || '')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  if (!isOpen) return null

  const validateEmail = (email) => {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
    return emailRegex.test(email)
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')

    if (!email.trim()) {
      setError('Email is required')
      return
    }

    if (!validateEmail(email.trim())) {
      setError('Please enter a valid email address')
      return
    }

    setLoading(true)
    try {
      await onSave(email.trim())
      onClose()
    } catch (error) {
      setError(error.response?.data?.detail || 'Failed to save sender email')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content sender-email-modal-content" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h2>Set Sender Email</h2>
          <button className="modal-close" onClick={onClose}>×</button>
        </div>
        <form onSubmit={handleSubmit} className="sender-email-form">
          <div className="form-info">
            <p>Configure the email address that will be used to send interview and rejection emails to candidates.</p>
          </div>

          <div className="form-group">
            <label htmlFor="sender-email">Sender Email *</label>
            <input
              id="sender-email"
              type="email"
              value={email}
              onChange={(e) => {
                setEmail(e.target.value)
                setError('')
              }}
              placeholder="your-email@example.com"
              required
              disabled={loading}
              autoFocus
            />
            {error && <div className="form-error">{error}</div>}
          </div>

          <div className="form-actions">
            <button type="button" onClick={onClose} disabled={loading}>
              Cancel
            </button>
            <button type="submit" disabled={loading || !email.trim()}>
              {loading ? 'Saving...' : 'Save'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}

export default SenderEmailModal





