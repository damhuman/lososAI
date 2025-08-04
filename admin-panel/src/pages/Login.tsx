import React, { useState } from 'react';
import { Form, Input, Button, Card, message, Layout } from 'antd';
import { UserOutlined, LockOutlined } from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';

const { Content } = Layout;

const Login: React.FC = () => {
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();
  const navigate = useNavigate();

  const onFinish = async (values: { username: string; password: string }) => {
    setLoading(true);
    try {
      await login(values.username, values.password);
      message.success('Успішний вхід!');
      navigate('/dashboard');
    } catch (error) {
      message.error('Невірні дані для входу');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Layout style={{ minHeight: '100vh', background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)' }}>
      <Content style={{ 
        display: 'flex', 
        justifyContent: 'center', 
        alignItems: 'center',
        padding: '20px'
      }}>
        <Card
          title={
            <div style={{ textAlign: 'center' }}>
              <h2 style={{ margin: 0, color: '#1890ff' }}>🐟 Seafood Admin</h2>
              <p style={{ margin: '8px 0 0 0', color: '#666' }}>Панель управління</p>
            </div>
          }
          style={{ width: 400, maxWidth: '100%' }}
          bodyStyle={{ padding: '32px' }}
        >
          <Form
            name="login"
            initialValues={{ remember: true }}
            onFinish={onFinish}
            size="large"
          >
            <Form.Item
              name="username"
              rules={[{ required: true, message: 'Будь ласка, введіть ім\'я користувача!' }]}
            >
              <Input 
                prefix={<UserOutlined />} 
                placeholder="Ім'я користувача" 
              />
            </Form.Item>
            <Form.Item
              name="password"
              rules={[{ required: true, message: 'Будь ласка, введіть пароль!' }]}
            >
              <Input.Password
                prefix={<LockOutlined />}
                placeholder="Пароль"
              />
            </Form.Item>
            <Form.Item style={{ marginBottom: 0 }}>
              <Button 
                type="primary" 
                htmlType="submit" 
                block 
                loading={loading}
                style={{ height: 48, fontSize: 16 }}
              >
                Увійти
              </Button>
            </Form.Item>
          </Form>
        </Card>
      </Content>
    </Layout>
  );
};

export default Login;