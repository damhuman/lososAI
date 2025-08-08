"""Tests for public API endpoints."""
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from unittest.mock import AsyncMock, patch

from app.db.models.product import Category, Product, District, PromoCode
from app.db.models.user import User
from app.db.models.order import Order

# Mark all test functions in this module as asyncio
pytestmark = pytest.mark.asyncio


class TestCategories:
    """Test public category endpoints."""
    
    async def test_get_categories(self, client: AsyncClient, sample_category):
        """Test getting active categories."""
        response = await client.get("/api/v1/categories")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["id"] == sample_category.id
        assert data[0]["name"] == sample_category.name
    
    async def test_get_categories_only_active(self, client: AsyncClient, test_session: AsyncSession):
        """Test that only active categories are returned."""
        # Create active category
        active_category = Category(
            id="active_category",
            name="Active Category",
            icon="🐟",
            order=1,
            is_active=True
        )
        test_session.add(active_category)
        
        # Create inactive category
        inactive_category = Category(
            id="inactive_category",
            name="Inactive Category",
            icon="🦐",
            order=2,
            is_active=False
        )
        test_session.add(inactive_category)
        await test_session.commit()
        
        response = await client.get("/api/v1/categories")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["id"] == "active_category"


class TestProducts:
    """Test public product endpoints."""
    
    async def test_get_products_by_category(self, client: AsyncClient, sample_product):
        """Test getting products by category."""
        response = await client.get(f"/api/v1/products?category_id={sample_product.category_id}")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["id"] == sample_product.id
        assert data[0]["category_id"] == sample_product.category_id
    
    async def test_get_products_all_categories(self, client: AsyncClient, sample_product):
        """Test getting all products."""
        response = await client.get("/api/v1/products")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["id"] == sample_product.id
    
    async def test_get_products_nonexistent_category(self, client: AsyncClient):
        """Test getting products for non-existent category."""
        response = await client.get("/api/v1/products?category_id=nonexistent")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 0
    
    async def test_get_featured_products(self, client: AsyncClient, test_session: AsyncSession, sample_category):
        """Test getting featured products."""
        # Create featured product
        featured_product = Product(
            id="featured_product",
            category_id=sample_category.id,
            name="Featured Product",
            price_per_kg=200.0,
            packages=[{"id": "1kg", "type": "1кг", "weight": 1.0, "unit": "кг", "price": 200.0, "available": True}],
            is_active=True,
            is_featured=True
        )
        test_session.add(featured_product)
        await test_session.commit()
        
        response = await client.get("/api/v1/products/featured")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["id"] == "featured_product"
        assert data[0]["is_featured"] is True
    
    async def test_get_product_by_id(self, client: AsyncClient, sample_product):
        """Test getting a specific product by ID."""
        response = await client.get(f"/api/v1/products/{sample_product.id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == sample_product.id
        assert data["name"] == sample_product.name
        assert len(data["packages"]) == 1
    
    async def test_get_nonexistent_product(self, client: AsyncClient):
        """Test getting a non-existent product."""
        response = await client.get("/api/v1/products/nonexistent")
        assert response.status_code == 404


class TestDistricts:
    """Test public district endpoints."""
    
    async def test_get_districts(self, client: AsyncClient, sample_district):
        """Test getting active districts."""
        response = await client.get("/api/v1/districts")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["name"] == sample_district.name
        assert data[0]["delivery_cost"] == sample_district.delivery_cost
    
    async def test_get_districts_only_active(self, client: AsyncClient, test_session: AsyncSession):
        """Test that only active districts are returned."""
        # Create active district
        active_district = District(
            name="Active District",
            delivery_cost=50.0,
            is_active=True
        )
        test_session.add(active_district)
        
        # Create inactive district
        inactive_district = District(
            name="Inactive District", 
            delivery_cost=75.0,
            is_active=False
        )
        test_session.add(inactive_district)
        await test_session.commit()
        
        response = await client.get("/api/v1/districts")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["name"] == "Active District"


class TestPromo:
    """Test promo code validation endpoints."""
    
    async def test_validate_promo_code_valid(self, client: AsyncClient, sample_promo_code):
        """Test validating a valid promo code."""
        response = await client.post("/api/v1/promo/validate", json={"code": sample_promo_code.code})
        assert response.status_code == 200
        data = response.json()
        assert data["valid"] is True
        assert data["discount_percent"] == sample_promo_code.discount_percent
        assert data["is_gold_code"] == sample_promo_code.is_gold_code
    
    async def test_validate_promo_code_invalid(self, client: AsyncClient):
        """Test validating an invalid promo code."""
        response = await client.post("/api/v1/promo/validate", json={"code": "INVALID"})
        assert response.status_code == 200
        data = response.json()
        assert data["valid"] is False
        assert data["discount_percent"] == 0
    
    async def test_validate_promo_code_inactive(self, client: AsyncClient, test_session: AsyncSession):
        """Test validating an inactive promo code."""
        inactive_promo = PromoCode(
            code="INACTIVE",
            discount_percent=20.0,
            is_active=False,
            is_gold_code=False
        )
        test_session.add(inactive_promo)
        await test_session.commit()
        
        response = await client.post("/api/v1/promo/validate", json={"code": "INACTIVE"})
        assert response.status_code == 200
        data = response.json()
        assert data["valid"] is False
        assert data["discount_percent"] == 0
    
    async def test_validate_promo_code_gold_only(self, client: AsyncClient, test_session: AsyncSession):
        """Test validating a gold-only promo code."""
        gold_promo = PromoCode(
            code="GOLD20",
            discount_percent=20.0,
            is_active=True,
            is_gold_code=True
        )
        test_session.add(gold_promo)
        await test_session.commit()
        
        response = await client.post("/api/v1/promo/validate", json={"code": "GOLD20"})
        assert response.status_code == 200
        data = response.json()
        assert data["valid"] is True
        assert data["is_gold_code"] is True


class TestOrders:
    """Test order creation and management endpoints."""
    
    async def test_create_order_success(self, client: AsyncClient, test_session: AsyncSession, 
                                       sample_product, sample_district, telegram_headers):
        """Test creating a new order successfully."""
        # User is already mocked via dependency injection
        # Messaging service will skip real API calls in test mode (settings.TESTING = True)
        
        order_data = {
            "user_id": 123456789,
            "user_name": "Test User",
            "items": [
                {
                    "product_id": sample_product.id,
                    "product_name": sample_product.name,
                    "package_id": "1kg",
                    "weight": 1.0,
                    "unit": "кг",
                    "quantity": 2,
                    "price_per_unit": 100.0,
                    "total_price": 200.0
                }
            ],
            "delivery": {
                "district": sample_district.name,
                "time_slot": "morning",
                "comment": "Test order comment"
            },
            "total": 200.0
        }
        
        response = await client.post("/api/v1/orders", json=order_data, headers=telegram_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "pending"
        assert len(data["items"]) == 1
        assert data["total_amount"] > 0
    
    async def test_create_order_invalid_product(self, client: AsyncClient, sample_district, telegram_headers):
        """Test creating order with invalid product."""
        order_data = {
            "user_id": 123456789,
            "user_name": "Test User",
            "items": [
                {
                    "product_id": "nonexistent",
                    "product_name": "Nonexistent Product",
                    "package_id": "1kg",
                    "weight": 1.0,
                    "unit": "кг",
                    "quantity": 1,
                    "price_per_unit": 100.0,
                    "total_price": 100.0
                }
            ],
            "delivery": {
                "district": sample_district.name,
                "time_slot": "morning"
            },
            "total": 100.0
        }
        
        response = await client.post("/api/v1/orders", json=order_data, headers=telegram_headers)
        assert response.status_code == 400
    
    async def test_create_order_invalid_district(self, client: AsyncClient, sample_product, telegram_headers):
        """Test creating order with invalid district."""
        order_data = {
            "user_id": 123456789,
            "user_name": "Test User",
            "items": [
                {
                    "product_id": sample_product.id,
                    "product_name": sample_product.name,
                    "package_id": "1kg",
                    "weight": 1.0,
                    "unit": "кг",
                    "quantity": 1,
                    "price_per_unit": 100.0,
                    "total_price": 100.0
                }
            ],
            "delivery": {
                "district": "Nonexistent District",
                "time_slot": "morning"
            },
            "total": 100.0
        }
        
        response = await client.post("/api/v1/orders", json=order_data, headers=telegram_headers)
        assert response.status_code == 400
    
    async def test_get_user_orders(self, client: AsyncClient, sample_order, telegram_headers):
        """Test getting user's orders."""
        response = await client.get("/api/v1/orders", headers=telegram_headers)
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1
        # Find our test order
        test_order = next((order for order in data if order["id"] == sample_order.id), None)
        assert test_order is not None
        assert test_order["status"] == sample_order.status.value
    
    async def test_get_order_by_id(self, client: AsyncClient, sample_order, telegram_headers):
        """Test getting a specific order by ID."""
        response = await client.get(f"/api/v1/orders/{sample_order.id}", headers=telegram_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == sample_order.id
        assert data["status"] == sample_order.status.value
        assert len(data["items"]) >= 1


class TestErrors:
    """Test error handling endpoints."""
    
    async def test_404_endpoint(self, client: AsyncClient):
        """Test accessing non-existent endpoint."""
        response = await client.get("/api/v1/nonexistent")
        assert response.status_code == 404
    
    async def test_method_not_allowed(self, client: AsyncClient):
        """Test using wrong HTTP method."""
        response = await client.delete("/api/v1/categories")
        assert response.status_code == 405
    
    async def test_validation_error(self, client: AsyncClient):
        """Test validation error with invalid data."""
        invalid_data = {"invalid": "data"}
        response = await client.post("/api/v1/promo/validate", json=invalid_data)
        assert response.status_code == 422  # Validation error


class TestHealthCheck:
    """Test health check and utility endpoints."""
    
    async def test_health_check(self, client: AsyncClient):
        """Test health check endpoint."""
        response = await client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
    
    async def test_root_redirect(self, client: AsyncClient):
        """Test root endpoint redirect."""
        response = await client.get("/", follow_redirects=False)
        assert response.status_code in [200, 301, 302]  # Could be redirect or direct response