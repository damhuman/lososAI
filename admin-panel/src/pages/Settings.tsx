import React, { useState } from 'react';
import { 
  Card, 
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
  Tabs
} from 'antd';
import { PlusOutlined, EditOutlined, DeleteOutlined } from '@ant-design/icons';
import { useQuery, useMutation, useQueryClient } from 'react-query';
import { districtsAPI, promoCodesAPI } from '../services/api';
import { District, PromoCode } from '../types';

const { TabPane } = Tabs;

const Settings: React.FC = () => {
  const [isDistrictModalVisible, setIsDistrictModalVisible] = useState(false);
  const [isPromoModalVisible, setIsPromoModalVisible] = useState(false);
  const [editingDistrict, setEditingDistrict] = useState<District | null>(null);
  const [editingPromo, setEditingPromo] = useState<PromoCode | null>(null);
  const [districtForm] = Form.useForm();
  const [promoForm] = Form.useForm();
  const queryClient = useQueryClient();

  const { data: districts, loading: districtsLoading } = useQuery('districts', districtsAPI.getAll);
  const { data: promoCodes, loading: promoLoading } = useQuery('promo-codes', promoCodesAPI.getAll);

  // District mutations
  const createDistrictMutation = useMutation(districtsAPI.create, {
    onSuccess: () => {
      queryClient.invalidateQueries('districts');
      message.success('Район створено успішно!');
      setIsDistrictModalVisible(false);
      districtForm.resetFields();
    },
    onError: () => {
      message.error('Помилка при створенні району');
    },
  });

  const updateDistrictMutation = useMutation(
    (data: { id: number; district: Partial<District> }) =>
      districtsAPI.update(data.id, data.district),
    {
      onSuccess: () => {
        queryClient.invalidateQueries('districts');
        message.success('Район оновлено успішно!');
        setIsDistrictModalVisible(false);
        setEditingDistrict(null);
        districtForm.resetFields();
      },
      onError: () => {
        message.error('Помилка при оновленні району');
      },
    }
  );

  const deleteDistrictMutation = useMutation(districtsAPI.delete, {
    onSuccess: () => {
      queryClient.invalidateQueries('districts');
      message.success('Район видалено успішно!');
    },
    onError: () => {
      message.error('Помилка при видаленні району');
    },
  });

  // Promo code mutations
  const createPromoMutation = useMutation(promoCodesAPI.create, {
    onSuccess: () => {
      queryClient.invalidateQueries('promo-codes');
      message.success('Промокод створено успішно!');
      setIsPromoModalVisible(false);
      promoForm.resetFields();
    },
    onError: () => {
      message.error('Помилка при створенні промокоду');
    },
  });

  const updatePromoMutation = useMutation(
    (data: { id: number; promoCode: Partial<PromoCode> }) =>
      promoCodesAPI.update(data.id, data.promoCode),
    {
      onSuccess: () => {
        queryClient.invalidateQueries('promo-codes');
        message.success('Промокод оновлено успішно!');
        setIsPromoModalVisible(false);
        setEditingPromo(null);
        promoForm.resetFields();
      },
      onError: () => {
        message.error('Помилка при оновленні промокоду');
      },
    }
  );

  const deletePromoMutation = useMutation(promoCodesAPI.delete, {
    onSuccess: () => {
      queryClient.invalidateQueries('promo-codes');
      message.success('Промокод видалено успішно!');
    },
    onError: () => {
      message.error('Помилка при видаленні промокоду');
    },
  });

  // District handlers
  const handleAddDistrict = () => {
    setEditingDistrict(null);
    districtForm.resetFields();
    setIsDistrictModalVisible(true);
  };

  const handleEditDistrict = (district: District) => {
    setEditingDistrict(district);
    districtForm.setFieldsValue(district);
    setIsDistrictModalVisible(true);
  };

  const handleDeleteDistrict = (id: number) => {
    deleteDistrictMutation.mutate(id);
  };

  const handleSubmitDistrict = async () => {
    try {
      const values = await districtForm.validateFields();
      
      if (editingDistrict) {
        updateDistrictMutation.mutate({ id: editingDistrict.id, district: values });
      } else {
        createDistrictMutation.mutate(values);
      }
    } catch (error) {
      console.error('Form validation failed:', error);
    }
  };

  // Promo code handlers
  const handleAddPromo = () => {
    setEditingPromo(null);
    promoForm.resetFields();
    setIsPromoModalVisible(true);
  };

  const handleEditPromo = (promo: PromoCode) => {
    setEditingPromo(promo);
    promoForm.setFieldsValue(promo);
    setIsPromoModalVisible(true);
  };

  const handleDeletePromo = (id: number) => {
    deletePromoMutation.mutate(id);
  };

  const handleSubmitPromo = async () => {
    try {
      const values = await promoForm.validateFields();
      
      if (editingPromo) {
        updatePromoMutation.mutate({ id: editingPromo.id, promoCode: values });
      } else {
        createPromoMutation.mutate(values);
      }
    } catch (error) {
      console.error('Form validation failed:', error);
    }
  };

  const districtColumns = [
    {
      title: 'ID',
      dataIndex: 'id',
      key: 'id',
      width: 80,
    },
    {
      title: 'Назва району',
      dataIndex: 'name',
      key: 'name',
    },
    {
      title: 'Вартість доставки',
      dataIndex: 'delivery_cost',
      key: 'delivery_cost',
      render: (cost: number) => `${cost} грн`,
    },
    {
      title: 'Статус',
      dataIndex: 'is_active',
      key: 'is_active',
      render: (isActive: boolean) => (
        <Tag color={isActive ? 'green' : 'red'}>
          {isActive ? 'Активний' : 'Неактивний'}
        </Tag>
      ),
    },
    {
      title: 'Дії',
      key: 'actions',
      width: 150,
      render: (_: any, record: District) => (
        <Space>
          <Button
            type="primary"
            ghost
            size="small"
            icon={<EditOutlined />}
            onClick={() => handleEditDistrict(record)}
          >
            Редагувати
          </Button>
          <Popconfirm
            title="Ви впевнені, що хочете видалити цей район?"
            onConfirm={() => handleDeleteDistrict(record.id)}
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

  const promoColumns = [
    {
      title: 'ID',
      dataIndex: 'id',
      key: 'id',
      width: 80,
    },
    {
      title: 'Код',
      dataIndex: 'code',
      key: 'code',
      render: (code: string) => <code style={{ backgroundColor: '#f5f5f5', padding: '2px 4px' }}>{code}</code>,
    },
    {
      title: 'Знижка',
      key: 'discount',
      render: (_: any, record: PromoCode) => (
        <div>
          {record.discount_percent > 0 && (
            <Tag color="blue">{record.discount_percent}%</Tag>
          )}
          {record.discount_amount > 0 && (
            <Tag color="green">{record.discount_amount} грн</Tag>
          )}
        </div>
      ),
    },
    {
      title: 'Використання',
      key: 'usage',
      render: (_: any, record: PromoCode) => (
        <div>
          <div>{record.usage_count} / {record.usage_limit || '∞'}</div>
        </div>
      ),
    },
    {
      title: 'Статус',
      key: 'status',
      render: (_: any, record: PromoCode) => (
        <Space direction="vertical" size="small">
          <Tag color={record.is_active ? 'green' : 'red'}>
            {record.is_active ? 'Активний' : 'Неактивний'}
          </Tag>
          {record.is_gold_code && <Tag color="gold">Для золотих клієнтів</Tag>}
        </Space>
      ),
    },
    {
      title: 'Дії',
      key: 'actions',
      width: 150,
      render: (_: any, record: PromoCode) => (
        <Space>
          <Button
            type="primary"
            ghost
            size="small"
            icon={<EditOutlined />}
            onClick={() => handleEditPromo(record)}
          >
            Редагувати
          </Button>
          <Popconfirm
            title="Ви впевнені, що хочете видалити цей промокод?"
            onConfirm={() => handleDeletePromo(record.id)}
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
      <h1 style={{ marginBottom: 24 }}>Налаштування</h1>

      <Tabs defaultActiveKey="districts">
        <TabPane tab="Райони доставки" key="districts">
          <div style={{ 
            display: 'flex', 
            justifyContent: 'space-between', 
            alignItems: 'center', 
            marginBottom: 16 
          }}>
            <h3>Райони доставки</h3>
            <Button
              type="primary"
              icon={<PlusOutlined />}
              onClick={handleAddDistrict}
            >
              Додати район
            </Button>
          </div>

          <Table
            columns={districtColumns}
            dataSource={districts}
            rowKey="id"
            loading={districtsLoading}
            pagination={false}
          />
        </TabPane>

        <TabPane tab="Промокоди" key="promo-codes">
          <div style={{ 
            display: 'flex', 
            justifyContent: 'space-between', 
            alignItems: 'center', 
            marginBottom: 16 
          }}>
            <h3>Промокоди</h3>
            <Button
              type="primary"
              icon={<PlusOutlined />}
              onClick={handleAddPromo}
            >
              Додати промокод
            </Button>
          </div>

          <Table
            columns={promoColumns}
            dataSource={promoCodes}
            rowKey="id"
            loading={promoLoading}
            pagination={{
              pageSize: 10,
              showSizeChanger: true,
            }}
          />
        </TabPane>
      </Tabs>

      {/* District Modal */}
      <Modal
        title={editingDistrict ? 'Редагувати район' : 'Додати район'}
        open={isDistrictModalVisible}
        onOk={handleSubmitDistrict}
        onCancel={() => {
          setIsDistrictModalVisible(false);
          setEditingDistrict(null);
          districtForm.resetFields();
        }}
        confirmLoading={createDistrictMutation.isLoading || updateDistrictMutation.isLoading}
      >
        <Form
          form={districtForm}
          layout="vertical"
          initialValues={{ is_active: true, delivery_cost: 0 }}
        >
          <Form.Item
            name="name"
            label="Назва району"
            rules={[{ required: true, message: 'Будь ласка, введіть назву району!' }]}
          >
            <Input placeholder="Центр, Печерський район..." />
          </Form.Item>

          <Form.Item
            name="delivery_cost"
            label="Вартість доставки (грн)"
            rules={[{ required: true, message: 'Будь ласка, введіть вартість доставки!' }]}
          >
            <InputNumber min={0} style={{ width: '100%' }} />
          </Form.Item>

          <Form.Item
            name="is_active"
            label="Активний"
            valuePropName="checked"
          >
            <Switch />
          </Form.Item>
        </Form>
      </Modal>

      {/* Promo Code Modal */}
      <Modal
        title={editingPromo ? 'Редагувати промокод' : 'Додати промокод'}
        open={isPromoModalVisible}
        onOk={handleSubmitPromo}
        onCancel={() => {
          setIsPromoModalVisible(false);
          setEditingPromo(null);
          promoForm.resetFields();
        }}
        confirmLoading={createPromoMutation.isLoading || updatePromoMutation.isLoading}
        width={600}
      >
        <Form
          form={promoForm}
          layout="vertical"
          initialValues={{ 
            is_active: true, 
            discount_percent: 0,
            discount_amount: 0,
            is_gold_code: false
          }}
        >
          <Form.Item
            name="code"
            label="Код промокоду"
            rules={[
              { required: true, message: 'Будь ласка, введіть код промокоду!' },
              { pattern: /^[A-Z0-9]+$/, message: 'Код повинен містити лише великі літери та цифри!' }
            ]}
          >
            <Input placeholder="GOLD2024, NEWBIE10..." />
          </Form.Item>

          <Form.Item
            name="discount_percent"
            label="Відсоткова знижка (%)"
          >
            <InputNumber min={0} max={100} style={{ width: '100%' }} />
          </Form.Item>

          <Form.Item
            name="discount_amount"
            label="Фіксована знижка (грн)"
          >
            <InputNumber min={0} style={{ width: '100%' }} />
          </Form.Item>

          <Form.Item
            name="usage_limit"
            label="Ліміт використань"
          >
            <InputNumber min={1} style={{ width: '100%' }} placeholder="Без ліміту" />
          </Form.Item>

          <Space>
            <Form.Item
              name="is_active"
              label="Активний"
              valuePropName="checked"
            >
              <Switch />
            </Form.Item>

            <Form.Item
              name="is_gold_code"
              label="Тільки для золотих клієнтів"
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

export default Settings;