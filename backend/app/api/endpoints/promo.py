from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.api.deps import get_async_session
from app.db.models.product import PromoCode
from app.schemas.product import PromoCodeValidation, PromoCodeResponse

router = APIRouter()


@router.post("/validate", response_model=PromoCodeResponse)
async def validate_promo_code(
    promo_data: PromoCodeValidation,
    session: AsyncSession = Depends(get_async_session)
):
    """Validate a promo code"""
    query = select(PromoCode).where(
        PromoCode.code == promo_data.code,
        PromoCode.is_active == True
    )
    
    result = await session.execute(query)
    promo = result.scalar_one_or_none()
    
    if not promo:
        return PromoCodeResponse(
            valid=False,
            message="Промокод не знайдено"
        )
    
    # Check usage limit
    if promo.usage_limit and promo.usage_count >= promo.usage_limit:
        return PromoCodeResponse(
            valid=False,
            message="Ліміт використання промокоду вичерпано"
        )
    
    return PromoCodeResponse(
        valid=True,
        discount_percent=promo.discount_percent,
        discount_amount=promo.discount_amount,
        is_gold_code=promo.is_gold_code,
        message="Gold клієнт!" if promo.is_gold_code else "Промокод дійсний"
    )