import { useAuth } from '../context/AuthContext';
import './Login.css';

const Login = () => {
  const { login } = useAuth();

  return (
    <div className="login-container">
      <div className="login-card">
        <div className="login-header">
          <div className="gmail-logo">
            <svg viewBox="0 0 24 24" width="40" height="40">
              <path
                fill="#EA4335"
                d="M24 5.457v13.909c0 .904-.732 1.636-1.636 1.636h-3.819V11.73L12 16.64l-6.545-4.91v9.273H1.636A1.636 1.636 0 0 1 0 19.366V5.457c0-2.023 2.309-3.178 3.927-1.964L5.455 4.64 12 9.548l6.545-4.91 1.528-1.145C21.69 2.28 24 3.434 24 5.457z"
              />
            </svg>
          </div>
          <h1 className="login-title">Email Clean Agent</h1>
          <p className="login-subtitle">Clean up your inbox with AI-powered automation</p>
        </div>

        <div className="login-content">
          <div className="instructions-box">
            <h3 className="instructions-title">What This App Does ⬇️</h3>
            <p className="instructions-text">
              Email Clean Agent uses AI to automatically classify and organize your Gmail inbox. 
              Here's what will happen:
            </p>
            <ol className="instructions-list">
              <li>You'll select how many emails to process (1-100)</li>
              <li>AI will analyze each email and categorize it</li>
              <li>Emails will be automatically labeled in your Gmail with color-coded tags</li>
              <li>You'll see a summary of how your emails were organized</li>
            </ol>
            <div className="output-preview">
              <strong>📧 End Result:</strong> Your Gmail inbox will have color-coded labels like 
              <span className="label-preview red">IMPORTANT_ACTION</span>, 
              <span className="label-preview green">FYI_READ_LATER</span>, 
              <span className="label-preview yellow">MARKETING</span>, and more!
            </div>
          </div>

          <div className="oauth-warning" role="note" aria-label="Google permissions notice">
            <div className="oauth-warning-title">Important (first-time sign in)</div>
            <div className="oauth-warning-text">
              On the Google consent screen, please <strong>check/allow all requested permissions</strong>.
              If you skip any, Google may prompt you to sign in a second time.
            </div>
          </div>

          <p className="login-description">
            Sign in with your Google account to get started. We only need access to organize your emails.
          </p>

          <button onClick={login} className="google-signin-button">
            <svg className="google-icon" viewBox="0 0 24 24" width="20" height="20">
              <path
                fill="#4285F4"
                d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
              />
              <path
                fill="#34A853"
                d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
              />
              <path
                fill="#FBBC05"
                d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"
              />
              <path
                fill="#EA4335"
                d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"
              />
            </svg>
            <span>Sign in with Google</span>
          </button>

          <div className="login-features">
            <div className="feature-item">
              <svg className="feature-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <span>AI-powered email classification</span>
            </div>
            <div className="feature-item">
              <svg className="feature-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
              </svg>
              <span>Automated cleanup actions</span>
            </div>
            <div className="feature-item">
              <svg className="feature-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <span>Quick and efficient</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Login;

