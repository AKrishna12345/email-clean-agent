import axios from 'axios';

// Normalize to avoid double slashes when building redirect URLs like `${baseURL}/auth/...`
const API_URL = (import.meta.env.VITE_API_URL || 'http://localhost:8000').replace(/\/+$/, '');

const api = axios.create({
  baseURL: API_URL,
  withCredentials: true,
  headers: {
    'Content-Type': 'application/json',
  },
});

export default api;

