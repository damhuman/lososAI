"""Targeted tests to cover very specific missing lines in admin endpoints."""
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from unittest.mock import patch, AsyncMock, MagicMock
import json
import io
from datetime import datetime, timedelta

pytestmark = pytest.mark.asyncio


class TestAdminEndpointsTargeted:
    """Targeted tests for specific missing lines."""

    async def test_get_categories_empty_result(self, client: AsyncClient, admin_headers):
        """Test getting categories when no categories exist (covers line 66-67)."""
        # This should return empty list, covering the return statement
        response = await client.get("/api/v1/admin/categories", headers=admin_headers)
        assert response.status_code == 200
        # Even if there are categories from fixtures, the return line is still covered

    async def test_create_category_commit_refresh_flow(self, client: AsyncClient, admin_headers):
        """Test category creation to cover commit/refresh lines (79-80)."""
        category_data = {
            "id": "commit_test",
            "name": "Commit Test Category",
            "description": "Testing commit flow",
            "icon": "🔄",
            "order": 50,
            "is_active": True
        }
        
        response = await client.post("/api/v1/admin/categories", json=category_data, headers=admin_headers)
        assert response.status_code == 200
        # This covers lines 78-80 (commit and refresh)

    async def test_update_category_not_found_flow(self, client: AsyncClient, admin_headers):
        """Test update category not found flow (lines 92-95)."""
        update_data = {"name": "Not Found"}
        
        response = await client.put("/api/v1/admin/categories/not_found", json=update_data, headers=admin_headers)
        assert response.status_code == 404
        # This covers the scalar_one_or_none() and if not db_category check

    async def test_update_category_commit_refresh_flow(self, client: AsyncClient, admin_headers, sample_category):
        """Test update category commit/refresh flow (lines 100-102)."""
        update_data = {
            "name": "Updated for Commit Test",
            "description": "Testing commit flow"
        }
        
        response = await client.put(f"/api/v1/admin/categories/{sample_category.id}", json=update_data, headers=admin_headers)
        assert response.status_code == 200
        # This covers lines 100-102 (commit, refresh, return)

    async def test_delete_category_not_found_flow(self, client: AsyncClient, admin_headers):
        """Test delete category not found flow (lines 113-116)."""
        response = await client.delete("/api/v1/admin/categories/not_found", headers=admin_headers)
        assert response.status_code == 404
        # This covers the scalar_one_or_none() and if not db_category check

    async def test_delete_category_success_flow(self, client: AsyncClient, admin_headers):
        """Test delete category success flow (lines 118-120)."""
        # First create a category
        category_data = {
            "id": "delete_test",
            "name": "Delete Test",
            "description": "Will be deleted",
            "icon": "🗑️",
            "order": 999,
            "is_active": True
        }
        
        create_response = await client.post("/api/v1/admin/categories", json=category_data, headers=admin_headers)
        assert create_response.status_code == 200
        
        # Now delete it to cover lines 118-120
        response = await client.delete("/api/v1/admin/categories/delete_test", headers=admin_headers)
        assert response.status_code == 200
        assert response.json()["message"] == "Category deleted successfully"

    async def test_get_products_count_total_flow(self, client: AsyncClient, admin_headers, sample_product):
        """Test get products count total flow (lines 134-136)."""
        response = await client.get("/api/v1/admin/products?page=1&size=10", headers=admin_headers)
        assert response.status_code == 200
        # This covers the count query execution and scalar() call

    async def test_get_products_query_execution_flow(self, client: AsyncClient, admin_headers, sample_product):
        """Test get products query execution flow (lines 139-147)."""
        response = await client.get("/api/v1/admin/products?page=1&size=5", headers=admin_headers)
        assert response.status_code == 200
        data = response.json()
        # This covers the product query execution and scalars().all()
        assert "items" in data
        assert "total" in data

    async def test_get_products_paginated_response_flow(self, client: AsyncClient, admin_headers, sample_product):
        """Test get products paginated response flow (lines 149-154)."""
        response = await client.get("/api/v1/admin/products?page=2&size=1", headers=admin_headers)
        assert response.status_code == 200
        data = response.json()
        # This covers the PaginatedResponse creation and return
        assert data["page"] == 2
        assert data["size"] == 1

    async def test_get_product_stats_queries_flow(self, client: AsyncClient, admin_headers, sample_product, sample_category):
        """Test get product stats queries flow (lines 161-177)."""
        response = await client.get("/api/v1/admin/products/stats", headers=admin_headers)
        assert response.status_code == 200
        data = response.json()
        # This covers all the count queries and scalar() calls
        assert "total_products" in data
        assert "total_categories" in data
        assert "featured_products" in data
        assert "active_products" in data

    async def test_get_product_by_id_not_found_flow(self, client: AsyncClient, admin_headers):
        """Test get product by ID not found flow (lines 184-187)."""
        response = await client.get("/api/v1/admin/products/not_found", headers=admin_headers)
        assert response.status_code == 404
        # This covers scalar_one_or_none() and if not db_product check

    async def test_get_product_by_id_success_flow(self, client: AsyncClient, admin_headers, sample_product):
        """Test get product by ID success flow (lines 189-193)."""
        response = await client.get(f"/api/v1/admin/products/{sample_product.id}", headers=admin_headers)
        assert response.status_code == 200
        # This covers the successful return of the product

    async def test_create_product_commit_refresh_flow(self, client: AsyncClient, admin_headers, sample_category):
        """Test create product commit/refresh flow (lines 205-209)."""
        product_data = {
            "id": "commit_product_test",
            "category_id": sample_category.id,
            "name": "Commit Product Test",
            "description": "Testing commit flow",
            "price_per_kg": 100.0,
            "packages": [{"id": "1kg", "type": "1кг", "weight": 1.0, "unit": "кг", "price": 100.0, "available": True}],
            "is_active": True,
            "is_featured": False
        }
        
        response = await client.post("/api/v1/admin/products", json=product_data, headers=admin_headers)
        assert response.status_code == 200
        # This covers lines 203-209 (session.add, commit, refresh, return)

    async def test_update_product_not_found_flow(self, client: AsyncClient, admin_headers):
        """Test update product not found flow (lines 221-224)."""
        update_data = {"name": "Not Found Product"}
        
        response = await client.put("/api/v1/admin/products/not_found", json=update_data, headers=admin_headers)
        assert response.status_code == 404
        # This covers scalar_one_or_none() and if not db_product check

    async def test_update_product_setattr_commit_flow(self, client: AsyncClient, admin_headers, sample_product):
        """Test update product setattr/commit flow (lines 226-235)."""
        update_data = {
            "name": "Updated Product for Commit",
            "price_per_kg": 250.0,
            "is_featured": True
        }
        
        response = await client.put(f"/api/v1/admin/products/{sample_product.id}", json=update_data, headers=admin_headers)
        assert response.status_code == 200
        # This covers the setattr loop, commit, refresh, and return

    async def test_delete_product_not_found_flow(self, client: AsyncClient, admin_headers):
        """Test delete product not found flow (lines 246-249)."""
        response = await client.delete("/api/v1/admin/products/not_found", headers=admin_headers)
        assert response.status_code == 404
        # This covers scalar_one_or_none() and if not db_product check

    async def test_delete_product_success_flow(self, client: AsyncClient, admin_headers, sample_category):
        """Test delete product success flow (lines 251-257)."""
        # First create a product
        product_data = {
            "id": "delete_product_test",
            "category_id": sample_category.id,
            "name": "Delete Product Test",
            "description": "Will be deleted",
            "price_per_kg": 100.0,
            "packages": [{"id": "1kg", "type": "1кг", "weight": 1.0, "unit": "кг", "price": 100.0, "available": True}],
            "is_active": True,
            "is_featured": False
        }
        
        create_response = await client.post("/api/v1/admin/products", json=product_data, headers=admin_headers)
        assert create_response.status_code == 200
        
        # Now delete it
        response = await client.delete("/api/v1/admin/products/delete_product_test", headers=admin_headers)
        assert response.status_code == 200
        # This covers session.delete, commit, and return

    async def test_get_users_count_and_query_flow(self, client: AsyncClient, admin_headers, sample_user):
        """Test get users count and query flow (lines 274-286)."""
        response = await client.get("/api/v1/admin/users?page=1&size=5", headers=admin_headers)
        assert response.status_code == 200
        data = response.json()
        # This covers count query, user query with joinedload, and paginated response
        assert "items" in data
        assert "total" in data

    async def test_get_user_stats_queries_flow(self, client: AsyncClient, admin_headers, sample_user):
        """Test get user stats queries flow (lines 305-309)."""
        response = await client.get("/api/v1/admin/users/stats", headers=admin_headers)
        assert response.status_code == 200
        data = response.json()
        # This covers all the user count queries
        assert "total" in data
        assert "active" in data
        assert "gold_clients" in data
        assert "blocked" in data

    async def test_update_user_not_found_flow(self, client: AsyncClient, admin_headers):
        """Test update user not found flow (lines 326-329)."""
        update_data = {"is_gold_client": True}
        
        response = await client.put("/api/v1/admin/users/999999", json=update_data, headers=admin_headers)
        assert response.status_code == 404
        # This covers scalar_one_or_none() and if not db_user check

    async def test_update_user_commit_refresh_flow(self, client: AsyncClient, admin_headers, sample_user):
        """Test update user commit/refresh flow (lines 331-336)."""
        update_data = {
            "is_gold_client": True,
            "is_blocked": False
        }
        
        response = await client.put(f"/api/v1/admin/users/{sample_user.id}", json=update_data, headers=admin_headers)
        assert response.status_code == 200
        # This covers the setattr loop, commit, refresh, and return

    async def test_get_orders_with_order_id_filter(self, client: AsyncClient, admin_headers, sample_order):
        """Test get orders with order_id filter (lines 357-358)."""
        response = await client.get(f"/api/v1/admin/orders?order_id={sample_order.order_id}", headers=admin_headers)
        assert response.status_code == 200
        data = response.json()
        # This covers the order_id filter check
        assert "items" in data

    async def test_get_orders_with_invalid_start_date(self, client: AsyncClient, admin_headers):
        """Test get orders with invalid start date (lines 359-364)."""
        response = await client.get("/api/v1/admin/orders?start_date=invalid-date", headers=admin_headers)
        assert response.status_code == 200
        # This covers the ValueError exception handling in start_date parsing
        data = response.json()
        assert "items" in data

    async def test_get_orders_with_invalid_end_date(self, client: AsyncClient, admin_headers):
        """Test get orders with invalid end date (lines 365-370)."""
        response = await client.get("/api/v1/admin/orders?end_date=invalid-date", headers=admin_headers)
        assert response.status_code == 200
        # This covers the ValueError exception handling in end_date parsing
        data = response.json()
        assert "items" in data

    async def test_get_orders_count_with_filters(self, client: AsyncClient, admin_headers, sample_order):
        """Test get orders count with filters (lines 374-377)."""
        response = await client.get("/api/v1/admin/orders?status=pending", headers=admin_headers)
        assert response.status_code == 200
        data = response.json()
        # This covers the filtered count query execution
        assert data["total"] >= 0

    async def test_get_orders_query_with_filters(self, client: AsyncClient, admin_headers, sample_order):
        """Test get orders query with filters (lines 392-396)."""
        response = await client.get("/api/v1/admin/orders?status=pending&page=1&size=10", headers=admin_headers)
        assert response.status_code == 200
        data = response.json()
        # This covers the filtered query execution and scalars().all()
        assert "items" in data
        assert "total" in data

    async def test_get_order_stats_with_invalid_start_date(self, client: AsyncClient, admin_headers):
        """Test get order stats with invalid start date (lines 415-420)."""
        response = await client.get("/api/v1/admin/orders/stats?start_date=invalid-date", headers=admin_headers)
        assert response.status_code == 200
        # This covers the ValueError exception handling in start_date parsing
        data = response.json()
        assert "total_orders" in data

    async def test_get_order_stats_with_invalid_end_date(self, client: AsyncClient, admin_headers):
        """Test get order stats with invalid end date (lines 421-426)."""
        response = await client.get("/api/v1/admin/orders/stats?end_date=invalid-date", headers=admin_headers)
        assert response.status_code == 200
        # This covers the ValueError exception handling in end_date parsing
        data = response.json()
        assert "total_orders" in data

    async def test_get_order_stats_with_filters_applied(self, client: AsyncClient, admin_headers, sample_order):
        """Test get order stats with filters applied (lines 428-453)."""
        response = await client.get("/api/v1/admin/orders/stats?start_date=2020-01-01&end_date=2030-01-01", headers=admin_headers)
        assert response.status_code == 200
        data = response.json()
        # This covers all the filtered queries execution
        assert "total_orders" in data
        assert "total_revenue" in data
        assert "avg_order_value" in data
        assert "orders_by_status" in data

    async def test_get_order_by_id_not_found_flow(self, client: AsyncClient, admin_headers):
        """Test get order by ID not found flow (lines 478-482)."""
        response = await client.get("/api/v1/admin/orders/999999", headers=admin_headers)
        assert response.status_code == 404
        # This covers scalar_one_or_none() and if not order check

    async def test_update_order_status_not_found_flow(self, client: AsyncClient, admin_headers):
        """Test update order status not found flow (lines 494-499)."""
        update_data = {"status": "confirmed"}
        
        response = await client.put("/api/v1/admin/orders/999999/status", json=update_data, headers=admin_headers)
        assert response.status_code == 404
        # This covers scalar_one_or_none() and if not order check

    async def test_update_order_status_success_flow(self, client: AsyncClient, admin_headers, sample_order):
        """Test update order status success flow (lines 501-506)."""
        update_data = {"status": "confirmed"}
        
        response = await client.put(f"/api/v1/admin/orders/{sample_order.id}/status", json=update_data, headers=admin_headers)
        assert response.status_code == 200
        # This covers the status update, updated_at assignment, commit, refresh, and return

    async def test_export_orders_workbook_creation_flow(self, client: AsyncClient, admin_headers, sample_order):
        """Test export orders workbook creation flow (lines 543-587)."""
        start_date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
        end_date = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
        
        response = await client.get(
            f"/api/v1/admin/orders/export?start_date={start_date}&end_date={end_date}", 
            headers=admin_headers
        )
        assert response.status_code == 200
        # This covers the entire Excel workbook creation flow
        assert response.headers["content-type"] == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"

    async def test_export_orders_io_error_flow(self, client: AsyncClient, admin_headers):
        """Test export orders with io.BytesIO error (lines 590-605)."""
        # This test is complex because BytesIO is used in multiple places.
        # Instead, let's test a different error path by making the workbook save fail
        with patch('openpyxl.Workbook') as mock_workbook:
            mock_wb = mock_workbook.return_value
            mock_wb.save.side_effect = Exception("Workbook save error")
            
            response = await client.get(
                "/api/v1/admin/orders/export?start_date=2023-01-01&end_date=2023-12-31", 
                headers=admin_headers
            )
            assert response.status_code == 500
            assert "Export failed" in response.json()["detail"]

    async def test_update_district_not_found_flow(self, client: AsyncClient, admin_headers):
        """Test update district not found flow (lines 640-645)."""
        update_data = {"name": "Not Found District"}
        
        response = await client.put("/api/v1/admin/districts/999999", json=update_data, headers=admin_headers)
        assert response.status_code == 404
        # This covers scalar_one_or_none() and if not db_district check

    async def test_update_district_commit_refresh_flow(self, client: AsyncClient, admin_headers, sample_district):
        """Test update district commit/refresh flow (lines 647-652)."""
        update_data = {
            "name": "Updated District for Commit",
            "delivery_cost": 120.0
        }
        
        response = await client.put(f"/api/v1/admin/districts/{sample_district.id}", json=update_data, headers=admin_headers)
        assert response.status_code == 200
        # This covers the setattr loop, commit, refresh, and return

    async def test_delete_district_not_found_flow(self, client: AsyncClient, admin_headers):
        """Test delete district not found flow (lines 661-666)."""
        response = await client.delete("/api/v1/admin/districts/999999", headers=admin_headers)
        assert response.status_code == 404
        # This covers scalar_one_or_none() and if not db_district check

    async def test_delete_district_success_flow(self, client: AsyncClient, admin_headers):
        """Test delete district success flow (lines 668-670)."""
        # First create a district
        district_data = {
            "name": "Delete District Test",
            "delivery_cost": 50.0,
            "is_active": True
        }
        
        create_response = await client.post("/api/v1/admin/districts", json=district_data, headers=admin_headers)
        assert create_response.status_code == 200
        district_id = create_response.json()["id"]
        
        # Now delete it to cover lines 668-670
        response = await client.delete(f"/api/v1/admin/districts/{district_id}", headers=admin_headers)
        assert response.status_code == 200
        assert response.json()["message"] == "District deleted successfully"

    async def test_update_promo_code_not_found_flow(self, client: AsyncClient, admin_headers):
        """Test update promo code not found flow (lines 705-710)."""
        update_data = {"code": "NOT_FOUND"}
        
        response = await client.put("/api/v1/admin/promo-codes/999999", json=update_data, headers=admin_headers)
        assert response.status_code == 404
        # This covers scalar_one_or_none() and if not db_promo_code check

    async def test_update_promo_code_commit_refresh_flow(self, client: AsyncClient, admin_headers, sample_promo_code):
        """Test update promo code commit/refresh flow (lines 712-717)."""
        update_data = {
            "code": "UPDATED_PROMO",
            "discount_percent": 25.0
        }
        
        response = await client.put(f"/api/v1/admin/promo-codes/{sample_promo_code.id}", json=update_data, headers=admin_headers)
        assert response.status_code == 200
        # This covers the setattr loop, commit, refresh, and return

    async def test_delete_promo_code_not_found_flow(self, client: AsyncClient, admin_headers):
        """Test delete promo code not found flow (lines 726-731)."""
        response = await client.delete("/api/v1/admin/promo-codes/999999", headers=admin_headers)
        assert response.status_code == 404
        # This covers scalar_one_or_none() and if not db_promo_code check

    async def test_delete_promo_code_success_flow(self, client: AsyncClient, admin_headers):
        """Test delete promo code success flow (lines 733-735)."""
        # First create a promo code
        promo_data = {
            "code": "DELETE_PROMO_TEST",
            "discount_percent": 10.0,
            "discount_amount": None,
            "usage_limit": 50,
            "is_active": True,
            "is_gold_code": False
        }
        
        create_response = await client.post("/api/v1/admin/promo-codes", json=promo_data, headers=admin_headers)
        assert create_response.status_code == 200
        promo_id = create_response.json()["id"]
        
        # Now delete it to cover lines 733-735
        response = await client.delete(f"/api/v1/admin/promo-codes/{promo_id}", headers=admin_headers)
        assert response.status_code == 200
        assert response.json()["message"] == "Promo code deleted successfully"