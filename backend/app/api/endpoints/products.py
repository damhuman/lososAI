from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.api.deps import get_async_session
from app.db.models.product import Product
from app.schemas.product import Product as ProductSchema

router = APIRouter()


@router.get("/", response_model=List[ProductSchema])
async def get_products(
    category_id: Optional[str] = Query(None, description="Filter by category ID"),
    featured: Optional[bool] = Query(None, description="Filter by featured products"),
    session: AsyncSession = Depends(get_async_session)
):
    """Get all active products with optional filtering"""
    query = (
        select(Product)
        .options(selectinload(Product.category))
        .where(Product.is_active == True)
    )
    
    # Apply filters
    if category_id:
        query = query.where(Product.category_id == category_id)
    
    if featured is not None:
        query = query.where(Product.is_featured == featured)
    
    # Order by featured first, then by name
    query = query.order_by(Product.is_featured.desc(), Product.name)
    
    result = await session.execute(query)
    products = result.scalars().all()
    return products


@router.get("/featured", response_model=List[ProductSchema])
async def get_featured_products(
    session: AsyncSession = Depends(get_async_session)
):
    """Get all featured products"""
    query = (
        select(Product)
        .options(selectinload(Product.category))
        .where(
            Product.is_active == True,
            Product.is_featured == True
        )
        .order_by(Product.name)
    )
    
    result = await session.execute(query)
    products = result.scalars().all()
    return products


@router.get("/{product_id}", response_model=ProductSchema)
async def get_product(
    product_id: str,
    session: AsyncSession = Depends(get_async_session)
):
    """Get product details by ID"""
    query = (
        select(Product)
        .options(selectinload(Product.category))
        .where(
            Product.id == product_id,
            Product.is_active == True
        )
    )
    
    result = await session.execute(query)
    product = result.scalar_one_or_none()
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    return product