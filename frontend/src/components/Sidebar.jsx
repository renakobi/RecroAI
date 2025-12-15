import './Sidebar.css'

function Sidebar({ jobs, selectedJob, onJobSelect }) {
  return (
    <aside className="sidebar">
      <div className="sidebar-header">
        <h1 className="sidebar-logo">RecroAI</h1>
      </div>
      <nav className="sidebar-nav">
        <div className="nav-section">
          <div className="nav-section-title">Jobs</div>
          {jobs.map((job) => (
            <button
              key={job.id}
              className={`nav-item ${selectedJob?.id === job.id ? 'active' : ''}`}
              onClick={() => onJobSelect(job)}
            >
              <span className="nav-item-icon">📋</span>
              <span className="nav-item-text">{job.title}</span>
            </button>
          ))}
        </div>
      </nav>
    </aside>
  )
}

export default Sidebar

