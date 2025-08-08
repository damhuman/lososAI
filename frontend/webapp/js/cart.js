// Shopping cart management
class ShoppingCart {
    constructor() {
        this.items = [];
        this.listeners = [];
        this.storageKey = 'seafood_store_cart';
        
        // Load cart from localStorage
        this.loadFromStorage();
    }
    
    // Event listeners
    addListener(callback) {
        this.listeners.push(callback);
    }
    
    removeListener(callback) {
        this.listeners = this.listeners.filter(l => l !== callback);
    }
    
    notifyListeners() {
        this.listeners.forEach(callback => callback(this.items));
        // Update cart badge
        this.updateCartBadge();
    }
    
    updateCartBadge() {
        const badge = document.getElementById('cart-badge');
        console.log('Updating cart badge, element found:', !!badge);
        if (badge) {
            const itemCount = this.getItemCount();
            console.log('Cart item count:', itemCount);
            badge.textContent = itemCount > 0 ? itemCount.toString() : '';
            badge.classList.toggle('hidden', itemCount === 0);
            
            // Apply NUCLEAR drag prevention to badge every time it's updated
            badge.setAttribute('draggable', 'false');
            badge.setAttribute('unselectable', 'on');
            badge.style.userSelect = 'none';
            badge.style.webkitUserSelect = 'none';
            badge.style.mozUserSelect = 'none';
            badge.style.msUserSelect = 'none';
            badge.style.webkitUserDrag = 'none';
            badge.style.webkitTouchCallout = 'none';
            badge.style.touchAction = 'none';
            badge.style.contain = 'layout style paint';
            badge.style.position = 'absolute';
            badge.style.top = '-4px';
            badge.style.right = '-4px';
            
            // Add event listeners to badge specifically
            const preventDrag = (e) => {
                e.preventDefault();
                e.stopPropagation();
                e.stopImmediatePropagation();
                return false;
            };
            
            const badgeEvents = [
                'dragstart', 'drag', 'dragend', 'dragenter', 'dragleave', 
                'dragover', 'drop', 'selectstart', 'mousedown', 'touchstart',
                'touchmove', 'touchend'
            ];
            
            badgeEvents.forEach(eventType => {
                badge.removeEventListener(eventType, preventDrag); // Remove old listeners
                badge.addEventListener(eventType, preventDrag, { 
                    capture: true, 
                    passive: false 
                });
            });
        }
    }
    
    // Storage management
    saveToStorage() {
        try {
            localStorage.setItem(this.storageKey, JSON.stringify(this.items));
        } catch (error) {
            console.error('Failed to save cart to storage:', error);
        }
    }
    
    loadFromStorage() {
        try {
            const stored = localStorage.getItem(this.storageKey);
            if (stored) {
                this.items = JSON.parse(stored);
            }
        } catch (error) {
            console.error('Failed to load cart from storage:', error);
            this.items = [];
        }
        // Update badge on load
        this.updateCartBadge();
    }
    
    clearStorage() {
        localStorage.removeItem(this.storageKey);
    }
    
    // Cart operations
    addItem(product, packageInfo, quantity = 1) {
        const existingItemIndex = this.items.findIndex(item => 
            item.product_id === product.id && item.package_id === packageInfo.id
        );
        
        if (existingItemIndex >= 0) {
            // Update existing item
            this.items[existingItemIndex].quantity += quantity;
            this.items[existingItemIndex].total_price = 
                this.items[existingItemIndex].quantity * this.items[existingItemIndex].price_per_unit;
        } else {
            // Add new item
            const cartItem = {
                product_id: product.id,
                product_name: product.name,
                package_id: packageInfo.id,
                package_name: packageInfo.name, // Use the formatted name from the package
                weight: packageInfo.weight,
                unit: packageInfo.unit,
                quantity: quantity,
                price_per_unit: packageInfo.price, // Use package price directly
                total_price: quantity * packageInfo.price,
                image_url: packageInfo.image_url || product.image_url // Prefer package image, fallback to product image
            };
            
            this.items.push(cartItem);
        }
        
        this.saveToStorage();
        this.notifyListeners();
        
        // Haptic feedback
        window.telegramWebApp?.hapticFeedback('light');
    }
    
