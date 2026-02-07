"""
Pydantic Schemas
Data models for API requests and responses.
"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime, date
from uuid import UUID
from enum import Enum


# Enums
class StrategyType(str, Enum):
    BEST_SELLER = "BEST_SELLER"
    DEAD_STOCK = "DEAD_STOCK"
    CHURN_RECOVERY = "CHURN_RECOVERY"
    SLOW_DAY = "SLOW_DAY"
    CUSTOM = "CUSTOM"


class CampaignStatus(str, Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    SENT = "SENT"
    FAILED = "FAILED"


# Restaurant
class RestaurantBase(BaseModel):
    name: str
    owner_phone: str


class RestaurantCreate(RestaurantBase):
    pass


class Restaurant(RestaurantBase):
    id: UUID
    whatsapp_phone_id: Optional[str] = None
    inbound_email_address: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


# Customer Records
class RecordBase(BaseModel):
    client_phone: str
    client_name: Optional[str] = None
    source: str = "Dine-In"
    item_ordered: Optional[str] = None
    bill_amount: Optional[float] = None
    visit_date: date


class RecordCreate(RecordBase):
    restaurant_id: UUID


class Record(RecordBase):
    id: UUID
    restaurant_id: UUID
    created_at: datetime

    class Config:
        from_attributes = True


# Campaigns
class CampaignBase(BaseModel):
    strategy_type: StrategyType
    insight_text: Optional[str] = None
    target_audience: Optional[Dict[str, Any]] = None


class CampaignCreate(CampaignBase):
    restaurant_id: UUID
    generated_image_url: Optional[str] = None
    generated_caption: Optional[str] = None
    item_name: Optional[str] = None


class CampaignUpdate(BaseModel):
    generated_image_url: Optional[str] = None
    generated_caption: Optional[str] = None
    status: Optional[CampaignStatus] = None


class Campaign(CampaignBase):
    id: UUID
    restaurant_id: UUID
    generated_image_url: Optional[str] = None
    generated_caption: Optional[str] = None
    status: CampaignStatus = CampaignStatus.PENDING
    approved_at: Optional[datetime] = None
    sent_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True


class CampaignApproval(BaseModel):
    """Request body for approving a campaign."""
    modified_caption: Optional[str] = None
    modified_image_url: Optional[str] = None


class CampaignRegenerate(BaseModel):
    """Request body for regenerating campaign image."""
    manual_prompt: Optional[str] = None


# Analytics
class WeeklyStats(BaseModel):
    new_customers: int = 0
    total_orders: int = 0
    total_revenue: float = 0
    bestseller_item: Optional[str] = None
    slowest_day: Optional[str] = None


class Insight(BaseModel):
    strategy_type: StrategyType
    insight_text: str
    target_data: Dict[str, Any] = Field(default_factory=dict)


# API Responses
class HealthResponse(BaseModel):
    status: str
    app: str
    version: str


class WebhookResponse(BaseModel):
    status: str
    restaurant_id: Optional[str] = None
    records_processed: int = 0
    records_saved: int = 0
    message: Optional[str] = None
