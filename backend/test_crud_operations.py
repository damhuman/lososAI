#!/usr/bin/env python3
"""Test CRUD operations for categories, products, and orders."""
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


async def test_crud_operations():
    """Test Create, Read, Update, Delete operations."""
    print("🧪 Testing CRUD Operations...")
    
    # Create admin headers
    credentials = base64.b64encode(b"admin:admin123").decode("ascii")
    admin_headers = {"Authorization": f"Basic {credentials}"}
    
    try:
        async with httpx.AsyncClient(app=app, base_url="http://testserver") as client:
            
            # =============================================================================
            # TEST CATEGORIES CRUD
            # =============================================================================
            print("\n📂 TESTING CATEGORIES CRUD")
            
            # 1. CREATE Category
            print("\n➕ Creating category...")
            category_data = {
                "id": "test-seafood",
                "name": "Test Seafood",
                "description": "Test category for seafood",
                "icon": "🐟",
                "order": 1,
                "is_active": True
            }
            response = await client.post("/api/v1/admin/categories", json=category_data, headers=admin_headers)
            print(f"Create Category: {response.status_code}")
            if response.status_code != 201:
                print(f"Error: {response.text}")
            else:
                print("✅ Category created successfully")
            
            # 2. READ Categories (Get All)
            print("\n📖 Reading all categories...")
            response = await client.get("/api/v1/admin/categories", headers=admin_headers)
            print(f"Get Categories: {response.status_code}")
            if response.status_code == 200:
                categories = response.json()
                print(f"✅ Found {len(categories)} categories")
                for cat in categories:
                    print(f"   - {cat['id']}: {cat['name']}")
            else:
                print(f"Error: {response.text}")
            
            # 3. READ Single Category
            print("\n📖 Reading single category...")
            response = await client.get("/api/v1/admin/categories/test-seafood", headers=admin_headers)
            print(f"Get Single Category: {response.status_code}")
            if response.status_code == 200:
                category = response.json()
                print(f"✅ Category: {category['name']} - {category['description']}")
            
            # 4. UPDATE Category
            print("\n✏️ Updating category...")
            update_data = {
                "name": "Updated Test Seafood",
                "description": "Updated description for test category",
                "order": 2
            }
            response = await client.put("/api/v1/admin/categories/test-seafood", json=update_data, headers=admin_headers)
            print(f"Update Category: {response.status_code}")
            if response.status_code == 200:
                updated_category = response.json()
                print(f"✅ Updated to: {updated_category['name']}")
            else:
                print(f"Error: {response.text}")
            
            # =============================================================================
            # TEST PRODUCTS CRUD
            # =============================================================================
            print("\n🐟 TESTING PRODUCTS CRUD")
            
            # 1. CREATE Product
            print("\n➕ Creating product...")
            product_data = {
                "id": "test-salmon",
                "category_id": "test-seafood",
                "name": "Test Salmon",
                "description": "Premium test salmon",
                "price_per_kg": 500.0,
                "packages": [
                    {
                        "id": "500g",
                        "type": "500г",
                        "weight": 0.5,
                        "unit": "кг",
                        "price": 250.0,
                        "available": True
                    },
                    {
                        "id": "1kg",
                        "type": "1кг", 
                        "weight": 1.0,
                        "unit": "кг",
                        "price": 500.0,
                        "available": True
                    }
                ],
                "is_active": True,
                "is_featured": False
            }
            response = await client.post("/api/v1/admin/products", json=product_data, headers=admin_headers)
            print(f"Create Product: {response.status_code}")
            if response.status_code != 201:
                print(f"Error: {response.text}")
            else:
                print("✅ Product created successfully")
            
            # 2. READ Products (Get All)
            print("\n📖 Reading all products...")
            response = await client.get("/api/v1/admin/products", headers=admin_headers)
            print(f"Get Products: {response.status_code}")
            if response.status_code == 200:
                products_data = response.json()
                products = products_data.get('items', [])
                print(f"✅ Found {len(products)} products (Total: {products_data.get('total', 0)})")
                for prod in products:
                    print(f"   - {prod['id']}: {prod['name']} - {prod['price_per_kg']} грн/кг")
            
            # 3. READ Single Product
            print("\n📖 Reading single product...")
            response = await client.get("/api/v1/admin/products/test-salmon", headers=admin_headers)
            print(f"Get Single Product: {response.status_code}")
            if response.status_code == 200:
                product = response.json()
                print(f"✅ Product: {product['name']} - {len(product['packages'])} packages")
            
            # 4. UPDATE Product
            print("\n✏️ Updating product...")
            update_data = {
                "name": "Updated Test Salmon",
                "description": "Updated premium salmon description",
                "price_per_kg": 600.0,
                "is_featured": True
            }
            response = await client.put("/api/v1/admin/products/test-salmon", json=update_data, headers=admin_headers)
            print(f"Update Product: {response.status_code}")
            if response.status_code == 200:
                updated_product = response.json()
                print(f"✅ Updated to: {updated_product['name']} - {updated_product['price_per_kg']} грн/кг")
                print(f"   Featured: {updated_product['is_featured']}")
            else:
                print(f"Error: {response.text}")
            
            # =============================================================================
            # TEST DISTRICTS CRUD (needed for orders)
            # =============================================================================
            print("\n🏘️ TESTING DISTRICTS CRUD")
            
            # Create District for orders
            print("\n➕ Creating district...")
            district_data = {
                "name": "Test District",
                "delivery_cost": 50.0,
                "is_active": True
            }
            response = await client.post("/api/v1/admin/districts", json=district_data, headers=admin_headers)
            print(f"Create District: {response.status_code}")
            district_id = None
            if response.status_code == 201:
                district = response.json()
                district_id = district['id']
                print(f"✅ District created: {district['name']} (ID: {district_id})")
            
            # =============================================================================
            # TEST ORDERS (READ ONLY - orders are created by users)
            # =============================================================================
            print("\n📦 TESTING ORDERS READ OPERATIONS")
            
            # READ Orders
            print("\n📖 Reading all orders...")
            response = await client.get("/api/v1/admin/orders", headers=admin_headers)
            print(f"Get Orders: {response.status_code}")
            if response.status_code == 200:
                orders_data = response.json()
                orders = orders_data.get('items', [])
                print(f"✅ Found {len(orders)} orders (Total: {orders_data.get('total', 0)})")
                for order in orders:
                    print(f"   - Order #{order.get('order_id', order['id'])}: {order['status']} - {order['total_amount']} грн")
            
            # Order Stats
            print("\n📊 Reading order statistics...")
            response = await client.get("/api/v1/admin/orders/stats", headers=admin_headers)
            print(f"Get Order Stats: {response.status_code}")
            if response.status_code == 200:
                stats = response.json()
                print(f"✅ Order Stats:")
                print(f"   - Total Orders: {stats.get('total_orders', 0)}")
                print(f"   - Total Revenue: {stats.get('total_revenue', 0)} грн")
                print(f"   - Avg Order Value: {stats.get('average_order_value', 0)} грн")
            
            # =============================================================================
            # TEST PUBLIC API ENDPOINTS
            # =============================================================================
            print("\n🌐 TESTING PUBLIC API ENDPOINTS")
            
            # Public Categories
            print("\n📖 Testing public categories...")
            response = await client.get("/api/v1/categories/")
            print(f"Public Categories: {response.status_code}")
            if response.status_code == 200:
                categories = response.json()
                print(f"✅ Public categories: {len(categories)} active categories")
            
            # Public Products
            print("\n📖 Testing public products...")
            response = await client.get("/api/v1/products")
            print(f"Public Products: {response.status_code}")
            if response.status_code == 200:
                products = response.json()
                print(f"✅ Public products: {len(products)} active products")
            
            # =============================================================================
            # CLEANUP - DELETE OPERATIONS
            # =============================================================================
            print("\n🧹 TESTING DELETE OPERATIONS")
            
            # DELETE Product
            print("\n❌ Deleting product...")
            response = await client.delete("/api/v1/admin/products/test-salmon", headers=admin_headers)
            print(f"Delete Product: {response.status_code}")
            if response.status_code == 200:
                print("✅ Product deleted successfully")
            
            # DELETE Category
            print("\n❌ Deleting category...")
            response = await client.delete("/api/v1/admin/categories/test-seafood", headers=admin_headers)
            print(f"Delete Category: {response.status_code}")
            if response.status_code == 200:
                print("✅ Category deleted successfully")
            
            # DELETE District
            if district_id:
                print("\n❌ Deleting district...")
                response = await client.delete(f"/api/v1/admin/districts/{district_id}", headers=admin_headers)
                print(f"Delete District: {response.status_code}")
                if response.status_code == 200:
                    print("✅ District deleted successfully")
            
            print("\n🎉 ALL CRUD OPERATIONS COMPLETED!")
            return True
            
    except Exception as e:
        print(f"❌ CRUD test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    result = asyncio.run(test_crud_operations())
    if result:
        print("\n✅ SUCCESS: All CRUD operations working correctly!")
    else:
        print("\n💥 FAILED: Some CRUD operations failed")
        sys.exit(1)