    removeItem(productId, packageId) {
        this.items = this.items.filter(item => 
            !(item.product_id === productId && item.package_id === packageId)
        );
        
        this.saveToStorage();
        this.notifyListeners();
        
        // Haptic feedback
        window.telegramWebApp?.hapticFeedback('light');
    }
    
    updateQuantity(productId, packageId, newQuantity) {
        const item = this.items.find(item => 
            item.product_id === productId && item.package_id === packageId
        );
        
        if (item) {
            if (newQuantity <= 0) {
                this.removeItem(productId, packageId);
            } else {
                item.quantity = newQuantity;
                item.total_price = item.quantity * item.price_per_unit;
                
                this.saveToStorage();
                this.notifyListeners();
            }
        }
    }
    
    clear() {
        this.items = [];
        this.clearStorage();
        this.notifyListeners();
    }
    
    // Initialize cart icon click handler
    initializeCartIcon() {
        const cartIcon = document.getElementById('cart-icon');
        if (cartIcon) {
            cartIcon.addEventListener('click', () => {
                window.router?.navigateTo('cart');
                window.telegramWebApp?.hapticFeedback('light');
            });
            
            // EXTREME drag prevention - multiple event types
            const preventDrag = (e) => {
                e.preventDefault();
                e.stopPropagation();
                e.stopImmediatePropagation();
                return false;
            };
            
            // Add multiple event listeners
            const dragEvents = [
                'dragstart', 'drag', 'dragend', 'dragenter', 'dragleave', 
                'dragover', 'drop', 'selectstart', 'mousedown'
            ];
            
            dragEvents.forEach(eventType => {
                cartIcon.addEventListener(eventType, preventDrag, { 
                    capture: true, 
                    passive: false 
                });
            });
            
            // Prevent touch drag on mobile with multiple events
            const touchEvents = ['touchstart', 'touchmove', 'touchend'];
            touchEvents.forEach(eventType => {
                cartIcon.addEventListener(eventType, (e) => {
                    if (eventType === 'touchmove') {
                        e.preventDefault();
                        e.stopPropagation();
                    }
                }, { passive: false });
            });
            
            // Force attributes
            cartIcon.setAttribute('draggable', 'false');
            cartIcon.setAttribute('unselectable', 'on');
            cartIcon.style.userSelect = 'none';
            cartIcon.style.webkitUserSelect = 'none';
            cartIcon.style.mozUserSelect = 'none';
            cartIcon.style.msUserSelect = 'none';
            
            // Apply to all child elements recursively
            const applyToElement = (element) => {
                element.setAttribute('draggable', 'false');
                element.setAttribute('unselectable', 'on');
                
                dragEvents.forEach(eventType => {
                    element.addEventListener(eventType, preventDrag, { 
                        capture: true, 
                        passive: false 
                    });
                });
                
                // Apply to children
                Array.from(element.children).forEach(child => {
                    applyToElement(child);
                });
            };
            
            applyToElement(cartIcon);
            
            // Global prevention for cart icon specifically
            document.addEventListener('dragstart', (e) => {
                if (e.target.closest('#cart-icon')) {
                    e.preventDefault();
                    e.stopPropagation();
                    return false;
                }
            }, { capture: true });
            
            // Force position reset if somehow moved
            const resetPosition = () => {
                cartIcon.style.position = 'fixed';
                cartIcon.style.top = '16px';
                cartIcon.style.right = '16px';
            };
            
            // Badge position reset
            const resetBadgePosition = () => {
                const badge = document.getElementById('cart-badge');
                if (badge) {
                    badge.style.position = 'absolute';
                    badge.style.top = '-4px';
                    badge.style.right = '-4px';
                    badge.style.pointerEvents = 'none';
                }
            };
            
            // Monitor for position changes on cart icon
            const observer = new MutationObserver((mutations) => {
                mutations.forEach((mutation) => {
                    if (mutation.type === 'attributes' && 
                        (mutation.attributeName === 'style' || 
                         mutation.attributeName === 'class')) {
                        resetPosition();
                    }
                });
            });
            
            observer.observe(cartIcon, {
                attributes: true,
                attributeFilter: ['style', 'class']
            });
            
            // Monitor badge specifically
            const badge = document.getElementById('cart-badge');
            if (badge) {
                const badgeObserver = new MutationObserver((mutations) => {
                    mutations.forEach((mutation) => {
                        if (mutation.type === 'attributes') {
                            resetBadgePosition();
                        }
                    });
                });
                
                badgeObserver.observe(badge, {
                    attributes: true,
                    attributeFilter: ['style', 'class', 'draggable']
                });
            }
        }
    }
    
