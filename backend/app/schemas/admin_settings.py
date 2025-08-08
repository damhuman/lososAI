from typing import Optional, Any, List
from datetime import datetime
from pydantic import BaseModel, field_validator
import json


class AdminSettingCreate(BaseModel):
    key: str
    value: str
    setting_type: str  # "float", "integer", "string", "boolean", "json"
    name: str
    description: Optional[str] = None
    category: Optional[str] = None
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    allowed_values: Optional[List[Any]] = None
    is_system: bool = False
    
    @field_validator('setting_type')
    def validate_setting_type(cls, v):
        allowed_types = ["float", "integer", "string", "boolean", "json"]
        if v not in allowed_types:
            raise ValueError(f'setting_type must be one of: {allowed_types}')
        return v


class AdminSettingUpdate(BaseModel):
    value: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    allowed_values: Optional[List[Any]] = None


class AdminSetting(BaseModel):
    id: int
    key: str
    value: str
    setting_type: str
    name: str
    description: Optional[str] = None
    category: Optional[str] = None
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    allowed_values: Optional[List[Any]] = None
    is_system: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    updated_by: Optional[str] = None
    
    class Config:
        from_attributes = True
    
    def get_typed_value(self) -> Any:
        """Return value converted to proper type"""
        if self.setting_type == "float":
            return float(self.value)
        elif self.setting_type == "integer":
            return int(self.value)
        elif self.setting_type == "boolean":
            return self.value.lower() in ("true", "1", "yes", "on")
        elif self.setting_type == "json":
            return json.loads(self.value)
        else:  # string
            return self.value


class AdminSettingResponse(AdminSetting):
    """Response model with typed value included"""
    typed_value: Any
    
    @classmethod
    def from_setting(cls, setting: AdminSetting):
        return cls(
            **setting.model_dump(),
            typed_value=setting.get_typed_value()
        )


# Predefined settings for order management
DEFAULT_ADMIN_SETTINGS = [
    {
        "key": "price_variance_threshold",
        "value": "10.0",
        "setting_type": "float",
        "name": "Price Variance Threshold (%)",
        "description": "Orders with price differences below this percentage will be auto-confirmed",
        "category": "order_processing",
        "min_value": 0.0,
        "max_value": 100.0,
        "is_system": False
    },
    {
        "key": "auto_confirmation_enabled", 
        "value": "true",
        "setting_type": "boolean",
        "name": "Auto-confirmation Enabled",
        "description": "Enable automatic confirmation of orders within threshold",
        "category": "order_processing",
        "is_system": False
    },
    {
        "key": "notification_sound_enabled",
        "value": "true", 
        "setting_type": "boolean",
        "name": "Notification Sounds",
        "description": "Play sound alerts for new orders",
        "category": "notifications",
        "is_system": False
    },
    {
        "key": "feedback_delay_hours",
        "value": "24",
        "setting_type": "integer", 
        "name": "Feedback Request Delay (Hours)",
        "description": "Hours to wait after delivery before requesting customer feedback",
        "category": "customer_feedback",
        "min_value": 1,
        "max_value": 168,  # 1 week
        "is_system": False
    },
    {
        "key": "websocket_enabled",
        "value": "true",
        "setting_type": "boolean",
        "name": "Real-time Notifications",
        "description": "Enable WebSocket real-time notifications to admin panel",
        "category": "notifications", 
        "is_system": False
    }
]