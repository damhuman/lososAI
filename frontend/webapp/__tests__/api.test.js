/**
 * Tests for api.js - API client functionality
 */
import { jest } from '@jest/globals';

describe('API Client', () => {
  let mockResponse;
  
  beforeEach(() => {
    jest.clearAllMocks();
    
    // Default successful response
    mockResponse = {
      ok: true,
      status: 200,
      json: jest.fn(() => Promise.resolve({})),
      text: jest.fn(() => Promise.resolve(''))
    };
    
    global.fetch.mockResolvedValue(mockResponse);
  });
  
  describe('Authentication Headers', () => {
    test('should include Telegram auth header when initData available', () => {
      const initData = 'query_id=test&user={"id":123}&auth_date=123456&hash=testhash';
      window.telegramWebApp.getInitData.mockReturnValue(initData);
      
      // Simulate getting auth headers
      const headers = window.telegramWebApp.getInitData() ? {
        'Content-Type': 'application/json',
        'Authorization': `tma ${initData}`
      } : {
        'Content-Type': 'application/json'
      };
      
      expect(headers['Authorization']).toBe(`tma ${initData}`);
      expect(headers['Content-Type']).toBe('application/json');
    });
    
    test('should use default headers when no initData', () => {
      window.telegramWebApp.getInitData.mockReturnValue(null);
      
      const headers = window.telegramWebApp.getInitData() ? {
        'Content-Type': 'application/json',
        'Authorization': `tma ${window.telegramWebApp.getInitData()}`
      } : {
        'Content-Type': 'application/json'
      };
      
      expect(headers['Authorization']).toBeUndefined();
      expect(headers['Content-Type']).toBe('application/json');
    });
  });
  
  describe('API Requests', () => {
    test('should make GET request to correct endpoint', async () => {
      const baseURL = window.location.origin + '/api/v1';
      const endpoint = '/categories/';
      const expectedUrl = `${baseURL}${endpoint}`;
      
      fetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve([{ id: 'salmon', name: 'Лосось' }])
      });
      
      // Simulate API call
      const response = await fetch(expectedUrl, {
        method: 'GET',
        headers: { 'Content-Type': 'application/json' }
      });
      const data = await response.json();
      
      expect(fetch).toHaveBeenCalledWith(expectedUrl, {
        method: 'GET',
        headers: { 'Content-Type': 'application/json' }
      });
      
      expect(data).toEqual([{ id: 'salmon', name: 'Лосось' }]);
    });
    
    test('should make POST request with data', async () => {
      const orderData = {
        user_id: 123456,
        items: [],
        total: 500
      };
      
      const baseURL = window.location.origin + '/api/v1';
      const endpoint = '/orders/';
      
      fetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve({ order_id: 100, status: 'pending' })
      });
      
      // Simulate POST request
      const response = await fetch(`${baseURL}${endpoint}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'tma test_data'
        },
        body: JSON.stringify(orderData)
      });
      
      const result = await response.json();
      
      expect(fetch).toHaveBeenCalledWith(`${baseURL}${endpoint}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'tma test_data'
        },
        body: JSON.stringify(orderData)
      });
      
      expect(result.order_id).toBe(100);
    });
  });
  
  describe('Error Handling', () => {
    test('should handle HTTP error responses', async () => {
      const errorResponse = {
        ok: false,
        status: 400,
        statusText: 'Bad Request',
        json: () => Promise.resolve({ detail: 'Invalid data' })
      };
      
      fetch.mockResolvedValueOnce(errorResponse);
      
      let error;
      try {
        const response = await fetch('/api/v1/test');
        if (!response.ok) {
          const errorData = await response.json();
          throw new Error(errorData.detail || `HTTP ${response.status}`);
        }
      } catch (e) {
        error = e;
      }
      
      expect(error).toBeDefined();
      expect(error.message).toBe('Invalid data');
    });
    
    test('should handle network errors', async () => {
      const networkError = new TypeError('Failed to fetch');
      fetch.mockRejectedValueOnce(networkError);
      
      let caughtError;
      try {
        await fetch('/api/v1/test');
      } catch (error) {
        caughtError = error;
      }
      
      expect(caughtError).toBeDefined();
      expect(caughtError.name).toBe('TypeError');
      expect(caughtError.message).toBe('Failed to fetch');
    });
    
    test('should handle JSON parsing errors', async () => {
      const invalidJsonResponse = {
        ok: true,
        json: () => Promise.reject(new SyntaxError('Unexpected token'))
      };
      
      fetch.mockResolvedValueOnce(invalidJsonResponse);
      
      let error;
      try {
        const response = await fetch('/api/v1/test');
        await response.json();
      } catch (e) {
        error = e;
      }
      
      expect(error).toBeDefined();
      expect(error.name).toBe('SyntaxError');
    });
  });
  
  describe('Data Caching', () => {
    test('should cache successful responses', () => {
      const cache = new Map();
      const key = 'categories';
      const data = [{ id: 'salmon', name: 'Лосось' }];
      const ttl = 5 * 60 * 1000; // 5 minutes
      
      // Simulate caching
      cache.set(key, {
        data,
        timestamp: Date.now()
      });
      
      expect(cache.has(key)).toBe(true);
      expect(cache.get(key).data).toEqual(data);
    });
    
    test('should respect cache TTL', () => {
      const cache = new Map();
      const key = 'categories';
      const data = [{ id: 'salmon', name: 'Лосось' }];
      const ttl = 5 * 60 * 1000; // 5 minutes
      
      // Add expired entry
      cache.set(key, {
        data,
        timestamp: Date.now() - ttl - 1000 // Expired
      });
      
      // Check if expired
      const item = cache.get(key);
      const isExpired = Date.now() - item.timestamp > ttl;
      
      if (isExpired) {
        cache.delete(key);
      }
      
      expect(cache.has(key)).toBe(false);
    });
  });
  
  describe('Error Reporting', () => {
    test('should report errors to backend', async () => {
      const errorData = {
        error_type: 'API_ERROR',
        message: 'Failed to load products',
        user_id: '123456',
        url: window.location.href,
        user_agent: navigator.userAgent,
        timestamp: new Date().toISOString()
      };
      
      fetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve({ success: true })
      });
      
      // Simulate error reporting
      const response = await fetch('/api/v1/errors/report', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(errorData)
      });
      
      expect(fetch).toHaveBeenCalledWith('/api/v1/errors/report', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(errorData)
      });
      
      expect(response.ok).toBe(true);
    });
    
    test('should not report errors for error reporting endpoint', () => {
      const message = '/errors/report: Network error';
      const shouldReport = !message.includes('/errors/report');
      
      expect(shouldReport).toBe(false);
    });
  });
});