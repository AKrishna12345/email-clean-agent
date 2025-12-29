import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import api from '../services/api';
import './Dashboard.css';

const Dashboard = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [emailCount, setEmailCount] = useState(20);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [emailData, setEmailData] = useState(null);
  const [showEmailPopup, setShowEmailPopup] = useState(false);

  const validateCount = (count) => {
    const num = parseInt(count, 10);
    if (isNaN(num) || num < 1 || num > 100) {
      return false;
    }
    return true;
  };

  const handleCountChange = (e) => {
    const value = e.target.value;
    setError('');
    if (value === '') {
      setEmailCount('');
      return;
    }
    const num = parseInt(value, 10);
    if (!isNaN(num)) {
      if (num < 1) {
        setEmailCount(1);
      } else if (num > 100) {
        setEmailCount(100);
      } else {
        setEmailCount(num);
      }
    }
  };

  const handleClean = async (count) => {
    if (!validateCount(count)) {
      setError('Please enter a number between 1 and 100');
      return;
    }

    setError('');
    setLoading(true);

    try {
      const response = await api.post('/api/clean', {
        email: user?.email,
        count: count
      });
      console.log('Clean request sent:', response.data);
      
      // Navigate to summary page with data
      if (response.data.status === 'completed') {
        navigate('/summary', { state: { data: response.data } });
      } else if (response.data.emails && response.data.emails.length > 0) {
        // Fallback: show popup if summary page not ready
        setEmailData(response.data);
        setShowEmailPopup(true);
      } else {
        alert(`No emails found or fetched. Requested: ${count}, Actual: ${response.data.actual_count || 0}`);
      }
    } catch (err) {
      console.error('Error starting clean:', err);
      setError(err.response?.data?.detail || 'Failed to start cleaning process');
    } finally {
      setLoading(false);
    }
  };

  const handleTest = () => {
    handleClean(5);
  };

  const handleStartCleaning = () => {
    handleClean(emailCount);
  };

  return (
    <div className="dashboard-container">
      <div className="dashboard-header">
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
            <h1 className="dashboard-title">Email Clean Agent</h1>
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

      <div className="dashboard-content">
        <div className="welcome-card">
          <h2 className="welcome-title">Welcome back!</h2>
          <p className="welcome-text">
            Ready to clean up your inbox? Choose how many emails you'd like to process.
          </p>
        </div>

        <div className="instructions-card">
          <h3 className="instructions-title">📋 How It Works ⬇️</h3>
          <div className="steps-list">
            <div className="step-item">
              <div className="step-number">1</div>
              <div className="step-content">
                <strong>Enter Email Count</strong>
                <p>Choose how many of your most recent emails to process (1-100)</p>
              </div>
            </div>
            <div className="step-item">
              <div className="step-number">2</div>
              <div className="step-content">
                <strong>AI Classification</strong>
                <p>Our AI analyzes each email and categorizes it into: Important Action, FYI, Marketing, Automated, Low Value, or Unknown</p>
              </div>
            </div>
            <div className="step-item">
              <div className="step-number">3</div>
              <div className="step-content">
                <strong>Auto-Labeling</strong>
                <p>Emails are automatically labeled in your Gmail with color-coded tags</p>
              </div>
            </div>
            <div className="step-item">
              <div className="step-number">4</div>
              <div className="step-content">
                <strong>View Results</strong>
                <p>See a summary of how your emails were organized, then refresh Gmail to see the labels!</p>
              </div>
            </div>
          </div>
          <div className="output-info">
            <strong>🎯 What You'll Get:</strong> Your Gmail inbox will have color-coded labels applied to each processed email. 
            Refresh your Gmail after processing to see them!
          </div>
        </div>

        <div className="action-card">
          <div className="action-header">
            <h3 className="action-title">Clean Your Inbox</h3>
            <p className="action-subtitle">
              Select the number of most recent emails to clean (1-100)
            </p>
          </div>

          <div className="input-section">
            <label htmlFor="email-count" className="input-label">
              Number of emails
            </label>
            <div className="input-group">
              <input
                type="number"
                id="email-count"
                min="1"
                max="100"
                value={emailCount}
                onChange={handleCountChange}
                className={`email-count-input ${error ? 'input-error' : ''}`}
                placeholder="Enter number (1-100)"
                disabled={loading}
              />
              <button 
                className="test-button"
                onClick={handleTest}
                disabled={loading}
              >
                Test with 5 emails
              </button>
            </div>
            {error && <div className="error-message">{error}</div>}
            {loading && (
              <div className="processing-warning">
                <div className="warning-icon">⏱️</div>
                <div className="warning-text">
                  <strong>Processing in progress...</strong>
                  <p>This may take up to 1-2 minutes MAX. Please DO NOT refresh the page.</p>
                </div>
              </div>
            )}
          </div>

          <button 
            className="clean-button"
            onClick={handleStartCleaning}
            disabled={loading || !emailCount || !validateCount(emailCount)}
          >
            {loading ? (
              <>
                <div className="spinner-small"></div>
                Processing...
              </>
            ) : (
              <>
                <svg className="button-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                </svg>
                Start Cleaning
              </>
            )}
          </button>
        </div>
      </div>

      {/* Email Data Popup/Modal */}
      {showEmailPopup && emailData && (
        <div className="popup-overlay" onClick={() => setShowEmailPopup(false)}>
          <div className="popup-content" onClick={(e) => e.stopPropagation()}>
            <div className="popup-header">
              <h2>Email Data (Testing)</h2>
              <button className="popup-close" onClick={() => setShowEmailPopup(false)}>
                ×
              </button>
            </div>
            <div className="popup-body">
              <div className="email-summary">
                <p><strong>Requested:</strong> {emailData.requested_count} emails</p>
                <p><strong>Fetched:</strong> {emailData.actual_count} emails</p>
                {emailData.summary && (
                  <div className="classification-summary">
                    <p><strong>Classifications:</strong></p>
                    <div className="category-breakdown">
                      {Object.entries(emailData.summary).map(([category, count]) => {
                        if (count > 0) {
                          return (
                            <span key={category} className="category-badge">
                              {category}: {count}
                            </span>
                          );
                        }
                        return null;
                      })}
                    </div>
                  </div>
                )}
              </div>
              <div className="emails-list">
                {emailData.emails.map((email, index) => {
                  // Find classification for this email
                  const classification = emailData.classifications?.find(
                    c => c.email_id === email.id
                  );
                  
                  return (
                    <div key={email.id} className="email-item">
                      <div className="email-header">
                        <span className="email-number">Email {index + 1}/{emailData.actual_count}</span>
                        <span className="email-id">ID: {email.id}</span>
                      </div>
                      
                      {classification && (
                        <div className="classification-info">
                          <div className={`category-label category-${classification.category.toLowerCase()}`}>
                            {classification.category}
                          </div>
                          <div className="confidence-badge">
                            Confidence: {(classification.confidence * 100).toFixed(0)}%
                          </div>
                          <div className="classification-reason">
                            <strong>Reason:</strong> {classification.reason}
                          </div>
                        </div>
                      )}
                      
                      <div className="email-field">
                        <strong>Subject:</strong> {email.subject || 'No Subject'}
                      </div>
                      <div className="email-field">
                        <strong>From:</strong> {email.from_name || email.from} ({email.from})
                      </div>
                      <div className="email-field">
                        <strong>Date:</strong> {new Date(email.date).toLocaleString()}
                      </div>
                      <div className="email-field">
                        <strong>Snippet:</strong> {email.snippet || 'No snippet'}
                      </div>
                      <div className="email-field">
                        <strong>Body Length:</strong> {email.body?.length || 0} characters
                      </div>
                      <div className="email-field">
                        <strong>Body Preview:</strong>
                        <div className="email-body-preview">
                          {email.body ? (email.body.substring(0, 300) + (email.body.length > 300 ? '...' : '')) : 'No body'}
                        </div>
                      </div>
                      <div className="email-field">
                        <strong>Labels:</strong> {email.labels?.join(', ') || 'None'}
                      </div>
                      <hr className="email-divider" />
                    </div>
                  );
                })}
              </div>
            </div>
            <div className="popup-footer">
              <button className="popup-close-button" onClick={() => setShowEmailPopup(false)}>
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Dashboard;

