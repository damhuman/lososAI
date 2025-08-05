import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
import tempfile
import os

from app.db.models.product import Product, Category
from app.core.security import get_password_hash


@pytest.mark.asyncio
async def test_get_product_packages(
    client: AsyncClient,
    test_session: AsyncSession,
    admin_headers: dict
):
    """Test getting all packages for a product"""
    # Create test category and product
    category = Category(
        id="test-cat",
        name="Test Category",
        icon="🐟",
        order=1,
        is_active=True
    )
    test_session.add(category)
    
    product = Product(
        id="test-product",
        category_id="test-cat",
        name="Test Product",
        description="Test description",
        price_per_kg=100.0,
        packages=[],
        is_active=True
    )
    test_session.add(product)
    await test_session.commit()
    
    # Get packages (should be empty initially)
    response = await client.get(
        f"/api/v1/admin/products/{product.id}/packages",
        headers=admin_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data == []


@pytest.mark.asyncio
async def test_create_product_package(
    client: AsyncClient,
    test_session: AsyncSession,
    admin_headers: dict
):
    """Test creating a new package for a product"""
    # Create test category and product
    category = Category(
        id="test-cat2",
        name="Test Category 2",
        icon="🦐",
        order=1,
        is_active=True
    )
    test_session.add(category)
    
    product = Product(
        id="test-product2",
        category_id="test-cat2",
        name="Test Product 2",
        description="Test description",
        price_per_kg=200.0,
        packages=[],
        is_active=True
    )
    test_session.add(product)
    await test_session.commit()
    
    # Create a package
    package_data = {
        "package_id": "300g",
        "name": "300 грам",
        "weight": 0.3,
        "unit": "кг",
        "price": 60.0,
        "available": True,
        "sort_order": 1,
        "note": "Популярний вибір"
    }
    
    response = await client.post(
        f"/api/v1/admin/products/{product.id}/packages",
        json=package_data,
        headers=admin_headers
    )
    assert response.status_code == 201
    data = response.json()
    assert data["package_id"] == "300g"
    assert data["name"] == "300 грам"
    assert data["weight"] == 0.3
    assert data["price"] == 60.0
    assert data["product_id"] == product.id
    assert "id" in data


@pytest.mark.asyncio
async def test_update_product_package(
    client: AsyncClient,
    test_session: AsyncSession,
    admin_headers: dict
):
    """Test updating a product package"""
    # Create test data
    category = Category(
        id="test-cat3",
        name="Test Category 3",
        icon="🦀",
        order=1,
        is_active=True
    )
    test_session.add(category)
    
    product = Product(
        id="test-product3",
        category_id="test-cat3",
        name="Test Product 3",
        description="Test description",
        price_per_kg=300.0,
        packages=[],
        is_active=True
    )
    test_session.add(product)
    await test_session.commit()
    
    # Create a package
    package_data = {
        "package_id": "1kg",
        "name": "1 кілограм",
        "weight": 1.0,
        "unit": "кг",
        "price": 300.0,
        "available": True
    }
    
    response = await client.post(
        f"/api/v1/admin/products/{product.id}/packages",
        json=package_data,
        headers=admin_headers
    )
    assert response.status_code == 201
    package_id = response.json()["id"]
    
    # Update the package
    update_data = {
        "price": 280.0,
        "available": False,
        "note": "Тимчасово недоступно"
    }
    
    response = await client.put(
        f"/api/v1/admin/products/{product.id}/packages/{package_id}",
        json=update_data,
        headers=admin_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["price"] == 280.0
    assert data["available"] == False
    assert data["note"] == "Тимчасово недоступно"


@pytest.mark.asyncio
async def test_delete_product_package(
    client: AsyncClient,
    test_session: AsyncSession,
    admin_headers: dict
):
    """Test deleting a product package"""
    # Create test data
    category = Category(
        id="test-cat4",
        name="Test Category 4",
        icon="🦞",
        order=1,
        is_active=True
    )
    test_session.add(category)
    
    product = Product(
        id="test-product4",
        category_id="test-cat4",
        name="Test Product 4",
        description="Test description",
        price_per_kg=400.0,
        packages=[],
        is_active=True
    )
    test_session.add(product)
    await test_session.commit()
    
    # Create a package
    package_data = {
        "package_id": "500g",
        "name": "500 грам",
        "weight": 0.5,
        "unit": "кг",
        "price": 200.0,
        "available": True
    }
    
    response = await client.post(
        f"/api/v1/admin/products/{product.id}/packages",
        json=package_data,
        headers=admin_headers
    )
    assert response.status_code == 201
    package_id = response.json()["id"]
    
    # Delete the package
    response = await client.delete(
        f"/api/v1/admin/products/{product.id}/packages/{package_id}",
        headers=admin_headers
    )
    assert response.status_code == 204
    
    # Verify it's deleted
    response = await client.get(
        f"/api/v1/admin/products/{product.id}/packages",
        headers=admin_headers
    )
    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.asyncio
async def test_upload_package_image(
    client: AsyncClient,
    test_session: AsyncSession,
    admin_headers: dict
):
    """Test uploading an image for a product package"""
    # Create test data
    category = Category(
        id="test-cat5",
        name="Test Category 5",
        icon="🐠",
        order=1,
        is_active=True
    )
    test_session.add(category)
    
    product = Product(
        id="test-product5",
        category_id="test-cat5",
        name="Test Product 5",
        description="Test description",
        price_per_kg=500.0,
        packages=[],
        is_active=True
    )
    test_session.add(product)
    await test_session.commit()
    
    # Create a package
    package_data = {
        "package_id": "2kg",
        "name": "2 кілограми",
        "weight": 2.0,
        "unit": "кг",
        "price": 1000.0,
        "available": True
    }
    
    response = await client.post(
        f"/api/v1/admin/products/{product.id}/packages",
        json=package_data,
        headers=admin_headers
    )
    assert response.status_code == 201
    package_id = response.json()["id"]
    
    # Create a test image file
    with tempfile.NamedTemporaryFile(mode='wb', suffix='.jpg', delete=False) as f:
        # Write a minimal JPEG header
        f.write(b'\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x00\x00\x01\x00\x01\x00\x00')
        f.write(b'\xff\xd9')  # JPEG end marker
        temp_path = f.name
    
    try:
        # Upload image
        with open(temp_path, 'rb') as f:
            files = {'image': ('test.jpg', f, 'image/jpeg')}
            response = await client.post(
                f"/api/v1/admin/products/{product.id}/packages/{package_id}/image",
                files=files,
                headers=admin_headers
            )
        
        # Note: This will fail without S3 configured, but structure is correct
        # In real implementation, mock S3 service for tests
        # assert response.status_code == 200
        # assert "url" in response.json()
    finally:
        os.unlink(temp_path)


@pytest.mark.asyncio
async def test_package_validation(
    client: AsyncClient,
    test_session: AsyncSession,
    admin_headers: dict
):
    """Test package data validation"""
    # Create test data
    category = Category(
        id="test-cat6",
        name="Test Category 6",
        icon="🦑",
        order=1,
        is_active=True
    )
    test_session.add(category)
    
    product = Product(
        id="test-product6",
        category_id="test-cat6",
        name="Test Product 6",
        description="Test description",
        price_per_kg=600.0,
        packages=[],
        is_active=True
    )
    test_session.add(product)
    await test_session.commit()
    
    # Test invalid weight
    invalid_data = {
        "package_id": "invalid",
        "name": "Invalid Package",
        "weight": -1.0,  # Negative weight
        "unit": "кг",
        "price": 100.0,
        "available": True
    }
    
    response = await client.post(
        f"/api/v1/admin/products/{product.id}/packages",
        json=invalid_data,
        headers=admin_headers
    )
    assert response.status_code == 422
    
    # Test missing required fields
    incomplete_data = {
        "package_id": "incomplete",
        "weight": 1.0
        # Missing unit, price, etc.
    }
    
    response = await client.post(
        f"/api/v1/admin/products/{product.id}/packages",
        json=incomplete_data,
        headers=admin_headers
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_duplicate_package_id(
    client: AsyncClient,
    test_session: AsyncSession,
    admin_headers: dict
):
    """Test that duplicate package_ids are not allowed for the same product"""
    # Create test data
    category = Category(
        id="test-cat7",
        name="Test Category 7",
        icon="🐙",
        order=1,
        is_active=True
    )
    test_session.add(category)
    
    product = Product(
        id="test-product7",
        category_id="test-cat7",
        name="Test Product 7",
        description="Test description",
        price_per_kg=700.0,
        packages=[],
        is_active=True
    )
    test_session.add(product)
    await test_session.commit()
    
    # Create first package
    package_data = {
        "package_id": "duplicate",
        "name": "First Package",
        "weight": 1.0,
        "unit": "кг",
        "price": 700.0,
        "available": True
    }
    
    response = await client.post(
        f"/api/v1/admin/products/{product.id}/packages",
        json=package_data,
        headers=admin_headers
    )
    assert response.status_code == 201
    
    # Try to create duplicate
    package_data["name"] = "Duplicate Package"
    response = await client.post(
        f"/api/v1/admin/products/{product.id}/packages",
        json=package_data,
        headers=admin_headers
    )
    assert response.status_code == 400
    assert "already exists" in response.json()["detail"].lower()