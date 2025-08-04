from typing import List, Optional
from pydantic import BaseModel


class PackageInfo(BaseModel):
    type: str  # Package type like "300g", "1kg", etc.
    weight: float
    unit: str
    price: float
    available: bool


class CategoryBase(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    icon: str
    order: int = 0


class Category(CategoryBase):
    is_active: bool = True
    
    class Config:
        from_attributes = True


class ProductBase(BaseModel):
    id: str
    category_id: str
    name: str
    description: Optional[str] = None
    price_per_kg: float
    image_url: Optional[str] = None
    packages: List[PackageInfo]


class ProductCreate(ProductBase):
    is_active: bool = True
    is_featured: bool = False


class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price_per_kg: Optional[float] = None
    image_url: Optional[str] = None
    packages: Optional[List[PackageInfo]] = None
    is_active: Optional[bool] = None
    is_featured: Optional[bool] = None


class Product(ProductBase):
    is_active: bool
    is_featured: bool
    stock_quantity: Optional[float] = None
    category: Category
    
    class Config:
        from_attributes = True


class ProductList(BaseModel):
    products: List[Product]
    total: int
    page: int
    size: int


class DistrictBase(BaseModel):
    name: str
    delivery_cost: float = 0


class District(DistrictBase):
    id: int
    is_active: bool = True
    
    class Config:
        from_attributes = True


class PromoCodeValidation(BaseModel):
    code: str


class PromoCodeResponse(BaseModel):
    valid: bool
    discount_percent: float = 0
    discount_amount: float = 0
    is_gold_code: bool = False
    message: Optional[str] = None