// API client for backend communication
class ApiClient {
    constructor() {
        this.baseURL = window.location.origin + '/api/v1';
        this.defaultHeaders = {
            'Content-Type': 'application/json'
        };
    }
    
    getAuthHeaders() {
        const initData = window.telegramWebApp?.getInitData();
        if (initData) {
            return {
                ...this.defaultHeaders,
                'Authorization': `tma ${initData}`
            };
        }
        return this.defaultHeaders;
    }
    
    async request(endpoint, options = {}) {
        const url = `${this.baseURL}${endpoint}`;
        
        const config = {
            method: 'GET',
            headers: this.defaultHeaders,
            ...options
        };
        
        try {
            const response = await fetch(url, config);
            
            if (!response.ok) {
                let errorData = {};
                let errorDetail = `HTTP ${response.status}`;
                
                try {
                    errorData = await response.json();
                    errorDetail = errorData.detail || errorData.message || `HTTP ${response.status}`;
                } catch (parseError) {
                    console.warn('Could not parse error response as JSON:', parseError);
                    errorDetail = `HTTP ${response.status} - ${response.statusText}`;
                }
                
                const error = new Error(errorDetail);
                // Attach the full response data for detailed error handling
                error.response = {
                    status: response.status,
                    statusText: response.statusText,
                    data: errorData
                };
                
                // Report error to backend for admin notification
                this.reportError('API_ERROR', `${endpoint}: ${error.message}`, {
                    status: response.status,
                    statusText: response.statusText,
                    url: url,
                    errorData: errorData
                });
                
                throw error;
            }
            
            return await response.json();
        } catch (error) {
            console.error(`API request failed: ${endpoint}`, error);
            
            // For network errors or other fetch failures, ensure we have a proper message
            if (error.name === 'TypeError' || error.message.includes('fetch')) {
                // Create a new error with a clearer message for network issues
                const networkError = new Error(`Мережева помилка: ${error.message}`);
                networkError.originalError = error;
                networkError.isNetworkError = true;
                
                this.reportError('NETWORK_ERROR', `${endpoint}: ${error.message}`, {
                    url: url,
                    originalError: error.message
                });
                
                throw networkError;
            }
            
            // Re-throw the error as-is if it's already formatted (from the !response.ok block above)
            throw error;
        }
    }
    
    async reportError(errorType, message, metadata = {}) {
        try {
            // Don't report errors for the error reporting endpoint itself
            if (message.includes('/errors/report')) return;
            
            const errorData = {
                error_type: errorType,
                message: message,
                user_id: window.telegramWebApp?.getInitDataUnsafe()?.user?.id?.toString(),
                url: window.location.href,
                user_agent: navigator.userAgent,
                timestamp: new Date().toISOString(),
                metadata: metadata
            };
            
            // Use a simple fetch to avoid recursion
            await fetch(`${this.baseURL}/errors/report`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(errorData)
            });
        } catch (e) {
            console.error('Failed to report error:', e);
        }
    }
    
    async get(endpoint) {
        return this.request(endpoint);
    }
    
    async post(endpoint, data) {
        return this.request(endpoint, {
            method: 'POST',
            headers: this.getAuthHeaders(),
            body: JSON.stringify(data)
        });
    }
    
    async put(endpoint, data) {
        return this.request(endpoint, {
            method: 'PUT',
            headers: this.getAuthHeaders(),
            body: JSON.stringify(data)
        });
    }
    
    async delete(endpoint) {
        return this.request(endpoint, {
            method: 'DELETE',
            headers: this.getAuthHeaders()
        });
    }
    
    // Categories API
    async getCategories() {
        return this.get('/categories/');
    }
    
    async getCategoryProducts(categoryId) {
        return this.get(`/categories/${categoryId}/products`);
    }
    
    // Products API
    async getProduct(productId) {
        return this.get(`/products/${productId}`);
    }
    
    // Packages API
    async getProductPackages(productId) {
        return this.get(`/packages/product/${productId}`);
    }
    
    // Orders API
    async createOrder(orderData) {
        return this.post('/orders/', orderData);
    }
    
    async getUserOrders() {
        return this.get('/orders/');
    }
    
    async getOrder(orderId) {
        return this.get(`/orders/${orderId}`);
    }
    
    // Districts API
    async getDistricts() {
        return this.get('/districts/');
    }
    
    // Promo codes API
    async validatePromoCode(code) {
        return this.post('/promo/validate', { code });
    }
}

// Data cache to avoid unnecessary API calls
class DataCache {
    constructor() {
        this.cache = new Map();
        this.ttl = 5 * 60 * 1000; // 5 minutes
    }
    
    set(key, data) {
        this.cache.set(key, {
            data,
            timestamp: Date.now()
        });
    }
    
    get(key) {
        const item = this.cache.get(key);
        if (!item) return null;
        
        // Check if data is still valid
        if (Date.now() - item.timestamp > this.ttl) {
            this.cache.delete(key);
            return null;
        }
        
        return item.data;
    }
    
    clear() {
        this.cache.clear();
    }
    
    delete(key) {
        this.cache.delete(key);
    }
}

// API service with caching
class ApiService {
    constructor() {
        this.client = new ApiClient();
        this.cache = new DataCache();
    }
    
    async getCategories() {
        const cacheKey = 'categories';
        let categories = this.cache.get(cacheKey);
        
        if (!categories) {
            categories = await this.client.getCategories();
            this.cache.set(cacheKey, categories);
        }
        
        return categories;
    }
    
    async getCategoryProducts(categoryId) {
        const cacheKey = `category_products_${categoryId}`;
        let products = this.cache.get(cacheKey);
        
        if (!products) {
            products = await this.client.getCategoryProducts(categoryId);
            this.cache.set(cacheKey, products);
        }
        
        return products;
    }
    
    async getProduct(productId) {
        const cacheKey = `product_${productId}`;
        let product = this.cache.get(cacheKey);
        
        if (!product) {
            product = await this.client.getProduct(productId);
            this.cache.set(cacheKey, product);
        }
        
        return product;
    }
    
    async getProductPackages(productId) {
        const cacheKey = `product_packages_${productId}`;
        let packages = this.cache.get(cacheKey);
        
        if (!packages) {
            packages = await this.client.getProductPackages(productId);
            this.cache.set(cacheKey, packages);
        }
        
        return packages;
    }
    
    async getDistricts() {
        const cacheKey = 'districts';
        let districts = this.cache.get(cacheKey);
        
        if (!districts) {
            districts = await this.client.getDistricts();
            this.cache.set(cacheKey, districts);
        }
        
        return districts;
    }
    
    async createOrder(orderData) {
        // Don't cache orders
        return this.client.createOrder(orderData);
    }
    
    async validatePromoCode(code) {
        // Don't cache promo validations
        return this.client.validatePromoCode(code);
    }
    
    clearCache() {
        this.cache.clear();
    }
}

// Global API service instance
window.apiService = new ApiService();