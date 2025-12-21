import { useState, useEffect } from 'react'
import { analyticsAPI } from '../services/api'
import './AnalyticsDashboard.css'

function AnalyticsDashboard({ jobs, onJobSelect }) {
  const [analytics, setAnalytics] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchAnalytics()
  }, [jobs])

  const fetchAnalytics = async () => {
    try {
      setLoading(true)
      const data = await analyticsAPI.getAnalytics()
      setAnalytics(data)
    } catch (error) {
      console.error('Error fetching analytics:', error)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="analytics-loading">
        <div className="loading-spinner"></div>
        <p>Loading analytics...</p>
      </div>
    )
  }

  if (!analytics) {
    return (
      <div className="analytics-empty">
        <p>No analytics data available</p>
      </div>
    )
  }

  return (
    <div className="analytics-dashboard">
      <div className="analytics-header">
        <h2>Analytics Dashboard</h2>
        <button onClick={fetchAnalytics} className="refresh-button">Refresh</button>
      </div>

      <div className="analytics-grid">
        {/* Overview Cards */}
        <div className="stat-card">
          <div className="stat-label">Total Jobs</div>
          <div className="stat-value">{analytics.total_jobs}</div>
        </div>

        <div className="stat-card">
          <div className="stat-label">Total Candidates</div>
          <div className="stat-value">{analytics.total_candidates}</div>
        </div>

        <div className="stat-card">
          <div className="stat-label">Candidates Scored</div>
          <div className="stat-value">{analytics.total_scores}</div>
        </div>

        <div className="stat-card">
          <div className="stat-label">Average Score</div>
          <div className="stat-value">{analytics.average_score.toFixed(1)}</div>
        </div>

        {/* Score Distribution */}
        <div className="analytics-section">
          <h3>Score Distribution</h3>
          <div className="score-distribution">
            {Object.entries(analytics.score_distribution).map(([range, count]) => (
              <div key={range} className="distribution-bar">
                <div className="distribution-label">{range}</div>
                <div className="distribution-bar-container">
                  <div 
                    className="distribution-bar-fill"
                    style={{ 
                      width: `${analytics.total_scores > 0 ? (count / analytics.total_scores) * 100 : 0}%` 
                    }}
                  >
                    {count}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Category Averages */}
        {Object.keys(analytics.category_averages).length > 0 && (
          <div className="analytics-section">
            <h3>Category Averages</h3>
            <div className="category-averages">
              {Object.entries(analytics.category_averages).map(([category, avg]) => (
                <div key={category} className="category-item">
                  <div className="category-name">{category.replace('_score', '').replace('_', ' ')}</div>
                  <div className="category-score-bar">
                    <div 
                      className="category-score-fill"
                      style={{ width: `${avg}%` }}
                    />
                    <span className="category-score-value">{avg.toFixed(1)}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Top Candidates */}
        {analytics.top_candidates.length > 0 && (
          <div className="analytics-section">
            <h3>Top Candidates</h3>
            <div className="top-candidates-list">
              {analytics.top_candidates.map((candidate, idx) => (
                <div 
                  key={`candidate-${candidate.candidate_id}-${candidate.job_id}-${idx}`} 
                  className="top-candidate-item"
                  onClick={() => onJobSelect && onJobSelect({ id: candidate.job_id, title: candidate.job_title })}
                >
                  <div className="candidate-rank">#{idx + 1}</div>
                  <div className="candidate-info">
                    <div className="candidate-name">{candidate.name}</div>
                    <div className="candidate-job">{candidate.job_title}</div>
                  </div>
                  <div className="candidate-score">{candidate.score.toFixed(1)}</div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Jobs Summary */}
        {analytics.jobs_summary.length > 0 && (
          <div className="analytics-section">
            <h3>Jobs Overview</h3>
            <div className="jobs-summary">
              {analytics.jobs_summary.map((job, idx) => (
                <div 
                  key={`job-${job.job_id}-${idx}`} 
                  className="job-summary-item"
                  onClick={() => onJobSelect && onJobSelect({ id: job.job_id, title: job.title })}
                >
                  <div className="job-title">{job.title}</div>
                  <div className="job-stats">
                    <span>{job.scored_count} scored</span>
                    {job.average_score !== null && (
                      <span className="job-avg-score">Avg: {job.average_score.toFixed(1)}</span>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Authenticity Stats */}
        {analytics.authenticity_stats.total_checked > 0 && (
          <div className="analytics-section">
            <h3>Authenticity Check</h3>
            <div className="authenticity-stats">
              <div className="auth-stat-item">
                <div className="auth-stat-label">Total Checked</div>
                <div className="auth-stat-value">{analytics.authenticity_stats.total_checked}</div>
              </div>
              <div className="auth-stat-item clean">
                <div className="auth-stat-label">Clean</div>
                <div className="auth-stat-value">{analytics.authenticity_stats.clean}</div>
              </div>
              <div className="auth-stat-item suspicious">
                <div className="auth-stat-label">Suspicious</div>
                <div className="auth-stat-value">{analytics.authenticity_stats.suspicious}</div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

export default AnalyticsDashboard

