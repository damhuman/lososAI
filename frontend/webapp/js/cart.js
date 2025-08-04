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
                weight: packageInfo.weight,
                unit: packageInfo.unit,
                quantity: quantity,
                price_per_unit: product.price_per_kg * packageInfo.weight,
                total_price: quantity * (product.price_per_kg * packageInfo.weight),
                image_url: product.image_url
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
        }
    }
    
    // Getters
    getItems() {
        return [...this.items];
    }
    
    getItemCount() {
        // Count unique items (positions) in cart, not total quantity
        const count = this.items.length;
        console.log('getItemCount - unique items:', count);
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
        
        this.cartItemsContainer.innerHTML = '';
        
        items.forEach(item => {
            const cartItemElement = this.createCartItemElement(item);
            this.cartItemsContainer.appendChild(cartItemElement);
        });
    }
    
    createCartItemElement(item) {
        const div = document.createElement('div');
        div.className = 'cart-item';
        
        div.innerHTML = `
            <div class="cart-item-header">
                <h4>${item.product_name}</h4>
                <button class="cart-item-remove" data-product-id="${item.product_id}" data-package-id="${item.package_id}">
                    ×
                </button>
            </div>
            <div class="cart-item-details">
                ${item.weight} ${item.unit} • ${item.price_per_unit} грн за одиницю
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
        `;
        
        this.attachCartItemListeners(div);
        
        return div;
    }
    
    attachCartItemListeners(element) {
        // Remove item
        const removeBtn = element.querySelector('.cart-item-remove');
        removeBtn.addEventListener('click', (e) => {
            const productId = e.target.dataset.productId;
            const packageId = e.target.dataset.packageId;
            this.cart.removeItem(productId, packageId);
        });
        
        // Quantity controls
        const quantityBtns = element.querySelectorAll('.cart-quantity-btn');
        quantityBtns.forEach(btn => {
            btn.addEventListener('click', (e) => {
                const action = e.target.dataset.action;
                const productId = e.target.dataset.productId;
                const packageId = e.target.dataset.packageId;
                const currentItem = this.cart.findItem(productId, packageId);
                
                if (currentItem) {
                    const newQuantity = action === 'increase' 
                        ? currentItem.quantity + 1 
                        : currentItem.quantity - 1;
                    
                    this.cart.updateQuantity(productId, packageId, newQuantity);
                }
            });
        });
        
        // Quantity input
        const quantityInput = element.querySelector('.cart-quantity-input');
        quantityInput.addEventListener('change', (e) => {
            const productId = e.target.dataset.productId;
            const packageId = e.target.dataset.packageId;
            const newQuantity = parseInt(e.target.value) || 1;
            
            this.cart.updateQuantity(productId, packageId, newQuantity);
        });
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