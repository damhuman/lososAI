"""Final targeted tests to achieve 100% coverage of admin endpoints."""
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from unittest.mock import patch, AsyncMock
from io import BytesIO

pytestmark = pytest.mark.asyncio


class TestAdminEndpointsFinal:
    """Final tests to cover remaining missing lines."""

    async def test_basic_auth_credentials_check_lines_30(self, client: AsyncClient):
        """Test basic auth credential verification (line 30)."""
        import base64
        
        # Test with wrong username but correct password
        credentials = base64.b64encode(b"wrong:admin123").decode("ascii")
        headers = {"Authorization": f"Basic {credentials}"}
        
        response = await client.get("/api/v1/admin/verify", headers=headers)
        assert response.status_code == 401
        # This covers line 30 where the HTTPException is raised

    async def test_s3_upload_service_lines_51_55(self, client: AsyncClient, admin_headers):
        """Test S3 upload service call and exception handling (lines 51-55)."""
        with patch('app.services.s3.s3_service.upload_image', new_callable=AsyncMock) as mock_upload:
            # Test successful upload first (line 52)
            mock_upload.return_value = "https://example.com/uploaded.jpg"
            image_data = b"fake image data"
            files = {"image": ("test.jpg", BytesIO(image_data), "image/jpeg")}
            
            response = await client.post("/api/v1/admin/upload/image", files=files, headers=admin_headers)
            assert response.status_code == 200
            # This covers line 52 (successful upload) and line 53 (return response)
            
            # Test upload failure (lines 54-55)
            mock_upload.side_effect = Exception("S3 upload failed")
            
            response = await client.post("/api/v1/admin/upload/image", files=files, headers=admin_headers)
            assert response.status_code == 500
            # This covers lines 54-55 (exception handling)

    async def test_product_image_deletion_lines_227_228(self, client: AsyncClient, admin_headers, sample_product):
        """Test product image deletion during update (lines 227-228)."""
        with patch('app.services.s3.s3_service.delete_image', new_callable=AsyncMock) as mock_delete:
            # Update product with new image URL to trigger old image deletion
            update_data = {
                "image_url": "https://example.com/new-image.jpg"
            }
            
            # First set an existing image on the product
            sample_product.image_url = "https://example.com/old-image.jpg"
            
            response = await client.put(f"/api/v1/admin/products/{sample_product.id}", json=update_data, headers=admin_headers)
            assert response.status_code == 200
            # This should cover lines 227-228 (image deletion check and call)

    async def test_product_deletion_with_image_lines_252_253(self, client: AsyncClient, admin_headers, sample_category):
        """Test product deletion with image cleanup (lines 252-253)."""
        with patch('app.services.s3.s3_service.delete_image', new_callable=AsyncMock) as mock_delete:
            # Create product with image
            product_data = {
                "id": "product_with_image",
                "category_id": sample_category.id,
                "name": "Product with Image",
                "description": "Has an image to delete",
                "price_per_kg": 100.0,
                "packages": [{"id": "1kg", "type": "1кг", "weight": 1.0, "unit": "кг", "price": 100.0, "available": True}],
                "image_url": "https://example.com/product-image.jpg",
                "is_active": True,
                "is_featured": False
            }
            
            create_response = await client.post("/api/v1/admin/products", json=product_data, headers=admin_headers)
            assert create_response.status_code == 200
            
            # Delete the product
            response = await client.delete("/api/v1/admin/products/product_with_image", headers=admin_headers)
            assert response.status_code == 200
            # This covers lines 252-253 (if db_product.image_url check and delete call)

    async def test_orders_date_parsing_exception_lines_362_368(self, client: AsyncClient, admin_headers):
        """Test orders date parsing with ValueError exceptions (lines 362, 368)."""
        # Test with completely invalid date format that will cause ValueError
        response = await client.get("/api/v1/admin/orders?start_date=not-a-date&end_date=also-not-a-date", headers=admin_headers)
        assert response.status_code == 200
        # This should cover lines 362 and 368 where ValueError exceptions are caught and passed

    async def test_order_stats_avg_calculation_zero_orders(self, client: AsyncClient, admin_headers):
        """Test order stats average calculation with zero orders."""
        # Get stats when there are no orders matching the filter
        response = await client.get("/api/v1/admin/orders/stats?start_date=1900-01-01&end_date=1900-01-02", headers=admin_headers)
        assert response.status_code == 200
        data = response.json()
        # This should cover the avg_order_value calculation with zero orders
        assert data["avg_order_value"] == 0

    async def test_promo_code_creation_commit_lines_692_695(self, client: AsyncClient, admin_headers):
        """Test promo code creation commit and refresh (lines 692-695)."""
        promo_data = {
            "code": "FINAL_TEST",
            "discount_percent": 15.0,
            "discount_amount": None,
            "usage_limit": 100,
            "is_active": True,
            "is_gold_code": False
        }
        
        response = await client.post("/api/v1/admin/promo-codes", json=promo_data, headers=admin_headers)
        assert response.status_code == 200
        # This covers lines 692-695 (session.add, commit, refresh, return)

    async def test_get_promo_codes_query_lines_681_682(self, client: AsyncClient, admin_headers, sample_promo_code):
        """Test get promo codes query execution (lines 681-682)."""
        response = await client.get("/api/v1/admin/promo-codes", headers=admin_headers)
        assert response.status_code == 200
        data = response.json()
        # This covers lines 681-682 (query execution and scalars().all())
        assert len(data) >= 1

    async def test_get_districts_query_lines_616_617(self, client: AsyncClient, admin_headers, sample_district):
        """Test get districts query execution (lines 616-617)."""
        response = await client.get("/api/v1/admin/districts", headers=admin_headers)
        assert response.status_code == 200
        data = response.json()
        # This covers lines 616-617 (query execution and scalars().all())
        assert len(data) >= 1

    async def test_create_district_commit_lines_629_630(self, client: AsyncClient, admin_headers):
        """Test district creation commit and refresh (lines 629-630)."""
        district_data = {
            "name": "Final Test District",
            "delivery_cost": 55.0,
            "is_active": True
        }
        
        response = await client.post("/api/v1/admin/districts", json=district_data, headers=admin_headers)
        assert response.status_code == 200
        # This covers lines 629-630 (commit and refresh)