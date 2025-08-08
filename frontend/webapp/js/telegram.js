// Telegram Web App integration
class TelegramWebApp {
    constructor() {
        console.log('TelegramWebApp constructor called');
        console.log('window.Telegram:', window.Telegram);
        console.log('window.Telegram.WebApp:', window.Telegram?.WebApp);
        
        this.tg = null;
        this.user = null;
        this.initData = '';
        this.isInitialized = false;
        this.initPromise = null;
        
        // Initialize with better error handling
        this.initPromise = this.safeInit();
    }
    
    async safeInit() {
        try {
            // Wait for Telegram object to be available
            await this.waitForTelegram();
            
            this.tg = window.Telegram.WebApp;
            
            if (!this.tg) {
                throw new Error('Telegram WebApp object is not available');
            }
            
            console.log('Telegram WebApp object:', this.tg);
            console.log('Telegram WebApp version:', this.tg.version);
            console.log('Platform:', this.tg.platform);
            
            // Check if we're actually running in Telegram
            if (!this.tg.initData && !this.tg.initDataUnsafe) {
                console.warn('Running outside Telegram environment - limited functionality');
                // Still initialize for testing purposes
            }
            
            this.init();
            this.isInitialized = true;
            console.log('Telegram WebApp successfully initialized');
            return true;
            
        } catch (error) {
            console.error('Failed to initialize Telegram WebApp:', error);
            this.handleInitializationError(error);
            return false;
        }
    }
    
    waitForTelegram(maxAttempts = 50, interval = 100) {
        return new Promise((resolve, reject) => {
            let attempts = 0;
            
            const checkTelegram = () => {
                attempts++;
                
                if (window.Telegram && window.Telegram.WebApp) {
                    console.log(`Telegram WebApp found after ${attempts} attempts`);
                    resolve();
                } else if (attempts >= maxAttempts) {
                    reject(new Error('Telegram WebApp not found after maximum attempts'));
                } else {
                    setTimeout(checkTelegram, interval);
                }
            };
            
            checkTelegram();
        });
    }
    
    handleInitializationError(error) {
        console.error('Telegram WebApp initialization failed:', error);
        
        // Create a mock object for development/testing
        this.tg = {
            ready: () => console.log('Mock: ready() called'),
            expand: () => console.log('Mock: expand() called'),
            enableClosingConfirmation: () => console.log('Mock: enableClosingConfirmation() called'),
            MainButton: {
                setText: (text) => console.log('Mock MainButton.setText:', text),
                show: () => console.log('Mock MainButton.show()'),
                hide: () => console.log('Mock MainButton.hide()'),
                enable: () => console.log('Mock MainButton.enable()'),
                disable: () => console.log('Mock MainButton.disable()'),
                onClick: (callback) => console.log('Mock MainButton.onClick registered'),
                setParams: (params) => console.log('Mock MainButton.setParams:', params)
            },
            BackButton: {
                show: () => console.log('Mock BackButton.show()'),
                hide: () => console.log('Mock BackButton.hide()'),
                onClick: (callback) => console.log('Mock BackButton.onClick registered')
            },
            themeParams: {},
            initData: '',
            initDataUnsafe: {},
            version: '7.0',
            platform: 'unknown',
            HapticFeedback: {
                impactOccurred: (type) => console.log('Mock haptic:', type),
                notificationOccurred: (type) => console.log('Mock notification:', type)
            },
            showPopup: (params) => {
                console.log('Mock showPopup:', params);
                alert(`${params.title}\n\n${params.message}`);
            },
            showAlert: (message) => {
                console.log('Mock showAlert:', message);
                alert(message);
            },
            sendData: (data) => console.log('Mock sendData:', data),
            onEvent: (event, callback) => console.log('Mock onEvent:', event),
            close: () => console.log('Mock close()'),
            openLink: (url) => console.log('Mock openLink:', url)
        };
        
        // Display user-friendly error message
        setTimeout(() => {
            const loadingText = document.querySelector('#loading p');
            if (loadingText && loadingText.textContent === 'Завантаження...') {
                loadingText.textContent = 'Помилка ініціалізації Telegram. Спробуйте оновити додаток.';
                loadingText.style.color = '#ff6b6b';
            }
        }, 2000);
    }
    
