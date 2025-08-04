// Telegram Web App integration
class TelegramWebApp {
    constructor() {
        console.log('TelegramWebApp constructor called');
        console.log('window.Telegram:', window.Telegram);
        console.log('window.Telegram.WebApp:', window.Telegram?.WebApp);
        
        this.tg = window.Telegram?.WebApp;
        this.user = null;
        this.initData = '';
        
        if (!this.tg) {
            console.error('Telegram WebApp is not available');
            console.error('Available Telegram object:', window.Telegram);
            return;
        }
        
        console.log('Telegram WebApp object:', this.tg);
        console.log('BackButton object:', this.tg.BackButton);
        
        this.init();
    }
    
    init() {
        // Signal that the app is ready
        this.tg.ready();
        
        // Expand the app to full height
        this.tg.expand();
        
        // Apply Telegram theme
        this.applyTheme();
        
        // Get user data and init data
        this.user = this.tg.initDataUnsafe?.user;
        this.initData = this.tg.initData;
        
        // Set up main button first (doesn't depend on router)
        this.setupMainButton();
        
        // Set up back button - will retry if router not ready
        this.setupBackButtonWhenReady();
        
        // Enable closing confirmation
        this.tg.enableClosingConfirmation();
        
        console.log('Telegram WebApp initialized');
        console.log('User:', this.user);
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
            console.error('Telegram BackButton not available');
            return;
        }
        
        try {
            // Simple direct approach
            window.Telegram.WebApp.BackButton.onClick(function() {
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
        } catch (error) {
            console.error('❌ Error setting up back button:', error);
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
                this.submitOrder();
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
            console.log('Showing back button');
            this.tg.BackButton.show();
        } catch (error) {
            console.error('Error showing back button:', error);
        }
    }
    
    hideBackButton() {
        try {
            console.log('Hiding back button');
            this.tg.BackButton.hide();
        } catch (error) {
            console.error('Error hiding back button:', error);
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
        
        // Set order confirmation flag
        sessionStorage.setItem('orderConfirmed', 'true');
        
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
        return this.tg.showPopup({
            title: title,
            message: message,
            buttons: buttons
        });
    }
    
    showAlert(message) {
        this.tg.showAlert(message);
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