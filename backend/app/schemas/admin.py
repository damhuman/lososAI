from typing import List, Optional, Generic, TypeVar, Any
from pydantic import BaseModel, validator, field_validator
from datetime import datetime
import html
import re

T = TypeVar('T')

# Authentication schemas
class AdminLogin(BaseModel):
    username: str
    password: str

class AdminUserResponse(BaseModel):
    id: int
    username: str
    email: str
    is_active: bool
    created_at: datetime
    last_login: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int

class LoginResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    admin: AdminUserResponse

class TokenRefresh(BaseModel):
    refresh_token: str

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
    
    @field_validator('name', 'description')
    @classmethod
    def sanitize_text(cls, v):
        if v is None:
            return v
        # Remove HTML tags and escape remaining content
        v = re.sub(r'<[^>]*>', '', v)  # Remove HTML tags
        v = html.escape(v)  # Escape remaining special chars
        return v.strip()

class CategoryUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    icon: Optional[str] = None
    order: Optional[int] = None
    is_active: Optional[bool] = None
    
    @field_validator('name', 'description')
    @classmethod
    def sanitize_text(cls, v):
        if v is None:
            return v
        # Remove HTML tags and escape remaining content
        v = re.sub(r'<[^>]*>', '', v)  # Remove HTML tags
        v = html.escape(v)  # Escape remaining special chars
        return v.strip()

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
    packages: Optional[List[PackageInfo]] = []
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
    packages: List[PackageInfo]  # Keep for backward compatibility
    # product_packages: List['ProductPackageResponse'] = []  # New relational packages - temporarily disabled
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

# Update the ProductResponse to properly reference CategoryResponse and ProductPackageResponse
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


# Product Package schemas
class ProductPackageCreate(BaseModel):
    package_id: str
    name: str
    weight: float
    unit: str
    price: float
    available: bool = True
    sort_order: int = 0
    note: Optional[str] = None
    
    @validator('weight')
    def weight_must_be_positive(cls, v):
        if v <= 0:
            raise ValueError('Weight must be positive')
        return v
    
    @validator('price')
    def price_must_be_positive(cls, v):
        if v <= 0:
            raise ValueError('Price must be positive')
        return v
    
    @validator('package_id')
    def package_id_must_not_be_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('Package ID cannot be empty')
        return v.strip()
    
    @validator('name')
    def name_must_not_be_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('Name cannot be empty')
        return v.strip()


class ProductPackageUpdate(BaseModel):
    name: Optional[str] = None
    weight: Optional[float] = None
    unit: Optional[str] = None
    price: Optional[float] = None
    image_url: Optional[str] = None
    available: Optional[bool] = None
    sort_order: Optional[int] = None
    note: Optional[str] = None
    
    @validator('weight')
    def weight_must_be_positive(cls, v):
        if v is not None and v <= 0:
            raise ValueError('Weight must be positive')
        return v
    
    @validator('price')
    def price_must_be_positive(cls, v):
        if v is not None and v <= 0:
            raise ValueError('Price must be positive')
        return v
    
    @validator('name')
    def name_must_not_be_empty(cls, v):
        if v is not None and (not v or not v.strip()):
            raise ValueError('Name cannot be empty')
        return v.strip() if v else None


class ProductPackageResponse(BaseModel):
    id: int
    product_id: str
    package_id: str
    name: str
    weight: float
    unit: str
    price: float
    image_url: Optional[str] = None
    available: bool
    sort_order: int
    note: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True