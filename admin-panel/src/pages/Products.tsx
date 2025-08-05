import React, { useState, useEffect } from 'react';
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
  Select,
  Upload,
  Image,
  Card,
  Divider
} from 'antd';
import { 
  PlusOutlined, 
  EditOutlined, 
  DeleteOutlined, 
  UploadOutlined,
  LoadingOutlined,
  AppstoreOutlined
} from '@ant-design/icons';
import { useQuery, useMutation, useQueryClient } from 'react-query';
import { categoriesAPI, productsAPI } from '../services/api';
import { Product, PackageInfo } from '../types';
import PackageManager from '../components/PackageManager';

const { Option } = Select;
const { TextArea } = Input;

const Products: React.FC = () => {
  const [isModalVisible, setIsModalVisible] = useState(false);
  const [editingProduct, setEditingProduct] = useState<Product | null>(null);
  const [form] = Form.useForm();
  const [imageUrl, setImageUrl] = useState<string>('');
  const [uploading, setUploading] = useState(false);
  const [isMobile, setIsMobile] = useState(false);
  const [packageManagerVisible, setPackageManagerVisible] = useState(false);
  const [selectedProductForPackages, setSelectedProductForPackages] = useState<Product | null>(null);
  const queryClient = useQueryClient();

  // Check if device is mobile
  useEffect(() => {
    const checkIsMobile = () => {
      setIsMobile(window.innerWidth < 768);
    };
    
    checkIsMobile();
    window.addEventListener('resize', checkIsMobile);
    return () => window.removeEventListener('resize', checkIsMobile);
  }, []);

  const { data: productsData, isLoading, error: productsError } = useQuery(
    'products', 
    () => productsAPI.getAll(1, 100)
  );
  const { data: categories, error: categoriesError } = useQuery('categories', categoriesAPI.getAll);

  const createMutation = useMutation(productsAPI.create, {
    onSuccess: () => {
      queryClient.invalidateQueries('products');
      message.success('Товар створено успішно!');
      setIsModalVisible(false);
      form.resetFields();
      setImageUrl('');
    },
    onError: () => {
      message.error('Помилка при створенні товару');
    },
  });

  const updateMutation = useMutation(
    (data: { id: string; product: Partial<Product> }) =>
      productsAPI.update(data.id, data.product),
    {
      onSuccess: () => {
        queryClient.invalidateQueries('products');
        message.success('Товар оновлено успішно!');
        setIsModalVisible(false);
        setEditingProduct(null);
        form.resetFields();
        setImageUrl('');
      },
      onError: () => {
        message.error('Помилка при оновленні товару');
      },
    }
  );

  const deleteMutation = useMutation(productsAPI.delete, {
    onSuccess: () => {
      queryClient.invalidateQueries('products');
      message.success('Товар видалено успішно!');
    },
    onError: () => {
      message.error('Помилка при видаленні товару');
    },
  });

  const handleImageUpload = async (file: File) => {
    setUploading(true);
    try {
      const result = await productsAPI.uploadImage(file);
      setImageUrl(result.url);
      form.setFieldsValue({ image_url: result.url });
      message.success('Зображення завантажено успішно!');
    } catch (error) {
      message.error('Помилка при завантаженні зображення');
    } finally {
      setUploading(false);
    }
  };

  const handleAdd = () => {
    setEditingProduct(null);
    form.resetFields();
    setImageUrl('');
    setIsModalVisible(true);
  };

  const handleEdit = (product: Product) => {
    setEditingProduct(product);
    setImageUrl(product.image_url || '');
    form.setFieldsValue(product);
    setIsModalVisible(true);
  };

  const handleDelete = (id: string) => {
    deleteMutation.mutate(id);
  };

  const handleSubmit = async () => {
    try {
      const values = await form.validateFields();
      const productData = {
        ...values,
        image_url: imageUrl
      };
      
      if (editingProduct) {
        updateMutation.mutate({ id: editingProduct.id, product: productData });
      } else {
        createMutation.mutate(productData);
      }
    } catch (error) {
      console.error('Form validation failed:', error);
    }
  };

  // Mobile columns - simplified view
  const mobileColumns = [
    {
      title: 'Товар',
      key: 'product',
      render: (_: any, record: Product) => (
        <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
          {record.image_url ? (
            <Image
              width={40}
              height={40}
              src={record.image_url}
              style={{ objectFit: 'cover', borderRadius: 4, flexShrink: 0 }}
              fallback="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAMIAAADDCAYAAADQvc6UAAABRWlDQ1BJQ0MgUHJvZmlsZQAAKJFjYGASSSwoyGFhYGDIzSspCnJ3UoiIjFJgf8LAwSDCIMogwMCcmFxc4BgQ4ANUwgCjUcG3awyMIPqyLsis7PPOq3QdDFcvjV3jOD1boQVTPQrgSkktTgbSf4A4LbmgqISBgTEFyFYuLykAsTuAbJEioKOA7DkgdjqEvQHEToKwj4DVhAQ5A9k3gGyB5IxEoBmML4BsnSQk8XQkNtReEOBxcfXxUQg1Mjc0dyHgXNJBSWpFCYh2zi+oLMpMzyhRcASGUqqCZ16yno6CkYGRAQMDKMwhqj/fAIcloxgHQqxAjIHBEugw5sUIsSQpBobtQPdLciLEVJYzMPBHMDBsayhILEqEO4DxG0txmrERhM29nYGBddr//5/DGRjYNRkY/l7////39v///y4Dmn+LgeHANwDrkl1AuO+pmgAAADhlWElmTU0AKgAAAAgAAYdpAAQAAAABAAAAGgAAAAAAAqACAAQAAAABAAAAwqADAAQAAAABAAAAwwAAAAD9b/HnAAAHlklEQVR4Ae3dP3Ik1RnG4W+GYA4CPsgKSCzKcQLiPaThJCuxKDEhJmQhHaMQyDEEOvFwKiLKOlYJNdGU9rYY5z1uLRvXXg5VPNVvvF/uUd5Gg4GBgYGBgYGBgYGBgYGBgYGBgYGBgYGBgYGBgYGBgYGBgYHLa/mS1oHGm+cINmczMzMzMzMzMzMz"
            />
          ) : (
            <div style={{ 
              width: 40, 
              height: 40, 
              backgroundColor: '#f5f5f5', 
              borderRadius: 4,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              flexShrink: 0
            }}>
              —
            </div>
          )}
          <div style={{ flex: 1, minWidth: 0 }}>
            <div style={{ fontWeight: 'bold', marginBottom: 4, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
              {record.name}
            </div>
            <div style={{ fontSize: '12px', color: '#666', marginBottom: 4 }}>
              <Tag color="blue">{record.category?.name}</Tag>
              <span style={{ marginLeft: 8 }}>{record.price_per_kg} грн/кг</span>
            </div>
            <div style={{ display: 'flex', gap: 2, flexWrap: 'wrap' }}>
              <Tag color="blue" style={{ fontSize: '11px' }}>
                Упаковки: {record.product_packages?.length || 0}
              </Tag>
            </div>
          </div>
        </div>
      ),
    },
    {
      title: 'Дії',
      key: 'actions',
      width: 100,
      render: (_: any, record: Product) => (
        <Space direction="vertical" size="small">
          <Button
            type="primary"
            ghost
            size="small"
            icon={<EditOutlined />}
            onClick={() => handleEdit(record)}
            style={{ width: '100%' }}
          >
            Редагувати
          </Button>
          <Button
            type="default"
            size="small"
            icon={<AppstoreOutlined />}
            onClick={() => {
              setSelectedProductForPackages(record);
              setPackageManagerVisible(true);
            }}
            style={{ width: '100%' }}
          >
            Упаковки
          </Button>
          <Popconfirm
            title="Видалити товар?"
            onConfirm={() => handleDelete(record.id)}
            okText="Так"
            cancelText="Ні"
          >
            <Button
              type="primary"
              danger
              size="small"
              icon={<DeleteOutlined />}
              style={{ width: '100%' }}
            >
              Видалити
            </Button>
          </Popconfirm>
        </Space>
      ),
    },
  ];

  // Desktop columns - full view
  const desktopColumns = [
    {
      title: 'Зображення',
      dataIndex: 'image_url',
      key: 'image_url',
      width: 80,
      render: (imageUrl: string) => (
        imageUrl ? (
          <Image
            width={50}
            height={50}
            src={imageUrl}
            style={{ objectFit: 'cover', borderRadius: 4 }}
            fallback="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAMIAAADDCAYAAADQvc6UAAABRWlDQ1BJQ0MgUHJvZmlsZQAAKJFjYGASSSwoyGFhYGDIzSspCnJ3UoiIjFJgf8LAwSDCIMogwMCcmFxc4BgQ4ANUwgCjUcG3awyMIPqyLsis7PPOq3QdDFcvjV3jOD1boQVTPQrgSkktTgbSf4A4LbmgqISBgTEFyFYuLykAsTuAbJEioKOA7DkgdjqEvQHEToKwj4DVhAQ5A9k3gGyB5IxEoBmML4BsnSQk8XQkNtReEOBxcfXxUQg1Mjc0dyHgXNJBSWpFCYh2zi+oLMpMzyhRcASGUqqCZ16yno6CkYGRAQMDKMwhqj/fAIcloxgHQqxAjIHBEugw5sUIsSQpBobtQPdLciLEVJYzMPBHMDBsayhILEqEO4DxG0txmrERhM29nYGBddr//5/DGRjYNRkY/l7////39v///y4Dmn+LgeHANwDrkl1AuO+pmgAAADhlWElmTU0AKgAAAAgAAYdpAAQAAAABAAAAGgAAAAAAAqACAAQAAAABAAAAwqADAAQAAAABAAAAwwAAAAD9b/HnAAAHlklEQVR4Ae3dP3Ik1RnG4W+GYA4CPsgKSCzKcQLiPaThJCuxKDEhJmQhHaMQyDEEOvFwKiLKOlYJNdGU9rYY5z1uLRvXXg5VPNVvvF/uUd5Gg4GBgYGBgYGBgYGBgYGBgYGBgYGBgYGBgYGBgYGBgYGBgYHLa/mS1oHGm+cINmczMzMzMzMzMzMz"
          />
        ) : (
          <div style={{ 
            width: 50, 
            height: 50, 
            backgroundColor: '#f5f5f5', 
            borderRadius: 4,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center'
          }}>
            —
          </div>
        )
      ),
    },
    {
      title: 'ID',
      dataIndex: 'id',
      key: 'id',
      width: 150,
    },
    {
      title: 'Назва',
      dataIndex: 'name',
      key: 'name',
    },
    {
      title: 'Категорія',
      dataIndex: ['category', 'name'],
      key: 'category',
      render: (categoryName: string) => (
        <Tag color="blue">{categoryName}</Tag>
      ),
    },
    {
      title: 'Ціна за кг',
      dataIndex: 'price_per_kg',
      key: 'price_per_kg',
      render: (price: number) => `${price} грн`,
    },
    {
      title: 'Упаковки',
      key: 'product_packages',
      render: (_: any, record: Product) => (
        <Tag color="blue">
          {record.product_packages?.length || 0} упаковок
        </Tag>
      ),
    },
    {
      title: 'Статус',
      key: 'status',
      render: (_: any, record: Product) => (
        <Space direction="vertical" size="small">
          <Tag color={record.is_active ? 'green' : 'red'}>
            {record.is_active ? 'Активний' : 'Неактивний'}
          </Tag>
          {record.is_featured && <Tag color="gold">Рекомендований</Tag>}
        </Space>
      ),
    },
    {
      title: 'Дії',
      key: 'actions',
      width: 150,
      render: (_: any, record: Product) => (
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
          <Button
            type="default"
            size="small"
            icon={<AppstoreOutlined />}
            onClick={() => {
              setSelectedProductForPackages(record);
              setPackageManagerVisible(true);
            }}
          >
            Упаковки
          </Button>
          <Popconfirm
            title="Ви впевнені, що хочете видалити цей товар?"
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
        marginBottom: isMobile ? 16 : 24,
        flexWrap: 'wrap',
        gap: 12
      }}>
        <h1 style={{ margin: 0, fontSize: isMobile ? '20px' : '24px' }}>Товари</h1>
        <Button
          type="primary"
          icon={<PlusOutlined />}
          onClick={handleAdd}
          size={isMobile ? 'large' : 'middle'}
        >
          {isMobile ? 'Додати' : 'Додати товар'}
        </Button>
      </div>

      <Table
        columns={isMobile ? mobileColumns : desktopColumns}
        dataSource={productsData?.items}
        rowKey="id"
        loading={isLoading}
        pagination={{
          pageSize: isMobile ? 5 : 10,
          showSizeChanger: !isMobile,
          showQuickJumper: !isMobile,
          total: productsData?.total,
          size: isMobile ? 'small' : undefined,
          showTotal: (total, range) => 
            isMobile 
              ? `${range[0]}-${range[1]} з ${total}`
              : `${range[0]}-${range[1]} з ${total} товарів`,
        }}
        scroll={{ x: isMobile ? 'max-content' : undefined }}
        size={isMobile ? 'small' : 'middle'}
      />

      <Modal
        title={editingProduct ? 'Редагувати товар' : 'Додати товар'}
        open={isModalVisible}
        onOk={handleSubmit}
        onCancel={() => {
          setIsModalVisible(false);
          setEditingProduct(null);
          form.resetFields();
          setImageUrl('');
        }}
        confirmLoading={createMutation.isLoading || updateMutation.isLoading}
        width={isMobile ? '95vw' : 800}
        style={isMobile ? { top: 20 } : undefined}
        destroyOnClose
      >
        <Form
          form={form}
          layout="vertical"
          initialValues={{ 
            is_active: true, 
            is_featured: false
          }}
        >
          <Form.Item
            name="id"
            label="ID товару"
            rules={[
              { required: true, message: 'Будь ласка, введіть ID товару!' },
              { pattern: /^[a-z_0-9-]+$/, message: 'ID повинен містити лише малі літери, цифри, підкреслення та дефіси!' }
            ]}
          >
            <Input disabled={!!editingProduct} placeholder="salmon_fresh_001" />
          </Form.Item>

          <Form.Item
            name="name"
            label="Назва товару"
            rules={[{ required: true, message: 'Будь ласка, введіть назву товару!' }]}
          >
            <Input placeholder="Свіжий лосось філе" />
          </Form.Item>

          <Form.Item
            name="category_id"
            label="Категорія"
            rules={[{ required: true, message: 'Будь ласка, оберіть категорію!' }]}
          >
            <Select placeholder="Оберіть категорію">
              {categories?.map(category => (
                <Option key={category.id} value={category.id}>
                  {category.icon} {category.name}
                </Option>
              ))}
            </Select>
          </Form.Item>

          <Form.Item
            name="description"
            label="Опис"
          >
            <TextArea 
              placeholder="Опис товару..." 
              rows={3}
            />
          </Form.Item>

          <Form.Item
            name="price_per_kg"
            label="Ціна за кг (грн)"
            rules={[{ required: true, message: 'Будь ласка, введіть ціну!' }]}
          >
            <InputNumber 
              min={0} 
              style={{ width: '100%' }} 
              placeholder="800"
            />
          </Form.Item>

          <Form.Item
            label="Зображення товару"
          >
            <Upload
              name="image"
              listType="picture-card"
              className="avatar-uploader"
              showUploadList={false}
              beforeUpload={(file) => {
                handleImageUpload(file);
                return false;
              }}
              disabled={uploading}
            >
              {imageUrl ? (
                <Image 
                  src={imageUrl} 
                  alt="product" 
                  style={{ width: '100%', height: '100%', objectFit: 'cover' }}
                  preview={false}
                />
              ) : (
                <div>
                  {uploading ? <LoadingOutlined /> : <UploadOutlined />}
                  <div style={{ marginTop: 8 }}>
                    {uploading ? 'Завантаження...' : 'Завантажити'}
                  </div>
                </div>
              )}
            </Upload>
          </Form.Item>

          <Divider />

          <Space>
            <Form.Item
              name="is_active"
              label="Активний"
              valuePropName="checked"
            >
              <Switch />
            </Form.Item>

            <Form.Item
              name="is_featured"
              label="Рекомендований"
              valuePropName="checked"
            >
              <Switch />
            </Form.Item>
          </Space>

          <Form.Item
            name="stock_quantity"
            label="Залишок на складі (кг)"
          >
            <InputNumber 
              min={0} 
              style={{ width: '100%' }} 
              placeholder="Не вказано"
            />
          </Form.Item>
        </Form>
      </Modal>

      {/* Package Manager Modal */}
      {selectedProductForPackages && (
        <PackageManager
          productId={selectedProductForPackages.id}
          productName={selectedProductForPackages.name}
          visible={packageManagerVisible}
          onClose={() => {
            setPackageManagerVisible(false);
            setSelectedProductForPackages(null);
          }}
        />
      )}
    </div>
  );
};

export default Products;