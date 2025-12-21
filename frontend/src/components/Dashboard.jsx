import CandidateTable from './CandidateTable'
import FilterPanel from './FilterPanel'
import AnalyticsDashboard from './AnalyticsDashboard'
import './Dashboard.css'

function Dashboard({ candidates, allCandidates, selectedJob, loading, filters, onFilterChange, universities, companies, onSendEmail, onViewCV, onAddUniversity, onAddCompany, onDeleteCandidate, onScoreCandidates, jobs, onJobSelect }) {
  const hasActiveFilters = filters.university || filters.company || filters.minExperience !== null
  const filteredCount = candidates.length
  const totalCount = allCandidates.length

  return (
    <main className="dashboard">
      <div className="dashboard-header">
        <div className="dashboard-title-section">
          <h2 className="dashboard-title">
            {selectedJob ? selectedJob.title : 'Analytics Dashboard'}
          </h2>
          {selectedJob && (
            <span className="dashboard-subtitle">
              {hasActiveFilters ? (
                <>
                  {filteredCount} of {totalCount} candidate{totalCount !== 1 ? 's' : ''}
                </>
              ) : (
                <>
                  {totalCount} candidate{totalCount !== 1 ? 's' : ''}
                </>
              )}
            </span>
          )}
        </div>
        {selectedJob && onScoreCandidates && (
          <button
            className="score-candidates-button"
            onClick={() => onScoreCandidates()}
            disabled={loading || candidates.length === 0}
            title="Score all candidates for this job"
          >
            Score Candidates
          </button>
        )}
      </div>
      {selectedJob ? (
        <div className="dashboard-content">
          {loading ? (
            <div className="loading-state">
              <div className="loading-spinner"></div>
              <p>Loading candidates...</p>
            </div>
          ) : (
            <>
              <FilterPanel
                filters={filters}
                onFilterChange={onFilterChange}
                universities={universities}
                companies={companies}
                loading={loading}
                onAddUniversity={onAddUniversity}
                onAddCompany={onAddCompany}
              />
              {candidates.length === 0 ? (
                <div className="empty-state">
                  <p>
                    {filters.university || filters.company || filters.minExperience !== null
                      ? 'No candidates match the selected filters'
                      : 'No candidates found for this job'}
                  </p>
                </div>
              ) : (
                <CandidateTable 
                  candidates={candidates} 
                  selectedJob={selectedJob}
                  onSendEmail={onSendEmail}
                  onViewCV={onViewCV}
                  onDeleteCandidate={onDeleteCandidate}
                />
              )}
            </>
          )}
        </div>
      ) : (
        <AnalyticsDashboard jobs={jobs} onJobSelect={onJobSelect} />
      )}
    </main>
  )
}

export default Dashboard
