#!/usr/bin/env python3
"""Final comprehensive CRUD test with cleanup."""
import asyncio
import httpx
import base64
import json
import sys
import os
import uuid

# Set test environment
os.environ['POSTGRES_DB'] = 'seafood_test'
sys.path.insert(0, '/app')

from app.main import app


async def test_final_crud():
    """Final comprehensive CRUD test."""
    print("🧪 Final CRUD Operations Test...")
    
    # Create admin headers
    credentials = base64.b64encode(b"admin:admin123").decode("ascii")
    admin_headers = {"Authorization": f"Basic {credentials}"}
    
    # Use unique IDs to avoid conflicts
    test_id = str(uuid.uuid4())[:8]
    category_id = f"test-cat-{test_id}"
    product_id = f"test-prod-{test_id}"
    
    results = {"success": 0, "total": 0, "details": []}
    
    def test_result(name, success, detail=""):
        results["total"] += 1
        if success:
            results["success"] += 1
            results["details"].append(f"✅ {name}")
        else:
            results["details"].append(f"❌ {name}: {detail}")
    
    try:
        async with httpx.AsyncClient(app=app, base_url="http://testserver") as client:
            
            print("\n" + "="*60)
            print("🧹 CLEANUP EXISTING TEST DATA")
            print("="*60)
            
            # Clean up any existing test data (ignore failures)
            try:
                await client.delete(f"/api/v1/admin/categories/{category_id}", headers=admin_headers)
                await client.delete(f"/api/v1/admin/products/{product_id}", headers=admin_headers)
            except:
                pass
            
            print("\n" + "="*60)
            print("📂 CATEGORIES CRUD")
            print("="*60)
            
            # CREATE Category
            print(f"\n➕ CREATE Category ({category_id})")
            category_data = {
                "id": category_id,
                "name": f"Test Category {test_id}",
                "description": "Test category description",
                "icon": "🧪",
                "order": 99,
                "is_active": True
            }
            response = await client.post("/api/v1/admin/categories", json=category_data, headers=admin_headers)
            success = response.status_code in [200, 201]
            test_result("Categories CREATE", success, f"{response.status_code}" if not success else "")
            print(f"Status: {response.status_code} {'✅' if success else '❌'}")
            
            # READ Categories
            print("\n📖 READ Categories")
            response = await client.get("/api/v1/admin/categories", headers=admin_headers)
            success = response.status_code == 200
            test_result("Categories READ", success, f"{response.status_code}" if not success else "")
            print(f"Status: {response.status_code} {'✅' if success else '❌'}")
            if success:
                categories = response.json()
                print(f"Found {len(categories)} categories")
            
            # UPDATE Category
            print("\n✏️ UPDATE Category")
            update_data = {"name": f"Updated Test Category {test_id}", "description": "Updated description"}
            response = await client.put(f"/api/v1/admin/categories/{category_id}", json=update_data, headers=admin_headers)
            success = response.status_code == 200
            test_result("Categories UPDATE", success, f"{response.status_code}" if not success else "")
            print(f"Status: {response.status_code} {'✅' if success else '❌'}")
            
            print("\n" + "="*60)
            print("🐟 PRODUCTS CRUD")
            print("="*60)
            
            # CREATE Product
            print(f"\n➕ CREATE Product ({product_id})")
            product_data = {
                "id": product_id,
                "category_id": category_id,
                "name": f"Test Product {test_id}",
                "description": "Test product description",
                "price_per_kg": 1000.0,
                "packages": [
                    {
                        "id": "500g",
                        "type": "500г",
                        "weight": 0.5,
                        "unit": "кг",
                        "price": 500.0,
                        "available": True
                    }
                ],
                "is_active": True,
                "is_featured": False
            }
            response = await client.post("/api/v1/admin/products", json=product_data, headers=admin_headers)
            success = response.status_code in [200, 201]
            test_result("Products CREATE", success, f"{response.status_code}" if not success else "")
            print(f"Status: {response.status_code} {'✅' if success else '❌'}")
            if not success:
                print(f"Error: {response.text}")
            
            # READ Products
            print("\n📖 READ Products")
            response = await client.get("/api/v1/admin/products", headers=admin_headers)
            success = response.status_code == 200
            test_result("Products READ", success, f"{response.status_code}" if not success else "")
            print(f"Status: {response.status_code} {'✅' if success else '❌'}")
            if success:
                products_data = response.json()
                products = products_data.get('items', [])
                print(f"Found {len(products)} products")
            elif response.status_code != 200:
                print(f"Error: {response.text[:200]}")
            
            # UPDATE Product
            print("\n✏️ UPDATE Product")
            update_data = {"name": f"Updated Test Product {test_id}", "price_per_kg": 1200.0}
            response = await client.put(f"/api/v1/admin/products/{product_id}", json=update_data, headers=admin_headers)
            success = response.status_code == 200
            test_result("Products UPDATE", success, f"{response.status_code}" if not success else "")
            print(f"Status: {response.status_code} {'✅' if success else '❌'}")
            
            print("\n" + "="*60)
            print("🏘️ DISTRICTS CRUD")
            print("="*60)
            
            # CREATE District
            print("\n➕ CREATE District")
            district_data = {
                "name": f"Test District {test_id}",
                "delivery_cost": 100.0,
                "is_active": True
            }
            response = await client.post("/api/v1/admin/districts", json=district_data, headers=admin_headers)
            success = response.status_code in [200, 201]
            district_id = None
            if success:
                district = response.json()
                district_id = district.get('id')
            test_result("Districts CREATE", success, f"{response.status_code}" if not success else "")
            print(f"Status: {response.status_code} {'✅' if success else '❌'}")
            
            # READ Districts
            print("\n📖 READ Districts")
            response = await client.get("/api/v1/admin/districts", headers=admin_headers)
            success = response.status_code == 200
            test_result("Districts READ", success, f"{response.status_code}" if not success else "")
            print(f"Status: {response.status_code} {'✅' if success else '❌'}")
            
            # UPDATE District
            if district_id:
                print("\n✏️ UPDATE District")
                update_data = {"name": f"Updated Test District {test_id}", "delivery_cost": 150.0}
                response = await client.put(f"/api/v1/admin/districts/{district_id}", json=update_data, headers=admin_headers)
                success = response.status_code == 200
                test_result("Districts UPDATE", success, f"{response.status_code}" if not success else "")
                print(f"Status: {response.status_code} {'✅' if success else '❌'}")
            
            print("\n" + "="*60)
            print("📦 ORDERS READ")
            print("="*60)
            
            # READ Orders
            print("\n📖 READ Orders")
            response = await client.get("/api/v1/admin/orders", headers=admin_headers)
            success = response.status_code == 200
            test_result("Orders READ", success, f"{response.status_code}" if not success else "")
            print(f"Status: {response.status_code} {'✅' if success else '❌'}")
            
            print("\n" + "="*60)
            print("🌐 PUBLIC API")
            print("="*60)
            
            # Public Categories
            print("\n📖 Public Categories")
            response = await client.get("/api/v1/categories/")
            success = response.status_code == 200
            test_result("Public Categories", success, f"{response.status_code}" if not success else "")
            print(f"Status: {response.status_code} {'✅' if success else '❌'}")
            
            # Public Products
            print("\n📖 Public Products")
            response = await client.get("/api/v1/products/")
            success = response.status_code == 200
            test_result("Public Products", success, f"{response.status_code}" if not success else "")
            print(f"Status: {response.status_code} {'✅' if success else '❌'}")
            if not success and response.status_code != 404:
                print(f"Error: {response.text[:200]}")
            
            # Public Districts
            print("\n📖 Public Districts")
            response = await client.get("/api/v1/districts/")
            success = response.status_code == 200
            test_result("Public Districts", success, f"{response.status_code}" if not success else "")
            print(f"Status: {response.status_code} {'✅' if success else '❌'}")
            
            print("\n" + "="*60)
            print("🧹 CLEANUP - DELETE")
            print("="*60)
            
            # DELETE Product
            print("\n❌ DELETE Product")
            response = await client.delete(f"/api/v1/admin/products/{product_id}", headers=admin_headers)
            success = response.status_code == 200
            test_result("Products DELETE", success, f"{response.status_code}" if not success else "")
            print(f"Status: {response.status_code} {'✅' if success else '❌'}")
            
            # DELETE District
            if district_id:
                print("\n❌ DELETE District")
                response = await client.delete(f"/api/v1/admin/districts/{district_id}", headers=admin_headers)
                success = response.status_code == 200
                test_result("Districts DELETE", success, f"{response.status_code}" if not success else "")
                print(f"Status: {response.status_code} {'✅' if success else '❌'}")
            
            # DELETE Category
            print("\n❌ DELETE Category")
            response = await client.delete(f"/api/v1/admin/categories/{category_id}", headers=admin_headers)
            success = response.status_code == 200
            test_result("Categories DELETE", success, f"{response.status_code}" if not success else "")
            print(f"Status: {response.status_code} {'✅' if success else '❌'}")
            
            return results
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return results


if __name__ == "__main__":
    results = asyncio.run(test_final_crud())
    
    print("\n" + "="*70)
    print("🎯 FINAL RESULTS SUMMARY")
    print("="*70)
    
    success_rate = (results["success"] / results["total"]) * 100 if results["total"] > 0 else 0
    
    print(f"\n📊 OVERALL SCORE: {results['success']}/{results['total']} ({success_rate:.1f}%)")
    
    print(f"\n📋 DETAILED RESULTS:")
    for detail in results["details"]:
        print(f"   {detail}")
    
    print(f"\n🏆 FINAL STATUS:")
    if success_rate >= 90:
        print("   🎉 EXCELLENT! Nearly all operations working!")
    elif success_rate >= 75:
        print("   👍 GOOD! Most operations working!")
    elif success_rate >= 50:
        print("   ⚠️  PARTIAL: Some operations working!")
    else:
        print("   ❌ POOR: Many operations failing!")
    
    print(f"\n{'✅ SUCCESS' if success_rate >= 75 else '⚠️ NEEDS WORK'}: CRUD test completed")