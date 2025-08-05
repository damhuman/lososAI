"""Test for the specific failing case: page=1&size=100"""
import pytest
import pytest_asyncio
from httpx import AsyncClient

pytestmark = pytest.mark.asyncio

async def test_get_products_large_page_size(client: AsyncClient, admin_headers, sample_product):
    """Test getting products with large page size (the failing case)."""
    response = await client.get("/api/v1/admin/products?page=1&size=100", headers=admin_headers)
    assert response.status_code == 200
    data = response.json()
    
    # Validate response structure
    assert "total" in data
    assert "page" in data
    assert "size" in data
    assert "items" in data
    
    # Validate pagination parameters
    assert data["page"] == 1
    assert data["size"] == 100
    
    # Validate at least one product is returned (sample_product)
    assert data["total"] >= 1
    assert len(data["items"]) >= 1
    
    # Validate first product structure
    first_product = data["items"][0]
    assert "id" in first_product
    assert "name" in first_product
    assert "packages" in first_product
    
    # Validate packages have the correct flexible structure
    if first_product["packages"]:
        first_package = first_product["packages"][0]
        assert "weight" in first_package
        assert "unit" in first_package
        assert "available" in first_package
        # These fields should be present but can be None due to our flexible schema
        assert "id" in first_package  # Can be None
        assert "type" in first_package  # Can be None
        assert "price" in first_package  # Can be None
        
    print(f"✅ SUCCESS: Retrieved {data['total']} products with page_size=100")
    if data["items"]:
        print(f"First product packages: {first_product['packages'][:1]}")  # Show first package only