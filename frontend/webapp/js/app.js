// Main application
class SeafoodStoreApp {
    constructor() {
        this.currentProduct = null;
        this.currentPackages = null;
        this.selectedPackage = null;
        this.promoCode = null;
        this.promoDiscount = 0;
    }
    
    async initialize() {
        console.log('Initializing Seafood Store App...');
        
        try {
            // Check dependencies
            console.log('Checking dependencies...');
            console.log('Router available:', !!window.router);
            console.log('CartUI available:', !!window.cartUI);
            console.log('API Service available:', !!window.apiService);
            
            // Initialize components
            if (window.router) {
                window.router.initialize();
                console.log('Router initialized');
            }
            
            if (window.cartUI) {
                window.cartUI.initialize();
                console.log('Cart UI initialized');
            }
            
            // Initialize cart icon
            if (window.cart) {
                window.cart.initializeCartIcon();
                console.log('Cart icon initialized');
            }
            
            // Set up event listeners
            this.setupEventListeners();
            
            // Load initial data
            await this.loadInitialData();
            
            // Navigate to categories screen after loading
            setTimeout(() => {
                console.log('Attempting navigation to categories...');
                if (window.router) {
                    console.log('Router found, navigating...');
                    window.router.navigateTo('categories');
                } else {
                    console.error('Router not available for navigation');
                }
            }, 1000);
            
            console.log('App initialized successfully');
            
        } catch (error) {
            console.error('Failed to initialize app:', error);
            window.telegramWebApp?.showAlert('Помилка ініціалізації додатку');
        }
    }
    
    async loadInitialData() {
        try {
            console.log('Loading initial data...');
            
            // Check if API service is available
            if (!window.apiService) {
                console.error('API service not available');
                return;
            }
            
            // Pre-load categories for faster navigation
            const categories = await window.apiService.getCategories();
            console.log('Categories loaded:', categories.length);
        } catch (error) {
            console.error('Error pre-loading data:', error);
            // Don't fail the entire app if data loading fails
        }
    }
    
    setupEventListeners() {
        // Router listener
        window.router.addListener((screenName, data) => {
            this.handleScreenChange(screenName, data);
        });
        
        // Product detail event listeners
        this.setupProductDetailListeners();
        
        // Checkout event listeners
        this.setupCheckoutListeners();
    }
    
    setupProductDetailListeners() {
        // Package selection
        document.addEventListener('change', (e) => {
            if (e.target.type === 'radio' && e.target.name === 'package') {
                this.handlePackageSelection(e.target.value);
                
                // Update visual selection
                document.querySelectorAll('.radio-option').forEach(option => {
                    option.classList.remove('selected');
                });
                e.target.closest('.radio-option').classList.add('selected');
            }
        });
        
        // Quantity controls
        document.getElementById('quantity-minus')?.addEventListener('click', () => {
            this.updateQuantity(-1);
        });
        
        document.getElementById('quantity-plus')?.addEventListener('click', () => {
            this.updateQuantity(1);
        });
        
        document.getElementById('quantity-input')?.addEventListener('change', (e) => {
            this.updateQuantity(0, parseInt(e.target.value));
        });
        
        // Add to cart button
        const addToCartBtn = document.getElementById('add-to-cart-btn');
        console.log('Add to cart button element:', addToCartBtn);
        
        if (addToCartBtn) {
            addToCartBtn.addEventListener('click', () => {
                console.log('Add to cart button clicked!');
                this.addToCart();
            });
            console.log('Add to cart event listener attached');
        } else {
            console.log('Add to cart button not found!');
        }
        
        // Debug navigation button
        document.getElementById('debug-nav')?.addEventListener('click', () => {
            console.log('Debug navigation clicked');
            
            // Direct screen switch for testing
            const loading = document.getElementById('loading');
            const categories = document.getElementById('categories');
            
            console.log('Loading element:', loading);
            console.log('Categories element:', categories);
            
            if (loading && categories) {
                loading.style.display = 'none';
                loading.classList.remove('active');
                
                categories.style.display = 'block';
                categories.classList.add('active');
                
                console.log('Direct navigation complete');
            }
            
            // Also try router
            if (window.router) {
                window.router.navigateTo('categories');
            } else {
                console.error('Router not available');
            }
        });
    }
    
