#!/usr/bin/env python3
"""
Test script for order flow with structured messaging
"""
import asyncio
import httpx
import json
from datetime import datetime

# Test data
test_order = {
    "user_id": 336394651,
    "user_name": "Test User",
    "items": [
        {
            "product_id": "salmon-steaks",
            "product_name": "Стейки лосося",
            "package_id": "500g",
            "weight": 0.5,
            "unit": "кг",
            "quantity": 2,
            "price_per_unit": 400,
            "total_price": 800
        }
    ],
    "delivery": {
        "district": "Печерський",
        "time_slot": "morning",
        "comment": "Test order comment"
    },
    "promo_code": None,
    "total": 800.0,
    "init_data": "test"
}

async def test_order_creation():
    """Test order creation through backend API"""
    try:
        async with httpx.AsyncClient() as client:
            print("🧪 Testing order creation...")
            
            response = await client.post(
                "http://127.0.0.1:8000/api/v1/orders/",
                json=test_order,
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"tma {test_order['init_data']}"
                },
                follow_redirects=True
            )
            
            print(f"📊 Response status: {response.status_code}")
            
            if response.status_code == 200:
                order_data = response.json()
                print(f"✅ Order created successfully!")
                print(f"📋 Order ID: #{order_data.get('order_id')}")
                print(f"🆔 Internal ID: {order_data.get('id')}")
                print(f"💰 Total: {order_data.get('total_amount')} грн")
                print(f"📅 Created at: {order_data.get('created_at')}")
                
                # Test admin orders endpoint with order_id filter
                admin_response = await client.get(
                    f"http://127.0.0.1:8000/api/v1/admin/orders?order_id={order_data.get('order_id')}"
                )
                
                if admin_response.status_code == 200:
                    admin_data = admin_response.json()
                    print(f"🔍 Admin query found {len(admin_data.get('items', []))} orders")
                else:
                    print(f"❌ Admin query failed: {admin_response.status_code}")
                
                return order_data
            else:
                print(f"❌ Order creation failed")
                print(f"📝 Response: {response.text}")
                return None
                
    except Exception as e:
        print(f"💥 Error: {e}")
        return None

async def main():
    print("🚀 Starting order flow test...")
    print(f"📅 Test time: {datetime.now()}")
    print(f"👤 Test user: {test_order['user_name']} (ID: {test_order['user_id']})")
    print(f"🛒 Test items: {len(test_order['items'])} items")
    print("─" * 50)
    
    order = await test_order_creation()
    
    if order:
        print("─" * 50)
        print("✅ Test completed successfully!")
        print("📱 Check Telegram for order confirmation and admin notification messages")
    else:
        print("❌ Test failed!")

if __name__ == "__main__":
    asyncio.run(main())