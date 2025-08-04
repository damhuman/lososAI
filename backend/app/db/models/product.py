from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship

from app.db.session import Base


class Category(Base):
    __tablename__ = "categories"
    
    id = Column(String, primary_key=True)  # e.g., "salmon", "shellfish"
    name = Column(String, nullable=False)
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
    
    # Available packages as JSON
    # Format: [{"id": "1kg", "weight": 1, "unit": "кг", "available": true}]
    packages = Column(JSON, nullable=False, default=list)
    
    # Status
    is_active = Column(Boolean, default=True)
    is_featured = Column(Boolean, default=False)
    
    # Stock management (optional)
    stock_quantity = Column(Float, nullable=True)  # in kg
    
    # Relationships
    category = relationship("Category", back_populates="products")
    # order_items = relationship("OrderItem", back_populates="product")  # Disabled to avoid circular import
    
    def __repr__(self):
        return f"<Product {self.id}: {self.name}>"


class District(Base):
    __tablename__ = "districts"
    
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, unique=True)
    is_active = Column(Boolean, default=True)
    delivery_cost = Column(Float, default=0)  # Additional delivery cost if any
    
    # Relationships
    # orders = relationship("Order", back_populates="district")  # Disabled to avoid circular import
    
    def __repr__(self):
        return f"<District {self.id}: {self.name}>"


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