    setupCheckoutListeners() {
        // Promo code validation
        document.getElementById('promo-check-btn')?.addEventListener('click', () => {
            this.validatePromoCode();
        });
        
        // Form validation
        document.getElementById('checkout-form')?.addEventListener('change', () => {
            this.validateCheckoutForm();
        });
        
        // Time slot selection visual feedback
        document.addEventListener('change', (e) => {
            if (e.target.type === 'radio' && e.target.name === 'delivery-time') {
                // Remove selected class from all time slot cards
                document.querySelectorAll('.time-slot-card').forEach(card => {
                    card.classList.remove('selected');
                });
                
                // Add selected class to the clicked card
                const selectedCard = e.target.closest('.time-slot-card');
                if (selectedCard) {
                    selectedCard.classList.add('selected');
                }
                
                // Trigger form validation
                this.validateCheckoutForm();
            }
        });
    }
    
    async handleScreenChange(screenName, data) {
        switch (screenName) {
            case 'product-detail':
                if (data.productId) {
                    // Small delay to ensure screen is visible
                    setTimeout(() => {
                        this.loadProductDetail(data.productId);
                    }, 100);
                }
                break;
            case 'cart':
                // Update cart UI when navigating to cart
                window.cartUI?.updateUI();
                break;
            case 'checkout':
                // Show main button for checkout
                this.setupCheckoutMainButton();
                break;
        }
    }
    
    setupCheckoutMainButton() {
        // Main button is already set up in router.js updateTelegramUI
        // Just ensure checkout form validation
        this.validateCheckoutForm();
    }
    
    async loadProductDetail(productId) {
        try {
            const product = await window.apiService.getProduct(productId);
            this.currentProduct = product;
            this.selectedPackage = null;
            
            // Update UI
            const productImg = document.getElementById('product-img');
            productImg.src = product.image_url || '/images/placeholder.svg';
            productImg.onerror = function() { this.src = '/images/placeholder.svg'; };
            document.getElementById('product-name').textContent = product.name;
            document.getElementById('product-description').textContent = product.description || '';
            document.getElementById('product-price').textContent = `${product.price_per_kg} грн/кг`;
            
            // Load packages from new API
            try {
                const packages = await window.apiService.getProductPackages(productId);
                console.log('Loaded packages from API:', packages);
                
                if (packages && packages.length > 0) {
                    this.currentPackages = packages;
                    this.loadPackageOptions(packages);
                } else {
                    console.log('No packages found, falling back to legacy packages');
                    // Fallback to legacy packages if no new packages exist
                    if (product.packages && product.packages.length > 0) {
                        this.currentPackages = product.packages;
                        this.loadLegacyPackageOptions(product.packages);
                    } else {
                        console.log('No packages available at all');
                        this.loadPackageOptions([]);
                    }
                }
            } catch (error) {
                console.error('Error loading packages:', error);
                // Fallback to legacy packages on error
                if (product.packages && product.packages.length > 0) {
                    console.log('Using legacy packages as fallback');
                    this.currentPackages = product.packages;
                    this.loadLegacyPackageOptions(product.packages);
                } else {
                    this.loadPackageOptions([]);
                }
            }
            
            // Reset quantity
            document.getElementById('quantity-input').value = 1;
            this.updateTotalPrice();
            
            // Set up Add to Cart button event listener (do it here when screen is active)
            this.setupAddToCartButton();
            
        } catch (error) {
            console.error('Error loading product detail:', error);
            window.telegramWebApp?.showAlert('Помилка завантаження товару');
            window.router.goBack();
        }
    }
    
