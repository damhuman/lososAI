import React, { useState } from 'react';
import { 
  Table, 
  Button, 
  Modal, 
  Form, 
  Switch, 
  message, 
  Space,
  Tag,
  Avatar,
  DatePicker,
  Input,
  Select
} from 'antd';
import { 
  EditOutlined, 
  UserOutlined,
  SearchOutlined,
  FilterOutlined
} from '@ant-design/icons';
import { useQuery, useMutation, useQueryClient } from 'react-query';
import { usersAPI } from '../services/api';
import { User } from '../types';
import moment from 'moment';

const { RangePicker } = DatePicker;
const { Option } = Select;

const Users: React.FC = () => {
  const [isModalVisible, setIsModalVisible] = useState(false);
  const [editingUser, setEditingUser] = useState<User | null>(null);
  const [searchText, setSearchText] = useState('');
  const [statusFilter, setStatusFilter] = useState<string>('all');
  const [form] = Form.useForm();
  const queryClient = useQueryClient();

  const { data: usersData, loading } = useQuery(
    'users', 
    () => usersAPI.getAll(1, 100)
  );

  const updateMutation = useMutation(
    (data: { id: number; user: Partial<User> }) =>
      usersAPI.update(data.id, data.user),
    {
      onSuccess: () => {
        queryClient.invalidateQueries('users');
        message.success('Користувача оновлено успішно!');
        setIsModalVisible(false);
        setEditingUser(null);
        form.resetFields();
      },
      onError: () => {
        message.error('Помилка при оновленні користувача');
      },
    }
  );

  const handleEdit = (user: User) => {
    setEditingUser(user);
    form.setFieldsValue(user);
    setIsModalVisible(true);
  };

  const handleSubmit = async () => {
    try {
      const values = await form.validateFields();
      
      if (editingUser) {
        updateMutation.mutate({ id: editingUser.id, user: values });
      }
    } catch (error) {
      console.error('Form validation failed:', error);
    }
  };

  const filteredUsers = usersData?.items?.filter(user => {
    const matchesSearch = 
      user.first_name.toLowerCase().includes(searchText.toLowerCase()) ||
      user.last_name?.toLowerCase().includes(searchText.toLowerCase()) ||
      user.username?.toLowerCase().includes(searchText.toLowerCase());
    
    const matchesStatus = statusFilter === 'all' || 
      (statusFilter === 'active' && !user.is_blocked) ||
      (statusFilter === 'blocked' && user.is_blocked) ||
      (statusFilter === 'gold' && user.is_gold_client) ||
      (statusFilter === 'premium' && user.is_premium);

    return matchesSearch && matchesStatus;
  });

  const columns = [
    {
      title: 'Аватар',
      key: 'avatar',
      width: 80,
      render: (_: any, record: User) => (
        <Avatar 
          size={40}
          style={{ backgroundColor: record.is_gold_client ? '#faad14' : '#1890ff' }}
          icon={<UserOutlined />}
        >
          {record.first_name.charAt(0)}
        </Avatar>
      ),
    },
    {
      title: 'ID',
      dataIndex: 'id',
      key: 'id',
      width: 100,
    },
    {
      title: 'Ім\'я',
      key: 'name',
      render: (_: any, record: User) => (
        <div>
          <div style={{ fontWeight: 500 }}>
            {record.first_name} {record.last_name || ''}
          </div>
          {record.username && (
            <div style={{ color: '#666', fontSize: '12px' }}>
              @{record.username}
            </div>
          )}
        </div>
      ),
    },
    {
      title: 'Статус',
      key: 'status',
      render: (_: any, record: User) => (
        <Space direction="vertical" size="small">
          <Tag color={record.is_blocked ? 'red' : 'green'}>
            {record.is_blocked ? 'Заблокований' : 'Активний'}
          </Tag>
          {record.is_gold_client && <Tag color="gold">Золотий клієнт</Tag>}
          {record.is_premium && <Tag color="purple">Преміум</Tag>}
          {record.is_bot && <Tag color="blue">Бот</Tag>}
        </Space>
      ),
    },
    {
      title: 'Мова',
      dataIndex: 'language_code',
      key: 'language_code',
      width: 80,
      render: (lang: string) => lang?.toUpperCase() || '—',
    },
    {
      title: 'Дата реєстрації',
      dataIndex: 'created_at',
      key: 'created_at',
      render: (date: string) => moment(date).format('DD.MM.YYYY HH:mm'),
    },
    {
      title: 'Дії',
      key: 'actions',
      width: 100,
      render: (_: any, record: User) => (
        <Button
          type="primary"
          ghost
          size="small"
          icon={<EditOutlined />}
          onClick={() => handleEdit(record)}
        >
          Редагувати
        </Button>
      ),
    },
  ];

  return (
    <div>
      <div style={{ 
        display: 'flex', 
        justifyContent: 'space-between', 
        alignItems: 'center', 
        marginBottom: 24 
      }}>
        <h1>Користувачі</h1>
      </div>

      <div style={{ marginBottom: 16, display: 'flex', gap: 16 }}>
        <Input
          placeholder="Пошук за ім'ям або username"
          prefix={<SearchOutlined />}
          value={searchText}
          onChange={(e) => setSearchText(e.target.value)}
          style={{ width: 300 }}
        />
        <Select
          value={statusFilter}
          onChange={setStatusFilter}
          style={{ width: 150 }}
          prefix={<FilterOutlined />}
        >
          <Option value="all">Всі користувачі</Option>
          <Option value="active">Активні</Option>
          <Option value="blocked">Заблоковані</Option>
          <Option value="gold">Золоті клієнти</Option>
          <Option value="premium">Преміум</Option>
        </Select>
      </div>

      <Table
        columns={columns}
        dataSource={filteredUsers}
        rowKey="id"
        loading={loading}
        pagination={{
          pageSize: 20,
          showSizeChanger: true,
          showQuickJumper: true,
          showTotal: (total) => `Всього: ${total} користувачів`,
        }}
      />

      <Modal
        title="Редагувати користувача"
        open={isModalVisible}
        onOk={handleSubmit}
        onCancel={() => {
          setIsModalVisible(false);
          setEditingUser(null);
          form.resetFields();
        }}
        confirmLoading={updateMutation.isLoading}
      >
        <Form
          form={form}
          layout="vertical"
        >
          <Form.Item
            name="first_name"
            label="Ім'я"
            rules={[{ required: true, message: 'Будь ласка, введіть ім\'я!' }]}
          >
            <Input />
          </Form.Item>

          <Form.Item
            name="last_name"
            label="Прізвище"
          >
            <Input />
          </Form.Item>

          <Form.Item
            name="username"
            label="Username"
          >
            <Input />
          </Form.Item>

          <Form.Item
            name="language_code"
            label="Мова"
          >
            <Select>
              <Option value="uk">Українська</Option>
              <Option value="ru">Російська</Option>
              <Option value="en">Англійська</Option>
            </Select>
          </Form.Item>

          <Space>
            <Form.Item
              name="is_gold_client"
              label="Золотий клієнт"
              valuePropName="checked"
            >
              <Switch />
            </Form.Item>

            <Form.Item
              name="is_premium"
              label="Преміум"
              valuePropName="checked"
            >
              <Switch />
            </Form.Item>

            <Form.Item
              name="is_blocked"
              label="Заблокований"
              valuePropName="checked"
            >
              <Switch />
            </Form.Item>
          </Space>
        </Form>
      </Modal>
    </div>
  );
};

export default Users;