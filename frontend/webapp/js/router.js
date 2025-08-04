// Simple SPA router for screen navigation
class Router {
    constructor() {
        this.currentScreen = 'loading';
        this.previousScreen = null;
        this.history = [];
        this.screens = {};
        this.listeners = [];
    }
    
    initialize() {
        console.log('Initializing router...');
        
        // Register all screens
        this.registerScreen('loading', document.getElementById('loading'));
        this.registerScreen('categories', document.getElementById('categories'));
        this.registerScreen('products', document.getElementById('products'));
        this.registerScreen('product-detail', document.getElementById('product-detail'));
        this.registerScreen('cart', document.getElementById('cart'));
        this.registerScreen('checkout', document.getElementById('checkout'));
        
        // Log registered screens
        console.log('Registered screens:', Object.keys(this.screens));
        
        // Set up event listeners
        this.setupEventListeners();
        
        console.log('Router initialized');
    }
    
    registerScreen(name, element) {
        if (element) {
            this.screens[name] = element;
        }
    }
    
    addListener(callback) {
        this.listeners.push(callback);
    }
    
    notifyListeners(screenName, data) {
        this.listeners.forEach(callback => callback(screenName, data));
    }
    
    setupEventListeners() {
        // Category cards
        document.querySelectorAll('.category-card').forEach(card => {
            card.addEventListener('click', () => {
                const categoryId = card.dataset.category;
                this.navigateTo('products', { categoryId });
            });
        });
        
        // Cart icon/button (if exists)
        const cartButton = document.getElementById('cart-button');
        if (cartButton) {
            cartButton.addEventListener('click', () => {
                this.navigateTo('cart');
            });
        }
    }
    
    getCurrentScreen() {
        return this.currentScreen;
    }
    
    navigateTo(screenName, data = {}) {
        console.log(`Attempting to navigate to: ${screenName}`);
        
        if (!this.screens[screenName]) {
            console.error(`Screen '${screenName}' not found. Available screens:`, Object.keys(this.screens));
            return;
        }
        
        console.log(`Hiding current screen: ${this.currentScreen}`);
        
        // Store previous screen for back navigation
        this.previousScreen = this.currentScreen;
        this.history.push(this.currentScreen);
        
        // Hide current screen
        if (this.screens[this.currentScreen]) {
            this.screens[this.currentScreen].classList.remove('active');
            this.screens[this.currentScreen].style.display = 'none';
            console.log(`Removed 'active' class from: ${this.currentScreen}`);
        }
        
        // Show new screen
        this.currentScreen = screenName;
        this.screens[screenName].classList.add('active');
        this.screens[screenName].style.display = 'block';
        console.log(`Added 'active' class to: ${screenName}`);
        console.log(`Screen element classes:`, this.screens[screenName].className);
        console.log(`Screen element style:`, this.screens[screenName].style.display);
        
        // Update Telegram UI
        this.updateTelegramUI();
        
        // Load screen data
        this.loadScreenData(screenName, data);
        
        // Notify listeners
        this.notifyListeners(screenName, data);
        
        // Haptic feedback
        window.telegramWebApp?.hapticFeedback('light');
        
        console.log(`Successfully navigated to: ${screenName}`);
    }
    
    goBack() {
        if (this.history.length > 0) {
            const previousScreen = this.history.pop();
            
            // Hide current screen
            if (this.screens[this.currentScreen]) {
                this.screens[this.currentScreen].classList.remove('active');
                this.screens[this.currentScreen].style.display = 'none';
            }
            
            // Show previous screen
            this.currentScreen = previousScreen;
            this.screens[previousScreen].classList.add('active');
            this.screens[previousScreen].style.display = 'block';
            
            // Update Telegram UI
            this.updateTelegramUI();
            
            // Reload screen data if needed
            this.loadScreenData(previousScreen, {});
            
            // Notify listeners
            this.notifyListeners(previousScreen, {});
            
            console.log(`Went back to: ${previousScreen}`);
        } else {
            // No history, go to categories
            this.navigateTo('categories');
        }
    }
    
    updateTelegramUI() {
        const tg = window.telegramWebApp;
        if (!tg) return;
        
        // Show/hide back button
        if (this.currentScreen === 'categories' || this.currentScreen === 'loading') {
            tg.hideBackButton();
        } else {
            tg.showBackButton();
        }
        
        // Update main button based on screen
        switch (this.currentScreen) {
            case 'cart':
                const itemCount = window.cart?.getItemCount() || 0;
                const total = window.cart?.getTotalPrice() || 0;
                if (itemCount > 0) {
                    tg.showMainButton(`Оформити (${total} грн)`);
                } else {
                    tg.hideMainButton();
                }
                break;
                
            case 'checkout':
                tg.showMainButton('Підтвердити замовлення');
                break;
                
            default:
                tg.hideMainButton();
                break;
        }
    }
    
