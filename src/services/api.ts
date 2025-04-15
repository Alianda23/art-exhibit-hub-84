
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

// Type definitions for our data models
export interface ArtworkData {
  id: string;
  title: string;
  artist: string;
  description: string;
  price: number;
  imageUrl: string;
  medium: string;
  dimensions: string;
  year: number;
  status: string;
}

export interface ExhibitionData {
  id: string;
  title: string;
  description: string;
  location: string;
  startDate: string;
  endDate: string;
  ticketPrice: number;
  imageUrl: string;
  totalSlots: number;
  availableSlots: number;
  status: string;
}

export interface ContactMessage {
  id: string;
  name: string;
  email: string;
  phone: string | null;
  message: string;
  date: string;
  status: 'new' | 'read' | 'replied';
  source?: 'contact_form' | 'chat_bot';
}

export interface TicketData {
  id: string;
  exhibitionId: string;
  exhibitionTitle: string;
  userId: string;
  userName: string;
  userEmail: string;
  purchaseDate: string;
  ticketCode: string;
  status: 'valid' | 'used' | 'cancelled';
  price: number;
}

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

// Authentication functions
export const loginUser = async (email: string, password: string) => {
  try {
    const response = await api.post('/auth/login', { email, password });
    // Store token in localStorage
    if (response.data.token) {
      localStorage.setItem('token', response.data.token);
      localStorage.setItem('user', JSON.stringify(response.data.user));
    }
    return response.data;
  } catch (error) {
    console.error('Login error:', error);
    throw new Error('Login failed');
  }
};

export const loginAdmin = async (email: string, password: string) => {
  try {
    const response = await api.post('/auth/admin-login', { email, password });
    // Store token in localStorage
    if (response.data.token) {
      localStorage.setItem('token', response.data.token);
      localStorage.setItem('user', JSON.stringify(response.data.user));
      localStorage.setItem('isAdmin', 'true');
    }
    return response.data;
  } catch (error) {
    console.error('Admin login error:', error);
    throw new Error('Admin login failed');
  }
};

export const registerUser = async (userData: any) => {
  try {
    const response = await api.post('/auth/register', userData);
    return response.data;
  } catch (error) {
    console.error('Registration error:', error);
    throw new Error('Registration failed');
  }
};

export const logout = () => {
  localStorage.removeItem('token');
  localStorage.removeItem('user');
  localStorage.removeItem('isAdmin');
};

export const isAuthenticated = (): boolean => {
  const token = localStorage.getItem('token');
  return !!token;
};

export const isAdmin = (): boolean => {
  return localStorage.getItem('isAdmin') === 'true';
};

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

export const getAllArtworks = async (): Promise<ArtworkData[]> => {
  try {
    const response = await api.get('/artworks/all');
    return response.data.artworks || [];
  } catch (error) {
    console.error('Error fetching all artworks:', error);
    throw new Error('Failed to fetch all artworks');
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

export const createArtwork = async (artworkData: ArtworkData): Promise<ArtworkData> => {
  try {
    const response = await api.post('/artworks', artworkData);
    return response.data;
  } catch (error) {
    console.error('Error creating artwork:', error);
    throw new Error('Failed to create artwork');
  }
};

export const updateArtwork = async (id: string, artworkData: ArtworkData): Promise<ArtworkData> => {
  try {
    const response = await api.put(`/artworks/${id}`, artworkData);
    return response.data;
  } catch (error) {
    console.error(`Error updating artwork ${id}:`, error);
    throw new Error('Failed to update artwork');
  }
};

export const deleteArtwork = async (id: string): Promise<void> => {
  try {
    await api.delete(`/artworks/${id}`);
  } catch (error) {
    console.error(`Error deleting artwork ${id}:`, error);
    throw new Error('Failed to delete artwork');
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

export const getAllExhibitions = async (): Promise<ExhibitionData[]> => {
  try {
    const response = await api.get('/exhibitions/all');
    return response.data.exhibitions || [];
  } catch (error) {
    console.error('Error fetching all exhibitions:', error);
    throw new Error('Failed to fetch all exhibitions');
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

export const createExhibition = async (exhibitionData: ExhibitionData): Promise<ExhibitionData> => {
  try {
    const response = await api.post('/exhibitions', exhibitionData);
    return response.data;
  } catch (error) {
    console.error('Error creating exhibition:', error);
    throw new Error('Failed to create exhibition');
  }
};

export const updateExhibition = async (id: string, exhibitionData: ExhibitionData): Promise<ExhibitionData> => {
  try {
    const response = await api.put(`/exhibitions/${id}`, exhibitionData);
    return response.data;
  } catch (error) {
    console.error(`Error updating exhibition ${id}:`, error);
    throw new Error('Failed to update exhibition');
  }
};

export const deleteExhibition = async (id: string): Promise<void> => {
  try {
    await api.delete(`/exhibitions/${id}`);
  } catch (error) {
    console.error(`Error deleting exhibition ${id}:`, error);
    throw new Error('Failed to delete exhibition');
  }
};

// Contact form endpoint
export const submitContact = async (formData: any) => {
  try {
    const response = await api.post('/contact', formData);
    return response.data;
  } catch (error) {
    console.error('Contact form submission error:', error);
    throw new Error('Failed to submit contact form');
  }
};

export const submitContactMessage = async (formData: any) => {
  try {
    const response = await api.post('/contact/message', formData);
    return response.data;
  } catch (error) {
    console.error('Contact message submission error:', error);
    throw new Error('Failed to submit contact message');
  }
};

// Messages management
export const getAllContactMessages = async (): Promise<ContactMessage[]> => {
  try {
    const response = await api.get('/contact/messages');
    return response.data.messages || [];
  } catch (error) {
    console.error('Error fetching contact messages:', error);
    throw new Error('Failed to fetch contact messages');
  }
};

export const updateMessageStatus = async (id: string, status: 'new' | 'read' | 'replied'): Promise<ContactMessage> => {
  try {
    const response = await api.put(`/contact/messages/${id}/status`, { status });
    return response.data;
  } catch (error) {
    console.error(`Error updating message status ${id}:`, error);
    throw new Error('Failed to update message status');
  }
};

// Ticket management
export const getAllTickets = async (): Promise<TicketData[]> => {
  try {
    const response = await api.get('/tickets');
    return response.data.tickets || [];
  } catch (error) {
    console.error('Error fetching tickets:', error);
    throw new Error('Failed to fetch tickets');
  }
};

export const generateExhibitionTicket = async (exhibitionId: string, userData: any): Promise<TicketData> => {
  try {
    const response = await api.post(`/exhibitions/${exhibitionId}/tickets`, userData);
    return response.data;
  } catch (error) {
    console.error('Error generating exhibition ticket:', error);
    throw new Error('Failed to generate exhibition ticket');
  }
};

export default api;
