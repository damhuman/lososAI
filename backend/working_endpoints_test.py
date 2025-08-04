#!/usr/bin/env python3
"""Test only the working endpoints."""
import asyncio
import httpx
import base64
import sys
import os

# Set test environment
os.environ['POSTGRES_DB'] = 'seafood_test'
sys.path.insert(0, '/app')

from app.main import app


async def test_working_endpoints():
    """Test endpoints that definitely work."""
    print("🧪 Testing Working CRUD Endpoints...")
    
    # Create admin headers
    credentials = base64.b64encode(b"admin:admin123").decode("ascii")
    admin_headers = {"Authorization": f"Basic {credentials}"}
    
    results = {
        "categories": {"create": False, "read": False, "update": False, "delete": False},
        "districts": {"create": False, "read": False, "update": False, "delete": False},
        "orders": {"read": False},
        "products": {"read": False},
        "public_api": {"categories": False, "products": False, "districts": False}
    }
    
    try:
        async with httpx.AsyncClient(app=app, base_url="http://testserver") as client:
            
            print("\n" + "="*50)
            print("📂 CATEGORIES CRUD TESTING")
            print("="*50)
            
            # CREATE Category
            print("\n➕ CREATE Category")
            category_data = {
                "id": "test-working",
                "name": "Test Working Category",
                "description": "A test category",
                "icon": "🧪",
                "order": 10,
                "is_active": True
            }
            response = await client.post("/api/v1/admin/categories", json=category_data, headers=admin_headers)
            print(f"Status: {response.status_code}")
            if response.status_code in [200, 201]:
                print("✅ CREATE: Working")
                results["categories"]["create"] = True
            else:
                print(f"❌ CREATE: Failed - {response.text}")
            
            # READ Categories
            print("\n📖 READ Categories")
            response = await client.get("/api/v1/admin/categories", headers=admin_headers)
            print(f"Status: {response.status_code}")
            if response.status_code == 200:
                categories = response.json()
                print(f"✅ READ: Working - Found {len(categories)} categories")
                results["categories"]["read"] = True
                for cat in categories:
                    print(f"   - {cat['id']}: {cat['name']}")
            else:
                print(f"❌ READ: Failed")
            
            # UPDATE Category
            print("\n✏️ UPDATE Category")
            update_data = {
                "name": "Updated Working Category",
                "description": "Updated description"
            }
            response = await client.put("/api/v1/admin/categories/test-working", json=update_data, headers=admin_headers)
            print(f"Status: {response.status_code}")
            if response.status_code == 200:
                result = response.json()
                print(f"✅ UPDATE: Working - {result['name']}")
                results["categories"]["update"] = True
            else:
                print(f"❌ UPDATE: Failed - {response.text}")
            
            print("\n" + "="*50)
            print("🏘️ DISTRICTS CRUD TESTING")
            print("="*50)
            
            # CREATE District
            print("\n➕ CREATE District")
            district_data = {
                "name": "Test Working District",
                "delivery_cost": 100.0,
                "is_active": True
            }
            response = await client.post("/api/v1/admin/districts", json=district_data, headers=admin_headers)
            print(f"Status: {response.status_code}")
            district_id = None
            if response.status_code in [200, 201]:
                result = response.json()
                district_id = result.get('id')
                print(f"✅ CREATE: Working - ID: {district_id}")
                results["districts"]["create"] = True
            else:
                print(f"❌ CREATE: Failed - {response.text}")
            
            # READ Districts
            print("\n📖 READ Districts")
            response = await client.get("/api/v1/admin/districts", headers=admin_headers)
            print(f"Status: {response.status_code}")
            if response.status_code == 200:
                districts = response.json()
                print(f"✅ READ: Working - Found {len(districts)} districts")
                results["districts"]["read"] = True
            else:
                print(f"❌ READ: Failed")
            
            # UPDATE District
            if district_id:
                print("\n✏️ UPDATE District")
                update_data = {
                    "name": "Updated Working District",
                    "delivery_cost": 150.0
                }
                response = await client.put(f"/api/v1/admin/districts/{district_id}", json=update_data, headers=admin_headers)
                print(f"Status: {response.status_code}")
                if response.status_code == 200:
                    print("✅ UPDATE: Working")
                    results["districts"]["update"] = True
                else:
                    print(f"❌ UPDATE: Failed - {response.text}")
            
            print("\n" + "="*50)
            print("📦 ORDERS READ TESTING")
            print("="*50)
            
            # READ Orders
            print("\n📖 READ Orders")
            response = await client.get("/api/v1/admin/orders", headers=admin_headers)
            print(f"Status: {response.status_code}")
            if response.status_code == 200:
                orders_data = response.json()
                orders = orders_data.get('items', [])
                print(f"✅ READ: Working - Found {len(orders)} orders")
                results["orders"]["read"] = True
            else:
                print(f"❌ READ: Failed - {response.text}")
            
            print("\n" + "="*50)
            print("🌐 PUBLIC API TESTING")
            print("="*50)
            
            # Public Categories
            print("\n📖 Public Categories")
            response = await client.get("/api/v1/categories/")
            print(f"Status: {response.status_code}")
            if response.status_code == 200:
                categories = response.json()
                print(f"✅ Public Categories: Working - {len(categories)} categories")
                results["public_api"]["categories"] = True
            else:
                print(f"❌ Public Categories: Failed")
            
            # Public Districts
            print("\n📖 Public Districts")
            response = await client.get("/api/v1/districts")
            print(f"Status: {response.status_code}")
            if response.status_code == 200:
                districts = response.json()
                print(f"✅ Public Districts: Working - {len(districts)} districts")
                results["public_api"]["districts"] = True
            else:
                print(f"❌ Public Districts: Failed")
            
            # Public Products (this might fail due to schema issue)
            print("\n📖 Public Products")
            try:
                response = await client.get("/api/v1/products")
                print(f"Status: {response.status_code}")
                if response.status_code == 200:
                    products = response.json()
                    print(f"✅ Public Products: Working - {len(products)} products")
                    results["public_api"]["products"] = True
                else:
                    print(f"❌ Public Products: Failed")
            except Exception as e:
                print(f"❌ Public Products: Schema error - {str(e)}")
            
            print("\n" + "="*50)
            print("🧹 CLEANUP - DELETE TESTING")
            print("="*50)
            
            # DELETE District
            if district_id:
                print("\n❌ DELETE District")
                response = await client.delete(f"/api/v1/admin/districts/{district_id}", headers=admin_headers)
                print(f"Status: {response.status_code}")
                if response.status_code == 200:
                    print("✅ DELETE: Working")
                    results["districts"]["delete"] = True
                else:
                    print(f"❌ DELETE: Failed")
            
            # DELETE Category
            print("\n❌ DELETE Category")
            response = await client.delete("/api/v1/admin/categories/test-working", headers=admin_headers)
            print(f"Status: {response.status_code}")
            if response.status_code == 200:
                print("✅ DELETE: Working")
                results["categories"]["delete"] = True
            else:
                print(f"❌ DELETE: Failed")
            
            return results
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return results