    setupAddToCartButton() {
        const addToCartBtn = document.getElementById('add-to-cart-btn');
        console.log('Setting up Add to Cart button:', addToCartBtn);
        
        if (addToCartBtn) {
            // Remove any existing event listeners
            addToCartBtn.replaceWith(addToCartBtn.cloneNode(true));
            const newBtn = document.getElementById('add-to-cart-btn');
            
            newBtn.addEventListener('click', () => {
                console.log('Add to cart button clicked!');
                this.addToCart();
            });
            console.log('Add to cart event listener attached to button');
        } else {
            console.log('Add to cart button not found when setting up!');
        }
    }
    
    loadPackageOptions(packages) {
        const packageList = document.getElementById('package-list');
        packageList.innerHTML = '';
        
        if (!packages || packages.length === 0) {
            packageList.innerHTML = '<p>Упаковки недоступні</p>';
            return;
        }
        
        // Sort packages by sort_order
        const sortedPackages = packages.sort((a, b) => (a.sort_order || 0) - (b.sort_order || 0));
        
        let firstAvailableIndex = -1;
        sortedPackages.forEach((pkg, index) => {
            if (!pkg.available) return;
            
            const label = document.createElement('label');
            label.className = 'radio-option';
            
            const note = pkg.note ? ` (${pkg.note})` : '';
            
            // Use package_id for the value (this is the unique identifier in the database)
            const isFirst = firstAvailableIndex === -1;
            if (isFirst) firstAvailableIndex = index;
            
            // Create package image element with better fallback
            const getPackageFallback = (name) => {
                if (name && name.toLowerCase().includes('0.5') || name.includes('500')) return '/images/package-500g.svg';
                if (name && name.toLowerCase().includes('1.0') || name.includes('1kg')) return '/images/package-1kg.svg';
                return '/images/placeholder.svg';
            };
            
            const packageImage = pkg.image_url ? 
                `<img src="${pkg.image_url}" alt="${pkg.name}" class="package-image loading" onload="this.classList.remove('loading')" onerror="this.onerror=null; this.src='${getPackageFallback(pkg.name)}'; this.classList.remove('loading'); this.classList.add('fallback-image');">` : 
                `<img src="${getPackageFallback(pkg.name)}" alt="${pkg.name}" class="package-image fallback-image" title="Зображення упаковки">`;
            
            label.innerHTML = `
                <input type="radio" name="package" value="${pkg.id}" ${isFirst ? 'checked' : ''}>
                <div class="package-content">
                    ${packageImage}
                    <span class="package-text">${pkg.name}${note} - ${pkg.price} грн</span>
                </div>
            `;
            
            packageList.appendChild(label);
            
            // Auto-select first available package
            if (isFirst) {
                this.selectedPackage = pkg;
                label.classList.add('selected');
            }
        });
        
        this.updateTotalPrice();
    }
    
