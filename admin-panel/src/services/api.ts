import axios from 'axios';
import { Category, Product, User, Order, PromoCode, District, AdminUser, PaginatedResponse } from '../types';

const API_BASE_URL = process.env.REACT_APP_API_URL || '/api/v1';

// Create axios instance
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add basic auth to requests
api.interceptors.request.use((config) => {
  const username = localStorage.getItem('admin_username');
  const password = localStorage.getItem('admin_password');
  if (username && password) {
    const encodedCredentials = btoa(`${username}:${password}`);
    config.headers.Authorization = `Basic ${encodedCredentials}`;
  }
  return config;
});

// Auth API
export const authAPI = {
  login: async (username: string, password: string): Promise<AdminUser> => {
    // Store credentials for basic auth
    localStorage.setItem('admin_username', username);
    localStorage.setItem('admin_password', password);
    
    // Verify credentials by making a test request
    try {
      const response = await api.get('/admin/verify');
      return { username, token: btoa(`${username}:${password}`) };
    } catch (error) {
      // Clear stored credentials if login fails
      localStorage.removeItem('admin_username');
      localStorage.removeItem('admin_password');
      throw error;
    }
  },
  
  logout: async (): Promise<void> => {
    localStorage.removeItem('admin_username');
    localStorage.removeItem('admin_password');
  },
  
  verifyToken: async (): Promise<boolean> => {
    try {
      await api.get('/admin/verify');
      return true;
    } catch {
      return false;
    }
  }
};

// Categories API
export const categoriesAPI = {
  getAll: async (): Promise<Category[]> => {
    const response = await api.get('/admin/categories');
    return response.data;
  },
  
  create: async (category: Omit<Category, 'id'>): Promise<Category> => {
    const response = await api.post('/admin/categories', category);
    return response.data;
  },
  
  update: async (id: string, category: Partial<Category>): Promise<Category> => {
    const response = await api.put(`/admin/categories/${id}`, category);
    return response.data;
  },
  
  delete: async (id: string): Promise<void> => {
    await api.delete(`/admin/categories/${id}`);
  }
};

// Products API
export const productsAPI = {
  getAll: async (page = 1, size = 20): Promise<PaginatedResponse<Product>> => {
    const response = await api.get(`/admin/products?page=${page}&size=${size}`);
    return response.data;
  },
  
  getById: async (id: string): Promise<Product> => {
    const response = await api.get(`/admin/products/${id}`);
    return response.data;
  },
  
  create: async (product: Omit<Product, 'id' | 'category'>): Promise<Product> => {
    const response = await api.post('/admin/products', product);
    return response.data;
  },
  
  update: async (id: string, product: Partial<Product>): Promise<Product> => {
    const response = await api.put(`/admin/products/${id}`, product);
    return response.data;
  },
  
  delete: async (id: string): Promise<void> => {
    await api.delete(`/admin/products/${id}`);
  },
  
  uploadImage: async (file: File): Promise<{ url: string }> => {
    const formData = new FormData();
    formData.append('image', file);
    const response = await api.post('/admin/upload/image', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },
  
  getStats: async (): Promise<{
    total_products: number;
    total_categories: number;
    featured_products: number;
    active_products: number;
  }> => {
    const response = await api.get('/admin/products/stats');
    return response.data;
  }
};

// Users API
export const usersAPI = {
  getAll: async (page = 1, size = 20): Promise<PaginatedResponse<User>> => {
    const response = await api.get(`/admin/users?page=${page}&size=${size}`);
    return response.data;
  },
  
  getById: async (id: number): Promise<User> => {
    const response = await api.get(`/admin/users/${id}`);
    return response.data;
  },
  
  update: async (id: number, user: Partial<User>): Promise<User> => {
    const response = await api.put(`/admin/users/${id}`, user);
    return response.data;
  },
  
  getStats: async (): Promise<{
    total: number;
    active: number;
    gold_clients: number;
    blocked: number;
  }> => {
    const response = await api.get('/admin/users/stats');
    return response.data;
  }
};

// Orders API
export const ordersAPI = {
  getAll: async (
    page = 1, 
    size = 20, 
    status?: string,
    startDate?: string,
    endDate?: string
  ): Promise<PaginatedResponse<Order>> => {
    const params = new URLSearchParams({
      page: page.toString(),
      size: size.toString(),
    });
    
    if (status) params.append('status', status);
    if (startDate) params.append('start_date', startDate);
    if (endDate) params.append('end_date', endDate);
    
    const response = await api.get(`/admin/orders?${params.toString()}`);
    return response.data;
  },
  
  getById: async (id: number): Promise<Order> => {
    const response = await api.get(`/admin/orders/${id}`);
    return response.data;
  },
  
  updateStatus: async (id: number, status: Order['status']): Promise<Order> => {
    const response = await api.put(`/admin/orders/${id}/status`, { status });
    return response.data;
  },
  
  getStats: async (startDate?: string, endDate?: string): Promise<{
    total_orders: number;
    total_revenue: number;
    avg_order_value: number;
    orders_by_status: Record<string, number>;
  }> => {
    const params = new URLSearchParams();
    if (startDate) params.append('start_date', startDate);
    if (endDate) params.append('end_date', endDate);
    
    const response = await api.get(`/admin/orders/stats?${params.toString()}`);
    return response.data;
  },
  
  exportReport: async (startDate: string, endDate: string): Promise<Blob> => {
    const response = await api.get(`/admin/orders/export`, {
      params: { start_date: startDate, end_date: endDate },
      responseType: 'blob',
    });
    return response.data;
  }
};

// Districts API
export const districtsAPI = {
  getAll: async (): Promise<District[]> => {
    const response = await api.get('/admin/districts');
    return response.data;
  },
  
  create: async (district: Omit<District, 'id'>): Promise<District> => {
    const response = await api.post('/admin/districts', district);
    return response.data;
  },
  
  update: async (id: number, district: Partial<District>): Promise<District> => {
    const response = await api.put(`/admin/districts/${id}`, district);
    return response.data;
  },
  
  delete: async (id: number): Promise<void> => {
    await api.delete(`/admin/districts/${id}`);
  }
};

// Promo codes API
export const promoCodesAPI = {
  getAll: async (): Promise<PromoCode[]> => {
    const response = await api.get('/admin/promo-codes');
    return response.data;
  },
  
  create: async (promoCode: Omit<PromoCode, 'id' | 'usage_count'>): Promise<PromoCode> => {
    const response = await api.post('/admin/promo-codes', promoCode);
    return response.data;
  },
  
  update: async (id: number, promoCode: Partial<PromoCode>): Promise<PromoCode> => {
    const response = await api.put(`/admin/promo-codes/${id}`, promoCode);
    return response.data;
  },
  
  delete: async (id: number): Promise<void> => {
    await api.delete(`/admin/promo-codes/${id}`);
  }
};

export default api;