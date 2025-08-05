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
  InputNumber,
  Card,
  Row,
  Col,
  Typography
} from 'antd';
import { PlusOutlined, EditOutlined, DeleteOutlined } from '@ant-design/icons';
import { useQuery, useMutation, useQueryClient } from 'react-query';
import { categoriesAPI } from '../services/api';
import { Category } from '../types';
import { useResponsive } from '../hooks/useResponsive';

const { Text } = Typography;

const Categories: React.FC = () => {
  const [isModalVisible, setIsModalVisible] = useState(false);
  const [editingCategory, setEditingCategory] = useState<Category | null>(null);
  const [form] = Form.useForm();
  const queryClient = useQueryClient();
  const { isMobile } = useResponsive();

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
      responsive: ['lg'] as any,
    },
    {
      title: 'Іконка',
      dataIndex: 'icon',
      key: 'icon',
      width: 60,
      render: (icon: string) => <span style={{ fontSize: isMobile ? '20px' : '24px' }}>{icon}</span>,
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
      responsive: ['md'] as any,
    },
    {
      title: 'Порядок',
      dataIndex: 'order',
      key: 'order',
      width: 80,
      sorter: (a: Category, b: Category) => a.order - b.order,
      responsive: ['sm'] as any,
    },
    {
      title: 'Статус',
      dataIndex: 'is_active',
      key: 'is_active',
      width: 90,
      render: (isActive: boolean) => (
        <Tag color={isActive ? 'green' : 'red'} style={{ fontSize: isMobile ? '10px' : '12px' }}>
          {isActive ? 'Активна' : 'Неактивна'}
        </Tag>
      ),
    },
    {
      title: 'Дії',
      key: 'actions',
      width: isMobile ? 80 : 150,
      render: (_: any, record: Category) => (
        <Space direction={isMobile ? 'vertical' : 'horizontal'} size="small">
          <Button
            type="primary"
            ghost
            size="small"
            icon={<EditOutlined />}
            onClick={() => handleEdit(record)}
            style={{ fontSize: isMobile ? '10px' : '12px' }}
          >
            {isMobile ? 'Ред.' : 'Редагувати'}
          </Button>
          <Popconfirm
            title="Ви впевнені, що хочете видалити цю категорію?"
            onConfirm={() => handleDelete(record.id)}
            okText="Так"
            cancelText="Ні"
            placement={isMobile ? 'top' : 'topRight'}
          >
            <Button
              type="primary"
              danger
              size="small"
              icon={<DeleteOutlined />}
              style={{ fontSize: isMobile ? '10px' : '12px' }}
            >
              {isMobile ? 'Вид.' : 'Видалити'}
            </Button>
          </Popconfirm>
        </Space>
      ),
    },
  ];

  const renderMobileCard = (category: Category) => (
    <Card
      key={category.id}
      size="small"
      style={{ marginBottom: 8 }}
      bodyStyle={{ padding: 12 }}
    >
      <Row gutter={[8, 8]} align="middle">
        <Col span={4}>
          <div style={{ fontSize: '20px', textAlign: 'center' }}>{category.icon}</div>
        </Col>
        <Col span={12}>
          <div>
            <Text strong>{category.name}</Text>
            <br />
            <Text type="secondary" style={{ fontSize: '12px' }}>#{category.order}</Text>
          </div>
        </Col>
        <Col span={4}>
          <Tag 
            color={category.is_active ? 'green' : 'red'} 
            style={{ fontSize: '10px', margin: 0 }}
          >
            {category.is_active ? 'Активна' : 'Неактивна'}
          </Tag>
        </Col>
        <Col span={4}>
          <Space direction="vertical" size={4}>
            <Button
              type="primary"
              ghost
              size="small"
              icon={<EditOutlined />}
              onClick={() => handleEdit(category)}
              style={{ fontSize: '10px', padding: '0 4px', height: '24px' }}
            />
            <Popconfirm
              title="Видалити категорію?"
              onConfirm={() => handleDelete(category.id)}
              okText="Так"
              cancelText="Ні"
              placement="topRight"
            >
              <Button
                type="primary"
                danger
                size="small"
                icon={<DeleteOutlined />}
                style={{ fontSize: '10px', padding: '0 4px', height: '24px' }}
              />
            </Popconfirm>
          </Space>
        </Col>
      </Row>
      {category.description && (
        <Row style={{ marginTop: 8 }}>
          <Col span={24}>
            <Text type="secondary" style={{ fontSize: '11px' }}>
              {category.description}
            </Text>
          </Col>
        </Row>
      )}
    </Card>
  );

  return (
    <div style={{ padding: isMobile ? '8px' : '0' }}>
      <div style={{ 
        display: 'flex', 
        justifyContent: 'space-between', 
        alignItems: 'center', 
        marginBottom: isMobile ? 16 : 24,
        flexWrap: isMobile ? 'wrap' : 'nowrap',
        gap: isMobile ? '8px' : '0'
      }}>
        <h1 style={{ 
          margin: 0, 
          fontSize: isMobile ? '18px' : '24px',
          flex: isMobile ? '1 1 100%' : 'initial'
        }}>Категорії</h1>
        <Button
          type="primary"
          icon={<PlusOutlined />}
          onClick={handleAdd}
          size={isMobile ? 'small' : 'middle'}
          style={isMobile ? { width: '100%' } : {}}
        >
          {isMobile ? 'Додати' : 'Додати категорію'}
        </Button>
      </div>

      {isMobile ? (
        <div>
          {isLoading ? (
            <div style={{ textAlign: 'center', padding: '20px' }}>
              <Text>Завантаження...</Text>
            </div>
          ) : (
            categories?.map(renderMobileCard)
          )}
        </div>
      ) : (
        <Table
          columns={columns}
          dataSource={categories}
          rowKey="id"
          loading={isLoading}
          pagination={{
            pageSize: 10,
            showSizeChanger: !isMobile,
            showQuickJumper: !isMobile,
            simple: isMobile,
          }}
          scroll={{ x: 800 }}
        />
      )}

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
              { pattern: /^[a-z_0-9-]+$/, message: 'ID повинен містити лише малі літери, цифри, підкреслення та дефіси!' }
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