import React, { useState } from 'react';
import { 
  Table, 
  Button, 
  Modal, 
  Form, 
  message, 
  Space,
  Tag,
  DatePicker,
  Select,
  Card,
  Row,
  Col,
  Descriptions,
  Divider,
  Input
} from 'antd';
import { 
  EyeOutlined, 
  DownloadOutlined,
  SearchOutlined,
  FilterOutlined,
  ShoppingCartOutlined
} from '@ant-design/icons';
import { useQuery, useMutation, useQueryClient } from 'react-query';
import { ordersAPI } from '../services/api';
import { Order, OrderItem } from '../types';
import dayjs, { Dayjs } from 'dayjs';
import { saveAs } from 'file-saver';

const { RangePicker } = DatePicker;
const { Option } = Select;

const Orders: React.FC = () => {
  const [isModalVisible, setIsModalVisible] = useState(false);
  const [selectedOrder, setSelectedOrder] = useState<Order | null>(null);
  const [statusFilter, setStatusFilter] = useState<string>('all');
  const [dateRange, setDateRange] = useState<[Dayjs | null, Dayjs | null] | null>(null);
  const [searchText, setSearchText] = useState('');
  const queryClient = useQueryClient();

  const { data: ordersData, isLoading } = useQuery(
    ['orders', statusFilter, dateRange, searchText], 
    () => ordersAPI.getAll(
      1, 
      100,
      statusFilter !== 'all' ? statusFilter : undefined,
      dateRange?.[0] ? dateRange[0].format('YYYY-MM-DD') : undefined,
      dateRange?.[1] ? dateRange[1].format('YYYY-MM-DD') : undefined
    )
  );

  const updateStatusMutation = useMutation(
    (data: { id: number; status: Order['status'] }) =>
      ordersAPI.updateStatus(data.id, data.status),
    {
      onSuccess: () => {
        queryClient.invalidateQueries('orders');
        message.success('Статус замовлення оновлено!');
      },
      onError: () => {
        message.error('Помилка при оновленні статусу');
      },
    }
  );

  const handleViewOrder = (order: Order) => {
    setSelectedOrder(order);
    setIsModalVisible(true);
  };

  const handleStatusChange = (orderId: number, status: Order['status']) => {
    updateStatusMutation.mutate({ id: orderId, status });
  };

  const handleExportReport = async () => {
    try {
      const startDate = (dateRange?.[0] && dateRange[0].format('YYYY-MM-DD')) || dayjs().subtract(30, 'day').format('YYYY-MM-DD');
      const endDate = (dateRange?.[1] && dateRange[1].format('YYYY-MM-DD')) || dayjs().format('YYYY-MM-DD');
      
      const blob = await ordersAPI.exportReport(startDate, endDate);
      saveAs(blob, `orders_report_${startDate}_${endDate}.xlsx`);
      message.success('Звіт завантажено успішно!');
    } catch (error) {
      message.error('Помилка при завантаженні звіту');
    }
  };

  const statusColors = {
    pending: 'orange',
    confirmed: 'blue',
    preparing: 'cyan',
    delivering: 'purple',
    delivered: 'green',
    cancelled: 'red',
  };

  const statusLabels = {
    pending: 'Очікує',
    confirmed: 'Підтверджено',
    preparing: 'Готується',
    delivering: 'Доставляється',
    delivered: 'Доставлено',
    cancelled: 'Скасовано',
  };

  const timeSlotLabels = {
    morning: 'Ранок (8:00-12:00)',
    afternoon: 'День (12:00-16:00)',
    evening: 'Вечір (16:00-20:00)',
  };

  const filteredOrders = ordersData?.items?.filter(order => {
    const matchesSearch = 
      order.contact_name.toLowerCase().includes(searchText.toLowerCase()) ||
      order.id.toString().includes(searchText) ||
      order.contact_phone?.toLowerCase().includes(searchText.toLowerCase());
    
    return matchesSearch;
  });

  const columns = [
    {
      title: 'ID',
      dataIndex: 'id',
      key: 'id',
      width: 80,
    },
    {
      title: 'Клієнт',
      key: 'customer',
      render: (_: any, record: Order) => (
        <div>
          <div style={{ fontWeight: 500 }}>{record.contact_name}</div>
          {record.contact_phone && (
            <div style={{ color: '#666', fontSize: '12px' }}>
              {record.contact_phone}
            </div>
          )}
        </div>
      ),
    },
    {
      title: 'Товари',
      dataIndex: 'items',
      key: 'items',
      render: (items: OrderItem[]) => (
        <div>
          <Tag icon={<ShoppingCartOutlined />} color="blue">
            {items.length} товар{items.length !== 1 ? 'ів' : ''}
          </Tag>
        </div>
      ),
    },
    {
      title: 'Сума',
      key: 'amount',
      render: (_: any, record: Order) => (
        <div>
          <div style={{ fontWeight: 500 }}>{record.total_amount} грн</div>
          {record.discount_amount > 0 && (
            <div style={{ color: '#52c41a', fontSize: '12px' }}>
              Знижка: -{record.discount_amount} грн
            </div>
          )}
        </div>
      ),
    },
    {
      title: 'Статус',
      dataIndex: 'status',
      key: 'status',
      render: (status: Order['status'], record: Order) => (
        <Select
          value={status}
          style={{ width: 120 }}
          onChange={(newStatus) => handleStatusChange(record.id, newStatus)}
          size="small"
        >
          {Object.entries(statusLabels).map(([key, label]) => (
            <Option key={key} value={key}>
              <Tag color={statusColors[key as keyof typeof statusColors]} style={{ margin: 0 }}>
                {label}
              </Tag>
            </Option>
          ))}
        </Select>
      ),
    },
    {
      title: 'Дата доставки',
      key: 'delivery',
      render: (_: any, record: Order) => (
        <div>
          <div>{dayjs(record.delivery_date).format('DD.MM.YYYY')}</div>
          <div style={{ color: '#666', fontSize: '12px' }}>
            {timeSlotLabels[record.delivery_time_slot]}
          </div>
        </div>
      ),
    },
    {
      title: 'Створено',
      dataIndex: 'created_at',
      key: 'created_at',
      render: (date: string) => dayjs(date).format('DD.MM.YYYY HH:mm'),
    },
    {
      title: 'Дії',
      key: 'actions',
      width: 100,
      render: (_: any, record: Order) => (
        <Button
          type="primary"
          ghost
          size="small"
          icon={<EyeOutlined />}
          onClick={() => handleViewOrder(record)}
        >
          Переглянути
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
        <h1>Замовлення</h1>
        <Button
          type="primary"
          icon={<DownloadOutlined />}
          onClick={handleExportReport}
        >
          Експорт звіту
        </Button>
      </div>

      <div style={{ marginBottom: 16, display: 'flex', gap: 16, flexWrap: 'wrap' }}>
        <Input
          placeholder="Пошук за ім'ям, телефоном або ID"
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
          <Option value="all">Всі статуси</Option>
          {Object.entries(statusLabels).map(([key, label]) => (
            <Option key={key} value={key}>{label}</Option>
          ))}
        </Select>
        <RangePicker
          value={dateRange}
          onChange={setDateRange}
          format="DD.MM.YYYY"
          placeholder={['Дата від', 'Дата до']}
        />
      </div>

      <Table
        columns={columns}
        dataSource={filteredOrders}
        rowKey="id"
        loading={isLoading}
        pagination={{
          pageSize: 20,
          showSizeChanger: true,
          showQuickJumper: true,
          showTotal: (total) => `Всього: ${total} замовлень`,
        }}
      />

      <Modal
        title={`Замовлення #${selectedOrder?.id}`}
        open={isModalVisible}
        onCancel={() => {
          setIsModalVisible(false);
          setSelectedOrder(null);
        }}
        footer={null}
        width={800}
      >
        {selectedOrder && (
          <div>
            <Row gutter={16}>
              <Col span={12}>
                <Card title="Інформація про клієнта" size="small">
                  <Descriptions column={1} size="small">
                    <Descriptions.Item label="Ім'я">{selectedOrder.contact_name}</Descriptions.Item>
                    <Descriptions.Item label="Телефон">{selectedOrder.contact_phone || '—'}</Descriptions.Item>
                    <Descriptions.Item label="Telegram ID">{selectedOrder.user_id}</Descriptions.Item>
                    <Descriptions.Item label="Золотий клієнт">
                      {selectedOrder.user?.is_gold_client ? 'Так' : 'Ні'}
                    </Descriptions.Item>
                  </Descriptions>
                </Card>
              </Col>
              <Col span={12}>
                <Card title="Доставка" size="small">
                  <Descriptions column={1} size="small">
                    <Descriptions.Item label="Район">{selectedOrder.district?.name}</Descriptions.Item>
                    <Descriptions.Item label="Адреса">{selectedOrder.delivery_address || '—'}</Descriptions.Item>
                    <Descriptions.Item label="Дата">{dayjs(selectedOrder.delivery_date).format('DD.MM.YYYY')}</Descriptions.Item>
                    <Descriptions.Item label="Час">{timeSlotLabels[selectedOrder.delivery_time_slot]}</Descriptions.Item>
                  </Descriptions>
                </Card>
              </Col>
            </Row>

            <Divider />

            <Card title="Товари в замовленні" size="small">
              <Table
                columns={[
                  {
                    title: 'Товар',
                    dataIndex: 'product_name',
                    key: 'product_name',
                  },
                  {
                    title: 'Фасування',
                    key: 'package',
                    render: (_: any, record: OrderItem) => `${record.weight} ${record.unit}`,
                  },
                  {
                    title: 'Кількість',
                    dataIndex: 'quantity',
                    key: 'quantity',
                  },
                  {
                    title: 'Ціна за одиницю',
                    dataIndex: 'price_per_unit',
                    key: 'price_per_unit',
                    render: (price: number) => `${price} грн`,
                  },
                  {
                    title: 'Загальна ціна',
                    dataIndex: 'total_price',
                    key: 'total_price',
                    render: (price: number) => `${price} грн`,
                  },
                ]}
                dataSource={selectedOrder.items}
                rowKey="id"
                pagination={false}
                size="small"
              />
            </Card>

            <Divider />

            <Row gutter={16}>
              <Col span={12}>
                <Card title="Фінанси" size="small">
                  <Descriptions column={1} size="small">
                    <Descriptions.Item label="Сума товарів">{selectedOrder.total_amount + selectedOrder.discount_amount} грн</Descriptions.Item>
                    {selectedOrder.promo_code_used && (
                      <Descriptions.Item label="Промокод">{selectedOrder.promo_code_used}</Descriptions.Item>
                    )}
                    {selectedOrder.discount_amount > 0 && (
                      <Descriptions.Item label="Знижка">-{selectedOrder.discount_amount} грн</Descriptions.Item>
                    )}
                    <Descriptions.Item label="Вартість доставки">{selectedOrder.district?.delivery_cost || 0} грн</Descriptions.Item>
                    <Descriptions.Item label="До сплати">
                      <strong>{selectedOrder.total_amount} грн</strong>
                    </Descriptions.Item>
                  </Descriptions>
                </Card>
              </Col>
              <Col span={12}>
                <Card title="Додатково" size="small">
                  <Descriptions column={1} size="small">
                    <Descriptions.Item label="Статус">
                      <Tag color={statusColors[selectedOrder.status]}>
                        {statusLabels[selectedOrder.status]}
                      </Tag>
                    </Descriptions.Item>
                    <Descriptions.Item label="Створено">{dayjs(selectedOrder.created_at).format('DD.MM.YYYY HH:mm')}</Descriptions.Item>
                    <Descriptions.Item label="Оновлено">{selectedOrder.updated_at ? dayjs(selectedOrder.updated_at).format('DD.MM.YYYY HH:mm') : '—'}</Descriptions.Item>
                    <Descriptions.Item label="Коментар">{selectedOrder.comment || '—'}</Descriptions.Item>
                  </Descriptions>
                </Card>
              </Col>
            </Row>
          </div>
        )}
      </Modal>
    </div>
  );
};

export default Orders;