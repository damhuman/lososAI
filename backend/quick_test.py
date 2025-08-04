#!/usr/bin/env python3
"""Quick API test using pytest-asyncio."""
import asyncio
import httpx
import base64
import os
import sys

# Set test environment
os.environ['POSTGRES_DB'] = 'seafood_test'

# Add the app directory to the path
sys.path.insert(0, '/app')

from app.main import app


async def test_api_endpoints():
    """Test basic API endpoints."""
    print("🧪 Testing API endpoints...")
    
    # Create admin headers
    credentials = base64.b64encode(b"admin:admin123").decode("ascii")
    admin_headers = {"Authorization": f"Basic {credentials}"}
    
    try:
        # Use the actual app instead of live server
        async with httpx.AsyncClient(app=app, base_url="http://testserver") as client:
            # Test health check
            print("📋 Testing health check...")
            response = await client.get("/health")
            print(f"Health: {response.status_code} - {response.text}")
            assert response.status_code == 200
            
            # Test categories endpoint
            print("📋 Testing categories...")
            response = await client.get("/api/v1/categories")
            print(f"Categories: {response.status_code}")
            if response.status_code == 307:
                # Follow redirect
                response = await client.get("/api/v1/categories/")
                print(f"Categories (after redirect): {response.status_code}")
            print(f"Response: {len(response.json()) if response.status_code == 200 else response.text}")
            assert response.status_code == 200
            
            # Test admin auth
            print("📋 Testing admin auth...")
            response = await client.get("/api/v1/admin/verify", headers=admin_headers)
            print(f"Admin auth: {response.status_code} - {response.text}")
            assert response.status_code == 200
            
            # Test admin categories
            print("📋 Testing admin categories...")
            response = await client.get("/api/v1/admin/categories", headers=admin_headers) 
            print(f"Admin categories: {response.status_code} - {len(response.json()) if response.status_code == 200 else response.text}")
            assert response.status_code == 200
            
            print("✅ All basic tests passed!")
            return True
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False


if __name__ == "__main__":
    result = asyncio.run(test_api_endpoints())
    if result:
        print("🎉 Success!")
    else:
        print("💥 Failed!")
        sys.exit(1)