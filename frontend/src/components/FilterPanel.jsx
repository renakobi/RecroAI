import { useState } from 'react'
import './FilterPanel.css'

function FilterPanel({ filters, onFilterChange, universities, companies, loading = false, onAddUniversity, onAddCompany }) {
  const [newUniversity, setNewUniversity] = useState('')
  const [newCompany, setNewCompany] = useState('')
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

  const handleMinScoreChange = (e) => {
    const value = e.target.value === '' ? null : parseInt(e.target.value)
    onFilterChange({
      ...filters,
      minScore: value,
    })
  }

  const handleMaxScoreChange = (e) => {
    const value = e.target.value === '' ? null : parseInt(e.target.value)
    onFilterChange({
      ...filters,
      maxScore: value,
    })
  }

  const handleAuthenticityChange = (e) => {
    const value = e.target.value
    onFilterChange({
      ...filters,
      authenticity: value === 'all' ? null : value,
    })
  }

  const clearFilters = () => {
    onFilterChange({
      university: null,
      universityMatchType: 'exact',
      company: null,
      minExperience: null,
      minScore: null,
      maxScore: null,
      authenticity: null,
    })
  }

  const handleAddUniversity = (e) => {
    e.preventDefault()
    if (newUniversity.trim() && onAddUniversity) {
      onAddUniversity(newUniversity.trim())
      setNewUniversity('')
    }
  }

  const handleAddCompany = (e) => {
    e.preventDefault()
    if (newCompany.trim() && onAddCompany) {
      onAddCompany(newCompany.trim())
      setNewCompany('')
    }
  }

  const hasActiveFilters = filters.university || filters.company || filters.minExperience !== null || filters.minScore !== null || filters.maxScore !== null || filters.authenticity

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
        {onAddUniversity && (
          <form className="filter-add-form" onSubmit={handleAddUniversity}>
            <input
              type="text"
              className="filter-add-input"
              placeholder="Add university..."
              value={newUniversity}
              onChange={(e) => setNewUniversity(e.target.value)}
              disabled={loading}
            />
            <button type="submit" className="filter-add-btn" disabled={loading || !newUniversity.trim()}>
              +
            </button>
          </form>
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
        {onAddCompany && (
          <form className="filter-add-form" onSubmit={handleAddCompany}>
            <input
              type="text"
              className="filter-add-input"
              placeholder="Add company..."
              value={newCompany}
              onChange={(e) => setNewCompany(e.target.value)}
              disabled={loading}
            />
            <button type="submit" className="filter-add-btn" disabled={loading || !newCompany.trim()}>
              +
            </button>
          </form>
        )}
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

      <div className="filter-group">
        <label className="filter-label">Score Range</label>
        <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
          <input
            type="number"
            className="filter-input"
            min="0"
            max="100"
            step="1"
            placeholder="Min"
            value={filters.minScore || ''}
            onChange={handleMinScoreChange}
            style={{ flex: 1 }}
          />
          <span style={{ color: '#8a8a8a', fontSize: '18px' }}>-</span>
          <input
            type="number"
            className="filter-input"
            min="0"
            max="100"
            step="1"
            placeholder="Max"
            value={filters.maxScore || ''}
            onChange={handleMaxScoreChange}
            style={{ flex: 1 }}
          />
        </div>
      </div>

      <div className="filter-group">
        <label className="filter-label">Authenticity</label>
        <select
          className="filter-select"
          value={filters.authenticity || 'all'}
          onChange={handleAuthenticityChange}
          disabled={loading}
        >
          <option value="all">All</option>
          <option value="clean">Clean Only</option>
          <option value="suspicious">Suspicious Only</option>
        </select>
      </div>
    </div>
  )
}

export default FilterPanel

