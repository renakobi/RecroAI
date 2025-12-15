import './SuspiciousFlag.css'

function SuspiciousFlag({ isSuspicious, riskScore }) {
  if (isSuspicious === null || isSuspicious === undefined) {
    return <span className="flag-neutral">—</span>
  }

  if (isSuspicious) {
    const riskLevel = riskScore >= 0.7 ? 'high' : riskScore >= 0.4 ? 'medium' : 'low'
    return (
      <div className={`flag-flag flag-${riskLevel}`}>
        <span className="flag-icon">⚠️</span>
        <span className="flag-text">Suspicious</span>
      </div>
    )
  }

  return (
    <div className="flag-clean">
      <span className="flag-icon">✓</span>
      <span className="flag-text">Clean</span>
    </div>
  )
}

export default SuspiciousFlag

