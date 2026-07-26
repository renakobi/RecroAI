import './ScoreBar.css'

function ScoreBar({ score, size = 'normal' }) {
  if (score === null || score === undefined) {
    return null
  }

  const percentage = Math.min(Math.max(score, 0), 100)
  const color = getScoreColor(percentage)

  return (
    <div className={`score-bar score-bar-${size}`}>
      <div
        className="score-bar-fill"
        style={{
          width: `${percentage}%`,
          backgroundColor: color,
        }}
      />
    </div>
  )
}

function getScoreColor(score) {
  if (score >= 80) return '#4caf50' // Green
  if (score >= 60) return '#ff9800' // Orange
  return '#f44336' // Red
}

export default ScoreBar

