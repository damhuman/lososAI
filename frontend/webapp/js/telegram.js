// Telegram Web App integration
class TelegramWebApp {
    constructor() {
        this.tg = window.Telegram?.WebApp;
        this.user = null;
        this.initData = '';
        
        if (!this.tg) {
            console.error('Telegram WebApp is not available');
            return;
        }
        
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
        
        // Set up navigation
        this.setupBackButton();
        this.setupMainButton();
        
        // Enable closing confirmation
        this.tg.enableClosingConfirmation();
        
        console.log('Telegram WebApp initialized');
        console.log('User:', this.user);
    }
    
    applyTheme() {
        const themeParams = this.tg.themeParams;
        const root = document.documentElement;
        
        // Apply theme colors
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
    }
    
    setupBackButton() {
        // Handle back button
        this.tg.BackButton.onClick(() => {
            window.router?.goBack();
        });
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
    }
    
    showBackButton() {
        this.tg.BackButton.show();
    }
    
    hideBackButton() {
        this.tg.BackButton.hide();
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
        this.tg.showPopup({
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
window.telegramWebApp = new TelegramWebApp();