import CandidateTable from './CandidateTable'
import './Dashboard.css'

function Dashboard({ candidates, selectedJob, loading }) {
  return (
    <main className="dashboard">
      <div className="dashboard-header">
        <div className="dashboard-title-section">
          <h2 className="dashboard-title">
            {selectedJob ? selectedJob.title : 'Select a Job'}
          </h2>
          {selectedJob && (
            <span className="dashboard-subtitle">
              {candidates.length} candidate{candidates.length !== 1 ? 's' : ''}
            </span>
          )}
        </div>
      </div>
      <div className="dashboard-content">
        {loading ? (
          <div className="loading-state">
            <div className="loading-spinner"></div>
            <p>Loading candidates...</p>
          </div>
        ) : selectedJob ? (
          <CandidateTable candidates={candidates} />
        ) : (
          <div className="empty-state">
            <p>Select a job from the sidebar to view candidates</p>
          </div>
        )}
      </div>
    </main>
  )
}

export default Dashboard

