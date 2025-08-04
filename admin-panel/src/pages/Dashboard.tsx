import React from 'react';
import { Card, Row, Col, Statistic, Table, Tag } from 'antd';
import { 
  ShoppingCartOutlined, 
  UserOutlined, 
  DollarOutlined,
  RiseOutlined,
  AppstoreOutlined,
  TagsOutlined
} from '@ant-design/icons';
import { useQuery } from 'react-query';
import { ordersAPI, usersAPI, productsAPI, categoriesAPI } from '../services/api';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

const Dashboard: React.FC = () => {
  const { data: orderStats } = useQuery('order-stats', () => ordersAPI.getStats());
  const { data: userStats } = useQuery('user-stats', () => usersAPI.getStats());
  const { data: productStats } = useQuery('product-stats', () => productsAPI.getStats());
  const { data: recentOrders } = useQuery('recent-orders', () => 
    ordersAPI.getAll(1, 5)
  );

  const chartData = [
    { name: 'Пн', orders: 12, revenue: 1200 },
    { name: 'Вт', orders: 19, revenue: 1900 },
    { name: 'Ср', orders: 15, revenue: 1500 },
    { name: 'Чт', orders: 22, revenue: 2200 },
    { name: 'Пт', orders: 28, revenue: 2800 },
    { name: 'Сб', orders: 35, revenue: 3500 },
    { name: 'Нд', orders: 30, revenue: 3000 },
  ];

  const columns = [
    {
      title: 'ID',
      dataIndex: 'id',
      key: 'id',
    },
    {
      title: 'Клієнт',
      dataIndex: 'contact_name',
      key: 'contact_name',
    },
    {
      title: 'Сума',
      dataIndex: 'total_amount',
      key: 'total_amount',
      render: (amount: number) => `${amount} грн`,
    },
    {
      title: 'Статус',
      dataIndex: 'status',
      key: 'status',
      render: (status: string) => {
        const colors = {
          pending: 'orange',
          confirmed: 'blue',
          preparing: 'cyan',
          delivering: 'purple',
          delivered: 'green',
          cancelled: 'red',
        };
        return <Tag color={colors[status as keyof typeof colors]}>{status}</Tag>;
      },
    },
    {
      title: 'Дата',
      dataIndex: 'created_at',
      key: 'created_at',
      render: (date: string) => new Date(date).toLocaleDateString('uk-UA'),
    },
  ];

  return (
    <div>
      <h1 style={{ marginBottom: 24 }}>Панель управління</h1>
      
      <Row gutter={16} style={{ marginBottom: 24 }}>
        <Col span={6}>
          <Card>
            <Statistic
              title="Загальна кількість замовлень"
              value={orderStats?.total_orders || 0}
              prefix={<ShoppingCartOutlined />}
              valueStyle={{ color: '#3f8600' }}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="Загальний дохід"
              value={orderStats?.total_revenue || 0}
              prefix={<DollarOutlined />}
              suffix="грн"
              valueStyle={{ color: '#cf1322' }}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="Загальна кількість товарів"
              value={productStats?.total_products || 0}
              prefix={<AppstoreOutlined />}
              valueStyle={{ color: '#1890ff' }}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="Кількість категорій"
              value={productStats?.total_categories || 0}
              prefix={<TagsOutlined />}
              valueStyle={{ color: '#722ed1' }}
            />
          </Card>
        </Col>
      </Row>

      <Row gutter={16} style={{ marginBottom: 24 }}>
        <Col span={6}>
          <Card>
            <Statistic
              title="Середня сума замовлення"
              value={orderStats?.avg_order_value || 0}
              prefix={<RiseOutlined />}
              suffix="грн"
              precision={2}
              valueStyle={{ color: '#52c41a' }}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="Загальна кількість користувачів"
              value={userStats?.total || 0}
              prefix={<UserOutlined />}
              valueStyle={{ color: '#fa8c16' }}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="Рекомендовані товари"
              value={productStats?.featured_products || 0}
              prefix={<RiseOutlined />}
              valueStyle={{ color: '#eb2f96' }}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="Активні товари"
              value={productStats?.active_products || 0}
              prefix={<AppstoreOutlined />}
              valueStyle={{ color: '#13c2c2' }}
            />
          </Card>
        </Col>
      </Row>

      <Row gutter={16} style={{ marginBottom: 24 }}>
        <Col span={16}>
          <Card title="Статистика замовлень за тиждень">
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" />
                <YAxis />
                <Tooltip />
                <Bar dataKey="orders" fill="#1890ff" />
              </BarChart>
            </ResponsiveContainer>
          </Card>
        </Col>
        <Col span={8}>
          <Card title="Статистика користувачів">
            <Statistic
              title="Активні користувачі"
              value={userStats?.active || 0}
              suffix={`/ ${userStats?.total || 0}`}
              style={{ marginBottom: 16 }}
            />
            <Statistic
              title="Золоті клієнти"
              value={userStats?.gold_clients || 0}
              valueStyle={{ color: '#faad14' }}
              style={{ marginBottom: 16 }}
            />
            <Statistic
              title="Заблоковані"
              value={userStats?.blocked || 0}
              valueStyle={{ color: '#f5222d' }}
            />
          </Card>
        </Col>
      </Row>

      <Card title="Останні замовлення">
        <Table
          columns={columns}
          dataSource={recentOrders?.items || []}
          rowKey="id"
          pagination={false}
        />
      </Card>
    </div>
  );
};

export default Dashboard;