    async loadScreenData(screenName, data) {
        try {
            switch (screenName) {
                case 'categories':
                    await this.loadCategories();
                    break;
                    
                case 'products':
                    if (data.categoryId) {
                        await this.loadProducts(data.categoryId);
                    }
                    break;
                    
                case 'product-detail':
                    if (data.productId) {
                        await this.loadProductDetail(data.productId);
                    }
                    break;
                    
                case 'cart':
                    window.cartUI?.updateUI();
                    break;
                    
                case 'checkout':
                    await this.loadCheckout();
                    break;
            }
        } catch (error) {
            console.error(`Error loading screen data for ${screenName}:`, error);
            window.telegramWebApp?.showAlert('Помилка завантаження даних');
        }
    }
    
    async loadCategories() {
        try {
            console.log('Loading categories from API...');
            const categories = await window.apiService.getCategories();
            const categoriesGrid = document.querySelector('.categories-grid');
            
            if (!categoriesGrid) {
                console.error('Categories grid container not found');
                return;
            }
            
            // Clear existing static categories
            categoriesGrid.innerHTML = '';
            
            // Add categories from API
            categories.forEach(category => {
                const categoryCard = document.createElement('div');
                categoryCard.className = 'category-card';
                categoryCard.dataset.category = category.id;
                
                categoryCard.innerHTML = `
                    <div class="category-icon">${category.icon}</div>
                    <h3>${category.name}</h3>
                    <p>${category.description || this.getCategoryDescription(category.id)}</p>
                `;
                
                categoryCard.addEventListener('click', () => {
                    this.navigateTo('products', { categoryId: category.id });
                });
                
                categoriesGrid.appendChild(categoryCard);
            });
            
            console.log('Categories loaded successfully');
        } catch (error) {
            console.error('Error loading categories:', error);
            // Fall back to static categories if API fails
            this.setupEventListeners();
        }
    }
    
    getCategoryDescription(categoryId) {
        const descriptions = {
            'salmon': 'Солений, копчений, холоджений',
            'shellfish': 'Креветки, мідії та інше',
            'tomyum': 'Все для приготування супу',
            'caviar': 'Різні види ікри'
        };
        return descriptions[categoryId] || '';
    }
    
    async loadProducts(categoryId) {
        try {
            const products = await window.apiService.getCategoryProducts(categoryId);
            const productsContainer = document.getElementById('products-list');
            const categoryTitle = document.getElementById('category-title');
            
            // Update category title
            const categoryNames = {
                'salmon': 'Лосось 🐟',
                'shellfish': 'Молюски 🦐',
                'tomyum': 'Tom Yum набір 🍜',
                'caviar': 'Ікра 🥚'
            };
            categoryTitle.textContent = categoryNames[categoryId] || 'Товари';
            
            // Clear and populate products
            productsContainer.innerHTML = '';
            
            products.forEach(product => {
                const productElement = this.createProductElement(product);
                productsContainer.appendChild(productElement);
            });
            
        } catch (error) {
            console.error('Error loading products:', error);
            document.getElementById('products-list').innerHTML = 
                '<p style="text-align: center; color: var(--tg-theme-hint-color);">Помилка завантаження товарів</p>';
        }
    }
    
    createProductElement(product) {
        const div = document.createElement('div');
        div.className = 'product-card';
        div.dataset.productId = product.id;
        
        div.innerHTML = `
            <div class="product-info">
                <div class="product-image">
                    <img src="${product.image_url || '/images/placeholder.jpg'}" alt="${product.name}">
                </div>
                <div class="product-details">
                    <h3>${product.name}</h3>
                    <p>${product.description || ''}</p>
                    <div class="product-price">${product.price_per_kg} грн/кг</div>
                </div>
            </div>
        `;
        
        div.addEventListener('click', () => {
            this.navigateTo('product-detail', { productId: product.id });
        });
        
        return div;
    }
    
    async loadProductDetail(productId) {
        // Implementation handled by app.js
        console.log(`Loading product detail for: ${productId}`);
    }
    
    async loadCheckout() {
        try {
            // Load districts
            const districts = await window.apiService.getDistricts();
            const districtSelect = document.getElementById('district-select');
            
            districtSelect.innerHTML = '<option value="">Оберіть район</option>';
            districts.forEach(district => {
                const option = document.createElement('option');
                option.value = district.name;
                option.textContent = district.name;
                districtSelect.appendChild(option);
            });
            
            // Update order summary
            this.updateCheckoutSummary();
            
        } catch (error) {
            console.error('Error loading checkout:', error);
        }
    }
    
    updateCheckoutSummary() {
        const items = window.cart?.getItems() || [];
        const checkoutItems = document.getElementById('checkout-items');
        const checkoutTotal = document.getElementById('checkout-total');
        
        checkoutItems.innerHTML = '';
        
        items.forEach(item => {
            const div = document.createElement('div');
            div.className = 'checkout-item';
            div.innerHTML = `
                <span>${item.product_name} (${item.weight} ${item.unit}) x${item.quantity}</span>
                <span>${item.total_price} грн</span>
            `;
            checkoutItems.appendChild(div);
        });
        
        const total = window.cart?.getTotalPrice() || 0;
        checkoutTotal.textContent = `${total} грн`;
    }
}

// Global router instance
window.router = new Router();