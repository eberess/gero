from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, Enum as SAEnum
from sqlalchemy.orm import declarative_base
from datetime import datetime
from pydantic import BaseModel
from enum import Enum
from typing import List, Optional

Base = declarative_base()


class CampaignStatus(str, Enum):
    ACTIVE = "active"
    PAUSED = "paused"
    EXPIRED = "expired"


class BidStrategy(str, Enum):
    CONTEXTUAL = "contextual"
    FLASH = "flash"


class Zone(str, Enum):
    ALL = "all"
    T2F_NORTH = "T2F_North"
    T2F_SOUTH = "T2F_South"
    T2F_CENTRAL = "T2F_Central"
    T2F_SATELLITE = "T2F_Satellite"


class Intent(str, Enum):
    HUNGRY = "hungry"
    THIRSTY = "thirsty"
    BORED = "bored"
    WAITING = "waiting"
    SHOPPING = "shopping"
    SOUVENIR = "souvenir"
    LOST = "lost"
    TIRED = "tired"


class CampaignDB(Base):
    __tablename__ = "campaigns"

    id = Column(Integer, primary_key=True, index=True)
    advertiser = Column(String, nullable=False)
    shop_name = Column(String, nullable=False)
    zone = Column(String, default=Zone.ALL)
    keywords = Column(Text, default="")
    budget_cents = Column(Integer, nullable=False)
    bid_cents = Column(Integer, nullable=False)
    strategy = Column(String, default=BidStrategy.CONTEXTUAL)
    status = Column(String, default=CampaignStatus.ACTIVE)
    daily_max_cents = Column(Integer, default=0)
    starts_at = Column(DateTime, nullable=False)
    ends_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class ImpressionDB(Base):
    __tablename__ = "impressions"

    id = Column(Integer, primary_key=True, index=True)
    campaign_id = Column(Integer, nullable=False)
    intent = Column(String, nullable=False)
    zone = Column(String, nullable=False)
    lang = Column(String, default="fr")
    served_at = Column(DateTime, default=datetime.utcnow)


class ShopDB(Base):
    __tablename__ = "shops"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    zone = Column(String, nullable=False)
    category = Column(String, default="")
    description = Column(Text, default="")
    tags = Column(Text, default="")
    lat = Column(Float, nullable=True)
    lon = Column(Float, nullable=True)
    is_artisan = Column(Boolean, default=False)


class CampaignCreate(BaseModel):
    advertiser: str
    shop_name: str
    zone: Zone = Zone.ALL
    keywords: List[str] = []
    budget_cents: int
    bid_cents: int
    strategy: BidStrategy = BidStrategy.CONTEXTUAL
    daily_max_cents: int = 0
    starts_at: datetime
    ends_at: Optional[datetime] = None


class CampaignOut(BaseModel):
    id: int
    advertiser: str
    shop_name: str
    zone: str
    keywords: str
    budget_cents: int
    bid_cents: int
    strategy: str
    status: str
    daily_max_cents: int
    starts_at: datetime
    ends_at: Optional[datetime]
    created_at: datetime


class RecommendationRequest(BaseModel):
    intent: str
    zone: str
    lang: str = "fr"


class AdRecommendation(BaseModel):
    shop_name: str
    advertiser: str
    tagline: str
    distance_hint: Optional[str] = None
    is_sponsored: bool = False


class RecommendationResponse(BaseModel):
    recommendations: List[AdRecommendation]


class ShopCreate(BaseModel):
    name: str
    zone: Zone
    category: str = ""
    description: str = ""
    tags: List[str] = []
    lat: Optional[float] = None
    lon: Optional[float] = None
    is_artisan: bool = False


class ShopOut(BaseModel):
    id: int
    name: str
    zone: str
    category: str
    description: str
    tags: str
    lat: Optional[float]
    lon: Optional[float]
    is_artisan: bool


class UserRole(str, Enum):
    ADMIN = "admin"
    MERCHANT = "merchant"


class UserDB(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    company = Column(String, nullable=False)
    role = Column(String, default=UserRole.MERCHANT)
    shop_name = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class UserOut(BaseModel):
    id: int
    email: str
    company: str
    role: str
    shop_name: Optional[str]


class LoginRequest(BaseModel):
    email: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut
