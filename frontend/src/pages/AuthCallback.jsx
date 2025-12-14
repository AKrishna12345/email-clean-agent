import { useEffect, useRef } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import api from '../services/api';
import './AuthCallback.css';

const AuthCallback = () => {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const { setUserData } = useAuth();
  const hasProcessed = useRef(false); // Prevent multiple executions

  useEffect(() => {
    const success = searchParams.get('success');
    const email = searchParams.get('email');
    const error = searchParams.get('error');

    // Only process if we have params and haven't processed yet
    if (!success && !error) {
      return; // Wait for params
    }

    // Create a unique key from the params to prevent duplicate processing
    const processKey = `${success}-${email}-${error}`;
    if (hasProcessed.current === processKey) {
      return; // Already processed this exact callback
    }

    console.log('AuthCallback - success:', success, 'email:', email, 'error:', error);

    // Mark as processed with this key
    hasProcessed.current = processKey;

    if (success === 'true' && email) {
      // First, set user data from email (fallback if API fails)
      const userDataFromEmail = { email: email };
      setUserData(userDataFromEmail);
      
      // Then try to fetch full user data from backend
      console.log('Fetching user data for email:', email);
      api
        .get(`/auth/me?email=${encodeURIComponent(email)}`)
        .then((response) => {
          console.log('User data received:', response.data);
          // Update with full user data if available
          setUserData(response.data);
          navigate('/dashboard', { replace: true });
        })
        .catch((err) => {
          console.error('Failed to fetch user data:', err);
          console.error('Error details:', err.response?.data || err.message);
          // User data already set from email, just navigate
          console.log('Using email-based user data, navigating to dashboard');
          navigate('/dashboard', { replace: true });
        });
    } else {
      // Handle error
      console.error('OAuth error:', error);
      navigate('/login', { replace: true });
    }
  }, [searchParams, navigate, setUserData]); // setUserData is now memoized

  return (
    <div className="callback-container">
      <div className="callback-spinner">
        <div className="spinner"></div>
      </div>
      <p className="callback-text">Completing sign in...</p>
    </div>
  );
};

export default AuthCallback;

