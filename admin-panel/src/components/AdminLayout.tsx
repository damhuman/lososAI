import React, { useState, useEffect } from 'react';
import { Layout, Menu, Avatar, Dropdown, Button, theme, Drawer } from 'antd';
import {
  DashboardOutlined,
  AppstoreOutlined,
  ShoppingOutlined,
  TeamOutlined,
  ShoppingCartOutlined,
  SettingOutlined,
  LogoutOutlined,
  MenuFoldOutlined,
  MenuUnfoldOutlined,
} from '@ant-design/icons';
import { useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';
import { useResponsive } from '../hooks/useResponsive';

const { Header, Sider, Content } = Layout;

interface AdminLayoutProps {
  children: React.ReactNode;
}

const AdminLayout: React.FC<AdminLayoutProps> = ({ children }) => {
  const [collapsed, setCollapsed] = useState(false);
  const [mobileDrawerVisible, setMobileDrawerVisible] = useState(false);
  const navigate = useNavigate();
  const location = useLocation();
  const { user, logout } = useAuth();
  const { isMobile } = useResponsive();
  const {
    token: { colorBgContainer },
  } = theme.useToken();

  // Auto-collapse sidebar on mobile
  useEffect(() => {
    if (isMobile) {
      setCollapsed(true);
    }
  }, [isMobile]);

  const menuItems = [
    {
      key: '/dashboard',
      icon: <DashboardOutlined />,
      label: 'Панель управління',
    },
    {
      key: '/categories',
      icon: <AppstoreOutlined />,
      label: 'Категорії',
    },
    {
      key: '/products',
      icon: <ShoppingOutlined />,
      label: 'Товари',
    },
    {
      key: '/users',
      icon: <TeamOutlined />,
      label: 'Користувачі',
    },
    {
      key: '/orders',
      icon: <ShoppingCartOutlined />,
      label: 'Замовлення',
    },
    {
      key: '/settings',
      icon: <SettingOutlined />,
      label: 'Налаштування',
    },
  ];

  const handleMenuClick = ({ key }: { key: string }) => {
    navigate(key);
    if (isMobile) {
      setMobileDrawerVisible(false);
    }
  };

  const toggleMobileMenu = () => {
    if (isMobile) {
      setMobileDrawerVisible(!mobileDrawerVisible);
    } else {
      setCollapsed(!collapsed);
    }
  };

  const handleLogout = async () => {
    await logout();
    navigate('/login');
  };

  const userMenuItems = [
    {
      key: 'logout',
      icon: <LogoutOutlined />,
      label: 'Вийти',
      onClick: handleLogout,
    },
  ];

  const SideMenu = () => (
    <>
      <div className="demo-logo-vertical" style={{ 
        height: 64, 
        margin: 0,
        background: '#002140',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        color: 'white',
        fontWeight: 'bold',
        fontSize: collapsed && !isMobile ? '16px' : '18px',
        borderBottom: '1px solid rgba(255, 255, 255, 0.1)'
      }}>
        {collapsed && !isMobile ? '🐟' : '🐟 Seafood Admin'}
      </div>
      <Menu
        theme="dark"
        mode="inline"
        selectedKeys={[location.pathname]}
        items={menuItems}
        onClick={handleMenuClick}
        style={{
          fontSize: isMobile ? '16px' : '14px'
        }}
      />
    </>
  );

  return (
    <Layout style={{ minHeight: '100vh' }}>
      {/* Desktop Sidebar */}
      {!isMobile && (
        <Sider 
          trigger={null} 
          collapsible 
          collapsed={collapsed}
          style={{
            background: '#001529',
            borderRight: '1px solid rgba(0, 0, 0, 0.1)'
          }}
        >
          <SideMenu />
        </Sider>
      )}

      {/* Mobile Drawer */}
      <Drawer
        title="Seafood Admin"
        placement="left"
        closable={true}
        onClose={() => setMobileDrawerVisible(false)}
        open={isMobile && mobileDrawerVisible}
        width={280}
        bodyStyle={{ padding: 0, backgroundColor: '#001529' }}
        headerStyle={{ backgroundColor: '#001529', color: 'white', borderBottom: '1px solid #303030' }}
      >
        <Menu
          theme="dark"
          mode="inline"
          selectedKeys={[location.pathname]}
          items={menuItems}
          onClick={handleMenuClick}
          style={{ backgroundColor: 'transparent', fontSize: '16px' }}
        />
      </Drawer>

      <Layout>
        <Header style={{ 
          padding: 0, 
          background: colorBgContainer,
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          position: 'sticky',
          top: 0,
          zIndex: 1000,
          boxShadow: '0 1px 4px rgba(0,0,0,0.08)',
          borderBottom: '1px solid #f0f0f0'
        }}>
          <Button
            type="text"
            icon={collapsed ? <MenuUnfoldOutlined /> : <MenuFoldOutlined />}
            onClick={toggleMobileMenu}
            style={{
              fontSize: isMobile ? '18px' : '16px',
              width: isMobile ? 48 : 64,
              height: isMobile ? 48 : 64,
            }}
          />
          <div style={{ marginRight: isMobile ? 8 : 24 }}>
            <Dropdown menu={{ items: userMenuItems }} placement="bottomRight">
              <div style={{ 
                display: 'flex', 
                alignItems: 'center', 
                cursor: 'pointer',
                padding: isMobile ? '0 8px' : '0 16px'
              }}>
                <Avatar 
                  size={isMobile ? "small" : "default"} 
                  style={{ 
                    backgroundColor: '#1890ff', 
                    marginRight: isMobile ? 4 : 8 
                  }}
                >
                  {user?.username?.charAt(0).toUpperCase()}
                </Avatar>
                {!isMobile && <span>{user?.username}</span>}
              </div>
            </Dropdown>
          </div>
        </Header>
        <Content
          style={{
            margin: 0,
            padding: isMobile ? 16 : 24,
            minHeight: 'calc(100vh - 64px)',
            background: colorBgContainer,
            overflow: 'auto'
          }}
        >
          {children}
        </Content>
      </Layout>
    </Layout>
  );
};

export default AdminLayout;