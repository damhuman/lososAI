#!/usr/bin/env python3
"""Test all CRUD operations after fixes."""
import asyncio
import httpx
import base64
import json
import sys
import os

# Set test environment
os.environ['POSTGRES_DB'] = 'seafood_test'
sys.path.insert(0, '/app')

from app.main import app


async def test_all_fixed_crud():
    """Test all CRUD operations after applying fixes."""
    print("🧪 Testing All CRUD Operations After Fixes...")
    
    # Create admin headers
    credentials = base64.b64encode(b"admin:admin123").decode("ascii")
    admin_headers = {"Authorization": f"Basic {credentials}"}
    
    results = {
        "categories": {"create": False, "read": False, "update": False, "delete": False},
        "products": {"create": False, "read": False, "update": False, "delete": False},
        "districts": {"create": False, "read": False, "update": False, "delete": False},
        "orders": {"read": False},
        "public_api": {"categories": False, "products": False, "districts": False}
    }
    
    try:
        async with httpx.AsyncClient(app=app, base_url="http://testserver") as client:
            
            print("\n" + "="*60)
            print("📂 CATEGORIES CRUD - COMPLETE TEST")
            print("="*60)
            
            # CREATE Category
            print("\n➕ CREATE Category")
            category_data = {
                "id": "test-complete",
                "name": "Complete Test Category",
                "description": "Full CRUD test category",
                "icon": "🧪",
                "order": 20,
                "is_active": True
            }
            response = await client.post("/api/v1/admin/categories", json=category_data, headers=admin_headers)
            print(f"Status: {response.status_code}")
            if response.status_code in [200, 201]:
                print("✅ CREATE: SUCCESS")
                results["categories"]["create"] = True
            else:
                print(f"❌ CREATE: FAILED - {response.text}")
            
            # READ Categories
            print("\n📖 READ Categories")
            response = await client.get("/api/v1/admin/categories", headers=admin_headers)
            print(f"Status: {response.status_code}")
            if response.status_code == 200:
                categories = response.json()
                print(f"✅ READ: SUCCESS - {len(categories)} categories")
                results["categories"]["read"] = True
            else:
                print(f"❌ READ: FAILED")
            
            # UPDATE Category
            print("\n✏️ UPDATE Category")
            update_data = {"name": "Updated Complete Test", "description": "Updated test"}
            response = await client.put("/api/v1/admin/categories/test-complete", json=update_data, headers=admin_headers)
            print(f"Status: {response.status_code}")
            if response.status_code == 200:
                print("✅ UPDATE: SUCCESS")
                results["categories"]["update"] = True
            else:
                print(f"❌ UPDATE: FAILED")
            
            print("\n" + "="*60)
            print("🐟 PRODUCTS CRUD - COMPLETE TEST")
            print("="*60)
            
            # CREATE Product (with correct schema)
            print("\n➕ CREATE Product")
            product_data = {
                "id": "test-product-complete",
                "category_id": "test-complete",
                "name": "Complete Test Product",
                "description": "Full CRUD test product",
                "price_per_kg": 1000.0,
                "packages": [
                    {
                        "id": "500g",
                        "type": "500г",
                        "weight": 0.5,
                        "unit": "кг",
                        "price": 500.0,
                        "available": True
                    },
                    {
                        "id": "1kg", 
                        "type": "1кг",
                        "weight": 1.0,
                        "unit": "кг",
                        "price": 1000.0,
                        "available": True
                    }
                ],
                "is_active": True,
                "is_featured": True
            }
            response = await client.post("/api/v1/admin/products", json=product_data, headers=admin_headers)
            print(f"Status: {response.status_code}")
            if response.status_code in [200, 201]:
                print("✅ CREATE: SUCCESS")
                results["products"]["create"] = True
            else:
                print(f"❌ CREATE: FAILED - {response.text}")
            
            # READ Products (Admin)
            print("\n📖 READ Products (Admin)")
            response = await client.get("/api/v1/admin/products", headers=admin_headers)
            print(f"Status: {response.status_code}")
            if response.status_code == 200:
                products_data = response.json()
                products = products_data.get('items', [])
                print(f"✅ READ: SUCCESS - {len(products)} products")
                results["products"]["read"] = True
            else:
                print(f"❌ READ: FAILED - {response.text}")
            
            # UPDATE Product
            print("\n✏️ UPDATE Product")
            update_data = {
                "name": "Updated Complete Test Product",
                "description": "Updated description",
                "price_per_kg": 1200.0,
                "is_featured": False
            }
            response = await client.put("/api/v1/admin/products/test-product-complete", json=update_data, headers=admin_headers)
            print(f"Status: {response.status_code}")
            if response.status_code == 200:
                print("✅ UPDATE: SUCCESS")
                results["products"]["update"] = True
            else:
                print(f"❌ UPDATE: FAILED - {response.text}")
            
            print("\n" + "="*60)
            print("🏘️ DISTRICTS CRUD - COMPLETE TEST")
            print("="*60)
            
            # CREATE District
            print("\n➕ CREATE District")
            district_data = {
                "name": "Complete Test District",
                "delivery_cost": 200.0,
                "is_active": True
            }
            response = await client.post("/api/v1/admin/districts", json=district_data, headers=admin_headers)
            print(f"Status: {response.status_code}")
            district_id = None
            if response.status_code in [200, 201]:
                result = response.json()
                district_id = result.get('id')
                print(f"✅ CREATE: SUCCESS - ID: {district_id}")
                results["districts"]["create"] = True
            else:
                print(f"❌ CREATE: FAILED")
            
            # READ Districts
            print("\n📖 READ Districts")
            response = await client.get("/api/v1/admin/districts", headers=admin_headers)
            print(f"Status: {response.status_code}")
            if response.status_code == 200:
                districts = response.json()
                print(f"✅ READ: SUCCESS - {len(districts)} districts")
                results["districts"]["read"] = True
            else:
                print(f"❌ READ: FAILED")
            
            # UPDATE District
            if district_id:
                print("\n✏️ UPDATE District")
                update_data = {"name": "Updated Complete District", "delivery_cost": 250.0}
                response = await client.put(f"/api/v1/admin/districts/{district_id}", json=update_data, headers=admin_headers)
                print(f"Status: {response.status_code}")
                if response.status_code == 200:
                    print("✅ UPDATE: SUCCESS")
                    results["districts"]["update"] = True
            
            print("\n" + "="*60)
            print("📦 ORDERS READ TEST")
            print("="*60)
            
            # READ Orders
            print("\n📖 READ Orders")
            response = await client.get("/api/v1/admin/orders", headers=admin_headers)
            print(f"Status: {response.status_code}")
            if response.status_code == 200:
                orders_data = response.json()
                orders = orders_data.get('items', [])
                print(f"✅ READ: SUCCESS - {len(orders)} orders")
                results["orders"]["read"] = True
            else:
                print(f"❌ READ: FAILED")
            
            print("\n" + "="*60)
            print("🌐 PUBLIC API - COMPLETE TEST")
            print("="*60)
            
            # Public Categories
            print("\n📖 Public Categories")
            response = await client.get("/api/v1/categories/")
            print(f"Status: {response.status_code}")
            if response.status_code == 200:
                categories = response.json()
                print(f"✅ PUBLIC CATEGORIES: SUCCESS - {len(categories)} categories")
                results["public_api"]["categories"] = True
            else:
                print(f"❌ PUBLIC CATEGORIES: FAILED")
            
            # Public Products (FIXED!)
            print("\n📖 Public Products")
            response = await client.get("/api/v1/products/")
            print(f"Status: {response.status_code}")
            if response.status_code == 200:
                products = response.json()
                print(f"✅ PUBLIC PRODUCTS: SUCCESS - {len(products)} products")
                results["public_api"]["products"] = True
            else:
                print(f"❌ PUBLIC PRODUCTS: FAILED - {response.text}")
            
            # Public Districts (FIXED!)
            print("\n📖 Public Districts")
            response = await client.get("/api/v1/districts/")
            print(f"Status: {response.status_code}")
            if response.status_code == 200:
                districts = response.json()
                print(f"✅ PUBLIC DISTRICTS: SUCCESS - {len(districts)} districts")
                results["public_api"]["districts"] = True
            else:
                print(f"❌ PUBLIC DISTRICTS: FAILED")
            
            print("\n" + "="*60)
            print("🧹 CLEANUP - DELETE TEST")
            print("="*60)
            
            # DELETE Product
            print("\n❌ DELETE Product")
            response = await client.delete("/api/v1/admin/products/test-product-complete", headers=admin_headers)
            print(f"Status: {response.status_code}")
            if response.status_code == 200:
                print("✅ DELETE PRODUCT: SUCCESS")
                results["products"]["delete"] = True
            else:
                print(f"❌ DELETE PRODUCT: FAILED")
            
            # DELETE District
            if district_id:
                print("\n❌ DELETE District")
                response = await client.delete(f"/api/v1/admin/districts/{district_id}", headers=admin_headers)
                print(f"Status: {response.status_code}")
                if response.status_code == 200:
                    print("✅ DELETE DISTRICT: SUCCESS")
                    results["districts"]["delete"] = True
            
            # DELETE Category
            print("\n❌ DELETE Category")
            response = await client.delete("/api/v1/admin/categories/test-complete", headers=admin_headers)
            print(f"Status: {response.status_code}")
            if response.status_code == 200:
                print("✅ DELETE CATEGORY: SUCCESS")
                results["categories"]["delete"] = True
            else:
                print(f"❌ DELETE CATEGORY: FAILED")
            
            return results
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return results