    loadLegacyPackageOptions(packages) {
        const packageList = document.getElementById('package-list');
        packageList.innerHTML = '';
        
        packages.forEach((pkg, index) => {
            if (!pkg.available) return;
            
            const label = document.createElement('label');
            label.className = 'radio-option';
            
            const note = pkg.note ? ` (${pkg.note})` : '';
            
            // For legacy packages, calculate price from weight
            const calculatedPrice = this.currentProduct.price_per_kg * pkg.weight;
            
            // For legacy packages, use product image as fallback with better error handling
            const getLegacyPackageFallback = (weight, unit) => {
                const weightStr = `${weight}${unit}`;
                if (weightStr.includes('0.5') || weightStr.includes('500')) return '/images/package-500g.svg';
                if (weightStr.includes('1') && unit === 'kg') return '/images/package-1kg.svg';
                return '/images/placeholder.svg';
            };
            
            const packageImage = this.currentProduct.image_url ? 
                `<img src="${this.currentProduct.image_url}" alt="${pkg.weight} ${pkg.unit}" class="package-image loading" onload="this.classList.remove('loading')" onerror="this.onerror=null; this.src='${getLegacyPackageFallback(pkg.weight, pkg.unit)}'; this.classList.remove('loading'); this.classList.add('fallback-image');">` : 
                `<img src="${getLegacyPackageFallback(pkg.weight, pkg.unit)}" alt="${pkg.weight} ${pkg.unit}" class="package-image fallback-image" title="Зображення упаковки ${pkg.weight} ${pkg.unit}">`;
            
            label.innerHTML = `
                <input type="radio" name="package" value="${pkg.id}" ${index === 0 ? 'checked' : ''}>
                <div class="package-content">
                    ${packageImage}
                    <span class="package-text">${pkg.weight} ${pkg.unit}${note} - ${calculatedPrice} грн</span>
                </div>
            `;
            
            packageList.appendChild(label);
            
            // Auto-select first package
            if (index === 0) {
                this.selectedPackage = {
                    ...pkg,
                    price: calculatedPrice // Add calculated price for legacy packages
                };
                label.classList.add('selected');
            }
        });
        
        this.updateTotalPrice();
    }
    
    handlePackageSelection(packageId) {
        if (!this.currentPackages) return;
        
        // Find the package by its database ID (not package_id)
        const foundPackage = this.currentPackages.find(pkg => pkg.id == packageId);
        
        if (foundPackage) {
            // For legacy packages, add calculated price if not present
            if (!foundPackage.price && this.currentProduct) {
                this.selectedPackage = {
                    ...foundPackage,
                    price: this.currentProduct.price_per_kg * foundPackage.weight
                };
            } else {
                this.selectedPackage = foundPackage;
            }
        }
        
        this.updateTotalPrice();
    }
    
    updateQuantity(delta, absoluteValue = null) {
        const input = document.getElementById('quantity-input');
        let newValue;
        
        if (absoluteValue !== null) {
            newValue = absoluteValue;
        } else {
            newValue = parseInt(input.value) + delta;
        }
        
        // Validate bounds
        newValue = Math.max(1, Math.min(10, newValue));
        
        input.value = newValue;
        this.updateTotalPrice();
    }
    
    updateTotalPrice() {
        if (!this.currentProduct || !this.selectedPackage) return;
        
        const quantity = parseInt(document.getElementById('quantity-input').value) || 1;
        
        // Get unit price - use package price if available, otherwise calculate from weight
        let unitPrice = this.selectedPackage.price;
        if (!unitPrice && this.selectedPackage.weight && this.currentProduct.price_per_kg) {
            unitPrice = this.currentProduct.price_per_kg * this.selectedPackage.weight;
        }
        
        const totalPrice = quantity * (unitPrice || 0);
        
        document.getElementById('total-price').textContent = `${Math.round(totalPrice)} грн`;
    }
    
    addToCart() {
        console.log('>>> ADD TO CART CLICKED <<<');
        console.log('Current product:', this.currentProduct);
        console.log('Selected package:', this.selectedPackage);
        
        if (!this.currentProduct || !this.selectedPackage) {
            console.log('Missing product or package');
            window.telegramWebApp?.showAlert('Оберіть фасування товару');
            return;
        }
        
        const quantity = parseInt(document.getElementById('quantity-input').value) || 1;
        console.log('Quantity:', quantity);
        console.log('Cart object:', window.cart);
        
        window.cart.addItem(this.currentProduct, this.selectedPackage, quantity);
        console.log('Item added to cart, current cart:', window.cart.getItems());
        
        // Manually update badge to ensure it's refreshed
        window.cart.updateCartBadge();
        
        // Show success feedback
        window.telegramWebApp?.hapticFeedback('success');
        
        // Show popup - navigation is handled by the telegram.js event listener
        window.telegramWebApp?.showPopup(
            'Додано до кошика',
            `${this.currentProduct.name} (${this.selectedPackage.weight} ${this.selectedPackage.unit}) x${quantity}`,
            [
                { type: 'default', text: 'Продовжити покупки' },
                { type: 'default', text: 'Перейти до кошика', id: 'goto_cart' }
            ]
        );
        
        console.log('Popup shown, waiting for user action...');
    }
    
