#!/usr/bin/env python3
"""Simple test runner to test endpoints without pytest complexity."""
import asyncio
import httpx
import base64
import sys
import os

# Add the app directory to the path
sys.path.insert(0, '/app')

from app.main import app


async def test_basic_endpoints():
    """Test basic endpoints."""
    print("🧪 Running basic endpoint tests...")
    
    # Create admin headers
    credentials = base64.b64encode(b"admin:admin123").decode("ascii")
    admin_headers = {"Authorization": f"Basic {credentials}"}
    
    async with httpx.AsyncClient(app=app, base_url="http://test") as client:
        
        # Test 1: Health check
        print("\n📋 Test 1: Health Check")
        try:
            response = await client.get("/health")
            assert response.status_code == 200, f"Health check failed: {response.status_code}"
            print("✅ Health check passed")
        except Exception as e:
            print(f"❌ Health check failed: {e}")
        
        # Test 2: Categories endpoint
        print("\n📋 Test 2: Categories Endpoint")
        try:
            response = await client.get("/api/v1/categories")
            assert response.status_code == 200, f"Categories failed: {response.status_code}"
            data = response.json()
            assert isinstance(data, list), "Categories should return a list"
            print(f"✅ Categories endpoint passed ({len(data)} categories)")
        except Exception as e:
            print(f"❌ Categories endpoint failed: {e}")
        
        # Test 3: Admin auth
        print("\n📋 Test 3: Admin Authentication")
        try:
            # Without auth
            response = await client.get("/api/v1/admin/verify")
            assert response.status_code == 401, "Should require authentication"
            
            # With auth
            response = await client.get("/api/v1/admin/verify", headers=admin_headers)
            assert response.status_code == 200, f"Admin auth failed: {response.status_code}"
            print("✅ Admin authentication passed")
        except Exception as e:
            print(f"❌ Admin authentication failed: {e}")
        
        # Test 4: Admin categories
        print("\n📋 Test 4: Admin Categories")
        try:
            response = await client.get("/api/v1/admin/categories", headers=admin_headers)
            assert response.status_code == 200, f"Admin categories failed: {response.status_code}"
            data = response.json()
            assert isinstance(data, list), "Admin categories should return a list"
            print(f"✅ Admin categories passed ({len(data)} categories)")
        except Exception as e:
            print(f"❌ Admin categories failed: {e}")
        
        # Test 5: Admin products
        print("\n📋 Test 5: Admin Products")
        try:
            response = await client.get("/api/v1/admin/products", headers=admin_headers)
            assert response.status_code == 200, f"Admin products failed: {response.status_code}"
            data = response.json()
            assert "items" in data, "Admin products should have items"
            assert "total" in data, "Admin products should have total"
            print(f"✅ Admin products passed ({data['total']} products)")
        except Exception as e:
            print(f"❌ Admin products failed: {e}")
        
        # Test 6: Products endpoint
        print("\n📋 Test 6: Products Endpoint")
        try:
            response = await client.get("/api/v1/products")
            assert response.status_code == 200, f"Products failed: {response.status_code}"
            data = response.json()
            assert isinstance(data, list), "Products should return a list"
            print(f"✅ Products endpoint passed ({len(data)} products)")
        except Exception as e:
            print(f"❌ Products endpoint failed: {e}")
        
        # Test 7: Districts endpoint
        print("\n📋 Test 7: Districts Endpoint")
        try:
            response = await client.get("/api/v1/districts")
            assert response.status_code == 200, f"Districts failed: {response.status_code}"
            data = response.json()
            assert isinstance(data, list), "Districts should return a list"
            print(f"✅ Districts endpoint passed ({len(data)} districts)")
        except Exception as e:
            print(f"❌ Districts endpoint failed: {e}")
        
        # Test 8: Promo code validation
        print("\n📋 Test 8: Promo Code Validation")
        try:
            response = await client.post("/api/v1/promo/validate", json={"code": "INVALID"})
            assert response.status_code == 200, f"Promo validation failed: {response.status_code}"
            data = response.json()
            assert "valid" in data, "Promo response should have valid field"
            assert data["valid"] is False, "Invalid code should return valid=False"
            print("✅ Promo code validation passed")
        except Exception as e:
            print(f"❌ Promo code validation failed: {e}")
    
    print("\n🎉 Basic endpoint tests completed!")


if __name__ == "__main__":
    asyncio.run(test_basic_endpoints())