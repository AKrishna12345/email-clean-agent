import { Navigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import '../pages/AuthCallback.css';

const ProtectedRoute = ({ children }) => {
  const { isAuthenticated, loading } = useAuth();

  if (loading) {
    return (
      <div style={{ 
        minHeight: '100vh', 
        display: 'flex', 
        alignItems: 'center', 
        justifyContent: 'center',
        flexDirection: 'column',
        gap: '16px'
      }}>
        <div className="spinner"></div>
        <p style={{ color: '#5f6368', fontSize: '14px' }}>Loading...</p>
      </div>
    );
  }

  return isAuthenticated ? children : <Navigate to="/login" replace />;
};

export default ProtectedRoute;

