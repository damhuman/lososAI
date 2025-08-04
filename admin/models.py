from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, Text, JSON, DateTime, BigInteger, Enum as SQLEnum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum

Base = declarative_base()

# Enums
class OrderStatus(enum.Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    PREPARING = "preparing"
    DELIVERING = "delivering"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"

class DeliveryTimeSlot(enum.Enum):
    MORNING = "morning"
    AFTERNOON = "afternoon"
    EVENING = "evening"

# Models
class Category(Base):
    __tablename__ = "categories"
    
    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    icon = Column(String, nullable=False)
    order = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    
    def __repr__(self):
        return f"<Category {self.id}: {self.name}>"

class Product(Base):
    __tablename__ = "products"
    
    id = Column(String, primary_key=True)
    category_id = Column(String, ForeignKey("categories.id"), nullable=False)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    price_per_kg = Column(Float, nullable=False)
    image_url = Column(String, nullable=True)
    packages = Column(JSON, nullable=False, default=list)
    is_active = Column(Boolean, default=True)
    is_featured = Column(Boolean, default=False)
    stock_quantity = Column(Float, nullable=True)
    
    def __repr__(self):
        return f"<Product {self.id}: {self.name}>"

class District(Base):
    __tablename__ = "districts"
    
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, unique=True)
    is_active = Column(Boolean, default=True)
    delivery_cost = Column(Float, default=0)
    
    def __repr__(self):
        return f"<District {self.id}: {self.name}>"

class PromoCode(Base):
    __tablename__ = "promo_codes"
    
    id = Column(Integer, primary_key=True)
    code = Column(String, unique=True, nullable=False, index=True)
    discount_percent = Column(Float, default=0)
    discount_amount = Column(Float, default=0)
    is_active = Column(Boolean, default=True)
    usage_limit = Column(Integer, nullable=True)
    usage_count = Column(Integer, default=0)
    is_gold_code = Column(Boolean, default=False)
    
    def __repr__(self):
        return f"<PromoCode {self.code}>"

class User(Base):
    __tablename__ = "users"
    
    id = Column(BigInteger, primary_key=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=True)
    username = Column(String, nullable=True)
    language_code = Column(String, default="uk")
    is_bot = Column(Boolean, default=False)
    is_premium = Column(Boolean, default=False)
    is_gold_client = Column(Boolean, default=False)
    is_blocked = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    def __repr__(self):
        return f"<User {self.id}: {self.first_name}>"

class Order(Base):
    __tablename__ = "orders"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(BigInteger, ForeignKey("users.id"), nullable=False)
    status = Column(SQLEnum(OrderStatus), default=OrderStatus.PENDING)
    total_amount = Column(Float, nullable=False)
    promo_code_used = Column(String, nullable=True)
    discount_amount = Column(Float, default=0)
    district_id = Column(Integer, ForeignKey("districts.id"), nullable=False)
    delivery_time_slot = Column(SQLEnum(DeliveryTimeSlot), nullable=False)
    delivery_date = Column(DateTime(timezone=True), nullable=False)
    delivery_address = Column(Text, nullable=True)
    comment = Column(Text, nullable=True)
    contact_name = Column(String, nullable=False)
    contact_phone = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<Order {self.id}: {self.contact_name}>"

class OrderItem(Base):
    __tablename__ = "order_items"
    
    id = Column(Integer, primary_key=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    product_id = Column(String, ForeignKey("products.id"), nullable=False)
    product_name = Column(String, nullable=False)
    package_id = Column(String, nullable=False)
    weight = Column(Float, nullable=False)
    unit = Column(String, nullable=False)
    quantity = Column(Integer, nullable=False)
    price_per_unit = Column(Float, nullable=False)
    total_price = Column(Float, nullable=False)
    
    def __repr__(self):
        return f"<OrderItem: {self.product_name} x{self.quantity}>"