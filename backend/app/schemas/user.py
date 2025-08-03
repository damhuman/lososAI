from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel

from app.schemas.order import OrderSummary


class UserBase(BaseModel):
    first_name: str
    last_name: Optional[str] = None
    username: Optional[str] = None
    language_code: str = "uk"


class UserCreate(UserBase):
    id: int  # Telegram user ID


class UserUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    username: Optional[str] = None
    language_code: Optional[str] = None
    phone: Optional[str] = None
    is_gold_client: Optional[bool] = None
    is_blocked: Optional[bool] = None


class User(UserBase):
    id: int
    phone: Optional[str] = None
    is_gold_client: bool = False
    is_blocked: bool = False
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class UserWithOrders(User):
    orders: List[OrderSummary] = []


class TelegramInitData(BaseModel):
    """For parsing Telegram Web App init data"""
    user: dict
    auth_date: int
    query_id: Optional[str] = None
    start_param: Optional[str] = None