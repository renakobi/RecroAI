import './CVViewerModal.css'

function CVViewerModal({ isOpen, onClose, candidate }) {
  if (!isOpen || !candidate) return null

  // Parse raw_profile
  let profile = null
  try {
    profile = typeof candidate.raw_profile === 'string' 
      ? JSON.parse(candidate.raw_profile) 
      : candidate.raw_profile
  } catch (e) {
    // If parsing fails, show raw text
    profile = { raw: candidate.raw_profile }
  }

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content cv-viewer-modal-content" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h2>CV / Resume - {candidate.name || 'Unknown Candidate'}</h2>
          <button className="modal-close" onClick={onClose}>×</button>
        </div>
        <div className="cv-content">
          {profile && !profile.raw ? (
            <>
              <div className="cv-section">
                <h3 className="cv-section-title">Personal Information</h3>
                <div className="cv-section-content">
                  <p><strong>Name:</strong> {profile.name || candidate.name || 'N/A'}</p>
                  <p><strong>Email:</strong> {candidate.email || profile.email || 'N/A'}</p>
                </div>
              </div>

              {profile.education && (
                <div className="cv-section">
                  <h3 className="cv-section-title">Education</h3>
                  <div className="cv-section-content">
                    {typeof profile.education === 'string' ? (
                      <p>{profile.education}</p>
                    ) : (
                      <pre className="cv-pre">{JSON.stringify(profile.education, null, 2)}</pre>
                    )}
                  </div>
                </div>
              )}

              {profile.experience && (
                <div className="cv-section">
                  <h3 className="cv-section-title">Experience</h3>
                  <div className="cv-section-content">
                    {typeof profile.experience === 'string' ? (
                      <p>{profile.experience}</p>
                    ) : (
                      <pre className="cv-pre">{JSON.stringify(profile.experience, null, 2)}</pre>
                    )}
                  </div>
                </div>
              )}

              {profile.skills && (
                <div className="cv-section">
                  <h3 className="cv-section-title">Skills</h3>
                  <div className="cv-section-content">
                    {typeof profile.skills === 'string' ? (
                      <p>{profile.skills}</p>
                    ) : (
                      <pre className="cv-pre">{JSON.stringify(profile.skills, null, 2)}</pre>
                    )}
                  </div>
                </div>
              )}

              {profile.summary && (
                <div className="cv-section">
                  <h3 className="cv-section-title">Summary</h3>
                  <div className="cv-section-content">
                    <p>{profile.summary}</p>
                  </div>
                </div>
              )}
            </>
          ) : (
            <div className="cv-section">
              <div className="cv-section-content">
                <pre className="cv-pre">{profile?.raw || candidate.raw_profile || 'No CV data available'}</pre>
              </div>
            </div>
          )}

          {candidate.total_score !== null && candidate.total_score !== undefined && (
            <div className="cv-section">
              <h3 className="cv-section-title">Score</h3>
              <div className="cv-section-content">
                <p><strong>Total Score:</strong> {candidate.total_score.toFixed(1)}/100</p>
                {candidate.category_scores && (
                  <div className="cv-scores">
                    {Object.entries(candidate.category_scores).map(([category, data]) => (
                      <div key={category} className="cv-score-item">
                        <strong>{category}:</strong> {data.score.toFixed(1)}/100
                        {data.reasoning && (
                          <div className="cv-score-reasoning">{data.reasoning}</div>
                        )}
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          )}
        </div>
        <div className="cv-footer">
          <button className="cv-close-btn" onClick={onClose}>Close</button>
        </div>
      </div>
    </div>
  )
}

export default CVViewerModal