if __name__ == "__main__":
    results = asyncio.run(test_working_endpoints())
    
    print("\n" + "="*70)
    print("📋 FINAL RESULTS SUMMARY")
    print("="*70)
    
    print(f"\n📂 CATEGORIES:")
    print(f"   CREATE: {'✅' if results['categories']['create'] else '❌'}")
    print(f"   READ:   {'✅' if results['categories']['read'] else '❌'}")
    print(f"   UPDATE: {'✅' if results['categories']['update'] else '❌'}")
    print(f"   DELETE: {'✅' if results['categories']['delete'] else '❌'}")
    
    print(f"\n🏘️ DISTRICTS:")
    print(f"   CREATE: {'✅' if results['districts']['create'] else '❌'}")
    print(f"   READ:   {'✅' if results['districts']['read'] else '❌'}")
    print(f"   UPDATE: {'✅' if results['districts']['update'] else '❌'}")
    print(f"   DELETE: {'✅' if results['districts']['delete'] else '❌'}")
    
    print(f"\n📦 ORDERS:")
    print(f"   READ:   {'✅' if results['orders']['read'] else '❌'} (Orders are created by users via public API)")
    
    print(f"\n🐟 PRODUCTS:")
    print(f"   READ:   ❌ (Schema mismatch - needs 'type' and 'price' fields in packages)")
    
    print(f"\n🌐 PUBLIC API:")
    print(f"   Categories: {'✅' if results['public_api']['categories'] else '❌'}")
    print(f"   Districts:  {'✅' if results['public_api']['districts'] else '❌'}")
    print(f"   Products:   ❌ (Schema mismatch)")
    
    print(f"\n🎯 OVERALL STATUS:")
    working_count = sum([
        sum(results['categories'].values()),
        sum(results['districts'].values()),
        sum(results['orders'].values()),
        sum(results['public_api'].values())
    ])
    total_count = 4 + 4 + 1 + 3  # Total possible working endpoints
    print(f"   Working Endpoints: {working_count}/{total_count}")
    
    if working_count >= 8:  # Most endpoints working
        print("   🎉 MOST CRUD OPERATIONS ARE WORKING!")
    else:
        print("   ⚠️  SOME ENDPOINTS NEED FIXING")