    async validatePromoCode() {
        const promoInput = document.getElementById('promo-input');
        const promoResult = document.getElementById('promo-result');
        const promoBtn = document.getElementById('promo-check-btn');
        
        const code = promoInput.value.trim();
        if (!code) return;
        
        promoBtn.textContent = 'Перевіряю...';
        promoBtn.disabled = true;
        
        try {
            const result = await window.apiService.validatePromoCode(code);
            
            if (result.valid) {
                this.promoCode = code;
                this.promoDiscount = result.discount_amount || (result.discount_percent / 100 * window.cart.getTotalPrice());
                
                promoResult.className = 'promo-result success';
                promoResult.textContent = result.message || 'Промокод застосовано';
                
                // Update checkout total
                this.updateCheckoutTotals();
                
                window.telegramWebApp?.hapticFeedback('success');
            } else {
                this.promoCode = null;
                this.promoDiscount = 0;
                
                promoResult.className = 'promo-result error';
                promoResult.textContent = result.message || 'Недійсний промокод';
                
                window.telegramWebApp?.hapticFeedback('error');
            }
            
        } catch (error) {
            console.error('Error validating promo code:', error);
            promoResult.className = 'promo-result error';
            promoResult.textContent = 'Помилка перевірки промокоду';
        }
        
        promoBtn.textContent = 'Перевірити';
        promoBtn.disabled = false;
    }
    
    updateCheckoutTotals() {
        const baseTotal = window.cart.getTotalPrice();
        const finalTotal = baseTotal - this.promoDiscount;
        
        const checkoutTotal = document.getElementById('checkout-total');
        if (checkoutTotal) {
            checkoutTotal.textContent = `${finalTotal} грн`;
        }
        
        // Update main button
        window.telegramWebApp?.updateMainButton(`Підтвердити (${finalTotal} грн)`);
    }
    
    validateCheckoutForm() {
        const form = document.getElementById('checkout-form');
        const formData = new FormData(form);
        
        const district = formData.get('district') || document.getElementById('district-select').value;
        const deliveryTime = formData.get('delivery-time');
        
        const isValid = district && deliveryTime;
        
        window.telegramWebApp?.updateMainButton(
            `Підтвердити (${window.cart.getTotalPrice() - this.promoDiscount} грн)`,
            isValid
        );
        
        return isValid;
    }
    
    getOrderData() {
        if (!this.validateCheckoutForm()) {
            return null;
        }
        
        const form = document.getElementById('checkout-form');
        const formData = new FormData(form);
        
        return {
            items: window.cart.getItems(),
            delivery: {
                district: document.getElementById('district-select').value,
                time_slot: formData.get('delivery-time'),
                comment: document.getElementById('comment-input').value || ''
            },
            promo_code: this.promoCode,
            total: window.cart.getTotalPrice() - this.promoDiscount
        };
    }
}

// Checkout manager
class CheckoutManager {
    constructor(app) {
        this.app = app;
    }
    
    getOrderData() {
        return this.app.getOrderData();
    }
}

// Initialize app when DOM is loaded
document.addEventListener('DOMContentLoaded', async () => {
    console.log('DOM loaded, initializing app...');
    
    // Wait a bit for other scripts to load
    setTimeout(async () => {
        try {
            window.app = new SeafoodStoreApp();
            window.checkoutManager = new CheckoutManager(window.app);
            
            await window.app.initialize();
        } catch (error) {
            console.error('App initialization error:', error);
            document.querySelector('#loading p').textContent = 'Помилка завантаження. Спробуйте оновити сторінку.';
        }
    }, 100);
});