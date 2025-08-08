# TODO List

## ✅ COMPLETED: Test Framework & Basic Auth Cleanup

### Testing Infrastructure ✅ DONE
- ✅ Comprehensive TDD framework implemented (commit 8dac07a)
- ✅ GitHub Actions CI/CD pipeline set up
- ✅ Backend tests organized and running
- ✅ Frontend Jest testing framework configured
- ✅ Unified test runner (`test.sh`) created
- ✅ Test coverage reporting enabled

### Authentication Cleanup ✅ MOSTLY DONE
- ✅ Remove `ADMIN_USERNAME` and `ADMIN_PASSWORD` from `.env.template` (uncommitted)
- ✅ JWT authentication fully implemented and tested
- ✅ Basic Auth code cleaned from backend endpoints
- [ ] **COMMIT PENDING**: Current Basic Auth cleanup changes
- [ ] Final verification that admin panel works with JWT only

**Status**: Ready to commit current Basic Auth cleanup changes

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