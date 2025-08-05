import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { authAPI } from '../services/api';
import { AdminUser } from '../types';

interface AuthContextType {
  user: AdminUser | null;
  isAuthenticated: boolean;
  loading: boolean;
  login: (username: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

interface AuthProviderProps {
  children: ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [user, setUser] = useState<AdminUser | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const initAuth = async () => {
      const accessToken = localStorage.getItem('access_token');
      const storedUser = localStorage.getItem('admin_user');
      
      if (accessToken && storedUser) {
        try {
          // Try to get current user info to verify token
          const currentUser = await authAPI.getCurrentUser();
          setUser(currentUser);
        } catch (error) {
          // If token is invalid, try to refresh
          const refreshToken = localStorage.getItem('refresh_token');
          if (refreshToken) {
            try {
              const tokens = await authAPI.refresh();
              localStorage.setItem('access_token', tokens.access_token);
              localStorage.setItem('refresh_token', tokens.refresh_token);
              
              // Get user info with new token
              const currentUser = await authAPI.getCurrentUser();
              setUser(currentUser);
            } catch (refreshError) {
              // Refresh failed, clear everything
              localStorage.removeItem('access_token');
              localStorage.removeItem('refresh_token');
              localStorage.removeItem('admin_user');
            }
          } else {
            // No refresh token, clear everything
            localStorage.removeItem('access_token');
            localStorage.removeItem('admin_user');
          }
        }
      }
      setLoading(false);
    };

    initAuth();
  }, []);

  const login = async (username: string, password: string) => {
    try {
      const userData = await authAPI.login(username, password);
      setUser(userData);
    } catch (error) {
      throw error;
    }
  };

  const logout = async () => {
    try {
      await authAPI.logout();
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      setUser(null);
    }
  };

  const value = {
    user,
    isAuthenticated: !!user,
    loading,
    login,
    logout,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};