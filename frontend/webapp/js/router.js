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
        
        // Store previous screen for back navigation (but skip loading screen in history)
        this.previousScreen = this.currentScreen;
        if (this.currentScreen !== 'loading') {
            this.history.push(this.currentScreen);
        }
        
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
        
        // Update logos when navigating
        window.telegramWebApp?.updateLogos();
        
        // Show/hide cart icon based on screen
        const cartIcon = document.getElementById('cart-icon');
        if (cartIcon) {
            cartIcon.style.display = (screenName === 'loading' || screenName === 'cart') ? 'none' : 'flex';
        }
        
        console.log(`Successfully navigated to: ${screenName}`);
    }
    
    goBack() {
        console.log('goBack() called');
        console.log('Current screen:', this.currentScreen);
        console.log('History:', this.history);
        
        if (this.history.length > 0) {
            const previousScreen = this.history.pop();
            
            console.log(`Going back to: ${previousScreen}`);
            
            // Hide current screen
            if (this.screens[this.currentScreen]) {
                this.screens[this.currentScreen].classList.remove('active');
                this.screens[this.currentScreen].style.display = 'none';
            }
            
            // Show previous screen
            this.currentScreen = previousScreen;
            if (this.screens[previousScreen]) {
                this.screens[previousScreen].classList.add('active');
                this.screens[previousScreen].style.display = 'block';
            } else {
                console.error(`Previous screen '${previousScreen}' not found`);
                this.navigateTo('categories');
                return;
            }
            
            // Update Telegram UI
            this.updateTelegramUI();
            
            // Reload screen data if needed
            this.loadScreenData(previousScreen, {});
            
            // Notify listeners
            this.notifyListeners(previousScreen, {});
            
            // Update logos when going back
            window.telegramWebApp?.updateLogos();
            
            console.log(`Successfully went back to: ${previousScreen}`);
        } else {
            console.log('No history available, going to categories');
            this.navigateTo('categories');
        }
    }
    
    updateTelegramUI() {
        const tg = window.telegramWebApp;
        if (!tg) {
            console.log('Telegram WebApp not available for UI update');
            return;
        }
        
        console.log(`Updating Telegram UI for screen: ${this.currentScreen} (history: ${this.history.length})`);
        
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
            
            // Check for order confirmation and show info box
            this.showOrderConfirmationIfNeeded();
            
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
            this.showApiErrorMessage();
        }
    }
    
    showOrderConfirmationIfNeeded() {
        // Check if order was just confirmed
        const orderConfirmed = sessionStorage.getItem('orderConfirmed');
        if (orderConfirmed === 'true') {
            // Clear the flag
            sessionStorage.removeItem('orderConfirmed');
            
            // Show confirmation info box
            this.showOrderConfirmationBox();
        }
    }
    
    showOrderConfirmationBox() {
        // Find the container after the header
        const categoriesScreen = document.getElementById('categories');
        const header = categoriesScreen.querySelector('.header, .screen-header');
        
        // Remove any existing confirmation box
        const existingBox = categoriesScreen.querySelector('.order-confirmation-box');
        if (existingBox) {
            existingBox.remove();
        }
        
        // Create confirmation box
        const confirmationBox = document.createElement('div');
        confirmationBox.className = 'order-confirmation-box';
        confirmationBox.innerHTML = `
            <div class="confirmation-content">
                <div class="confirmation-icon">✅</div>
                <div class="confirmation-text">
                    <h3>Замовлення прийнято!</h3>
                    <p>Ваше замовлення успішно оформлено. Менеджер зв'яжеться з вами найближчим часом для уточнення часу доставки.</p>
                </div>
                <button class="confirmation-close" onclick="this.parentElement.parentElement.remove()">×</button>
            </div>
        `;
        
        // Insert after header or at the beginning
        if (header) {
            header.insertAdjacentElement('afterend', confirmationBox);
        } else {
            categoriesScreen.insertBefore(confirmationBox, categoriesScreen.firstChild);
        }
        
        // Auto-hide after 10 seconds
        setTimeout(() => {
            if (confirmationBox.parentElement) {
                confirmationBox.remove();
            }
        }, 10000);
        
        // Haptic feedback
        window.telegramWebApp?.hapticFeedback('success');
    }
    
    showApiErrorMessage() {
        const categoriesGrid = document.querySelector('.categories-grid');
        if (!categoriesGrid) return;
        
        categoriesGrid.innerHTML = `
            <div class="error-message">
                <div class="error-icon">⚠️</div>
                <h3>Тимчасові технічні проблеми</h3>
                <p>Вибачте, зараз виникли проблеми з завантаженням каталогу товарів.</p>
                <p>Спробуйте оновити сторінку або зверніться до адміністратора.</p>
                <button class="retry-button" onclick="window.location.reload()">
                    Оновити сторінку
                </button>
            </div>
        `;
        
        // Show Telegram alert as well
        if (window.telegramWebApp) {
            window.telegramWebApp.showAlert(
                'Виникли технічні проблеми. Адміністратора повідомлено про помилку. Спробуйте пізніше.'
            );
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