from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, JSON
from sqlalchemy.sql import func
import enum

from app.db.session import Base


class SettingType(enum.Enum):
    FLOAT = "float"
    INTEGER = "integer" 
    STRING = "string"
    BOOLEAN = "boolean"
    JSON = "json"


class AdminSetting(Base):
    """Admin configurable settings for business logic"""
    __tablename__ = "admin_settings"
    
    id = Column(Integer, primary_key=True)
    key = Column(String, unique=True, nullable=False, index=True)  # e.g., "price_variance_threshold"
    value = Column(Text, nullable=False)  # Stored as string, parsed based on type
    setting_type = Column(String, nullable=False)  # "float", "integer", "string", "boolean", "json"
    
    # Metadata
    name = Column(String, nullable=False)  # Human-readable name
    description = Column(Text, nullable=True)  # Description for admin UI
    category = Column(String, nullable=True)  # e.g., "order_processing", "notifications"
    
    # Validation
    min_value = Column(Float, nullable=True)  # For numeric settings
    max_value = Column(Float, nullable=True)  # For numeric settings
    allowed_values = Column(JSON, nullable=True)  # For restricted choice settings
    
    # System
    is_system = Column(Boolean, default=False)  # System settings (not user-editable)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    updated_by = Column(String, nullable=True)  # Admin who last updated
    
    def __repr__(self):
        return f"<AdminSetting {self.key}={self.value}>"
    
    def get_typed_value(self):
        """Return value converted to proper type"""
        if self.setting_type == "float":
            return float(self.value)
        elif self.setting_type == "integer":
            return int(self.value)
        elif self.setting_type == "boolean":
            return self.value.lower() in ("true", "1", "yes", "on")
        elif self.setting_type == "json":
            import json
            return json.loads(self.value)
        else:  # string
            return self.value