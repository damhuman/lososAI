import { useEffect } from 'react';
import { Modal, notification } from 'antd';
import { ExclamationCircleOutlined } from '@ant-design/icons';

export const useErrorHandler = () => {
  const showErrorModal = (error: any, title: string = 'Помилка завантаження даних') => {
    const errorMessage = error?.response?.data?.detail || 
                        error?.message || 
                        'Виникла невідома помилка';

    Modal.error({
      title: title,
      icon: <ExclamationCircleOutlined />,
      content: (
        <div>
          <p>{errorMessage}</p>
          {error?.response?.status === 500 && (
            <p style={{ marginTop: 10, fontSize: '12px', color: '#666' }}>
              Сервер тимчасово недоступний. Спробуйте пізніше.
            </p>
          )}
          {!error?.response && (
            <p style={{ marginTop: 10, fontSize: '12px', color: '#666' }}>
              Перевірте підключення до інтернету.
            </p>
          )}
        </div>
      ),
      okText: 'Закрити',
      okType: 'danger',
    });
  };

  const showErrorNotification = (error: any, description?: string) => {
    notification.error({
      message: 'Помилка',
      description: description || error?.response?.data?.detail || error?.message || 'Виникла помилка',
      placement: 'topRight',
      duration: 5,
    });
  };

  return {
    showErrorModal,
    showErrorNotification,
  };
};