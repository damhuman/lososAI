import React, { useState } from 'react';
import {
  Card,
  Button,
  Table,
  Modal,
  Form,
  Input,
  InputNumber,
  Switch,
  Upload,
  Image,
  message,
  Popconfirm,
  Space,
  Tag,
  Row,
  Col,
  Typography
} from 'antd';
import {
  PlusOutlined,
  EditOutlined,
  DeleteOutlined,
  UploadOutlined,
  EyeOutlined
} from '@ant-design/icons';
import { useQuery, useMutation, useQueryClient } from 'react-query';
import { packagesAPI } from '../services/api';
import { ProductPackage } from '../types';
import { useResponsive } from '../hooks/useResponsive';

const { Text } = Typography;

interface PackageManagerProps {
  productId: string;
  productName: string;
  visible: boolean;
  onClose: () => void;
}

const PackageManager: React.FC<PackageManagerProps> = ({
  productId,
  productName,
  visible,
  onClose
}) => {
  const [form] = Form.useForm();
  const [editingPackage, setEditingPackage] = useState<ProductPackage | null>(null);
  const [isModalVisible, setIsModalVisible] = useState(false);
  const [uploadingImage, setUploadingImage] = useState<number | null>(null);
  const queryClient = useQueryClient();
  const { isMobile } = useResponsive();

  const { data: packages, isLoading } = useQuery(
    ['packages', productId],
    () => packagesAPI.getByProduct(productId),
    { enabled: visible }
  );

  const createMutation = useMutation(
    (packageData: Omit<ProductPackage, 'id' | 'product_id' | 'created_at' | 'updated_at'>) =>
      packagesAPI.create(productId, packageData),
    {
      onSuccess: () => {
        queryClient.invalidateQueries(['packages', productId]);
        message.success('Упаковку створено успішно!');
        setIsModalVisible(false);
        form.resetFields();
      },
      onError: (error: any) => {
        message.error(error.response?.data?.detail || 'Помилка при створенні упаковки');
      },
    }
  );

  const updateMutation = useMutation(
    ({ packageId, data }: { packageId: number; data: Partial<ProductPackage> }) =>
      packagesAPI.update(productId, packageId, data),
    {
      onSuccess: () => {
        queryClient.invalidateQueries(['packages', productId]);
        message.success('Упаковку оновлено успішно!');
        setIsModalVisible(false);
        setEditingPackage(null);
        form.resetFields();
      },
      onError: (error: any) => {
        message.error(error.response?.data?.detail || 'Помилка при оновленні упаковки');
      },
    }
  );

  const deleteMutation = useMutation(
    (packageId: number) => packagesAPI.delete(productId, packageId),
    {
      onSuccess: () => {
        queryClient.invalidateQueries(['packages', productId]);
        message.success('Упаковку видалено успішно!');
      },
      onError: (error: any) => {
        message.error(error.response?.data?.detail || 'Помилка при видаленні упаковки');
      },
    }
  );

  const uploadImageMutation = useMutation(
    ({ packageId, file }: { packageId: number; file: File }) =>
      packagesAPI.uploadImage(productId, packageId, file),
    {
      onSuccess: () => {
        queryClient.invalidateQueries(['packages', productId]);
        message.success('Зображення завантажено успішно!');
        setUploadingImage(null);
      },
      onError: (error: any) => {
        message.error(error.response?.data?.detail || 'Помилка при завантаженні зображення');
        setUploadingImage(null);
      },
    }
  );

  const handleAdd = () => {
    setEditingPackage(null);
    form.resetFields();
    setIsModalVisible(true);
  };

  const handleEdit = (pkg: ProductPackage) => {
    setEditingPackage(pkg);
    form.setFieldsValue(pkg);
    setIsModalVisible(true);
  };

  const handleDelete = (packageId: number) => {
    deleteMutation.mutate(packageId);
  };

  const handleSubmit = async () => {
    try {
      const values = await form.validateFields();
      
      if (editingPackage) {
        updateMutation.mutate({ packageId: editingPackage.id, data: values });
      } else {
        createMutation.mutate(values);
      }
    } catch (error) {
      console.error('Form validation failed:', error);
    }
  };

  const handleImageUpload = async (packageId: number, file: File) => {
    setUploadingImage(packageId);
    uploadImageMutation.mutate({ packageId, file });
  };

  const columns = [
    {
      title: 'ID',
      dataIndex: 'package_id',
      key: 'package_id',
      width: 100,
      responsive: ['md'] as any,
    },
    {
      title: 'Зображення',
      dataIndex: 'image_url',
      key: 'image_url',
      width: 80,
      render: (imageUrl: string, record: ProductPackage) => (
        <div style={{ position: 'relative' }}>
          {imageUrl ? (
            <Image
              src={imageUrl}
              width={60}
              height={60}
              style={{ objectFit: 'cover', borderRadius: 4 }}
              preview={{ mask: <EyeOutlined /> }}
            />
          ) : (
            <div
              style={{
                width: 60,
                height: 60,
                border: '1px dashed #d9d9d9',
                borderRadius: 4,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                color: '#999'
              }}
            >
              Немає
            </div>
          )}
          <Upload
            showUploadList={false}
            beforeUpload={(file) => {
              handleImageUpload(record.id, file);
              return false;
            }}
            accept="image/*"
            style={{ position: 'absolute', top: 0, left: 0, width: '100%', height: '100%' }}
          >
            <Button
              size="small"
              loading={uploadingImage === record.id}
              style={{
                position: 'absolute',
                top: -5,
                right: -5,
                zIndex: 10,
                padding: '2px 6px',
                height: 'auto',
                minWidth: 'auto'
              }}
            >
              <UploadOutlined />
            </Button>
          </Upload>
        </div>
      ),
    },
    {
      title: 'Назва',
      dataIndex: 'name',
      key: 'name',
    },
    {
      title: 'Вага',
      key: 'weight',
      width: 100,
      render: (record: ProductPackage) => `${record.weight} ${record.unit}`,
    },
    {
      title: 'Ціна',
      dataIndex: 'price',
      key: 'price',
      width: 100,
      render: (price: number) => `${price}₴`,
    },
    {
      title: 'Статус',
      dataIndex: 'available',
      key: 'available',
      width: 80,
      render: (available: boolean) => (
        <Tag color={available ? 'green' : 'red'}>
          {available ? 'Доступно' : 'Недоступно'}
        </Tag>
      ),
    },
    {
      title: 'Порядок',
      dataIndex: 'sort_order',
      key: 'sort_order',
      width: 80,
      responsive: ['lg'] as any,
    },
    {
      title: 'Дії',
      key: 'actions',
      width: isMobile ? 80 : 120,
      render: (record: ProductPackage) => (
        <Space size="small">
          <Button
            type="primary"
            ghost
            size="small"
            icon={<EditOutlined />}
            onClick={() => handleEdit(record)}
          >
            {isMobile ? '' : 'Ред.'}
          </Button>
          <Popconfirm
            title="Ви впевнені, що хочете видалити цю упаковку?"
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
              {isMobile ? '' : 'Вид.'}
            </Button>
          </Popconfirm>
        </Space>
      ),
    },
  ];

  const renderMobileCard = (pkg: ProductPackage) => (
    <Card
      key={pkg.id}
      size="small"
      style={{ marginBottom: 8 }}
      bodyStyle={{ padding: 12 }}
    >
      <Row gutter={[8, 8]} align="middle">
        <Col span={6}>
          {pkg.image_url ? (
            <Image
              src={pkg.image_url}
              width={50}
              height={50}
              style={{ objectFit: 'cover', borderRadius: 4 }}
            />
          ) : (
            <div
              style={{
                width: 50,
                height: 50,
                border: '1px dashed #d9d9d9',
                borderRadius: 4,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                fontSize: '10px',
                color: '#999'
              }}
            >
              Немає
            </div>
          )}
        </Col>
        <Col span={12}>
          <div>
            <Text strong>{pkg.name}</Text>
            <br />
            <Text type="secondary" style={{ fontSize: '12px' }}>
              {pkg.weight} {pkg.unit} • {pkg.price}₴
            </Text>
          </div>
        </Col>
        <Col span={6}>
          <Space direction="vertical" size={4}>
            <Tag 
              color={pkg.available ? 'green' : 'red'} 
              style={{ fontSize: '10px', margin: 0 }}
            >
              {pkg.available ? 'Доступно' : 'Недоступно'}
            </Tag>
            <Space size={4}>
              <Button
                type="primary"
                ghost
                size="small"
                icon={<EditOutlined />}
                onClick={() => handleEdit(pkg)}
                style={{ fontSize: '10px', padding: '0 4px', height: '24px' }}
              />
              <Popconfirm
                title="Видалити упаковку?"
                onConfirm={() => handleDelete(pkg.id)}
                okText="Так"
                cancelText="Ні"
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
          </Space>
        </Col>
      </Row>
      {pkg.note && (
        <Row style={{ marginTop: 8 }}>
          <Col span={24}>
            <Text type="secondary" style={{ fontSize: '11px' }}>
              {pkg.note}
            </Text>
          </Col>
        </Row>
      )}
    </Card>
  );

  return (
    <Modal
      title={`Управління упаковками - ${productName}`}
      open={visible}
      onCancel={onClose}
      width={isMobile ? '95%' : 1000}
      footer={null}
      style={isMobile ? { top: 10 } : {}}
    >
      <div style={{ marginBottom: 16 }}>
        <Button
          type="primary"
          icon={<PlusOutlined />}
          onClick={handleAdd}
          style={isMobile ? { width: '100%' } : {}}
        >
          Додати упаковку
        </Button>
      </div>

      {isMobile ? (
        <div>
          {isLoading ? (
            <div style={{ textAlign: 'center', padding: '20px' }}>
              <Text>Завантаження...</Text>
            </div>
          ) : (
            packages?.map(renderMobileCard)
          )}
        </div>
      ) : (
        <Table
          columns={columns}
          dataSource={packages}
          rowKey="id"
          loading={isLoading}
          pagination={{ pageSize: 10 }}
          scroll={{ x: 800 }}
        />
      )}

      <Modal
        title={editingPackage ? 'Редагувати упаковку' : 'Додати упаковку'}
        open={isModalVisible}
        onOk={handleSubmit}
        onCancel={() => {
          setIsModalVisible(false);
          setEditingPackage(null);
          form.resetFields();
        }}
        confirmLoading={createMutation.isLoading || updateMutation.isLoading}
      >
        <Form
          form={form}
          layout="vertical"
          initialValues={{ available: true, sort_order: 0 }}
        >
          <Form.Item
            name="package_id"
            label="ID упаковки"
            rules={[
              { required: true, message: 'Будь ласка, введіть ID упаковки!' },
              { pattern: /^[a-z0-9_-]+$/, message: 'ID повинен містити лише малі літери, цифри, підкреслення та дефіси!' }
            ]}
          >
            <Input disabled={!!editingPackage} placeholder="300g, 1kg, 500g..." />
          </Form.Item>

          <Form.Item
            name="name"
            label="Назва упаковки"
            rules={[{ required: true, message: 'Будь ласка, введіть назву упаковки!' }]}
          >
            <Input placeholder="300 грам, 1 кілограм..." />
          </Form.Item>

          <Row gutter={16}>
            <Col span={12}>
              <Form.Item
                name="weight"
                label="Вага"
                rules={[{ required: true, message: 'Будь ласка, введіть вагу!' }]}
              >
                <InputNumber min={0} step={0.1} style={{ width: '100%' }} />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item
                name="unit"
                label="Одиниця виміру"
                rules={[{ required: true, message: 'Будь ласка, введіть одиницю виміру!' }]}
              >
                <Input placeholder="г, кг, шт, набір..." />
              </Form.Item>
            </Col>
          </Row>

          <Form.Item
            name="price"
            label="Ціна (₴)"
            rules={[{ required: true, message: 'Будь ласка, введіть ціну!' }]}
          >
            <InputNumber min={0} step={0.01} style={{ width: '100%' }} />
          </Form.Item>

          <Form.Item
            name="sort_order"
            label="Порядок сортування"
            tooltip="Чим менше число, тим вище буде упаковка в списку"
          >
            <InputNumber min={0} style={{ width: '100%' }} />
          </Form.Item>

          <Form.Item
            name="note"
            label="Примітка"
          >
            <Input.TextArea rows={2} placeholder="Додаткова інформація про упаковку..." />
          </Form.Item>

          <Form.Item
            name="available"
            label="Доступна для замовлення"
            valuePropName="checked"
          >
            <Switch />
          </Form.Item>
        </Form>
      </Modal>
    </Modal>
  );
};

export default PackageManager;