from typing import List, Optional, Generic, TypeVar, Any
from pydantic import BaseModel
from datetime import datetime

T = TypeVar('T')

# Authentication schemas
class AdminLogin(BaseModel):
    username: str
    password: str

class AdminUserResponse(BaseModel):
    username: str
    token: str

# Generic response schemas
class PaginatedResponse(BaseModel, Generic[T]):
    items: List[T]
    total: int
    page: int
    size: int

class ImageUploadResponse(BaseModel):
    url: str

# Category schemas
class CategoryCreate(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    icon: str
    order: int = 0
    is_active: bool = True

class CategoryUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    icon: Optional[str] = None
    order: Optional[int] = None
    is_active: Optional[bool] = None

# Product schemas  
class PackageInfo(BaseModel):
    id: Optional[str] = None  # Make optional for backward compatibility
    type: Optional[str] = None  # Alternative to id field
    weight: float
    unit: str
    price: Optional[float] = None  # Allow price field from database
    available: bool
    note: Optional[str] = None

class ProductCreate(BaseModel):
    id: str
    category_id: str
    name: str
    description: Optional[str] = None
    price_per_kg: float
    image_url: Optional[str] = None
    packages: List[PackageInfo]
    is_active: bool = True
    is_featured: bool = False
    stock_quantity: Optional[float] = None

class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price_per_kg: Optional[float] = None
    image_url: Optional[str] = None
    packages: Optional[List[PackageInfo]] = None
    is_active: Optional[bool] = None
    is_featured: Optional[bool] = None
    stock_quantity: Optional[float] = None

# Admin Product Response Schema
class ProductResponse(BaseModel):
    id: str
    category_id: str
    name: str
    description: Optional[str] = None
    price_per_kg: float
    image_url: Optional[str] = None
    packages: List[PackageInfo]
    is_active: bool
    is_featured: bool
    stock_quantity: Optional[float] = None
    category: Optional['CategoryResponse'] = None
    
    class Config:
        from_attributes = True

# Forward reference for category
class CategoryResponse(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    icon: str
    order: int = 0
    is_active: bool = True
    
    class Config:
        from_attributes = True

# Update the ProductResponse to properly reference CategoryResponse
ProductResponse.model_rebuild()

# User schemas
class UserResponse(BaseModel):
    id: int
    first_name: str
    last_name: Optional[str] = None
    username: Optional[str] = None
    language_code: str = "uk"
    is_bot: bool = False
    is_premium: bool = False
    is_gold_client: bool = False
    is_blocked: bool = False
    created_at: datetime
    
    class Config:
        from_attributes = True

class UserUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    username: Optional[str] = None
    language_code: Optional[str] = None
    is_gold_client: Optional[bool] = None
    is_blocked: Optional[bool] = None

class UserStats(BaseModel):
    total: int
    active: int
    gold_clients: int
    blocked: int

# Order schemas
class OrderItemResponse(BaseModel):
    id: int
    order_id: int
    product_id: str
    product_name: str
    package_id: str
    weight: float
    unit: str
    quantity: int
    price_per_unit: float
    total_price: float
    
    class Config:
        from_attributes = True

class OrderResponse(BaseModel):
    id: int
    order_id: int
    user_id: int
    status: str
    total_amount: float
    promo_code_used: Optional[str] = None
    discount_amount: float = 0
    district_id: int
    delivery_time_slot: str
    delivery_date: datetime
    delivery_address: Optional[str] = None
    comment: Optional[str] = None
    contact_name: str
    contact_phone: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    items: List[OrderItemResponse] = []
    user: Optional[UserResponse] = None
    
    class Config:
        from_attributes = True

class OrderStatusUpdate(BaseModel):
    status: str

class OrderStats(BaseModel):
    total_orders: int
    total_revenue: float
    avg_order_value: float
    orders_by_status: dict

# District schemas
class DistrictCreate(BaseModel):
    name: str
    is_active: bool = True
    delivery_cost: float = 0

class DistrictUpdate(BaseModel):
    name: Optional[str] = None
    is_active: Optional[bool] = None
    delivery_cost: Optional[float] = None

class DistrictResponse(BaseModel):
    id: int
    name: str
    is_active: bool
    delivery_cost: float
    
    class Config:
        from_attributes = True

# Promo code schemas
class PromoCodeCreate(BaseModel):
    code: str
    discount_percent: Optional[float] = None
    discount_amount: Optional[float] = None
    is_active: bool = True
    usage_limit: Optional[int] = None
    is_gold_code: bool = False

class PromoCodeUpdate(BaseModel):
    code: Optional[str] = None
    discount_percent: Optional[float] = None
    discount_amount: Optional[float] = None
    is_active: Optional[bool] = None
    usage_limit: Optional[int] = None
    is_gold_code: Optional[bool] = None

class PromoCodeResponse(BaseModel):
    id: int
    code: str
    discount_percent: float
    discount_amount: float
    is_active: bool
    usage_limit: Optional[int] = None
    usage_count: int
    is_gold_code: bool
    
    class Config:
        from_attributes = True