import './Sidebar.css'

function Sidebar({ jobs, selectedJob, onJobSelect, onCreateJobClick, onUploadCSVClick, onParseCVClick, onDeleteJob, onLogout, onGoToDashboard }) {
  return (
    <aside className="sidebar">
      <div className="sidebar-header">
        <button className="sidebar-logo-button" onClick={onGoToDashboard} title="Go to Dashboard">
          <h1 className="sidebar-logo">RecroAI</h1>
        </button>
      </div>
      {onLogout && (
        <div className="sidebar-logout">
          <button className="logout-button" onClick={onLogout} title="Logout">
            Logout
          </button>
        </div>
      )}
      <nav className="sidebar-nav">
        <div className="nav-section">
          <div className="nav-section-title">Jobs</div>
          <div className="nav-actions">
            <button
              className="nav-action-button"
              onClick={onCreateJobClick}
              title="Create New Job"
            >
              <span>Create Job</span>
            </button>
            <button
              className="nav-action-button"
              onClick={onUploadCSVClick}
              title="Upload Candidates CSV"
            >
              <span>Upload CSV</span>
            </button>
            <button
              className="nav-action-button"
              onClick={onParseCVClick}
              title="Parse CV to CSV"
            >
              <span>Parse CV to CSV</span>
            </button>
          </div>
          {jobs.length === 0 ? (
            <div className="nav-empty-state">
              <p>No jobs yet</p>
              <p className="nav-empty-hint">Create your first job to get started</p>
            </div>
          ) : (
            jobs.map((job) => (
              <div key={job.id} className="nav-item-wrapper">
                <button
                  className={`nav-item ${selectedJob?.id === job.id ? 'active' : ''}`}
                  onClick={() => onJobSelect(job)}
                >
                  <span className="nav-item-text">{job.title}</span>
                </button>
                {onDeleteJob && (
                  <button
                    className="nav-item-delete"
                    onClick={(e) => {
                      e.stopPropagation()
                      onDeleteJob(job.id)
                    }}
                    title="Delete job"
                  >
                    ×
                  </button>
                )}
              </div>
            ))
          )}
        </div>
      </nav>
    </aside>
  )
}

export default Sidebar

