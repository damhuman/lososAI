import React from 'react';
import { Alert, Button } from 'antd';
import { ReloadOutlined } from '@ant-design/icons';

interface ErrorAlertProps {
  error: any;
  onRetry?: () => void;
  message?: string;
}

const ErrorAlert: React.FC<ErrorAlertProps> = ({ error, onRetry, message }) => {
  const errorMessage = message || 
    error?.response?.data?.detail || 
    error?.message || 
    'Виникла помилка при завантаженні даних';

  return (
    <Alert
      message="Помилка"
      description={errorMessage}
      type="error"
      showIcon
      action={
        onRetry && (
          <Button 
            size="small" 
            danger 
            icon={<ReloadOutlined />}
            onClick={onRetry}
          >
            Спробувати ще раз
          </Button>
        )
      }
      style={{ marginBottom: 16 }}
    />
  );
};

export default ErrorAlert;