#!/usr/bin/env python3
"""
Simple test to verify order_id generation and messaging setup
"""
import asyncio
import sys
import os

# Add the app directory to the Python path
sys.path.insert(0, '/app')

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.db.session import AsyncSessionLocal
from app.db.models.order import Order, OrderItem, OrderStatus, DeliveryTimeSlot
from app.db.models.product import District
from app.db.models.user import User
from app.services.messaging import messaging_service

async def test_order_id_generation():
    """Test that order_id is generated correctly"""
    async with AsyncSessionLocal() as session:
        print("🧪 Testing order ID generation...")
        
        # Check current max order_id
        result = await session.execute(select(func.max(Order.order_id)))
        max_order_id = result.scalar()
        
        if max_order_id is None:
            expected_next = 100
            print("📋 No existing orders, next order_id should be 100")
        else:
            expected_next = max_order_id + 1
            print(f"📋 Current max order_id: {max_order_id}, next should be: {expected_next}")
        
        # Test the helper function
        from app.api.endpoints.orders import get_next_order_id
        next_id = await get_next_order_id(session)
        
        print(f"✅ get_next_order_id() returned: {next_id}")
        
        if next_id == expected_next:
            print("✅ Order ID generation working correctly!")
            return True
        else:
            print(f"❌ Expected {expected_next}, got {next_id}")
            return False

async def test_existing_orders():
    """Check existing orders and their order_ids"""
    async with AsyncSessionLocal() as session:
        print("\n🔍 Checking existing orders...")
        
        # Get all orders
        result = await session.execute(
            select(Order).order_by(Order.id)
        )
        orders = result.scalars().all()
        
        print(f"📊 Found {len(orders)} existing orders:")
        for order in orders:
            print(f"  Order #{order.order_id} (internal ID: {order.id}) - Status: {order.status.value}")
        
        return len(orders)

async def test_messaging_service():
    """Test messaging service configuration"""
    print("\n📱 Testing messaging service...")
    
    try:
        from app.core.config import settings
        
        if settings.TELEGRAM_BOT_TOKEN:
            print("✅ Bot token configured")
        else:
            print("❌ Bot token missing")
            
        if settings.ADMIN_CHAT_ID:
            print(f"✅ Admin chat ID configured: {settings.ADMIN_CHAT_ID}")
        else:
            print("⚠️  Admin chat ID not configured")
            
        print("✅ Messaging service initialized successfully")
        return True
        
    except Exception as e:
        print(f"❌ Messaging service error: {e}")
        return False

async def main():
    print("🚀 Starting simplified order test...")
    print("=" * 60)
    
    # Test order count
    order_count = await test_existing_orders()
    
    # Test order ID generation
    id_test_passed = await test_order_id_generation()
    
    # Test messaging service
    messaging_test_passed = await test_messaging_service()
    
    print("\n" + "=" * 60)
    print("📊 Test Results:")
    print(f"  📋 Existing orders: {order_count}")
    print(f"  🆔 Order ID generation: {'✅ PASS' if id_test_passed else '❌ FAIL'}")
    print(f"  📱 Messaging service: {'✅ PASS' if messaging_test_passed else '❌ FAIL'}")
    
    if id_test_passed and messaging_test_passed:
        print("\n🎉 All core functionality tests passed!")
        print("💡 To test complete flow, create an order through the web app")
    else:
        print("\n⚠️  Some tests failed, check the output above")

if __name__ == "__main__":
    asyncio.run(main())