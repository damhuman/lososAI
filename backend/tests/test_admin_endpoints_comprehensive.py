"""Comprehensive tests for admin endpoints to achieve 100% coverage."""
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from io import BytesIO
from unittest.mock import patch, AsyncMock
import json

from app.db.models.product import Category, Product, District, PromoCode
from app.db.models.user import User
from app.db.models.order import Order, OrderItem

pytestmark = pytest.mark.asyncio


class TestAdminEndpointsComprehensive:
    """Additional tests to achieve 100% coverage."""

    async def test_verify_basic_auth_invalid_username(self, client: AsyncClient):
        """Test basic auth with invalid username."""
        import base64
        credentials = base64.b64encode(b"wrong:admin123").decode("ascii")
        headers = {"Authorization": f"Basic {credentials}"}
        
        response = await client.get("/api/v1/admin/verify", headers=headers)
        assert response.status_code == 401
        assert "Invalid authentication credentials" in response.json()["detail"]

    async def test_verify_basic_auth_invalid_password(self, client: AsyncClient):
        """Test basic auth with invalid password."""
        import base64
        credentials = base64.b64encode(b"admin:wrong").decode("ascii")
        headers = {"Authorization": f"Basic {credentials}"}
        
        response = await client.get("/api/v1/admin/verify", headers=headers)
        assert response.status_code == 401
        assert "Invalid authentication credentials" in response.json()["detail"]

    async def test_upload_image_success(self, client: AsyncClient, admin_headers):
        """Test successful image upload."""
        with patch('app.services.s3.s3_service.upload_image', new_callable=AsyncMock) as mock_upload:
            mock_upload.return_value = "https://example.com/image.jpg"
            
            # Create a fake image file
            image_data = b"fake image data"
            files = {"image": ("test.jpg", BytesIO(image_data), "image/jpeg")}
            
            response = await client.post("/api/v1/admin/upload/image", files=files, headers=admin_headers)
            assert response.status_code == 200
            assert response.json()["url"] == "https://example.com/image.jpg"
            mock_upload.assert_called_once()

    async def test_upload_image_failure(self, client: AsyncClient, admin_headers):
        """Test image upload failure."""
        with patch('app.services.s3.s3_service.upload_image', new_callable=AsyncMock) as mock_upload:
            mock_upload.side_effect = Exception("Upload failed")
            
            image_data = b"fake image data"
            files = {"image": ("test.jpg", BytesIO(image_data), "image/jpeg")}
            
            response = await client.post("/api/v1/admin/upload/image", files=files, headers=admin_headers)
            assert response.status_code == 500
            assert "Upload failed" in response.json()["detail"]

    async def test_create_category_with_existing_id(self, client: AsyncClient, admin_headers, sample_category):
        """Test creating category with existing ID (should fail)."""
        category_data = {
            "id": sample_category.id,  # Same ID as existing category
            "name": "Duplicate Category",
            "description": "This should fail",
            "icon": "🦐",
            "order": 2,
            "is_active": True
        }
        
        response = await client.post("/api/v1/admin/categories", json=category_data, headers=admin_headers)
        # Should fail due to unique constraint
        assert response.status_code == 500 or response.status_code == 400

    async def test_update_nonexistent_category(self, client: AsyncClient, admin_headers):
        """Test updating a category that doesn't exist."""
        update_data = {
            "name": "Updated Name",
            "description": "Updated description"
        }
        
        response = await client.put("/api/v1/admin/categories/nonexistent", json=update_data, headers=admin_headers)
        assert response.status_code == 404
        assert "Category not found" in response.json()["detail"]

    async def test_delete_nonexistent_category(self, client: AsyncClient, admin_headers):
        """Test deleting a category that doesn't exist."""
        response = await client.delete("/api/v1/admin/categories/nonexistent", headers=admin_headers)
        assert response.status_code == 404
        assert "Category not found" in response.json()["detail"]

    async def test_get_products_with_pagination(self, client: AsyncClient, admin_headers, sample_product):
        """Test getting products with different pagination parameters."""
        # Test with page 2 (should be empty)
        response = await client.get("/api/v1/admin/products?page=2&size=1", headers=admin_headers)
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 0
        assert data["page"] == 2
        assert data["size"] == 1

    async def test_get_nonexistent_product(self, client: AsyncClient, admin_headers):
        """Test getting a product that doesn't exist."""
        response = await client.get("/api/v1/admin/products/nonexistent", headers=admin_headers)
        assert response.status_code == 404
        assert "Product not found" in response.json()["detail"]

    async def test_create_product_with_invalid_category(self, client: AsyncClient, admin_headers):
        """Test creating product with non-existent category."""
        product_data = {
            "id": "invalid_product",
            "category_id": "nonexistent_category",
            "name": "Invalid Product",
            "description": "Should fail",
            "price_per_kg": 100.0,
            "packages": [{"id": "1kg", "type": "1кг", "weight": 1.0, "unit": "кг", "price": 100.0, "available": True}],
            "is_active": True,
            "is_featured": False
        }
        
        response = await client.post("/api/v1/admin/products", json=product_data, headers=admin_headers)
        # Should fail due to foreign key constraint
        assert response.status_code == 500 or response.status_code == 400

    async def test_update_nonexistent_product(self, client: AsyncClient, admin_headers):
        """Test updating a product that doesn't exist."""
        update_data = {
            "name": "Updated Product",
            "price_per_kg": 150.0
        }
        
        response = await client.put("/api/v1/admin/products/nonexistent", json=update_data, headers=admin_headers)
        assert response.status_code == 404
        assert "Product not found" in response.json()["detail"]

    async def test_delete_nonexistent_product(self, client: AsyncClient, admin_headers):
        """Test deleting a product that doesn't exist."""
        response = await client.delete("/api/v1/admin/products/nonexistent", headers=admin_headers)
        assert response.status_code == 404
        assert "Product not found" in response.json()["detail"]

    async def test_get_users_with_pagination(self, client: AsyncClient, admin_headers, sample_user):
        """Test getting users with pagination."""
        response = await client.get("/api/v1/admin/users?page=1&size=5", headers=admin_headers)
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert data["page"] == 1

    async def test_get_nonexistent_user(self, client: AsyncClient, admin_headers):
        """Test getting a user that doesn't exist."""
        response = await client.get("/api/v1/admin/users/999999", headers=admin_headers)
        assert response.status_code == 404
        assert "User not found" in response.json()["detail"]

    async def test_update_nonexistent_user(self, client: AsyncClient, admin_headers):
        """Test updating a user that doesn't exist."""
        update_data = {
            "is_gold_client": True
        }
        
        response = await client.put("/api/v1/admin/users/999999", json=update_data, headers=admin_headers)
        assert response.status_code == 404
        assert "User not found" in response.json()["detail"]

    async def test_get_orders_with_status_filter(self, client: AsyncClient, admin_headers, sample_order):
        """Test getting orders with status filter."""
        # Test with confirmed status (should be empty)
        response = await client.get("/api/v1/admin/orders?status=confirmed", headers=admin_headers)
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 0

    async def test_get_orders_with_date_filter(self, client: AsyncClient, admin_headers, sample_order):
        """Test getting orders with date filter."""
        from datetime import datetime
        start_date = "2023-01-01"
        end_date = "2023-12-31"
        
        response = await client.get(
            f"/api/v1/admin/orders?start_date={start_date}&end_date={end_date}", 
            headers=admin_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert "items" in data

    async def test_get_nonexistent_order(self, client: AsyncClient, admin_headers):
        """Test getting an order that doesn't exist."""
        response = await client.get("/api/v1/admin/orders/999999", headers=admin_headers)
        assert response.status_code == 404
        assert "Order not found" in response.json()["detail"]

    async def test_update_order_status_nonexistent(self, client: AsyncClient, admin_headers):
        """Test updating status of non-existent order."""
        update_data = {"status": "confirmed"}
        
        response = await client.put("/api/v1/admin/orders/999999/status", json=update_data, headers=admin_headers)
        assert response.status_code == 404
        assert "Order not found" in response.json()["detail"]

    async def test_get_order_stats_with_dates(self, client: AsyncClient, admin_headers):
        """Test getting order stats with date filters."""
        start_date = "2023-01-01"
        end_date = "2023-12-31"
        
        response = await client.get(
            f"/api/v1/admin/orders/stats?start_date={start_date}&end_date={end_date}", 
            headers=admin_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert "total_orders" in data
        assert "total_revenue" in data

    async def test_export_orders_report(self, client: AsyncClient, admin_headers):
        """Test exporting orders report."""
        start_date = "2023-01-01"
        end_date = "2023-12-31"
        
        response = await client.get(
            f"/api/v1/admin/orders/export?start_date={start_date}&end_date={end_date}", 
            headers=admin_headers
        )
        assert response.status_code == 200
        assert response.headers["content-type"] == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"

    async def test_get_nonexistent_district(self, client: AsyncClient, admin_headers):
        """Test getting a district that doesn't exist."""
        response = await client.get("/api/v1/admin/districts/999999", headers=admin_headers)
        assert response.status_code == 404
        assert "District not found" in response.json()["detail"]

    async def test_update_nonexistent_district(self, client: AsyncClient, admin_headers):
        """Test updating a district that doesn't exist."""
        update_data = {
            "name": "Updated District",
            "delivery_cost": 75.0
        }
        
        response = await client.put("/api/v1/admin/districts/999999", json=update_data, headers=admin_headers)
        assert response.status_code == 404
        assert "District not found" in response.json()["detail"]

    async def test_delete_nonexistent_district(self, client: AsyncClient, admin_headers):
        """Test deleting a district that doesn't exist."""
        response = await client.delete("/api/v1/admin/districts/999999", headers=admin_headers)
        assert response.status_code == 404
        assert "District not found" in response.json()["detail"]

    async def test_get_nonexistent_promo_code(self, client: AsyncClient, admin_headers):
        """Test getting a promo code that doesn't exist."""
        response = await client.get("/api/v1/admin/promo-codes/999999", headers=admin_headers)
        assert response.status_code == 404
        assert "Promo code not found" in response.json()["detail"]

    async def test_update_nonexistent_promo_code(self, client: AsyncClient, admin_headers):
        """Test updating a promo code that doesn't exist."""
        update_data = {
            "code": "UPDATED10",
            "discount_percent": 15.0
        }
        
        response = await client.put("/api/v1/admin/promo-codes/999999", json=update_data, headers=admin_headers)
        assert response.status_code == 404
        assert "Promo code not found" in response.json()["detail"]

    async def test_delete_nonexistent_promo_code(self, client: AsyncClient, admin_headers):
        """Test deleting a promo code that doesn't exist."""
        response = await client.delete("/api/v1/admin/promo-codes/999999", headers=admin_headers)
        assert response.status_code == 404
        assert "Promo code not found" in response.json()["detail"]

    async def test_create_promo_code_duplicate(self, client: AsyncClient, admin_headers, sample_promo_code):
        """Test creating promo code with duplicate code."""
        promo_data = {
            "code": sample_promo_code.code,  # Same code
            "discount_percent": 15.0,
            "discount_amount": None,
            "usage_limit": 100,
            "is_active": True,
            "is_gold_code": False
        }
        
        response = await client.post("/api/v1/admin/promo-codes", json=promo_data, headers=admin_headers)
        # Should fail due to unique constraint
        assert response.status_code == 500 or response.status_code == 400

    async def test_create_promo_code_with_amount_discount(self, client: AsyncClient, admin_headers):
        """Test creating promo code with amount discount."""
        promo_data = {
            "code": "AMOUNT50",
            "discount_percent": None,
            "discount_amount": 50.0,
            "usage_limit": 50,
            "is_active": True,
            "is_gold_code": False
        }
        
        response = await client.post("/api/v1/admin/promo-codes", json=promo_data, headers=admin_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == "AMOUNT50"
        assert data["discount_amount"] == 50.0

    async def test_create_gold_promo_code(self, client: AsyncClient, admin_headers):
        """Test creating gold-only promo code."""
        promo_data = {
            "code": "GOLD20",
            "discount_percent": 20.0,
            "discount_amount": None,
            "usage_limit": 10,
            "is_active": True,
            "is_gold_code": True
        }
        
        response = await client.post("/api/v1/admin/promo-codes", json=promo_data, headers=admin_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == "GOLD20"
        assert data["is_gold_code"] == True