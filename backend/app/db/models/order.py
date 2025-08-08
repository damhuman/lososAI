from sqlalchemy import Column, Integer, BigInteger, String, Float, DateTime, ForeignKey, Text, Enum as SQLEnum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum

from app.db.session import Base


class OrderStatus(enum.Enum):
    PENDING = "pending"
    VERIFICATION = "verification"      # Manager is verifying weights
    WEIGHING = "weighing"             # Manager is weighing items  
    PRICE_CALCULATED = "price_calculated"  # System calculated new price
    AUTO_CONFIRMED = "auto_confirmed"  # Auto-confirmed (< threshold)
    MANUAL_CONFIRM = "manual_confirm"  # Requires manual confirmation (> threshold)
    CONFIRMED = "confirmed"
    PREPARING = "preparing"
    DELIVERING = "delivering"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"


class DeliveryTimeSlot(enum.Enum):
    MORNING = "morning"      # 8:00-12:00
    AFTERNOON = "afternoon"  # 12:00-16:00
    EVENING = "evening"      # 16:00-20:00


class Order(Base):
    __tablename__ = "orders"
    
    id = Column(Integer, primary_key=True)
    order_id = Column(Integer, unique=True, nullable=False)
    user_id = Column(BigInteger, ForeignKey("users.id"), nullable=False)
    
    # Order details
    status = Column(SQLEnum(OrderStatus), default=OrderStatus.PENDING)
    total_amount = Column(Float, nullable=False)
    promo_code_used = Column(String, nullable=True)
    discount_amount = Column(Float, default=0)
    
    # Verification details (for enhanced admin flow)
    expected_total = Column(Float, nullable=True)  # Original expected total
    actual_total = Column(Float, nullable=True)    # Total after verification
    price_variance_percent = Column(Float, nullable=True)  # Calculated variance %
    auto_confirmed = Column(String, nullable=True)  # "yes" if auto-confirmed
    verified_at = Column(DateTime(timezone=True), nullable=True)  # When verification completed
    verified_by = Column(String, nullable=True)  # Manager who verified
    
    # Delivery information
    district_id = Column(Integer, ForeignKey("districts.id"), nullable=False)
    delivery_time_slot = Column(SQLEnum(DeliveryTimeSlot), nullable=False)
    delivery_date = Column(DateTime(timezone=True), nullable=False)
    delivery_address = Column(Text, nullable=True)
    comment = Column(Text, nullable=True)
    
    # Contact info (cached from user at order time)
    contact_name = Column(String, nullable=False)
    contact_phone = Column(String, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="orders")
    district = relationship("District")  # Temporarily removed back_populates
    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Order #{self.order_id}: User {self.user_id}, Status {self.status.value}>"


class OrderItem(Base):
    __tablename__ = "order_items"
    
    id = Column(Integer, primary_key=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    product_id = Column(String, ForeignKey("products.id"), nullable=False)
    
    # Item details (expected/ordered)
    product_name = Column(String, nullable=False)  # Cached at order time
    package_id = Column(String, nullable=False)    # e.g., "1kg"
    weight = Column(Float, nullable=False)         # Expected weight
    unit = Column(String, nullable=False)          # e.g., "кг", "пласт"
    quantity = Column(Integer, nullable=False)     # Expected quantity
    price_per_unit = Column(Float, nullable=False) # Price at order time
    total_price = Column(Float, nullable=False)    # Expected total price
    
    # Verification details (actual measurements)
    actual_weight = Column(Float, nullable=True)   # Manager-verified weight
    actual_quantity = Column(Integer, nullable=True)  # Manager-verified quantity
    actual_price_per_unit = Column(Float, nullable=True)  # Recalculated price per unit
    actual_total_price = Column(Float, nullable=True)  # Recalculated total
    weight_variance_percent = Column(Float, nullable=True)  # Weight difference %
    price_variance_percent = Column(Float, nullable=True)   # Price difference %
    
    # Relationships
    order = relationship("Order", back_populates="items")
    product = relationship("Product")  # Temporarily removed back_populates
    
    def __repr__(self):
        return f"<OrderItem: {self.product_name} x{self.quantity}>"