if __name__ == "__main__":
    results = asyncio.run(test_all_fixed_crud())
    
    print("\n" + "="*70)
    print("🎯 FINAL COMPREHENSIVE RESULTS")
    print("="*70)
    
    print(f"\n📂 CATEGORIES CRUD:")
    cat_success = sum(results['categories'].values())
    print(f"   CREATE: {'✅' if results['categories']['create'] else '❌'}")
    print(f"   READ:   {'✅' if results['categories']['read'] else '❌'}")
    print(f"   UPDATE: {'✅' if results['categories']['update'] else '❌'}")
    print(f"   DELETE: {'✅' if results['categories']['delete'] else '❌'}")
    print(f"   SCORE:  {cat_success}/4 {'✅' if cat_success == 4 else '⚠️'}")
    
    print(f"\n🐟 PRODUCTS CRUD:")
    prod_success = sum(results['products'].values())
    print(f"   CREATE: {'✅' if results['products']['create'] else '❌'}")
    print(f"   READ:   {'✅' if results['products']['read'] else '❌'}")
    print(f"   UPDATE: {'✅' if results['products']['update'] else '❌'}")
    print(f"   DELETE: {'✅' if results['products']['delete'] else '❌'}")
    print(f"   SCORE:  {prod_success}/4 {'✅' if prod_success == 4 else '⚠️'}")
    
    print(f"\n🏘️ DISTRICTS CRUD:")
    dist_success = sum(results['districts'].values())
    print(f"   CREATE: {'✅' if results['districts']['create'] else '❌'}")
    print(f"   READ:   {'✅' if results['districts']['read'] else '❌'}")
    print(f"   UPDATE: {'✅' if results['districts']['update'] else '❌'}")
    print(f"   DELETE: {'✅' if results['districts']['delete'] else '❌'}")
    print(f"   SCORE:  {dist_success}/4 {'✅' if dist_success == 4 else '⚠️'}")
    
    print(f"\n📦 ORDERS:")
    ord_success = sum(results['orders'].values())
    print(f"   READ:   {'✅' if results['orders']['read'] else '❌'}")
    print(f"   SCORE:  {ord_success}/1 {'✅' if ord_success == 1 else '⚠️'}")
    
    print(f"\n🌐 PUBLIC API:")
    pub_success = sum(results['public_api'].values())
    print(f"   Categories: {'✅' if results['public_api']['categories'] else '❌'}")
    print(f"   Products:   {'✅' if results['public_api']['products'] else '❌'}")
    print(f"   Districts:  {'✅' if results['public_api']['districts'] else '❌'}")
    print(f"   SCORE:      {pub_success}/3 {'✅' if pub_success == 3 else '⚠️'}")
    
    # Calculate overall success
    total_success = cat_success + prod_success + dist_success + ord_success + pub_success
    total_possible = 4 + 4 + 4 + 1 + 3  # 16 total endpoints
    
    print(f"\n🏆 OVERALL RESULTS:")
    print(f"   Working Endpoints: {total_success}/{total_possible}")
    print(f"   Success Rate: {(total_success/total_possible)*100:.1f}%")
    
    if total_success == total_possible:
        print("   🎉 PERFECT! ALL CRUD OPERATIONS WORKING!")
    elif total_success >= 14:
        print("   🎊 EXCELLENT! Nearly all operations working!")
    elif total_success >= 12:
        print("   👍 GOOD! Most operations working!")
    else:
        print("   ⚠️  NEEDS IMPROVEMENT: Some operations failing")
    
    print(f"\n{'✅ SUCCESS' if total_success >= 14 else '⚠️ PARTIAL SUCCESS'}: CRUD operations test completed")