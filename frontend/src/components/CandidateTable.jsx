import ScoreBar from './ScoreBar'
import SuspiciousFlag from './SuspiciousFlag'
import './CandidateTable.css'

function CandidateTable({ candidates }) {
  if (candidates.length === 0) {
    return (
      <div className="empty-table">
        <p>No candidates found for this job</p>
      </div>
    )
  }

  return (
    <div className="candidate-table-container">
      <table className="candidate-table">
        <thead>
          <tr>
            <th className="col-name">Candidate</th>
            <th className="col-score">Score</th>
            <th className="col-categories">Categories</th>
            <th className="col-status">Status</th>
          </tr>
        </thead>
        <tbody>
          {candidates.map((candidate) => (
            <tr key={candidate.candidate_id} className="table-row">
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
                {candidate.category_scores ? (
                  <div className="category-scores">
                    {Object.entries(candidate.category_scores).map(([category, data]) => (
                      <div key={category} className="category-item">
                        <div className="category-name">{category}</div>
                        <ScoreBar score={data.score} size="small" />
                      </div>
                    ))}
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
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}

export default CandidateTable

