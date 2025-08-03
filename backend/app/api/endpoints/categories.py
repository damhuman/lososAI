from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.api.deps import get_async_session
from app.db.models.product import Category, Product
from app.schemas.product import Category as CategorySchema, Product as ProductSchema

router = APIRouter()


@router.get("/", response_model=List[CategorySchema])
async def get_categories(
    session: AsyncSession = Depends(get_async_session)
):
    """Get all active categories"""
    query = select(Category).where(Category.is_active == True).order_by(Category.order)
    result = await session.execute(query)
    categories = result.scalars().all()
    return categories


@router.get("/{category_id}/products", response_model=List[ProductSchema])
async def get_category_products(
    category_id: str,
    session: AsyncSession = Depends(get_async_session)
):
    """Get all active products in a category"""
    # First check if category exists
    category_result = await session.execute(
        select(Category).where(
            Category.id == category_id,
            Category.is_active == True
        )
    )
    category = category_result.scalar_one_or_none()
    
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )
    
    # Get products
    query = (
        select(Product)
        .options(selectinload(Product.category))
        .where(
            Product.category_id == category_id,
            Product.is_active == True
        )
        .order_by(Product.is_featured.desc(), Product.name)
    )
    
    result = await session.execute(query)
    products = result.scalars().all()
    
    return products