    // Getters
    getItems() {
        return [...this.items];
    }
    
    getItemCount() {
        // Count total quantity of all items in cart
        const count = this.items.reduce((total, item) => total + item.quantity, 0);
        console.log('getItemCount - total quantity:', count);
        return count;
    }
    
    getTotalPrice() {
        return this.items.reduce((total, item) => total + item.total_price, 0);
    }
    
    isEmpty() {
        return this.items.length === 0;
    }
    
    // Find specific item
    findItem(productId, packageId) {
        return this.items.find(item => 
            item.product_id === productId && item.package_id === packageId
        );
    }
}

// Cart UI Manager
class CartUIManager {
    constructor(cart) {
        this.cart = cart;
        this.cartItemsContainer = null;
        this.cartEmptyElement = null;
        this.cartSummaryElement = null;
        this.cartTotalElement = null;
        
        // Listen to cart changes
        this.cart.addListener(() => this.updateUI());
    }
    
    initialize() {
        this.cartItemsContainer = document.getElementById('cart-items');
        this.cartEmptyElement = document.getElementById('cart-empty');
        this.cartSummaryElement = document.getElementById('cart-summary');
        this.cartTotalElement = document.getElementById('cart-total');
        
        this.updateUI();
    }
    
    updateUI() {
        if (!this.cartItemsContainer) return;
        
        const items = this.cart.getItems();
        
        if (items.length === 0) {
            this.showEmptyState();
        } else {
            this.showCartItems(items);
        }
        
        this.updateTotal();
        this.updateMainButton();
    }
    
    showEmptyState() {
        this.cartItemsContainer.style.display = 'none';
        this.cartSummaryElement.style.display = 'none';
        this.cartEmptyElement.style.display = 'block';
    }
    
    showCartItems(items) {
        this.cartItemsContainer.style.display = 'block';
        this.cartSummaryElement.style.display = 'block';
        this.cartEmptyElement.style.display = 'none';
        
        // Clear existing items
        this.cartItemsContainer.innerHTML = '';
        
        // Create and append new items with event listeners
        items.forEach(item => {
            const cartItemElement = this.createCartItemElement(item);
            this.cartItemsContainer.appendChild(cartItemElement);
            // Attach event listeners to this specific item
            this.attachEventListeners(cartItemElement, item);
        });
    }
    
