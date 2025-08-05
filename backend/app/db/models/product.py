from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, Text, JSON, DateTime, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.session import Base


class Category(Base):
    __tablename__ = "categories"
    
    id = Column(String, primary_key=True)  # e.g., "salmon", "shellfish"
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)  # Category description
    icon = Column(String, nullable=False)  # emoji
    order = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    
    # Relationships
    products = relationship("Product", back_populates="category")
    
    def __repr__(self):
        return f"<Category {self.id}: {self.name}>"


class Product(Base):
    __tablename__ = "products"
    
    id = Column(String, primary_key=True)  # e.g., "salmon_smoked_001"
    category_id = Column(String, ForeignKey("categories.id"), nullable=False)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    price_per_kg = Column(Float, nullable=False)
    image_url = Column(String, nullable=True)
    
    # Available packages as JSON (DEPRECATED - use ProductPackage model instead)
    # Format: [{"id": "1kg", "weight": 1, "unit": "кг", "available": true}]
    packages = Column(JSON, nullable=True, default=list)
    
    # Status
    is_active = Column(Boolean, default=True)
    is_featured = Column(Boolean, default=False)
    
    # Stock management (optional)
    stock_quantity = Column(Float, nullable=True)  # in kg
    
    # Relationships
    category = relationship("Category", back_populates="products")
    product_packages = relationship("ProductPackage", back_populates="product", cascade="all, delete-orphan", order_by="ProductPackage.sort_order")
    # order_items = relationship("OrderItem", back_populates="product")  # Temporarily disabled
    
    def __repr__(self):
        return f"<Product {self.id}: {self.name}>"


class District(Base):
    __tablename__ = "districts"
    
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, unique=True)
    is_active = Column(Boolean, default=True)
    delivery_cost = Column(Float, default=0)  # Additional delivery cost if any
    
    # Relationships - using string reference to avoid circular import
    # orders = relationship("Order", back_populates="district")  # Temporarily disabled
    
    def __repr__(self):
        return f"<District {self.id}: {self.name}>"


class ProductPackage(Base):
    __tablename__ = "product_packages"
    
    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(String, ForeignKey("products.id", ondelete="CASCADE"), nullable=False, index=True)
    package_id = Column(String, nullable=False, index=True)  # e.g., "300g", "1kg"
    name = Column(String, nullable=False)  # Display name e.g., "300 грам"
    weight = Column(Float, nullable=False)
    unit = Column(String, nullable=False)  # "г", "кг", "шт", "набір"
    price = Column(Float, nullable=False)
    image_url = Column(String, nullable=True)
    available = Column(Boolean, default=True)
    sort_order = Column(Integer, default=0)
    note = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    product = relationship("Product", back_populates="product_packages")
    
    def __repr__(self):
        return f"<ProductPackage {self.product_id}:{self.package_id}>"
    
    __table_args__ = (
        UniqueConstraint('product_id', 'package_id', name='uq_product_package_id'),
    )


class PromoCode(Base):
    __tablename__ = "promo_codes"
    
    id = Column(Integer, primary_key=True)
    code = Column(String, unique=True, nullable=False, index=True)
    discount_percent = Column(Float, default=0)  # Percentage discount
    discount_amount = Column(Float, default=0)   # Fixed amount discount
    is_active = Column(Boolean, default=True)
    usage_limit = Column(Integer, nullable=True)  # None = unlimited
    usage_count = Column(Integer, default=0)
    
    # For Gold clients identification
    is_gold_code = Column(Boolean, default=False)
    
    def __repr__(self):
        return f"<PromoCode {self.code}>"