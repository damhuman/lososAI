from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from sqlalchemy.orm import selectinload

from app.api.deps import get_async_session
from app.db.models.product import ProductPackage, Product
from app.schemas.product import (
    ProductPackage as ProductPackageSchema,
    ProductPackageCreate,
    ProductPackageUpdate,
)

router = APIRouter()


@router.get("/product/{product_id}", response_model=List[ProductPackageSchema])
async def get_product_packages(
    product_id: str,
    session: AsyncSession = Depends(get_async_session)
):
    """Get all packages for a specific product"""
    # First, verify the product exists
    product_query = select(Product).where(Product.id == product_id)
    product_result = await session.execute(product_query)
    product = product_result.scalar_one_or_none()
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    # Get packages for the product
    packages_query = (
        select(ProductPackage)
        .where(ProductPackage.product_id == product_id)
        .order_by(ProductPackage.sort_order, ProductPackage.package_id)
    )
    
    result = await session.execute(packages_query)
    packages = result.scalars().all()
    return packages


@router.get("/{package_id}", response_model=ProductPackageSchema)
async def get_package(
    package_id: int,
    session: AsyncSession = Depends(get_async_session)
):
    """Get a specific package by ID"""
    query = select(ProductPackage).where(ProductPackage.id == package_id)
    result = await session.execute(query)
    package = result.scalar_one_or_none()
    
    if not package:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Package not found"
        )
    
    return package


@router.post("/", response_model=ProductPackageSchema)
async def create_package(
    package_data: ProductPackageCreate,
    session: AsyncSession = Depends(get_async_session)
):
    """Create a new package for a product"""
    # Verify the product exists
    product_query = select(Product).where(Product.id == package_data.product_id)
    product_result = await session.execute(product_query)
    product = product_result.scalar_one_or_none()
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    # Check if package_id already exists for this product
    existing_query = select(ProductPackage).where(
        ProductPackage.product_id == package_data.product_id,
        ProductPackage.package_id == package_data.package_id
    )
    existing_result = await session.execute(existing_query)
    existing_package = existing_result.scalar_one_or_none()
    
    if existing_package:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Package with ID '{package_data.package_id}' already exists for this product"
        )
    
    # Create new package
    new_package = ProductPackage(**package_data.model_dump())
    session.add(new_package)
    await session.commit()
    await session.refresh(new_package)
    
    return new_package


@router.put("/{package_id}", response_model=ProductPackageSchema)
async def update_package(
    package_id: int,
    package_data: ProductPackageUpdate,
    session: AsyncSession = Depends(get_async_session)
):
    """Update a package"""
    query = select(ProductPackage).where(ProductPackage.id == package_id)
    result = await session.execute(query)
    package = result.scalar_one_or_none()
    
    if not package:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Package not found"
        )
    
    # Update package fields
    update_data = package_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(package, field, value)
    
    await session.commit()
    await session.refresh(package)
    
    return package


@router.delete("/{package_id}")
async def delete_package(
    package_id: int,
    session: AsyncSession = Depends(get_async_session)
):
    """Delete a package"""
    query = select(ProductPackage).where(ProductPackage.id == package_id)
    result = await session.execute(query)
    package = result.scalar_one_or_none()
    
    if not package:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Package not found"
        )
    
    await session.delete(package)
    await session.commit()
    
    return {"message": "Package deleted successfully"}


@router.post("/{package_id}/upload-image")
async def upload_package_image(
    package_id: int,
    # Note: Image upload functionality would typically use File upload
    # For now, this is a placeholder that would accept image_url in request body
    session: AsyncSession = Depends(get_async_session)
):
    """Upload image for a package (placeholder endpoint)"""
    # This endpoint would handle image upload to S3/DigitalOcean Spaces
    # and update the package's image_url
    
    query = select(ProductPackage).where(ProductPackage.id == package_id)
    result = await session.execute(query)
    package = result.scalar_one_or_none()
    
    if not package:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Package not found"
        )
    
    # TODO: Implement actual image upload logic
    # For now, return placeholder response
    return {
        "message": "Image upload endpoint - to be implemented with actual file upload logic",
        "package_id": package_id
    }