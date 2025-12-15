import './FilterPanel.css'

function FilterPanel({ filters, onFilterChange, universities, companies, loading = false }) {
  const handleUniversityChange = (e) => {
    const value = e.target.value
    onFilterChange({
      ...filters,
      university: value === 'all' ? null : value,
      universityMatchType: value === 'all' ? null : filters.universityMatchType,
    })
  }

  const handleUniversityMatchTypeChange = (e) => {
    onFilterChange({
      ...filters,
      universityMatchType: e.target.value,
    })
  }

  const handleCompanyChange = (e) => {
    const value = e.target.value
    onFilterChange({
      ...filters,
      company: value === 'all' ? null : value,
    })
  }

  const handleMinExperienceChange = (e) => {
    const value = e.target.value === '' ? null : parseInt(e.target.value)
    onFilterChange({
      ...filters,
      minExperience: value,
    })
  }

  const clearFilters = () => {
    onFilterChange({
      university: null,
      universityMatchType: 'exact',
      company: null,
      minExperience: null,
    })
  }

  const hasActiveFilters = filters.university || filters.company || filters.minExperience

  return (
    <div className="filter-panel">
      <div className="filter-panel-header">
        <h3 className="filter-panel-title">Filters</h3>
        {hasActiveFilters && (
          <button className="filter-clear-btn" onClick={clearFilters}>
            Clear
          </button>
        )}
      </div>

      <div className="filter-group">
        <label className="filter-label">University</label>
        <select
          className="filter-select"
          value={filters.university || 'all'}
          onChange={handleUniversityChange}
          disabled={loading}
        >
          <option value="all">All Universities</option>
          {loading ? (
            <option disabled>Loading...</option>
          ) : (
            universities.map((uni) => (
              <option key={uni} value={uni}>
                {uni}
              </option>
            ))
          )}
        </select>
        {filters.university && (
          <select
            className="filter-select filter-select-small"
            value={filters.universityMatchType || 'exact'}
            onChange={handleUniversityMatchTypeChange}
          >
            <option value="exact">Exact Match</option>
            <option value="close">Close Match</option>
          </select>
        )}
      </div>

      <div className="filter-group">
        <label className="filter-label">Company</label>
        <select
          className="filter-select"
          value={filters.company || 'all'}
          onChange={handleCompanyChange}
          disabled={loading}
        >
          <option value="all">All Companies</option>
          {loading ? (
            <option disabled>Loading...</option>
          ) : (
            companies.map((company) => (
              <option key={company} value={company}>
                {company}
              </option>
            ))
          )}
        </select>
      </div>

      <div className="filter-group">
        <label className="filter-label">Minimum Experience (years)</label>
        <input
          type="number"
          className="filter-input"
          min="0"
          step="1"
          placeholder="Any"
          value={filters.minExperience || ''}
          onChange={handleMinExperienceChange}
        />
      </div>
    </div>
  )
}

export default FilterPanel

