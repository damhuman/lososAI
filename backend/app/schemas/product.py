from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel


class PackageInfo(BaseModel):
    id: Optional[str] = None  # Package ID
    type: Optional[str] = None  # Package type like "300g", "1kg", etc.
    weight: float
    unit: str
    price: Optional[float] = None
    available: bool
    note: Optional[str] = None
    
    def __init__(self, **data):
        # If id is missing but type exists, use type as id
        if 'id' not in data and 'type' in data:
            data['id'] = data['type']
        super().__init__(**data)


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
    packages: Optional[List[PackageInfo]] = []


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


# ProductPackage schemas
class ProductPackageBase(BaseModel):
    package_id: str
    name: str
    weight: float
    unit: str
    price: float
    image_url: Optional[str] = None
    available: bool = True
    sort_order: int = 0
    note: Optional[str] = None


class ProductPackageCreate(ProductPackageBase):
    product_id: str


class ProductPackageUpdate(BaseModel):
    name: Optional[str] = None
    weight: Optional[float] = None
    unit: Optional[str] = None
    price: Optional[float] = None
    image_url: Optional[str] = None
    available: Optional[bool] = None
    sort_order: Optional[int] = None
    note: Optional[str] = None


class ProductPackage(ProductPackageBase):
    id: int
    product_id: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class ProductWithPackages(Product):
    product_packages: List[ProductPackage] = []
    
    class Config:
        from_attributes = True