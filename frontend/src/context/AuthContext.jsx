import { createContext, useContext, useState, useEffect, useCallback } from 'react';
import api from '../services/api';

const AuthContext = createContext(null);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Check if user is logged in from localStorage
    const savedUser = localStorage.getItem('user');
    if (savedUser) {
      try {
        const userData = JSON.parse(savedUser);
        setUser(userData);
      } catch (e) {
        localStorage.removeItem('user');
      }
    }
    setLoading(false);
  }, []);

  const login = () => {
    // Redirect to backend OAuth endpoint
    window.location.href = `${api.defaults.baseURL}/auth/google/login`;
  };

  const logout = async () => {
    try {
      await api.post('/auth/logout');
    } catch (e) {
      console.error('Logout error:', e);
    }
    setUser(null);
    localStorage.removeItem('user');
  };

  const setUserData = useCallback((userData) => {
    setUser(userData);
    localStorage.setItem('user', JSON.stringify(userData));
  }, []);

  const value = {
    user,
    loading,
    login,
    logout,
    setUserData,
    isAuthenticated: !!user,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

