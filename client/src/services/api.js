import axios from 'axios';

/**
 * Centralized Axios client for HypothesisLab AI
 * Communicates with the FastAPI backend at VITE_API_BASE_URL
 */
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1';

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 45000,
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
  },
});

// Request interceptor: add authentication tokens or correlation IDs if needed
apiClient.interceptors.request.use(
  (config) => {
    // Teammate integration point: Auth header injection can be added here
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor: standardize error messages
apiClient.interceptors.response.use(
  (response) => {
    return response.data;
  },
  (error) => {
    const customError = {
      status: error.response?.status || 500,
      message:
        error.response?.data?.detail ||
        error.response?.data?.message ||
        error.message ||
        'Unable to reach the HypothesisLab backend service. Please ensure FastAPI server is running.',
      raw: error,
    };
    return Promise.reject(customError);
  }
);

export default apiClient;

