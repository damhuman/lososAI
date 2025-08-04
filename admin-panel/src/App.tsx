import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from 'react-query';
import { ConfigProvider } from 'antd';
import ukUA from 'antd/locale/uk_UA';
import AdminLayout from './components/AdminLayout';
import Login from './pages/Login';
import Dashboard from './pages/Dashboard';
import Categories from './pages/Categories';
import Products from './pages/Products';
import Users from './pages/Users';
import Orders from './pages/Orders';
import Settings from './pages/Settings';
import { AuthProvider, useAuth } from './hooks/useAuth';
import './App.css';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      refetchOnWindowFocus: false,
    },
  },
});

const ProtectedRoute: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { isAuthenticated, loading } = useAuth();
  
  if (loading) {
    return <div>Loading...</div>;
  }
  
  return isAuthenticated ? <>{children}</> : <Navigate to="/login" />;
};

const App: React.FC = () => {
  return (
    <QueryClientProvider client={queryClient}>
      <ConfigProvider locale={ukUA}>
        <AuthProvider>
          <Router basename="/adminpanel">
            <div className="App">
              <Routes>
                <Route path="/login" element={<Login />} />
                <Route
                  path="/*"
                  element={
                    <ProtectedRoute>
                      <AdminLayout>
                        <Routes>
                          <Route path="/" element={<Navigate to="/dashboard" />} />
                          <Route path="/dashboard" element={<Dashboard />} />
                          <Route path="/categories" element={<Categories />} />
                          <Route path="/products" element={<Products />} />
                          <Route path="/users" element={<Users />} />
                          <Route path="/orders" element={<Orders />} />
                          <Route path="/settings" element={<Settings />} />
                        </Routes>
                      </AdminLayout>
                    </ProtectedRoute>
                  }
                />
              </Routes>
            </div>
          </Router>
        </AuthProvider>
      </ConfigProvider>
    </QueryClientProvider>
  );
};

export default App;