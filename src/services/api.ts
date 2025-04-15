
import axios from 'axios';

// Base URL for API requests
// For deployed application use relative URLs
const API_BASE_URL = '/api';

// Create an axios instance with default config
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor for adding auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Artwork API endpoints
export const getArtworks = async () => {
  try {
    const response = await api.get('/artworks');
    return response.data;
  } catch (error) {
    console.error('Error fetching artworks:', error);
    throw new Error('Failed to fetch artworks');
  }
};

export const getArtwork = async (id: string) => {
  try {
    const response = await api.get(`/artworks/${id}`);
    return response.data;
  } catch (error) {
    console.error(`Error fetching artwork ${id}:`, error);
    throw new Error('Failed to fetch artwork');
  }
};

// Exhibition API endpoints
export const getExhibitions = async () => {
  try {
    const response = await api.get('/exhibitions');
    return response.data;
  } catch (error) {
    console.error('Error fetching exhibitions:', error);
    throw new Error('Failed to fetch exhibitions');
  }
};

export const getExhibition = async (id: string) => {
  try {
    const response = await api.get(`/exhibitions/${id}`);
    return response.data;
  } catch (error) {
    console.error(`Error fetching exhibition ${id}:`, error);
    throw new Error('Failed to fetch exhibition');
  }
};

// Authentication endpoints
export const login = async (email: string, password: string) => {
  try {
    const response = await axios.post('/login', { email, password });
    return response.data;
  } catch (error) {
    console.error('Login error:', error);
    throw new Error('Login failed');
  }
};

export const adminLogin = async (email: string, password: string) => {
  try {
    const response = await axios.post('/admin-login', { email, password });
    return response.data;
  } catch (error) {
    console.error('Admin login error:', error);
    throw new Error('Admin login failed');
  }
};

export const register = async (userData: any) => {
  try {
    const response = await axios.post('/register', userData);
    return response.data;
  } catch (error) {
    console.error('Registration error:', error);
    throw new Error('Registration failed');
  }
};

// Contact form endpoint
export const submitContact = async (formData: any) => {
  try {
    const response = await axios.post('/contact', formData);
    return response.data;
  } catch (error) {
    console.error('Contact form submission error:', error);
    throw new Error('Failed to submit contact form');
  }
};

export default api;
