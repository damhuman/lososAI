#!/usr/bin/env python3
"""Simple test to verify setup works."""
import asyncio
import httpx
import base64
import sys
import os
import asyncpg

# Set test environment
os.environ['POSTGRES_DB'] = 'seafood_test'

# Add the app directory to the path
sys.path.insert(0, '/app')

from app.main import app


async def test_database_connection():
    """Test database connection."""
    try:
        conn = await asyncpg.connect(
            "postgresql://seafood_user:seafood123@host.docker.internal:5432/seafood_test"
        )
        result = await conn.fetchval("SELECT 1")
        await conn.close()
        print(f"✅ Database connection successful: {result}")
        return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False


async def test_app_startup():
    """Test if the app starts without errors."""
    try:
        async with httpx.AsyncClient(app=app, base_url="http://test") as client:
            response = await client.get("/health")
            print(f"✅ App startup successful: {response.status_code}")
            return response.status_code == 200
    except Exception as e:
        print(f"❌ App startup failed: {e}")
        return False


async def test_basic_endpoints():
    """Test basic endpoints."""
    print("🧪 Running basic endpoint tests...")
    
    # Create admin headers
    credentials = base64.b64encode(b"admin:admin123").decode("ascii")
    admin_headers = {"Authorization": f"Basic {credentials}"}
    
    try:
        async with httpx.AsyncClient(app=app, base_url="http://test") as client:
            
            # Test 1: Health check
            print("\n📋 Test 1: Health Check")
            response = await client.get("/health")
            assert response.status_code == 200, f"Health check failed: {response.status_code}"
            print("✅ Health check passed")
            
            # Test 2: Categories endpoint
            print("\n📋 Test 2: Categories Endpoint")
            response = await client.get("/api/v1/categories")
            assert response.status_code == 200, f"Categories failed: {response.status_code}"
            data = response.json()
            assert isinstance(data, list), "Categories should return a list"
            print(f"✅ Categories endpoint passed ({len(data)} categories)")
            
            # Test 3: Admin auth
            print("\n📋 Test 3: Admin Authentication")
            # Without auth
            response = await client.get("/api/v1/admin/verify")
            assert response.status_code == 401, "Should require authentication"
            
            # With auth
            response = await client.get("/api/v1/admin/verify", headers=admin_headers)
            assert response.status_code == 200, f"Admin auth failed: {response.status_code}"
            print("✅ Admin authentication passed")
            
            # Test 4: Admin categories
            print("\n📋 Test 4: Admin Categories")
            response = await client.get("/api/v1/admin/categories", headers=admin_headers)
            assert response.status_code == 200, f"Admin categories failed: {response.status_code}"
            data = response.json()
            assert isinstance(data, list), "Admin categories should return a list"
            print(f"✅ Admin categories passed ({len(data)} categories)")
            
            # Test 5: Admin products
            print("\n📋 Test 5: Admin Products")
            response = await client.get("/api/v1/admin/products", headers=admin_headers)
            assert response.status_code == 200, f"Admin products failed: {response.status_code}"
            data = response.json()
            assert "items" in data, "Admin products should have items"
            assert "total" in data, "Admin products should have total"
            print(f"✅ Admin products passed ({data['total']} products)")
            
            print("\n🎉 All tests passed!")
            return True
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False


async def main():
    """Run all tests."""
    print("🚀 Starting test suite...")
    
    # Test database connection
    db_ok = await test_database_connection()
    if not db_ok:
        print("❌ Database tests failed, stopping")
        return
    
    # Test app startup
    app_ok = await test_app_startup()
    if not app_ok:
        print("❌ App startup failed, stopping")
        return
    
    # Test endpoints
    endpoints_ok = await test_basic_endpoints()
    
    if db_ok and app_ok and endpoints_ok:
        print("\n✅ All tests completed successfully!")
    else:
        print("\n❌ Some tests failed")


if __name__ == "__main__":
    asyncio.run(main())