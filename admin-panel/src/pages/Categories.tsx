import React, { useState } from 'react';
import { 
  Table, 
  Button, 
  Modal, 
  Form, 
  Input, 
  Switch, 
  message, 
  Popconfirm,
  Space,
  Tag,
  InputNumber
} from 'antd';
import { PlusOutlined, EditOutlined, DeleteOutlined } from '@ant-design/icons';
import { useQuery, useMutation, useQueryClient } from 'react-query';
import { categoriesAPI } from '../services/api';
import { Category } from '../types';

const Categories: React.FC = () => {
  const [isModalVisible, setIsModalVisible] = useState(false);
  const [editingCategory, setEditingCategory] = useState<Category | null>(null);
  const [form] = Form.useForm();
  const queryClient = useQueryClient();

  const { data: categories, isLoading } = useQuery('categories', categoriesAPI.getAll);

  const createMutation = useMutation(categoriesAPI.create, {
    onSuccess: () => {
      queryClient.invalidateQueries('categories');
      message.success('Категорію створено успішно!');
      setIsModalVisible(false);
      form.resetFields();
    },
    onError: () => {
      message.error('Помилка при створенні категорії');
    },
  });

  const updateMutation = useMutation(
    (data: { id: string; category: Partial<Category> }) =>
      categoriesAPI.update(data.id, data.category),
    {
      onSuccess: () => {
        queryClient.invalidateQueries('categories');
        message.success('Категорію оновлено успішно!');
        setIsModalVisible(false);
        setEditingCategory(null);
        form.resetFields();
      },
      onError: () => {
        message.error('Помилка при оновленні категорії');
      },
    }
  );

  const deleteMutation = useMutation(categoriesAPI.delete, {
    onSuccess: () => {
      queryClient.invalidateQueries('categories');
      message.success('Категорію видалено успішно!');
    },
    onError: () => {
      message.error('Помилка при видаленні категорії');
    },
  });

  const handleAdd = () => {
    setEditingCategory(null);
    form.resetFields();
    setIsModalVisible(true);
  };

  const handleEdit = (category: Category) => {
    setEditingCategory(category);
    form.setFieldsValue(category);
    setIsModalVisible(true);
  };

  const handleDelete = (id: string) => {
    deleteMutation.mutate(id);
  };

  const handleSubmit = async () => {
    try {
      const values = await form.validateFields();
      
      if (editingCategory) {
        updateMutation.mutate({ id: editingCategory.id, category: values });
      } else {
        createMutation.mutate(values);
      }
    } catch (error) {
      console.error('Form validation failed:', error);
    }
  };

  const columns = [
    {
      title: 'ID',
      dataIndex: 'id',
      key: 'id',
      width: 120,
    },
    {
      title: 'Іконка',
      dataIndex: 'icon',
      key: 'icon',
      width: 80,
      render: (icon: string) => <span style={{ fontSize: '24px' }}>{icon}</span>,
    },
    {
      title: 'Назва',
      dataIndex: 'name',
      key: 'name',
    },
    {
      title: 'Опис',
      dataIndex: 'description',
      key: 'description',
      render: (description: string) => description || '—',
    },
    {
      title: 'Порядок',
      dataIndex: 'order',
      key: 'order',
      width: 100,
      sorter: (a: Category, b: Category) => a.order - b.order,
    },
    {
      title: 'Статус',
      dataIndex: 'is_active',
      key: 'is_active',
      width: 100,
      render: (isActive: boolean) => (
        <Tag color={isActive ? 'green' : 'red'}>
          {isActive ? 'Активна' : 'Неактивна'}
        </Tag>
      ),
    },
    {
      title: 'Дії',
      key: 'actions',
      width: 150,
      render: (_: any, record: Category) => (
        <Space>
          <Button
            type="primary"
            ghost
            size="small"
            icon={<EditOutlined />}
            onClick={() => handleEdit(record)}
          >
            Редагувати
          </Button>
          <Popconfirm
            title="Ви впевнені, що хочете видалити цю категорію?"
            onConfirm={() => handleDelete(record.id)}
            okText="Так"
            cancelText="Ні"
          >
            <Button
              type="primary"
              danger
              size="small"
              icon={<DeleteOutlined />}
            >
              Видалити
            </Button>
          </Popconfirm>
        </Space>
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
        <h1>Категорії</h1>
        <Button
          type="primary"
          icon={<PlusOutlined />}
          onClick={handleAdd}
        >
          Додати категорію
        </Button>
      </div>

      <Table
        columns={columns}
        dataSource={categories}
        rowKey="id"
        loading={isLoading}
        pagination={{
          pageSize: 10,
          showSizeChanger: true,
          showQuickJumper: true,
        }}
      />

      <Modal
        title={editingCategory ? 'Редагувати категорію' : 'Додати категорію'}
        open={isModalVisible}
        onOk={handleSubmit}
        onCancel={() => {
          setIsModalVisible(false);
          setEditingCategory(null);
          form.resetFields();
        }}
        confirmLoading={createMutation.isLoading || updateMutation.isLoading}
      >
        <Form
          form={form}
          layout="vertical"
          initialValues={{ is_active: true, order: 0 }}
        >
          <Form.Item
            name="id"
            label="ID категорії"
            rules={[
              { required: true, message: 'Будь ласка, введіть ID категорії!' },
              { pattern: /^[a-z_]+$/, message: 'ID повинен містити лише малі літери та підкреслення!' }
            ]}
          >
            <Input disabled={!!editingCategory} placeholder="salmon, shellfish, caviar..." />
          </Form.Item>

          <Form.Item
            name="name"
            label="Назва"
            rules={[{ required: true, message: 'Будь ласка, введіть назву категорії!' }]}
          >
            <Input placeholder="Лосось, Молюски, Ікра..." />
          </Form.Item>

          <Form.Item
            name="description"
            label="Опис"
          >
            <Input.TextArea 
              placeholder="Короткий опис категорії..." 
              rows={3}
            />
          </Form.Item>

          <Form.Item
            name="icon"
            label="Іконка (емодзі)"
            rules={[{ required: true, message: 'Будь ласка, введіть іконку!' }]}
          >
            <Input placeholder="🐟 🦐 🥚..." />
          </Form.Item>

          <Form.Item
            name="order"
            label="Порядок сортування"
            rules={[{ required: true, message: 'Будь ласка, введіть порядок!' }]}
          >
            <InputNumber min={0} style={{ width: '100%' }} />
          </Form.Item>

          <Form.Item
            name="is_active"
            label="Активна"
            valuePropName="checked"
          >
            <Switch />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
};

export default Categories;