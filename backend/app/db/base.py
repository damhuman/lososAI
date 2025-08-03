# Import all models here for Alembic to pick them up
from app.db.session import Base  # noqa
from app.db.models.user import User  # noqa
from app.db.models.product import Category, Product, District, PromoCode  # noqa
from app.db.models.order import Order, OrderItem, OrderStatus, DeliveryTimeSlot  # noqa