    createCartItemElement(item) {
        const div = document.createElement('div');
        div.className = 'cart-item';
        
        // Create product image with fallback logic
        const getCartItemFallback = (packageName, weight, unit) => {
            if (packageName && typeof packageName === 'string' && (packageName.toLowerCase().includes('0.5') || packageName.toLowerCase().includes('500'))) return '/images/package-500g.svg';
            if (packageName && typeof packageName === 'string' && (packageName.toLowerCase().includes('1.0') || packageName.toLowerCase().includes('1kg'))) return '/images/package-1kg.svg';
            if (weight && unit) {
                const weightStr = `${weight}${unit}`;
                if (weightStr.includes('0.5') || weightStr.includes('500')) return '/images/package-500g.svg';
                if (weightStr.includes('1') && unit === 'kg') return '/images/package-1kg.svg';
            }
            return '/images/placeholder.svg';
        };
        
        const productImage = item.image_url ? 
            `<img src="${item.image_url}" alt="${item.product_name}" class="cart-item-image loading" onload="this.classList.remove('loading')" onerror="this.onerror=null; this.src='${getCartItemFallback(item.package_name, item.weight, item.unit)}'; this.classList.remove('loading'); this.classList.add('fallback-image');">` : 
            `<img src="${getCartItemFallback(item.package_name, item.weight, item.unit)}" alt="${item.product_name}" class="cart-item-image fallback-image">`;
        
        div.innerHTML = `
            <div class="cart-item-content">
                <div class="cart-item-image-container">
                    ${productImage}
                </div>
                <div class="cart-item-info">
                    <div class="cart-item-header">
                        <h4>${item.product_name}</h4>
                        <button class="cart-item-remove" data-product-id="${item.product_id}" data-package-id="${item.package_id}">
                            ×
                        </button>
                    </div>
                    <div class="cart-item-details">
                        ${item.package_name || `${item.weight} ${item.unit}`} • ${item.price_per_unit} грн за одиницю
                    </div>
                    <div class="cart-item-controls">
                        <div class="cart-quantity-controls">
                            <button class="cart-quantity-btn" data-action="decrease" data-product-id="${item.product_id}" data-package-id="${item.package_id}">-</button>
                            <input type="number" class="cart-quantity-input" value="${item.quantity}" min="1" max="10" 
                                   data-product-id="${item.product_id}" data-package-id="${item.package_id}">
                            <button class="cart-quantity-btn" data-action="increase" data-product-id="${item.product_id}" data-package-id="${item.package_id}">+</button>
                        </div>
                        <div class="cart-item-price">
                            ${item.total_price} грн
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        return div;
    }
    
    attachEventListeners(element, item) {
        // Get all interactive elements
        const removeBtn = element.querySelector('.cart-item-remove');
        const increaseBtn = element.querySelector('[data-action="increase"]');
        const decreaseBtn = element.querySelector('[data-action="decrease"]');
        const quantityInput = element.querySelector('.cart-quantity-input');
        
        // Remove button
        if (removeBtn) {
            removeBtn.addEventListener('click', (e) => {
                e.preventDefault();
                e.stopPropagation();
                console.log('Remove clicked for:', item.product_id, item.package_id);
                this.cart.removeItem(item.product_id, item.package_id);
            });
        }
        
        // Increase button
        if (increaseBtn) {
            increaseBtn.addEventListener('click', (e) => {
                e.preventDefault();
                e.stopPropagation();
                console.log('Increase clicked for:', item.product_id, item.package_id);
                this.cart.updateQuantity(item.product_id, item.package_id, item.quantity + 1);
            });
        }
        
        // Decrease button
        if (decreaseBtn) {
            decreaseBtn.addEventListener('click', (e) => {
                e.preventDefault();
                e.stopPropagation();
                console.log('Decrease clicked for:', item.product_id, item.package_id);
                const newQuantity = Math.max(1, item.quantity - 1);
                this.cart.updateQuantity(item.product_id, item.package_id, newQuantity);
            });
        }
        
        // Quantity input
        if (quantityInput) {
            quantityInput.addEventListener('change', (e) => {
                const newQuantity = Math.max(1, parseInt(e.target.value) || 1);
                console.log('Quantity input changed for:', item.product_id, item.package_id, 'to:', newQuantity);
                this.cart.updateQuantity(item.product_id, item.package_id, newQuantity);
            });
        }
    }
    
    updateTotal() {
        if (this.cartTotalElement) {
            const total = this.cart.getTotalPrice();
            this.cartTotalElement.textContent = `${total} грн`;
        }
    }
    
    updateMainButton() {
        const itemCount = this.cart.getItemCount();
        const total = this.cart.getTotalPrice();
        
        if (itemCount > 0 && window.router?.getCurrentScreen() === 'cart') {
            window.telegramWebApp?.showMainButton(`Оформити (${total} грн)`);
        } else {
            window.telegramWebApp?.hideMainButton();
        }
    }
}

// Global cart instance
window.cart = new ShoppingCart();
window.cartUI = new CartUIManager(window.cart);