    init() {
        try {
            console.log('Starting Telegram WebApp initialization...');
            
            // Signal that the app is ready
            this.tg.ready();
            console.log('✅ Telegram WebApp ready() called');
            
            // Expand the app to full height
            this.tg.expand();
            console.log('✅ Telegram WebApp expand() called');
            
            // Apply Telegram theme
            this.applyTheme();
            console.log('✅ Theme applied');
            
            // Get user data and init data
            this.user = this.tg.initDataUnsafe?.user;
            this.initData = this.tg.initData;
            console.log('✅ User data retrieved:', this.user);
            console.log('✅ Init data length:', this.initData?.length || 0);
            
            // Set up main button first (doesn't depend on router)
            this.setupMainButton();
            console.log('✅ Main button configured');
            
            // Set up back button - will retry if router not ready
            this.setupBackButtonWhenReady();
            console.log('✅ Back button setup scheduled');
            
            // Enable closing confirmation
            this.tg.enableClosingConfirmation();
            console.log('✅ Closing confirmation enabled');
            
            console.log('✅ Telegram WebApp initialization completed successfully');
            
        } catch (error) {
            console.error('❌ Error during Telegram WebApp initialization:', error);
            throw error;
        }
    }
    
    applyTheme() {
        const themeParams = this.tg.themeParams;
        const root = document.documentElement;
        
        // Apply Telegram theme params
        if (themeParams.bg_color) {
            root.style.setProperty('--tg-theme-bg-color', themeParams.bg_color);
        }
        if (themeParams.text_color) {
            root.style.setProperty('--tg-theme-text-color', themeParams.text_color);
        }
        if (themeParams.hint_color) {
            root.style.setProperty('--tg-theme-hint-color', themeParams.hint_color);
        }
        if (themeParams.button_color) {
            root.style.setProperty('--tg-theme-button-color', themeParams.button_color);
        }
        if (themeParams.button_text_color) {
            root.style.setProperty('--tg-theme-button-text-color', themeParams.button_text_color);
        }
        if (themeParams.secondary_bg_color) {
            root.style.setProperty('--tg-theme-secondary-bg-color', themeParams.secondary_bg_color);
        }
        if (themeParams.link_color) {
            root.style.setProperty('--tg-theme-link-color', themeParams.link_color);
        }
        
        // Detect theme and apply class
        const isDark = this.isBackgroundDark();
        document.body.classList.add(isDark ? 'theme-dark' : 'theme-light');
        
        // Update all logos based on theme
        this.updateLogos();
    }
    
    hexToRgb(hex) {
        const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
        return result ? {
            r: parseInt(result[1], 16),
            g: parseInt(result[2], 16),
            b: parseInt(result[3], 16)
        } : null;
    }
    
    isBackgroundDark() {
        const bgColor = this.tg.themeParams.bg_color;
        if (!bgColor) return false;
        
        const rgb = this.hexToRgb(bgColor);
        if (!rgb) return false;
        
        const luminance = (0.299 * rgb.r + 0.587 * rgb.g + 0.114 * rgb.b) / 255;
        return luminance < 0.5;
    }
    
    isBackgroundBlue() {
        const bgColor = this.tg.themeParams.bg_color;
        if (!bgColor) return false;
        
        const rgb = this.hexToRgb(bgColor);
        if (!rgb) return false;
        
        return rgb.b > rgb.r && rgb.b > rgb.g;
    }
    
    getBackgroundType() {
        const isDark = this.isBackgroundDark();
        const isBlue = this.isBackgroundBlue();
        
        if (isDark && isBlue) return 'dark-blue';
        if (isDark) return 'dark';
        if (isBlue) return 'blue';
        return 'light';
    }
    
    setupBackButtonWhenReady() {
        // Much simpler approach - just set it up when DOM is ready
        document.addEventListener('DOMContentLoaded', () => {
            setTimeout(() => {
                this.setupBackButton();
            }, 2000); // Wait 2 seconds for everything to load
        });
        
        // Also try immediately if DOM already loaded
        if (document.readyState === 'complete' || document.readyState === 'interactive') {
            setTimeout(() => {
                this.setupBackButton();
            }, 2000);
        }
    }
    
