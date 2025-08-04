"""Tests for admin endpoints."""
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.product import Category, Product, District, PromoCode
from app.db.models.user import User
from app.db.models.order import Order

# Mark all test functions in this module as asyncio
pytestmark = pytest.mark.asyncio


class TestAdminAuth:
    """Test admin authentication."""
    
    async def test_verify_endpoint_without_auth(self, client: AsyncClient):
        """Test admin verify endpoint without authentication."""
        response = await client.get("/api/v1/admin/verify")
        assert response.status_code == 401
    
    async def test_verify_endpoint_with_auth(self, client: AsyncClient, admin_headers):
        """Test admin verify endpoint with authentication."""
        response = await client.get("/api/v1/admin/verify", headers=admin_headers)
        assert response.status_code == 200
        assert response.json() == {"message": "Admin authenticated"}
    
    async def test_verify_endpoint_invalid_auth(self, client: AsyncClient):
        """Test admin verify endpoint with invalid authentication."""
        headers = {"Authorization": "Basic invalid"}
        response = await client.get("/api/v1/admin/verify", headers=headers)
        assert response.status_code == 401


class TestAdminCategories:
    """Test admin category endpoints."""
    
    async def test_get_categories(self, client: AsyncClient, admin_headers, sample_category):
        """Test getting categories."""
        response = await client.get("/api/v1/admin/categories", headers=admin_headers)
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["id"] == sample_category.id
        assert data[0]["name"] == sample_category.name
    
    async def test_create_category(self, client: AsyncClient, admin_headers):
        """Test creating a new category."""
        category_data = {
            "id": "new_category",
            "name": "New Category",
            "description": "New category description",
            "icon": "🦐",
            "order": 2,
            "is_active": True
        }
        response = await client.post("/api/v1/admin/categories", json=category_data, headers=admin_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == category_data["id"]
        assert data["name"] == category_data["name"]
    
    async def test_create_category_duplicate_id(self, client: AsyncClient, admin_headers, sample_category):
        """Test creating category with duplicate ID."""
        category_data = {
            "id": sample_category.id,
            "name": "Duplicate Category",
            "icon": "🦐",
            "order": 2
        }
        response = await client.post("/api/v1/admin/categories", json=category_data, headers=admin_headers)
        assert response.status_code == 400
    
    async def test_update_category(self, client: AsyncClient, admin_headers, sample_category):
        """Test updating a category."""
        update_data = {
            "name": "Updated Category Name",
            "description": "Updated description"
        }
        response = await client.put(f"/api/v1/admin/categories/{sample_category.id}", json=update_data, headers=admin_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == update_data["name"]
        assert data["description"] == update_data["description"]
    
    async def test_update_nonexistent_category(self, client: AsyncClient, admin_headers):
        """Test updating a non-existent category."""
        update_data = {"name": "Updated Name"}
        response = await client.put("/api/v1/admin/categories/nonexistent", json=update_data, headers=admin_headers)
        assert response.status_code == 404
    
    async def test_delete_category(self, client: AsyncClient, admin_headers, sample_category):
        """Test deleting a category."""
        response = await client.delete(f"/api/v1/admin/categories/{sample_category.id}", headers=admin_headers)
        assert response.status_code == 200
        
        # Verify category is deleted
        get_response = await client.get("/api/v1/admin/categories", headers=admin_headers)
        categories = get_response.json()
        assert len(categories) == 0
    
    async def test_delete_nonexistent_category(self, client: AsyncClient, admin_headers):
        """Test deleting a non-existent category."""
        response = await client.delete("/api/v1/admin/categories/nonexistent", headers=admin_headers)
        assert response.status_code == 404


class TestAdminProducts:
    """Test admin product endpoints."""
    
    async def test_get_products(self, client: AsyncClient, admin_headers, sample_product):
        """Test getting products."""
        response = await client.get("/api/v1/admin/products", headers=admin_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert len(data["items"]) == 1
        assert data["items"][0]["id"] == sample_product.id
    
    async def test_get_products_pagination(self, client: AsyncClient, admin_headers, sample_product):
        """Test product pagination."""
        response = await client.get("/api/v1/admin/products?page=1&size=10", headers=admin_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["page"] == 1
        assert data["size"] == 10
    
    async def test_get_product_by_id(self, client: AsyncClient, admin_headers, sample_product):
        """Test getting a product by ID."""
        response = await client.get(f"/api/v1/admin/products/{sample_product.id}", headers=admin_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == sample_product.id
        assert data["name"] == sample_product.name
    
    async def test_get_nonexistent_product(self, client: AsyncClient, admin_headers):
        """Test getting a non-existent product."""
        response = await client.get("/api/v1/admin/products/nonexistent", headers=admin_headers)
        assert response.status_code == 404
    
    async def test_create_product(self, client: AsyncClient, admin_headers, sample_category):
        """Test creating a new product."""
        product_data = {
            "id": "new_product",
            "category_id": sample_category.id,
            "name": "New Product",
            "description": "New product description",
            "price_per_kg": 200.0,
            "packages": [
                {
                    "id": "500g",
                    "type": "500г",
                    "weight": 0.5,
                    "unit": "г",
                    "price": 100.0,
                    "available": True
                }
            ],
            "is_active": True,
            "is_featured": False
        }
        response = await client.post("/api/v1/admin/products", json=product_data, headers=admin_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == product_data["id"]
        assert data["name"] == product_data["name"]
        assert len(data["packages"]) == 1
    
    async def test_update_product(self, client: AsyncClient, admin_headers, sample_product):
        """Test updating a product."""
        update_data = {
            "name": "Updated Product Name",
            "price_per_kg": 150.0,
            "is_featured": True
        }
        response = await client.put(f"/api/v1/admin/products/{sample_product.id}", json=update_data, headers=admin_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == update_data["name"]
        assert data["price_per_kg"] == update_data["price_per_kg"]
        assert data["is_featured"] == update_data["is_featured"]
    
    async def test_delete_product(self, client: AsyncClient, admin_headers, sample_product):
        """Test deleting a product."""
        response = await client.delete(f"/api/v1/admin/products/{sample_product.id}", headers=admin_headers)
        assert response.status_code == 200
        
        # Verify product is deleted
        get_response = await client.get(f"/api/v1/admin/products/{sample_product.id}", headers=admin_headers)
        assert get_response.status_code == 404
    
    async def test_get_product_stats(self, client: AsyncClient, admin_headers, sample_product):
        """Test getting product statistics."""
        response = await client.get("/api/v1/admin/products/stats", headers=admin_headers)
        assert response.status_code == 200
        data = response.json()
        assert "total_products" in data
        assert "total_categories" in data
        assert "featured_products" in data
        assert "active_products" in data


class TestAdminUsers:
    """Test admin user endpoints."""
    
    async def test_get_users(self, client: AsyncClient, admin_headers, sample_user):
        """Test getting users."""
        response = await client.get("/api/v1/admin/users", headers=admin_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert len(data["items"]) == 1
        assert data["items"][0]["telegram_id"] == sample_user.telegram_id
    
    async def test_get_user_stats(self, client: AsyncClient, admin_headers, sample_user):
        """Test getting user statistics."""
        response = await client.get("/api/v1/admin/users/stats", headers=admin_headers)
        assert response.status_code == 200
        data = response.json()
        assert "total" in data
        assert "active" in data
        assert "gold_clients" in data
        assert "blocked" in data
    
    async def test_update_user(self, client: AsyncClient, admin_headers, sample_user):
        """Test updating a user."""
        update_data = {
            "is_gold_client": True,
            "is_blocked": False
        }
        response = await client.put(f"/api/v1/admin/users/{sample_user.id}", json=update_data, headers=admin_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["is_gold_client"] == update_data["is_gold_client"]


class TestAdminOrders:
    """Test admin order endpoints."""
    
    async def test_get_orders(self, client: AsyncClient, admin_headers, sample_order):
        """Test getting orders."""
        response = await client.get("/api/v1/admin/orders", headers=admin_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert len(data["items"]) == 1
        assert data["items"][0]["id"] == sample_order.id
    
    async def test_get_orders_with_filters(self, client: AsyncClient, admin_headers, sample_order):
        """Test getting orders with filters."""
        response = await client.get("/api/v1/admin/orders?status=pending", headers=admin_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
    
    async def test_get_order_by_id(self, client: AsyncClient, admin_headers, sample_order):
        """Test getting an order by ID."""
        response = await client.get(f"/api/v1/admin/orders/{sample_order.id}", headers=admin_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == sample_order.id
        assert data["status"] == sample_order.status
    
    async def test_update_order_status(self, client: AsyncClient, admin_headers, sample_order):
        """Test updating order status."""
        update_data = {"status": "confirmed"}
        response = await client.put(f"/api/v1/admin/orders/{sample_order.id}/status", json=update_data, headers=admin_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "confirmed"
    
    async def test_get_order_stats(self, client: AsyncClient, admin_headers, sample_order):
        """Test getting order statistics."""
        response = await client.get("/api/v1/admin/orders/stats", headers=admin_headers)
        assert response.status_code == 200
        data = response.json()
        assert "total_orders" in data
        assert "total_revenue" in data
        assert "avg_order_value" in data
        assert "orders_by_status" in data


class TestAdminDistricts:
    """Test admin district endpoints."""
    
    async def test_get_districts(self, client: AsyncClient, admin_headers, sample_district):
        """Test getting districts."""
        response = await client.get("/api/v1/admin/districts", headers=admin_headers)
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["name"] == sample_district.name
    
    async def test_create_district(self, client: AsyncClient, admin_headers):
        """Test creating a new district."""
        district_data = {
            "name": "New District",
            "delivery_cost": 75.0,
            "is_active": True
        }
        response = await client.post("/api/v1/admin/districts", json=district_data, headers=admin_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == district_data["name"]
        assert data["delivery_cost"] == district_data["delivery_cost"]
    
    async def test_update_district(self, client: AsyncClient, admin_headers, sample_district):
        """Test updating a district."""
        update_data = {
            "delivery_cost": 100.0,
            "is_active": False
        }
        response = await client.put(f"/api/v1/admin/districts/{sample_district.id}", json=update_data, headers=admin_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["delivery_cost"] == update_data["delivery_cost"]
        assert data["is_active"] == update_data["is_active"]
    
    async def test_delete_district(self, client: AsyncClient, admin_headers, sample_district):
        """Test deleting a district."""
        response = await client.delete(f"/api/v1/admin/districts/{sample_district.id}", headers=admin_headers)
        assert response.status_code == 200


class TestAdminPromoCodes:
    """Test admin promo code endpoints."""
    
    async def test_get_promo_codes(self, client: AsyncClient, admin_headers, sample_promo_code):
        """Test getting promo codes."""
        response = await client.get("/api/v1/admin/promo-codes", headers=admin_headers)
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["code"] == sample_promo_code.code
    
    async def test_create_promo_code(self, client: AsyncClient, admin_headers):
        """Test creating a new promo code."""
        promo_data = {
            "code": "NEWCODE20",
            "discount_percent": 20.0,
            "is_active": True,
            "is_gold_code": False
        }
        response = await client.post("/api/v1/admin/promo-codes", json=promo_data, headers=admin_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == promo_data["code"]
        assert data["discount_percent"] == promo_data["discount_percent"]
    
    async def test_update_promo_code(self, client: AsyncClient, admin_headers, sample_promo_code):
        """Test updating a promo code."""
        update_data = {
            "discount_percent": 15.0,
            "is_active": False
        }
        response = await client.put(f"/api/v1/admin/promo-codes/{sample_promo_code.id}", json=update_data, headers=admin_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["discount_percent"] == update_data["discount_percent"]
        assert data["is_active"] == update_data["is_active"]
    
    async def test_delete_promo_code(self, client: AsyncClient, admin_headers, sample_promo_code):
        """Test deleting a promo code."""
        response = await client.delete(f"/api/v1/admin/promo-codes/{sample_promo_code.id}", headers=admin_headers)
        assert response.status_code == 200