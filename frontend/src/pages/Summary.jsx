import { useEffect } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import './Summary.css';

const Summary = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const { user, logout } = useAuth();
  const data = location.state?.data;

  // Scroll to top when component mounts
  useEffect(() => {
    window.scrollTo(0, 0);
  }, []);

  if (!data) {
    return (
      <div className="summary-container">
        <div className="summary-error">
          <h2>No data available</h2>
          <button onClick={() => navigate('/dashboard')} className="back-button">
            Go Back
          </button>
        </div>
      </div>
    );
  }

  const {
    requested_count,
    actual_count,
    summary,
    labeling,
    classifications
  } = data;

  // Calculate statistics
  const totalClassified = Object.values(summary || {}).reduce((sum, count) => sum + count, 0);
  const successRate = labeling?.success_count 
    ? ((labeling.success_count / actual_count) * 100).toFixed(1)
    : '0';

  // Category display info
  const categoryInfo = {
    'IMPORTANT_ACTION': { name: 'Important Action', color: '#ea4335', icon: '🔴' },
    'FYI_READ_LATER': { name: 'FYI / Read Later', color: '#34a853', icon: '🟢' },
    'MARKETING': { name: 'Marketing', color: '#fbbc04', icon: '🟡' },
    'AUTOMATED': { name: 'Automated', color: '#4285f4', icon: '🔵' },
    'LOW_VALUE_NOISE': { name: 'Low Value / Noise', color: '#5f6368', icon: '⚫' },
    'UNKNOWN': { name: 'Unknown', color: '#ff9800', icon: '🟠' },
    'ERROR': { name: 'Error', color: '#9aa0a6', icon: '⚠️' }
  };

  return (
    <div className="summary-container">
      <div className="summary-header">
        <div className="header-content">
          <div className="header-left">
            <div className="gmail-logo-small">
              <svg viewBox="0 0 24 24" width="32" height="32">
                <path
                  fill="#EA4335"
                  d="M24 5.457v13.909c0 .904-.732 1.636-1.636 1.636h-3.819V11.73L12 16.64l-6.545-4.91v9.273H1.636A1.636 1.636 0 0 1 0 19.366V5.457c0-2.023 2.309-3.178 3.927-1.964L5.455 4.64 12 9.548l6.545-4.91 1.528-1.145C21.69 2.28 24 3.434 24 5.457z"
                />
              </svg>
            </div>
            <h1 className="summary-title">Email Clean Summary</h1>
          </div>
          <div className="header-right">
            <div className="user-info">
              <div className="user-avatar">
                {user?.email?.charAt(0).toUpperCase()}
              </div>
              <span className="user-email">{user?.email}</span>
            </div>
            <button onClick={logout} className="logout-button">
              Sign out
            </button>
          </div>
        </div>
      </div>

      <div className="summary-content">
        {/* Success Banner */}
        <div className="success-banner">
          <div className="success-icon">✅</div>
          <div className="success-text">
            <h2>Processing Complete!</h2>
            <p>Your emails have been classified and labeled in Gmail</p>
            <div className="refresh-notice">
              <span className="refresh-icon">🔄</span>
              <span><strong>Next Step:</strong> Refresh your Gmail inbox to see the color-coded labels!</span>
            </div>
          </div>
        </div>

        {/* Instructions Box */}
        <div className="instructions-summary-box">
          <h3 className="instructions-title">📬 What to Expect in Gmail</h3>
          <p className="instructions-text">
            After refreshing your Gmail, you'll see color-coded labels on each processed email:
          </p>
          <div className="label-examples">
            <div className="label-example">
              <span className="label-badge red">IMPORTANT_ACTION</span>
              <span className="label-description">Emails requiring your action (meetings, tasks, urgent items)</span>
            </div>
            <div className="label-example">
              <span className="label-badge green">FYI_READ_LATER</span>
              <span className="label-description">Informational emails you can read later (newsletters, articles)</span>
            </div>
            <div className="label-example">
              <span className="label-badge yellow">MARKETING</span>
              <span className="label-description">Promotional content (sales, deals, ads)</span>
            </div>
            <div className="label-example">
              <span className="label-badge blue">AUTOMATED</span>
              <span className="label-description">Automated emails (receipts, confirmations, notifications)</span>
            </div>
            <div className="label-example">
              <span className="label-badge grey">LOW_VALUE_NOISE</span>
              <span className="label-description">Low-value emails that don't need attention</span>
            </div>
          </div>
          <div className="gmail-instructions">
            <strong>💡 How to View Labels:</strong>
            <ol>
              <li>Open your Gmail inbox in a new tab</li>
              <li>Press <kbd>F5</kbd> or click the refresh button</li>
              <li>Look for colored label tags next to each email</li>
              <li>Click on a label to filter emails by category</li>
            </ol>
          </div>
        </div>

        {/* Overview Stats */}
        <div className="stats-grid">
          <div className="stat-card">
            <div className="stat-icon">📧</div>
            <div className="stat-value">{actual_count}</div>
            <div className="stat-label">Emails Processed</div>
            <div className="stat-subtext">Requested: {requested_count}</div>
          </div>

          <div className="stat-card">
            <div className="stat-icon">🏷️</div>
            <div className="stat-value">{labeling?.success_count || 0}</div>
            <div className="stat-label">Labels Applied</div>
            <div className="stat-subtext">{successRate}% success rate</div>
          </div>

          <div className="stat-card">
            <div className="stat-icon">📊</div>
            <div className="stat-value">{totalClassified}</div>
            <div className="stat-label">Classified</div>
            <div className="stat-subtext">All emails categorized</div>
          </div>
        </div>

        {/* Category Breakdown */}
        <div className="category-section">
          <h2 className="section-title">Category Breakdown</h2>
          <div className="category-grid">
            {Object.entries(summary || {}).map(([category, count]) => {
              if (count === 0) return null;
              const info = categoryInfo[category] || categoryInfo['UNKNOWN'];
              
              return (
                <div 
                  key={category} 
                  className="category-card"
                  style={{ borderLeftColor: info.color }}
                >
                  <div className="category-header">
                    <span className="category-icon">{info.icon}</span>
                    <span className="category-name">{info.name}</span>
                  </div>
                  <div className="category-count" style={{ color: info.color }}>
                    {count}
                  </div>
                  <div className="category-percentage">
                    {((count / actual_count) * 100).toFixed(1)}%
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Labeling Results */}
        {labeling && (
          <div className="labeling-section">
            <h2 className="section-title">Labeling Results</h2>
            <div className="labeling-stats">
              <div className="labeling-stat success">
                <div className="labeling-icon">✅</div>
                <div className="labeling-info">
                  <div className="labeling-value">{labeling.success_count}</div>
                  <div className="labeling-label">Successfully Labeled</div>
                </div>
              </div>
              {labeling.failed_count > 0 && (
                <div className="labeling-stat failed">
                  <div className="labeling-icon">❌</div>
                  <div className="labeling-info">
                    <div className="labeling-value">{labeling.failed_count}</div>
                    <div className="labeling-label">Failed to Label</div>
                  </div>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Action Button */}
        <div className="action-section">
          <button 
            className="try-again-button"
            onClick={() => navigate('/dashboard')}
          >
            <svg className="button-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
            Clean More Emails
          </button>
        </div>
      </div>
    </div>
  );
};

export default Summary;

