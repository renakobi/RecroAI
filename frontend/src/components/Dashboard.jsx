import CandidateTable from './CandidateTable'
import FilterPanel from './FilterPanel'
import './Dashboard.css'

function Dashboard({ candidates, allCandidates, selectedJob, loading, filters, onFilterChange, universities, companies }) {
  const hasActiveFilters = filters.university || filters.company || filters.minExperience !== null
  const filteredCount = candidates.length
  const totalCount = allCandidates.length

  return (
    <main className="dashboard">
      <div className="dashboard-header">
        <div className="dashboard-title-section">
          <h2 className="dashboard-title">
            {selectedJob ? selectedJob.title : 'Select a Job'}
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
      </div>
      <div className="dashboard-content">
        {loading ? (
          <div className="loading-state">
            <div className="loading-spinner"></div>
            <p>Loading candidates...</p>
          </div>
        ) : selectedJob ? (
          <>
            <FilterPanel
              filters={filters}
              onFilterChange={onFilterChange}
              universities={universities}
              companies={companies}
              loading={loading}
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
              <CandidateTable candidates={candidates} />
            )}
          </>
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
