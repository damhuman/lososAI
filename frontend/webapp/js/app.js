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
        
        // Clear any stale session storage flags on app initialization
        sessionStorage.removeItem('orderConfirmed');
        console.log('Cleared stale orderConfirmed flag');
        
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
                console.log('Telegram WebApp debug info:', window.telegramWebApp?.getDebugInfo());
                
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
        
        // Order review event listeners will be set up when the screen loads
        // via setupOrderReview() -> setupOrderReviewListeners()
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
        
        // Quantity controls using event delegation with additional Telegram WebApp handling
        document.addEventListener('click', (e) => {
            if (e.target.id === 'quantity-minus') {
                e.preventDefault();
                e.stopPropagation();
                console.log('Quantity minus clicked');
                this.updateQuantity(-1);
            } else if (e.target.id === 'quantity-plus') {
                e.preventDefault();
                e.stopPropagation();
                console.log('Quantity plus clicked');
                this.updateQuantity(1);
            }
        }, { passive: false });
        
        // Additional touch event handling for Telegram WebApp
        document.addEventListener('touchend', (e) => {
            if (e.target.id === 'quantity-minus') {
                e.preventDefault();
                e.stopPropagation();
                console.log('Quantity minus touched');
                this.updateQuantity(-1);
            } else if (e.target.id === 'quantity-plus') {
                e.preventDefault();
                e.stopPropagation();
                console.log('Quantity plus touched');
                this.updateQuantity(1);
            }
        }, { passive: false });
        
        document.addEventListener('change', (e) => {
            if (e.target.id === 'quantity-input') {
                this.updateQuantity(0, parseInt(e.target.value));
            }
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
        
        // Form submission handler
        document.getElementById('checkout-form')?.addEventListener('submit', (e) => {
            e.preventDefault();
            console.log('📋 Checkout form submitted');
            
            // Validate form first
            if (!this.validateCheckoutForm()) {
                console.log('❌ Form validation failed');
                window.telegramWebApp?.showAlert('Будь ласка, заповніть всі обов\'язкові поля');
                return;
            }
            
            // Navigate directly to order review screen
            console.log('📱 Navigating to order review screen');
            window.router?.navigateTo('order-review');
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
                // Load checkout data and setup
                await this.setupCheckout();
                break;
            case 'order-review':
                // Load order review data
                await this.setupOrderReview();
                break;
        }
    }
    
    async setupCheckout() {
        console.log('🛒 Setting up checkout screen');
        
        try {
            // Load checkout items from cart
            await this.updateCheckoutItems();
            
            // Load districts for delivery
            await this.loadDistricts();
            
            // Validate form and update main button
            this.validateCheckoutForm();
            
            console.log('✅ Checkout setup completed');
            
        } catch (error) {
            console.error('❌ Error setting up checkout:', error);
            window.telegramWebApp?.showAlert('Помилка завантаження даних для оформлення замовлення');
        }
    }
    
    async updateCheckoutItems() {
        const checkoutItemsContainer = document.getElementById('checkout-items');
        const checkoutTotal = document.getElementById('checkout-total');
        
        if (!checkoutItemsContainer || !checkoutTotal) {
            console.log('⚠️ Checkout containers not found');
            return;
        }
        
        const cartItems = window.cart?.getItems() || [];
        const totalPrice = window.cart?.getTotalPrice() || 0;
        
        // Clear existing items
        checkoutItemsContainer.innerHTML = '';
        
        if (cartItems.length === 0) {
            checkoutItemsContainer.innerHTML = '<p>Кошик порожній</p>';
            checkoutTotal.textContent = '0 грн';
            return;
        }
        
        // Add each cart item
        cartItems.forEach(item => {
            const itemElement = document.createElement('div');
            itemElement.className = 'checkout-item';
            itemElement.innerHTML = `
                <div class="checkout-item-info">
                    <div class="item-name">${item.product_name}</div>
                    <div class="item-details">${item.weight} ${item.unit} x ${item.quantity}</div>
                </div>
                <div class="checkout-item-price">${item.total_price} грн</div>
            `;
            checkoutItemsContainer.appendChild(itemElement);
        });
        
        // Update total
        const finalTotal = totalPrice - this.promoDiscount;
        checkoutTotal.textContent = `${finalTotal} грн`;
    }
    
    async loadDistricts() {
        try {
            console.log('📍 Loading districts...');
            const districts = await window.apiService.getDistricts();
            
            const districtSelect = document.getElementById('district-select');
            if (!districtSelect) {
                console.log('⚠️ District select not found');
                return;
            }
            
            // Clear existing options (except placeholder)
            const placeholder = districtSelect.querySelector('option[value=""]');
            districtSelect.innerHTML = '';
            if (placeholder) {
                districtSelect.appendChild(placeholder);
            } else {
                districtSelect.innerHTML = '<option value="">Оберіть район</option>';
            }
            
            // Add district options
            districts.forEach(district => {
                const option = document.createElement('option');
                option.value = district.name;
                option.textContent = district.name;
                if (!district.is_active) {
                    option.disabled = true;
                    option.textContent += ' (недоступний)';
                }
                districtSelect.appendChild(option);
            });
            
            console.log(`✅ Loaded ${districts.length} districts`);
            
        } catch (error) {
            console.error('❌ Error loading districts:', error);
            // Add fallback districts
            const districtSelect = document.getElementById('district-select');
            if (districtSelect) {
                districtSelect.innerHTML = `
                    <option value="">Оберіть район</option>
                    <option value="Печерський">Печерський</option>
                    <option value="Шевченківський">Шевченківський</option>
                    <option value="Подільський">Подільський</option>
                    <option value="Оболонський">Оболонський</option>
                    <option value="Дарницький">Дарницький</option>
                    <option value="Дніпровський">Дніпровський</option>
                    <option value="Деснянський">Деснянський</option>
                    <option value="Святошинський">Святошинський</option>
                    <option value="Солом'янський">Солом'янський</option>
                    <option value="Голосіївський">Голосіївський</option>
                `;
            }
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
            const input = document.getElementById('quantity-input');
            const display = document.getElementById('quantity-display');
            if (input) {
                input.value = 1;
                input.setAttribute('value', 1);
            }
            if (display) {
                display.textContent = 1;
                display.innerHTML = 1;
                display.innerText = 1;
                display.setAttribute('data-value', 1);
            }
            this.updateQuantity(0, 1); // Reset button states
            this.updateTotalPrice();
            
            // Set up quantity controls specifically for this product detail view
            this.setupQuantityControls();
            
            // Set up Add to Cart button event listener (do it here when screen is active)
            this.setupAddToCartButton();
            
        } catch (error) {
            console.error('Error loading product detail:', error);
            window.telegramWebApp?.showAlert('Помилка завантаження товару');
            window.router.goBack();
        }
    }
    
    setupQuantityControls() {
        console.log('Setting up quantity controls for product detail screen');
        
        const minusBtn = document.getElementById('quantity-minus');
        const plusBtn = document.getElementById('quantity-plus');
        const input = document.getElementById('quantity-input');
        const display = document.getElementById('quantity-display');
        
        console.log('Quantity elements:', { minus: !!minusBtn, plus: !!plusBtn, input: !!input, display: !!display });
        
        // Remove existing listeners by replacing elements
        if (minusBtn) {
            const newMinusBtn = minusBtn.cloneNode(true);
            minusBtn.parentNode.replaceChild(newMinusBtn, minusBtn);
            
            newMinusBtn.addEventListener('click', (e) => {
                e.preventDefault();
                e.stopPropagation();
                console.log('Direct minus button clicked');
                this.updateQuantity(-1);
            });
            
            newMinusBtn.addEventListener('touchend', (e) => {
                e.preventDefault();
                e.stopPropagation();
                console.log('Direct minus button touched');
                this.updateQuantity(-1);
            });
        }
        
        if (plusBtn) {
            const newPlusBtn = plusBtn.cloneNode(true);
            plusBtn.parentNode.replaceChild(newPlusBtn, plusBtn);
            
            newPlusBtn.addEventListener('click', (e) => {
                e.preventDefault();
                e.stopPropagation();
                console.log('Direct plus button clicked');
                this.updateQuantity(1);
            });
            
            newPlusBtn.addEventListener('touchend', (e) => {
                e.preventDefault();
                e.stopPropagation();
                console.log('Direct plus button touched');
                this.updateQuantity(1);
            });
        }
        
        if (input) {
            const newInput = input.cloneNode(true);
            input.parentNode.replaceChild(newInput, input);
            
            newInput.addEventListener('change', (e) => {
                console.log('Direct input changed');
                this.updateQuantity(0, parseInt(e.target.value));
            });
        }
        
        console.log('Quantity controls setup completed');
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
            
            const note = pkg.note ? `<br><small>${pkg.note}</small>` : '';
            
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
                    <span class="package-text">${pkg.name}${note}<br><strong>${pkg.price} грн</strong></span>
                </div>
            `;
            
            label.addEventListener('click', () => {
                // Remove selected class from all
                packageList.querySelectorAll('.radio-option').forEach(opt => {
                    opt.classList.remove('selected');
                });
                // Add selected class to this one
                label.classList.add('selected');
            });
            
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
        
        let firstAvailableIndex = -1;
        packages.forEach((pkg, index) => {
            if (!pkg.available) return;
            
            const label = document.createElement('label');
            label.className = 'radio-option';
            
            const note = pkg.note ? `<br><small>${pkg.note}</small>` : '';
            
            // For legacy packages, calculate price from weight
            const calculatedPrice = Math.round(this.currentProduct.price_per_kg * pkg.weight);
            
            // Check if this is the first available package
            const isFirst = firstAvailableIndex === -1;
            if (isFirst) firstAvailableIndex = index;
            
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
                <input type="radio" name="package" value="${pkg.id}" ${isFirst ? 'checked' : ''}>
                <div class="package-content">
                    ${packageImage}
                    <span class="package-text">${pkg.weight} ${pkg.unit}${note}<br><strong>${calculatedPrice} грн</strong></span>
                </div>
            `;
            
            label.addEventListener('click', () => {
                // Remove selected class from all
                packageList.querySelectorAll('.radio-option').forEach(opt => {
                    opt.classList.remove('selected');
                });
                // Add selected class to this one
                label.classList.add('selected');
            });
            
            packageList.appendChild(label);
            
            // Auto-select first package
            if (isFirst) {
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
        console.log('updateQuantity called:', { delta, absoluteValue });
        
        const input = document.getElementById('quantity-input');
        const display = document.getElementById('quantity-display');
        
        console.log('Elements found:', { input: !!input, display: !!display });
        
        let newValue;
        
        if (absoluteValue !== null) {
            newValue = absoluteValue;
        } else {
            const currentValue = parseInt(input ? input.value : display ? display.textContent : '1') || 1;
            console.log('Current value:', currentValue);
            newValue = currentValue + delta;
        }
        
        // Validate bounds
        newValue = Math.max(1, Math.min(10, newValue));
        console.log('New value after bounds:', newValue);
        
        // Update both input (hidden) and display with multiple methods for Telegram WebApp compatibility
        if (input) {
            input.value = newValue;
            input.setAttribute('value', newValue);
        }
        
        if (display) {
            // Multiple update methods to ensure Telegram WebApp compatibility
            const updateDisplay = () => {
                display.textContent = newValue;
                display.innerHTML = newValue;
                display.innerText = newValue;
                
                // Set data attribute as backup
                display.setAttribute('data-value', newValue);
                
                console.log('Display updated to:', display.textContent);
            };
            
            // Update immediately
            updateDisplay();
            
            // Also update after next frame for Telegram WebApp compatibility
            requestAnimationFrame(() => {
                updateDisplay();
                
                // Force a DOM reflow to ensure updates are applied
                display.style.display = 'none';
                display.offsetHeight; // Trigger reflow
                display.style.display = '';
                
                // Triple-check update after reflow
                setTimeout(updateDisplay, 0);
            });
        }
        
        // Update button states
        const minusBtn = document.getElementById('quantity-minus');
        const plusBtn = document.getElementById('quantity-plus');
        if (minusBtn) minusBtn.disabled = newValue <= 1;
        if (plusBtn) plusBtn.disabled = newValue >= 10;
        
        // Add haptic feedback for Telegram WebApp
        if (window.telegramWebApp?.hapticFeedback) {
            window.telegramWebApp.hapticFeedback('light');
        }
        
        this.updateTotalPrice();
        
        console.log('updateQuantity completed');
    }
    
    updateTotalPrice() {
        if (!this.currentProduct || !this.selectedPackage) return;
        
        const input = document.getElementById('quantity-input');
        const display = document.getElementById('quantity-display');
        const quantity = parseInt(input ? input.value : display ? display.textContent : 1) || 1;
        
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
        
        const input = document.getElementById('quantity-input');
        const display = document.getElementById('quantity-display');
        const quantity = parseInt(input ? input.value : display ? display.textContent : 1) || 1;
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
    
    submitOrderViaTelegram() {
        console.log('🚀 Submitting order via Telegram Web App');
        
        try {
            // Use the existing Telegram submitOrder method
            if (window.telegramWebApp && window.telegramWebApp.submitOrder) {
                window.telegramWebApp.submitOrder();
            } else {
                console.log('⚠️ Telegram WebApp not available, using fallback');
                this.submitOrderFallback();
            }
            
        } catch (error) {
            console.error('❌ Error submitting order:', error);
            const errorMsg = error.message || 'Помилка відправки замовлення. Спробуйте ще раз.';
            window.telegramWebApp?.showAlert(errorMsg);
        }
    }
    
    submitOrderFallback() {
        // Fallback order submission if Telegram Web App is not available
        console.log('📤 Using fallback order submission');
        
        const orderData = this.getOrderData();
        if (!orderData) {
            console.log('❌ Could not get order data');
            return;
        }
        
        // Add user data (fallback values if Telegram not available)
        orderData.user_id = window.telegramWebApp?.user?.id || Math.floor(Math.random() * 1000000);
        orderData.user_name = window.telegramWebApp?.user?.first_name || 'Користувач';
        orderData.init_data = window.telegramWebApp?.initData || '';
        
        console.log('📦 Order data prepared:', orderData);
        
        // Show success message
        alert(`Замовлення №${Date.now()} прийнято!\n\nВаше замовлення успішно оформлено. Менеджер зв'яжеться з вами найближчим часом для уточнення часу доставки.`);
        
        // Clear cart and return to categories
        window.cart?.clear();
        window.router?.navigateTo('categories');
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
    
    setupOrderReviewListeners() {
        console.log('🔧 Setting up order review listeners...');
        
        // Edit order button
        const editBtn = document.getElementById('edit-order-btn');
        console.log('Edit button found:', !!editBtn);
        editBtn?.addEventListener('click', () => {
            console.log('✏️ Edit order clicked');
            window.router?.goBack();
        });
        
        // Confirm order button - show confirmation dialog
        const confirmBtn = document.getElementById('confirm-order-btn');
        console.log('Confirm button found:', !!confirmBtn);
        confirmBtn?.addEventListener('click', async () => {
            console.log('✅ Confirm order clicked - submitting to backend');
            await this.submitOrderToBackend();
        });
        
        console.log('✅ Order review listeners attached');
    }
    
    async setupOrderReview() {
        console.log('📋 Setting up order review screen');
        
        const orderData = this.getOrderData();
        if (!orderData) {
            console.log('❌ Could not get order data for review');
            window.router?.goBack();
            return;
        }
        
        // Populate order items
        const reviewItemsContainer = document.getElementById('review-items');
        reviewItemsContainer.innerHTML = '';
        
        orderData.items.forEach(item => {
            const itemElement = document.createElement('div');
            itemElement.className = 'review-item';
            
            // Get product image (fallback to placeholder)
            const imageUrl = item.image_url || '/images/placeholder.svg';
            
            itemElement.innerHTML = `
                <img src="${imageUrl}" alt="${item.product_name}" class="review-item-image" 
                     onerror="this.onerror=null; this.src='/images/placeholder.svg';">
                <div class="review-item-details">
                    <div class="review-item-name">${item.product_name}</div>
                    <div class="review-item-info">
                        <span>${item.weight} ${item.unit}</span>
                        <span>•</span>
                        <span>Кількість: ${item.quantity}</span>
                    </div>
                </div>
                <div class="review-item-price">${item.total_price} грн</div>
            `;
            
            reviewItemsContainer.appendChild(itemElement);
        });
        
        // Populate delivery info
        const districtSelect = document.getElementById('district-select');
        const selectedDistrict = districtSelect.options[districtSelect.selectedIndex]?.text || orderData.delivery.district;
        document.getElementById('review-district').textContent = selectedDistrict;
        
        // Time slot display
        const timeSlotMap = {
            'morning': '🌅 Ранок (8:00-12:00)',
            'afternoon': '☀️ День (12:00-16:00)',
            'evening': '🌆 Вечір (16:00-20:00)'
        };
        document.getElementById('review-time-slot').textContent = timeSlotMap[orderData.delivery.time_slot] || orderData.delivery.time_slot;
        
        // Calculate delivery date
        const now = new Date();
        const deliveryDate = new Date(now);
        if (now.getHours() < 18) {
            deliveryDate.setDate(deliveryDate.getDate() + 1);
        } else {
            deliveryDate.setDate(deliveryDate.getDate() + 2);
        }
        const formattedDate = deliveryDate.toLocaleDateString('uk-UA', { 
            weekday: 'long', 
            year: 'numeric', 
            month: 'long', 
            day: 'numeric' 
        });
        document.getElementById('review-delivery-date').textContent = formattedDate;
        
        // Comment
        if (orderData.delivery.comment) {
            document.getElementById('review-comment').textContent = orderData.delivery.comment;
            document.getElementById('review-comment-row').style.display = 'flex';
        } else {
            document.getElementById('review-comment-row').style.display = 'none';
        }
        
        // Price summary
        const subtotal = window.cart.getTotalPrice();
        document.getElementById('review-subtotal').textContent = `${subtotal} грн`;
        
        // Promo code and discount
        if (this.promoDiscount > 0) {
            document.getElementById('review-discount').textContent = `-${this.promoDiscount} грн`;
            document.getElementById('review-promo-row').style.display = 'flex';
        } else {
            document.getElementById('review-promo-row').style.display = 'none';
        }
        
        // Total
        document.getElementById('review-total').textContent = `${orderData.total} грн`;
        
        // Set up order review listeners after everything is loaded
        this.setupOrderReviewListeners();
        
        console.log('✅ Order review setup completed with listeners');
    }
    
    async setupOrderConfirmation() {
        console.log('⚠️ Setting up order confirmation screen');
        
        const orderData = this.getOrderData();
        if (!orderData) {
            console.log('❌ Could not get order data for confirmation screen');
            window.router?.goBack();
            return;
        }
        
        // Populate confirmation summary
        document.getElementById('confirm-total').textContent = `${orderData.total} грн`;
        
        const districtSelect = document.getElementById('district-select');
        const selectedDistrict = districtSelect.options[districtSelect.selectedIndex]?.text || orderData.delivery.district;
        document.getElementById('confirm-district').textContent = selectedDistrict;
        
        // Time slot display
        const timeSlotMap = {
            'morning': '🌅 Ранок (8:00-12:00)',
            'afternoon': '☀️ День (12:00-16:00)',
            'evening': '🌆 Вечір (16:00-20:00)'
        };
        document.getElementById('confirm-time-slot').textContent = timeSlotMap[orderData.delivery.time_slot] || orderData.delivery.time_slot;
        
        // Calculate delivery date
        const now = new Date();
        const deliveryDate = new Date(now);
        if (now.getHours() < 18) {
            deliveryDate.setDate(deliveryDate.getDate() + 1);
        } else {
            deliveryDate.setDate(deliveryDate.getDate() + 2);
        }
        const formattedDate = deliveryDate.toLocaleDateString('uk-UA', { 
            weekday: 'long', 
            day: 'numeric', 
            month: 'long' 
        });
        document.getElementById('confirm-delivery-date').textContent = formattedDate;
        
        // Set up confirmation screen listeners
        this.setupOrderConfirmationListeners();
        
        console.log('✅ Order confirmation setup completed with listeners');
    }
    
    setupOrderConfirmationListeners() {
        console.log('🔧 Setting up order confirmation listeners...');
        
        // Back to checkout button
        const backBtn = document.getElementById('back-to-checkout-btn');
        console.log('Back to checkout button found:', !!backBtn);
        backBtn?.addEventListener('click', () => {
            console.log('⬅️ Back to checkout clicked');
            window.router?.goBack();
        });
        
        // Proceed to review button
        const proceedBtn = document.getElementById('proceed-to-review-btn');
        console.log('Proceed to review button found:', !!proceedBtn);
        proceedBtn?.addEventListener('click', () => {
            console.log('➡️ Proceed to review clicked');
            window.router?.navigateTo('order-review');
        });
        
        console.log('✅ Order confirmation listeners attached');
    }
    
    showOrderConfirmationDialog() {
        console.log('📱 Showing order confirmation dialog');
        
        const orderData = this.getOrderData();
        if (!orderData) {
            console.log('❌ Could not get order data for dialog');
            return;
        }
        
        // Populate dialog with order summary
        document.getElementById('dialog-total').textContent = `${orderData.total} грн`;
        
        const districtSelect = document.getElementById('district-select');
        const selectedDistrict = districtSelect.options[districtSelect.selectedIndex]?.text || orderData.delivery.district;
        document.getElementById('dialog-district').textContent = selectedDistrict;
        
        // Calculate delivery date (same logic as in setupOrderReview)
        const now = new Date();
        const deliveryDate = new Date(now);
        if (now.getHours() < 18) {
            deliveryDate.setDate(deliveryDate.getDate() + 1);
        } else {
            deliveryDate.setDate(deliveryDate.getDate() + 2);
        }
        const formattedDate = deliveryDate.toLocaleDateString('uk-UA', { 
            day: 'numeric', 
            month: 'short' 
        });
        document.getElementById('dialog-date').textContent = formattedDate;
        
        // Show dialog
        const dialog = document.getElementById('order-confirmation-dialog');
        dialog.style.display = 'flex';
        
        // Set up dialog listeners NOW that dialog is visible
        this.setupDialogListeners();
        
        // Haptic feedback
        window.telegramWebApp?.hapticFeedback('light');
        
        // Prevent body scrolling
        document.body.style.overflow = 'hidden';
        
        console.log('✅ Dialog shown and listeners attached');
    }
    
    hideOrderConfirmationDialog() {
        const dialog = document.getElementById('order-confirmation-dialog');
        dialog.style.display = 'none';
        
        // Restore body scrolling
        document.body.style.overflow = 'auto';
    }
    
    async submitOrderToBackend() {
        console.log('🚀 STARTING submitOrderToBackend() function');
        
        // Debug: Check if function is actually called
        console.log('🔍 Function called at:', new Date().toISOString());
        
        const orderData = this.getOrderData();
        console.log('🔍 Order data retrieved:', orderData);
        
        if (!orderData) {
            console.log('❌ Could not get order data - aborting');
            window.telegramWebApp?.showAlert('Помилка: не вдалося отримати дані замовлення');
            return;
        }
        
        // Show loading overlay
        const loadingOverlay = document.getElementById('order-loading');
        console.log('🔍 Loading overlay element:', loadingOverlay);
        if (loadingOverlay) {
            loadingOverlay.style.display = 'flex';
            console.log('✅ Loading overlay shown');
        }
        
        // Disable confirm button
        const confirmBtn = document.getElementById('confirm-order-btn');
        if (confirmBtn) {
            confirmBtn.disabled = true;
            console.log('✅ Confirm button disabled');
        }
        
        try {
            // Add user data from Telegram
            orderData.user_id = window.telegramWebApp?.user?.id || Math.floor(Math.random() * 1000000);
            orderData.user_name = window.telegramWebApp?.user?.first_name || 'Користувач';
            orderData.init_data = window.telegramWebApp?.initData || '';
            
            console.log('📦 Final order data to send:', JSON.stringify(orderData, null, 2));
            console.log('🔍 API Service available:', !!window.apiService);
            console.log('🔍 createOrder function available:', !!window.apiService?.createOrder);
            
            if (!window.apiService) {
                throw new Error('API Service not available');
            }
            
            if (!window.apiService.createOrder) {
                throw new Error('createOrder function not available in API Service');
            }
            
            console.log('🚀 Making API call to backend...');
            
            // Submit to backend API with timeout
            const result = await Promise.race([
                window.apiService.createOrder(orderData),
                new Promise((_, reject) => 
                    setTimeout(() => reject(new Error('API call timeout after 30 seconds')), 30000)
                )
            ]);
            
            console.log('✅ Order created successfully:', result);
            console.log('🔍 Result type:', typeof result);
            console.log('🔍 Result keys:', Object.keys(result || {}));
            
            // Show success message
            window.telegramWebApp?.showPopup(
                'Замовлення прийнято!',
                `Ваше замовлення №${result.order_id} успішно оформлено. Очікуйте підтвердження.`,
                [{type: 'ok', text: 'OK'}]
            );
            
            // Clear cart
            window.cart?.clear();
            
            // Send confirmation via Telegram (optional, backend already does this)
            if (window.telegramWebApp?.sendData) {
                window.telegramWebApp.sendData(JSON.stringify({
                    type: 'order_created',
                    order_id: result.order_id
                }));
            }
            
            // Navigate to categories with confirmation
            sessionStorage.setItem('orderConfirmed', 'true');
            sessionStorage.setItem('lastOrderId', result.order_id);
            
            setTimeout(() => {
                window.router?.navigateTo('categories');
            }, 1000);
            
        } catch (error) {
            console.error('❌ ERROR in submitOrderToBackend:', error);
            console.error('❌ Error type:', typeof error);
            console.error('❌ Error constructor name:', error.constructor.name);
            console.error('❌ Error toString:', error.toString());
            console.error('❌ Error message:', error.message);
            console.error('❌ Error stack:', error.stack);
            
            // Log the full error object to see its structure
            console.error('❌ Full error object:', JSON.stringify(error, Object.getOwnPropertyNames(error), 2));
            
            if (error.response) {
                console.error('❌ HTTP Response error:', error.response);
                console.error('❌ Response status:', error.response.status);
                console.error('❌ Response data:', error.response.data);
            }
            
            // Enhanced error message extraction
            let errorMessage = 'Помилка при оформленні замовлення';
            
            try {
                // First, try to get backend error details
                if (error.response?.data?.detail) {
                    errorMessage = `Помилка: ${String(error.response.data.detail)}`;
                    console.log('🔍 Using backend error detail:', error.response.data.detail);
                } else if (error.response?.data?.message) {
                    errorMessage = `Помилка: ${String(error.response.data.message)}`;
                    console.log('🔍 Using backend message:', error.response.data.message);
                } else if (error.message && typeof error.message === 'string') {
                    errorMessage = `Помилка: ${error.message}`;
                    console.log('🔍 Using error message:', error.message);
                } else if (error.toString && typeof error.toString === 'function') {
                    const errorStr = error.toString();
                    if (errorStr !== '[object Object]') {
                        errorMessage = `Помилка: ${errorStr}`;
                        console.log('🔍 Using error toString:', errorStr);
                    } else {
                        errorMessage = 'Помилка при оформленні замовлення. Спробуйте ще раз.';
                        console.log('🔍 Using fallback - toString returned [object Object]');
                    }
                } else {
                    errorMessage = 'Помилка при оформленні замовлення. Спробуйте ще раз.';
                    console.log('🔍 Using fallback - no usable error message found');
                }
            } catch (extractionError) {
                console.error('❌ Error while extracting error message:', extractionError);
                errorMessage = 'Помилка при оформленні замовлення. Спробуйте ще раз.';
            }
            
            console.log('🔍 Final error message to show:', errorMessage);
            
            // Show alert
            if (window.telegramWebApp?.showAlert) {
                window.telegramWebApp.showAlert(errorMessage);
                console.log('✅ Error alert shown via Telegram');
            } else {
                alert(errorMessage);
                console.log('✅ Error alert shown via browser alert');
            }
            
        } finally {
            console.log('🔧 Cleaning up - hiding loading and re-enabling button');
            
            // Hide loading overlay
            const loadingOverlay = document.getElementById('order-loading');
            if (loadingOverlay) {
                loadingOverlay.style.display = 'none';
                console.log('✅ Loading overlay hidden');
            }
            
            // Re-enable confirm button
            const confirmBtn = document.getElementById('confirm-order-btn');
            if (confirmBtn) {
                confirmBtn.disabled = false;
                console.log('✅ Confirm button re-enabled');
            }
            
            console.log('🏁 submitOrderToBackend() function completed');
        }
    }
    
    // Debug function for testing
    testOrderFlow() {
        console.log('🧪 Testing order confirmation flow...');
        
        // Check if we're on order-review screen
        const currentScreen = window.router?.getCurrentScreen();
        console.log('Current screen:', currentScreen);
        
        if (currentScreen !== 'order-review') {
            console.log('❌ Not on order review screen. Navigate there first.');
            return;
        }
        
        // Try to show confirmation dialog
        this.showOrderConfirmationDialog();
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

// Global debug function - creates debug panel dynamically
window.showDebugInfo = function() {
    // Remove existing debug panel if any
    const existingPanel = document.getElementById('debug-info');
    if (existingPanel) {
        existingPanel.remove();
    }
    
    // Get debug information
    const debugData = window.telegramWebApp?.getDebugInfo() || {};
    
    // Create debug panel
    const debugPanel = document.createElement('div');
    debugPanel.id = 'debug-info';
    debugPanel.innerHTML = `
        <div style="margin-bottom: 10px;"><strong>🔧 Debug Info</strong></div>
        <div>Telegram: ${debugData.hasTelegram ? 'Available' : 'Not Found'}</div>
        <div>WebApp: ${debugData.hasWebApp ? 'Available' : 'Not Found'}</div>
        <div>Init Data: ${debugData.hasInitData ? 'Present' : 'Missing'}</div>
        <div>User: ${debugData.hasUser ? 'Present' : 'Missing'}</div>
        <div>Version: ${debugData.version || 'Unknown'}</div>
        <div>Platform: ${debugData.platform || 'Unknown'}</div>
        <button onclick="document.getElementById('debug-info').remove()" style="margin-top: 15px; padding: 8px 16px; background: #dc3545; color: white; border: none; border-radius: 6px; cursor: pointer;">Close Debug</button>
    `;
    
    // Style the panel
    debugPanel.style.cssText = 'position: fixed; top: 50%; left: 50%; transform: translate(-50%, -50%); z-index: 9999; background: rgba(0,0,0,0.9); color: white; padding: 20px; border-radius: 12px; font-size: 12px; text-align: left; max-width: 90vw; box-shadow: 0 4px 20px rgba(0,0,0,0.5);';
    
    // Add to document
    document.body.appendChild(debugPanel);
};

// Triple-tap on loading screen to show debug
let tapCount = 0;
document.addEventListener('DOMContentLoaded', () => {
    const loadingScreen = document.getElementById('loading');
    if (loadingScreen) {
        loadingScreen.addEventListener('click', () => {
            tapCount++;
            if (tapCount === 3) {
                window.showDebugInfo();
                tapCount = 0;
            }
            // Reset counter after 2 seconds
            setTimeout(() => {
                tapCount = 0;
            }, 2000);
        });
    }
});

// Initialize app when DOM is loaded
document.addEventListener('DOMContentLoaded', async () => {
    console.log('DOM loaded, initializing app...');
    
    // Wait for Telegram WebApp to initialize first
    try {
        console.log('Waiting for Telegram WebApp initialization...');
        
        // Wait for Telegram WebApp to be ready
        if (window.telegramWebApp && window.telegramWebApp.initPromise) {
            const telegramReady = await window.telegramWebApp.initPromise;
            console.log('Telegram WebApp initialization result:', telegramReady);
        } else {
            console.log('Telegram WebApp not found, continuing without it');
        }
        
        // Additional wait to ensure all scripts are loaded
        await new Promise(resolve => setTimeout(resolve, 500));
        
        console.log('Initializing main app...');
        window.app = new SeafoodStoreApp();
        window.checkoutManager = new CheckoutManager(window.app);
        
        await window.app.initialize();
        console.log('App initialization completed successfully');
        
        // Add global debug helper
        window.testOrderFlow = () => {
            if (window.app && window.app.testOrderFlow) {
                window.app.testOrderFlow();
            } else {
                console.log('❌ App not available or testOrderFlow method not found');
            }
        };
        
        console.log('💡 Debug: You can test the order flow by calling testOrderFlow() in the console');
        
    } catch (error) {
        console.error('App initialization error:', error);
        const loadingText = document.querySelector('#loading p');
        if (loadingText) {
            loadingText.textContent = 'Помилка завантаження. Спробуйте оновити додаток.';
            loadingText.style.color = '#ff6b6b';
        }
        
        // Show error details in console for debugging
        console.error('Error details:', {
            message: error.message,
            stack: error.stack,
            telegramAvailable: !!window.Telegram,
            telegramWebAppAvailable: !!window.Telegram?.WebApp,
            telegramWebAppInstance: !!window.telegramWebApp
        });
    }
});