    setupBackButton() {
        console.log('Setting up back button...');
        
        if (!this.tg || !this.tg.BackButton) {
            console.warn('Telegram BackButton not available in this version');
            return;
        }
        
        try {
            // Check if BackButton is supported
            if (this.tg.BackButton && typeof this.tg.BackButton.onClick === 'function') {
                this.tg.BackButton.onClick(function() {
                    console.log('>>> BACK BUTTON CLICKED <<<');
                
                // Simple fallback navigation
                if (window.router && window.router.goBack) {
                    console.log('Using router.goBack()');
                    window.router.goBack();
                } else {
                    console.log('Router not available, going to categories');
                    if (window.router && window.router.navigateTo) {
                        window.router.navigateTo('categories');
                    }
                }
                });
                
                console.log('✅ Back button handler set up');
            } else {
                console.warn('BackButton.onClick not supported in this WebApp version');
            }
        } catch (error) {
            console.warn('BackButton not supported in this WebApp version:', error.message);
        }
    }
    
    setupMainButton() {
        // Configure main button
        this.tg.MainButton.setParams({
            text: 'Оформити замовлення',
            color: this.tg.themeParams.button_color || '#2481cc',
            text_color: this.tg.themeParams.button_text_color || '#ffffff'
        });
        
        // Handle main button click
        this.tg.MainButton.onClick(() => {
            const currentScreen = window.router?.getCurrentScreen();
            
            if (currentScreen === 'cart') {
                window.router?.navigateTo('checkout');
            } else if (currentScreen === 'checkout') {
                // Trigger form submission which will navigate to order confirmation
                const checkoutForm = document.getElementById('checkout-form');
                if (checkoutForm) {
                    checkoutForm.dispatchEvent(new Event('submit', { bubbles: true, cancelable: true }));
                }
            } else if (currentScreen === 'order-review') {
                // Submit order directly
                const confirmBtn = document.getElementById('confirm-order-btn');
                if (confirmBtn) {
                    confirmBtn.click();
                }
            }
        });
        
        // Handle popup events
        this.tg.onEvent('popupClosed', (eventData) => {
            console.log('Popup closed with button:', eventData.button_id);
            
            if (eventData.button_id === 'goto_cart') {
                console.log('Navigating to cart...');
                window.router?.navigateTo('cart');
            }
        });
    }
    
    updateLogos() {
        // This function will be called to update all logo elements on the page
        const isDark = this.isBackgroundDark();
        const logos = document.querySelectorAll('.loading-logo, .header-logo, .header-logo-small');
        
        logos.forEach(logo => {
            if (isDark) {
                // For dark theme, show emoji placeholder
                logo.style.display = 'none';
                let emojiLogo = logo.nextElementSibling;
                if (!emojiLogo || !emojiLogo.classList.contains('logo-emoji')) {
                    emojiLogo = document.createElement('div');
                    emojiLogo.className = logo.className + ' logo-emoji';
                    emojiLogo.textContent = '🐟'; // Fish emoji as placeholder
                    logo.parentNode.insertBefore(emojiLogo, logo.nextSibling);
                }
                emojiLogo.style.display = 'flex';
            } else {
                // For light theme, show regular logo
                logo.style.display = 'block';
                const emojiLogo = logo.nextElementSibling;
                if (emojiLogo && emojiLogo.classList.contains('logo-emoji')) {
                    emojiLogo.style.display = 'none';
                }
            }
        });
    }
    
    showBackButton() {
        try {
            if (this.tg.BackButton && typeof this.tg.BackButton.show === 'function') {
                console.log('Showing back button');
                this.tg.BackButton.show();
            } else {
                console.warn('BackButton.show not supported in this WebApp version');
            }
        } catch (error) {
            console.warn('Error showing back button:', error.message);
        }
    }
    
    hideBackButton() {
        try {
            if (this.tg.BackButton && typeof this.tg.BackButton.hide === 'function') {
                console.log('Hiding back button');
                this.tg.BackButton.hide();
            } else {
                console.warn('BackButton.hide not supported in this WebApp version');
            }
        } catch (error) {
            console.warn('Error hiding back button:', error.message);
        }
    }
    
    showMainButton(text = 'Продовжити') {
        this.tg.MainButton.setText(text);
        this.tg.MainButton.show();
    }
    
