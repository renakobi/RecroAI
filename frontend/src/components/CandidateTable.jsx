import React, { useState } from 'react'
import ScoreBar from './ScoreBar'
import SuspiciousFlag from './SuspiciousFlag'
import './CandidateTable.css'

function CandidateTable({ candidates, selectedJob, onSendEmail, onViewCV, onDeleteCandidate }) {
  const [expandedRows, setExpandedRows] = useState(new Set())

  if (candidates.length === 0) {
    return (
      <div className="empty-table">
        <p>No candidates found for this job</p>
      </div>
    )
  }

  const toggleRow = (candidateId) => {
    const newExpanded = new Set(expandedRows)
    if (newExpanded.has(candidateId)) {
      newExpanded.delete(candidateId)
    } else {
      newExpanded.add(candidateId)
    }
    setExpandedRows(newExpanded)
  }

  return (
    <div className="candidate-table-container">
      <table className="candidate-table">
        <thead>
          <tr>
            <th className="col-expand"></th>
            <th className="col-name">Candidate</th>
            <th className="col-score">Score</th>
            <th className="col-categories">Categories</th>
            <th className="col-status">Status</th>
            <th className="col-actions">Actions</th>
          </tr>
        </thead>
        <tbody>
          {candidates.map((candidate) => {
            const isExpanded = expandedRows.has(candidate.candidate_id)
            return (
              <React.Fragment key={candidate.candidate_id}>
                <tr className="table-row">
                  <td className="col-expand">
                    {candidate.explanation && (
                      <button
                        className="expand-button"
                        onClick={() => toggleRow(candidate.candidate_id)}
                        aria-label={isExpanded ? 'Collapse' : 'Expand'}
                      >
                        {isExpanded ? '▼' : '▶'}
                      </button>
                    )}
                  </td>
                  <td className="col-name">
                    <div className="candidate-info">
                      <div className="candidate-name">{candidate.name || 'Unknown'}</div>
                      <div className="candidate-email">{candidate.email || 'No email'}</div>
                    </div>
                  </td>
                  <td className="col-score">
                    {candidate.total_score !== null && candidate.total_score !== undefined ? (
                      <div className="score-cell">
                        <div className="score-value">{candidate.total_score.toFixed(1)}</div>
                        <ScoreBar score={candidate.total_score} />
                      </div>
                    ) : (
                      <span className="no-score">Not scored</span>
                    )}
                  </td>
                  <td className="col-categories">
                    {candidate.category_scores && Object.keys(candidate.category_scores).length > 0 ? (
                      <div className="category-scores">
                        {Object.entries(candidate.category_scores).map(([category, data]) => {
                          // Handle both object format {score: X} and direct number
                          const scoreValue = typeof data === 'object' && data !== null ? data.score : data
                          return (
                            <div key={category} className="category-item">
                              <div className="category-name">{category.replace('_score', '').replace('_', ' ')}</div>
                              <ScoreBar score={Number(scoreValue) || 0} size="small" />
                            </div>
                          )
                        })}
                      </div>
                    ) : (
                      <span className="no-categories">No categories</span>
                    )}
                  </td>
                  <td className="col-status">
                    <SuspiciousFlag
                      isSuspicious={candidate.is_suspicious}
                      riskScore={candidate.risk_score}
                    />
                  </td>
                  <td className="col-actions">
                    <div className="action-buttons">
                      {onViewCV && (
                        <button
                          className="action-btn action-view-cv"
                          onClick={() => onViewCV(candidate)}
                          title="View CV/Resume"
                        >
                          View CV
                        </button>
                      )}
                      {candidate.email && selectedJob && onSendEmail && (
                        <>
                          <button
                            className="action-btn action-interview"
                            onClick={() => onSendEmail(candidate, 'interview')}
                            title="Send interview email"
                          >
                            Interview
                          </button>
                          <button
                            className="action-btn action-rejection"
                            onClick={() => onSendEmail(candidate, 'rejection')}
                            title="Send rejection email"
                          >
                            Reject
                          </button>
                        </>
                      )}
                      {onDeleteCandidate && (
                        <button
                          className="action-btn action-delete"
                          onClick={() => onDeleteCandidate(candidate.candidate_id)}
                          title="Delete candidate"
                        >
                          Delete
                        </button>
                      )}
                    </div>
                  </td>
                </tr>
                {isExpanded && candidate.explanation && (
                  <tr className="expanded-row">
                    <td colSpan="6" className="expanded-content">
                      <div className="explanation-section">
                        <h4>Scoring Explanation</h4>
                        <div className="explanation-text">{candidate.explanation}</div>
                        {candidate.category_scores && (
                          <div className="category-details">
                            <h4>Category Details</h4>
                            {Object.entries(candidate.category_scores).map(([category, data]) => (
                              <div key={category} className="category-detail-item">
                                <div className="category-detail-header">
                                  <span className="category-detail-name">{category}</span>
                                  <span className="category-detail-score">{data.score.toFixed(1)}</span>
                                </div>
                                <div className="category-detail-reasoning">{data.reasoning}</div>
                              </div>
                            ))}
                          </div>
                        )}
                      </div>
                    </td>
                  </tr>
                )}
              </React.Fragment>
            )
          })}
        </tbody>
      </table>
    </div>
  )
}

export default CandidateTable

