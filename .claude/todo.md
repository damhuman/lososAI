# TODO List

## 🔴 HIGHEST PRIORITY: Test Framework Setup

### Unified Testing Infrastructure
- [ ] Audit all existing backend tests and verify they run
- [ ] Clean up duplicate/obsolete test files (test_simple.py, quick_test.py, etc.)
- [ ] Fix failing backend tests and update for JWT auth
- [ ] Set up Jest testing framework for frontend Telegram Mini App
- [ ] Create root-level test runner script for all services
- [ ] Add test coverage reporting

### Backend Test Organization
- [ ] Consolidate test files into proper structure:
  - `tests/unit/` - Model and service tests
  - `tests/integration/` - API endpoint tests  
  - `tests/e2e/` - Full flow tests
- [ ] Remove duplicate test files (multiple test_admin_endpoints variants)
- [ ] Update all tests for JWT authentication (remove Basic Auth)
- [ ] Ensure async tests work properly with pytest-asyncio

### Frontend Testing (Telegram Mini App)
- [ ] Install Jest and testing dependencies
- [ ] Configure Jest for vanilla JS with ES6 modules
- [ ] Write tests for:
  - `cart.js` - Cart calculations, add/remove items
  - `api.js` - API client error handling
  - `app.js` - Order submission flow
  - `router.js` - Navigation logic
- [ ] Mock Telegram WebApp API for tests
- [ ] Test critical user flows (add to cart → checkout → order)

### Unified Test Command
- [ ] Create `test.sh` script in root directory
- [ ] Add Docker Compose command to run all tests
- [ ] Separate commands for:
  - `test:backend` - Python/pytest tests
  - `test:frontend` - Jest tests for mini app
  - `test:all` - Run everything in parallel

**Priority**: HIGHEST  
**Status**: Not Started  
**Notes**: Testing is critical before implementing new features. Focus on testing existing functionality first, especially order flow and authentication. Admin panel tests postponed for later.

## Authentication System Cleanup

### Remove Legacy HTTP Basic Auth
- [ ] Remove HTTP Basic Auth references from documentation (CLAUDE.md)
- [ ] Remove `ADMIN_USERNAME` and `ADMIN_PASSWORD` environment variables from `.env.template`
- [ ] Clean up any remaining Basic Auth code in backend admin endpoints
- [ ] Remove Basic Auth headers from API client configurations
- [ ] Update admin panel documentation to reflect JWT-only authentication
- [ ] Test admin panel functionality with only JWT authentication
- [ ] Remove Basic Auth fallback mechanisms if any exist
- [ ] Update deployment scripts/configs to remove Basic Auth credentials

**Priority**: Medium  
**Status**: Not Started  
**Notes**: JWT authentication is already implemented and working. Basic Auth is legacy and should be completely removed to avoid confusion and security issues.

## Enhanced Admin Order Management System

### Phase 1: Core Order Verification Features

#### Real-time Notifications
- [ ] Implement native WebSocket connection for admin panel
- [ ] Add WebSocket notification service to backend
- [ ] Create notification sound system ("casino win" style)
- [ ] Add order notification UI components in admin panel
- [ ] Test multi-channel notifications (WebSocket + Telegram backup)

#### Order Verification Interface
- [ ] Create order verification screen in admin panel
- [ ] Design side-by-side comparison table (Expected vs Actual)
  - Product name
  - Expected weight/quantity → Actual weight/quantity input fields
  - Expected price → Calculated actual price (real-time)
- [ ] Implement real-time price recalculation engine
- [ ] Add Confirm/Cancel buttons for order processing
- [ ] Create pick list generation for managers

#### Auto-confirmation System
- [ ] Add admin configurable threshold setting (default: 10% price variance)
- [ ] Implement threshold check AFTER manager enters actual weights
- [ ] Auto-proceed if difference < threshold (no additional confirmation needed)
- [ ] Require manual confirmation only if difference > threshold
- [ ] Add verified orders to delivery queue automatically

#### Order Status Management
- [ ] Update order status workflow: pending → verified → confirmed → delivering → delivered
- [ ] Create "waiting for delivery" order list
- [ ] Add manual order cancellation functionality for managers
- [ ] Implement delivery queue management

**Priority**: High  
**Status**: Not Started  
**Notes**: This is the core enhancement for small seafood business owners. Focus on manager workflow efficiency.

### Phase 2: Advanced Features (Future)

#### Customer Re-confirmation Flow
- [ ] Customer notification for significant order changes
- [ ] Customer approval/decline interface
- [ ] Integrate customer re-confirmation with order flow

#### Enhanced Configuration
- [ ] Per-category price variance thresholds
- [ ] Configurable notification sounds
- [ ] Delivery address requirement toggle
- [ ] Manager permission levels

#### Feedback System
- [ ] Automated post-delivery feedback collection
- [ ] 1-5 star rating system
- [ ] Detailed feedback for ratings <5 stars
- [ ] Configurable feedback timing (admin setting)

#### Integrations
- [ ] Auto-payment processing integration
- [ ] Invoice generation system
- [ ] Accounting software integration
- [ ] Inventory management integration

**Priority**: Medium  
**Status**: Future Planning  
**Notes**: Features for scaling to larger businesses and enhanced customer experience.

## Technical Infrastructure

### WebSocket Implementation
- [ ] Set up native WebSocket server (avoid Socket.IO for simplicity)
- [ ] Create WebSocket connection management in React admin panel
- [ ] Implement connection recovery and reconnection logic
- [ ] Add WebSocket authentication and security

### Database Schema Updates
- [ ] Add order verification fields (actual_weights, actual_quantities)
- [ ] Create admin settings table for thresholds and configurations
- [ ] Add delivery queue status tracking
- [ ] Update order status enum with new verification states

### API Enhancements
- [ ] Create order verification endpoints
- [ ] Add real-time price calculation API
- [ ] Implement admin settings management endpoints
- [ ] Add delivery queue management endpoints

**Priority**: High  
**Status**: Required for Phase 1  
**Notes**: Technical foundation for enhanced admin features.