    hideMainButton() {
        this.tg.MainButton.hide();
    }
    
    updateMainButton(text, enabled = true) {
        this.tg.MainButton.setText(text);
        if (enabled) {
            this.tg.MainButton.enable();
        } else {
            this.tg.MainButton.disable();
        }
    }
    
    submitOrder() {
        const orderData = window.checkoutManager?.getOrderData();
        
        if (!orderData) {
            this.showPopup('Помилка', 'Не вдалося сформувати дані замовлення');
            return;
        }
        
        // Add Telegram data
        orderData.user_id = this.user?.id;
        orderData.user_name = this.user?.first_name || 'Користувач';
        orderData.init_data = this.initData;
        
        // Send data to bot
        this.tg.sendData(JSON.stringify(orderData));
        
        // Handle successful order submission
        this.handleOrderSuccess();
    }
    
    handleOrderSuccess() {
        // Clear cart
        if (window.cart) {
            window.cart.clear();
        }
        
        // Don't set orderConfirmed flag here - it should only be set after actual backend submission
        // The flag will be set in app.js after successful API call
        
        // Navigate to main page (categories)
        setTimeout(() => {
            if (window.router) {
                window.router.navigateTo('categories');
            }
        }, 500);
    }
    
    hapticFeedback(type = 'light') {
        // Provide haptic feedback
        if (this.tg.HapticFeedback) {
            switch (type) {
                case 'light':
                    this.tg.HapticFeedback.impactOccurred('light');
                    break;
                case 'medium':
                    this.tg.HapticFeedback.impactOccurred('medium');
                    break;
                case 'heavy':
                    this.tg.HapticFeedback.impactOccurred('heavy');
                    break;
                case 'success':
                    this.tg.HapticFeedback.notificationOccurred('success');
                    break;
                case 'warning':
                    this.tg.HapticFeedback.notificationOccurred('warning');
                    break;
                case 'error':
                    this.tg.HapticFeedback.notificationOccurred('error');
                    break;
            }
        }
    }
    
    showPopup(title, message, buttons = [{ type: 'close' }]) {
        try {
            if (this.tg.showPopup) {
                return this.tg.showPopup({
                    title: title,
                    message: message,
                    buttons: buttons
                });
            } else {
                // Fallback for older Telegram WebApp versions
                console.warn('Telegram showPopup not supported, using alert:', title, message);
                alert(`${title}\n\n${message}`);
            }
        } catch (error) {
            console.warn('Telegram showPopup not supported:', error.message);
            alert(`${title}\n\n${message}`);
        }
    }
    
    showAlert(message) {
        try {
            if (this.tg.showAlert) {
                this.tg.showAlert(message);
            } else {
                // Fallback for older versions
                console.warn('Telegram showAlert not supported, using console:', message);
                alert(message);
            }
        } catch (error) {
            console.warn('Telegram showAlert not supported:', error.message);
            alert(message);
        }
    }
    
    openLink(url) {
        this.tg.openLink(url);
    }
    
    close() {
        this.tg.close();
    }
    
    getUserData() {
        return this.user;
    }
    
    getInitData() {
        return this.initData;
    }
    
    isReady() {
        return this.isInitialized && this.tg;
    }
    
    getDebugInfo() {
        return {
            isInitialized: this.isInitialized,
            hasTelegram: !!window.Telegram,
            hasWebApp: !!window.Telegram?.WebApp,
            hasUser: !!this.user,
            hasInitData: !!this.initData,
            version: this.tg?.version,
            platform: this.tg?.platform
        };
    }
}

// Initialize Telegram WebApp
console.log('Initializing Telegram WebApp...');
window.telegramWebApp = new TelegramWebApp();

// Global test function for debugging
window.testBackButton = function() {
    console.log('=== TESTING BACK BUTTON ===');
    console.log('Telegram:', window.Telegram);
    console.log('WebApp:', window.Telegram?.WebApp);
    console.log('BackButton:', window.Telegram?.WebApp?.BackButton);
    
    if (window.Telegram?.WebApp?.BackButton) {
        console.log('✅ BackButton is available');
        console.log('Trying to show back button...');
        window.Telegram.WebApp.BackButton.show();
        console.log('Back button should now be visible');
    } else {
        console.log('❌ BackButton not available');
    }
};