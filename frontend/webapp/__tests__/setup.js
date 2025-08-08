/**
 * Jest setup file for Telegram WebApp testing
 * Mocks the Telegram WebApp API and other browser APIs
 */

// Mock Telegram WebApp API
const mockTelegramWebApp = {
  // User data
  user: {
    id: 123456789,
    first_name: 'Test',
    last_name: 'User',
    username: 'testuser',
    language_code: 'uk'
  },
  
  // WebApp methods
  ready: jest.fn(),
  close: jest.fn(),
  expand: jest.fn(),
  
  // Navigation
  showBackButton: jest.fn(),
  hideBackButton: jest.fn(),
  showMainButton: jest.fn(),
  hideMainButton: jest.fn(),
  updateMainButton: jest.fn((text, enabled = true) => {
    mockTelegramWebApp.MainButton.text = text;
    mockTelegramWebApp.MainButton.isVisible = true;
    if (enabled) {
      mockTelegramWebApp.MainButton.show();
    }
  }),
  
  // Main Button
  MainButton: {
    text: '',
    isVisible: false,
    isActive: true,
    show: jest.fn(function() {
      this.isVisible = true;
    }),
    hide: jest.fn(function() {
      this.isVisible = false;
    }),
    setText: jest.fn(function(text) {
      this.text = text;
    }),
    onClick: jest.fn(),
    offClick: jest.fn()
  },
  
  // Back Button
  BackButton: {
    isVisible: false,
    show: jest.fn(function() {
      this.isVisible = true;
    }),
    hide: jest.fn(function() {
      this.isVisible = false;
    }),
    onClick: jest.fn(),
    offClick: jest.fn()
  },
  
  // Feedback
  hapticFeedback: jest.fn(),
  showPopup: jest.fn(),
  showAlert: jest.fn(),
  showConfirm: jest.fn(),
  
  // Data
  getInitData: jest.fn(() => 'query_id=test_query_id&user={"id":123456789,"first_name":"Test","last_name":"User","username":"testuser","language_code":"uk"}&auth_date=1234567890&hash=test_hash'),
  getInitDataUnsafe: jest.fn(() => ({
    query_id: 'test_query_id',
    user: {
      id: 123456789,
      first_name: 'Test',
      last_name: 'User',
      username: 'testuser',
      language_code: 'uk'
    },
    auth_date: 1234567890,
    hash: 'test_hash'
  })),
  
  sendData: jest.fn(),
  
  // Theme
  colorScheme: 'light',
  themeParams: {
    bg_color: '#ffffff',
    text_color: '#000000',
    hint_color: '#707579',
    link_color: '#3390ec',
    button_color: '#3390ec',
    button_text_color: '#ffffff'
  },
  
  // Debug
  getDebugInfo: jest.fn(() => ({
    hasTelegram: true,
    hasWebApp: true,
    hasInitData: true,
    hasUser: true,
    version: '6.0',
    platform: 'unknown'
  })),
  
  // Initialize promise for testing
  initPromise: Promise.resolve(true)
};

// Mock global Telegram object
global.Telegram = {
  WebApp: mockTelegramWebApp
};

// Mock window.telegramWebApp (our wrapper)
global.window = global.window || {};
window.telegramWebApp = mockTelegramWebApp;

// Mock localStorage with proper Jest mocks
const localStorageMock = (() => {
  let store = {};
  return {
    getItem: jest.fn((key) => store[key] || null),
    setItem: jest.fn((key, value) => {
      store[key] = value.toString();
    }),
    removeItem: jest.fn((key) => {
      delete store[key];
    }),
    clear: jest.fn(() => {
      store = {};
    })
  };
})();
global.localStorage = localStorageMock;

// Mock sessionStorage with proper Jest mocks
const sessionStorageMock = (() => {
  let store = {};
  return {
    getItem: jest.fn((key) => store[key] || null),
    setItem: jest.fn((key, value) => {
      store[key] = value.toString();
    }),
    removeItem: jest.fn((key) => {
      delete store[key];
    }),
    clear: jest.fn(() => {
      store = {};
    })
  };
})();
global.sessionStorage = sessionStorageMock;

// Mock fetch for API calls
global.fetch = jest.fn(() =>
  Promise.resolve({
    ok: true,
    status: 200,
    json: () => Promise.resolve({}),
    text: () => Promise.resolve('')
  })
);

// Mock document methods that might be used
global.document.addEventListener = jest.fn();
global.document.getElementById = jest.fn();
global.document.querySelector = jest.fn();
global.document.querySelectorAll = jest.fn(() => []);
global.document.createElement = jest.fn(() => ({
  addEventListener: jest.fn(),
  appendChild: jest.fn(),
  setAttribute: jest.fn(),
  classList: {
    add: jest.fn(),
    remove: jest.fn(),
    toggle: jest.fn()
  },
  style: {}
}));

// Mock console methods for cleaner test output
global.console = {
  ...console,
  log: jest.fn(),
  error: jest.fn(),
  warn: jest.fn()
};

// Export for tests that need to access the mock
export { mockTelegramWebApp };