from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, field_validator

from app.db.models.order import OrderStatus, DeliveryTimeSlot


class OrderItemCreate(BaseModel):
    product_id: str
    product_name: str
    package_id: str
    weight: float
    unit: str
    quantity: int
    price_per_unit: float
    total_price: float


class OrderItem(OrderItemCreate):
    id: int
    order_id: int
    
    # Verification fields (nullable for existing orders)
    actual_weight: Optional[float] = None
    actual_quantity: Optional[int] = None
    actual_price_per_unit: Optional[float] = None
    actual_total_price: Optional[float] = None
    weight_variance_percent: Optional[float] = None
    price_variance_percent: Optional[float] = None
    
    class Config:
        from_attributes = True


class OrderCreate(BaseModel):
    user_id: int
    user_name: str
    items: List[OrderItemCreate]
    delivery: dict  # Contains district, time_slot, comment
    promo_code: Optional[str] = None
    total: float
    
    @field_validator('items')
    def validate_items(cls, v):
        if not v:
            raise ValueError('Order must contain at least one item')
        return v


class OrderUpdate(BaseModel):
    status: Optional[OrderStatus] = None
    delivery_address: Optional[str] = None
    contact_phone: Optional[str] = None


class Order(BaseModel):
    id: int
    order_id: int
    user_id: int
    status: OrderStatus
    total_amount: float
    promo_code_used: Optional[str] = None
    discount_amount: float
    
    # Verification fields (for enhanced admin flow)
    expected_total: Optional[float] = None
    actual_total: Optional[float] = None
    price_variance_percent: Optional[float] = None
    auto_confirmed: Optional[str] = None
    verified_at: Optional[datetime] = None
    verified_by: Optional[str] = None
    
    # Delivery info  
    district_id: int
    delivery_time_slot: DeliveryTimeSlot
    delivery_date: datetime
    delivery_address: Optional[str] = None
    comment: Optional[str] = None
    
    # Contact
    contact_name: str
    contact_phone: Optional[str] = None
    
    # Timestamps
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    # Items
    items: List[OrderItem]
    
    class Config:
        from_attributes = True


class OrderList(BaseModel):
    orders: List[Order]
    total: int
    page: int
    size: int


class OrderSummary(BaseModel):
    """Simplified order for list views"""
    id: int
    order_id: int
    user_id: int
    status: OrderStatus
    total_amount: float
    delivery_date: datetime
    contact_name: str
    created_at: datetime
    items_count: int
    
    class Config:
        from_attributes = True