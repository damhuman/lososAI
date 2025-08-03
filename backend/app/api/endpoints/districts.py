from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.api.deps import get_async_session
from app.db.models.product import District
from app.schemas.product import District as DistrictSchema

router = APIRouter()


@router.get("/", response_model=List[DistrictSchema])
async def get_districts(
    session: AsyncSession = Depends(get_async_session)
):
    """Get all active delivery districts"""
    query = select(District).where(District.is_active == True).order_by(District.name)
    result = await session.execute(query)
    districts = result.scalars().all()
    return districts