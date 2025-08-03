from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.api.deps import get_async_session
from app.db.models.product import Product
from app.schemas.product import Product as ProductSchema

router = APIRouter()


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