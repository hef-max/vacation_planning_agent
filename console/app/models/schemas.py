from pydantic import BaseModel, Field
from typing import Optional
from datetime import date, datetime
from enum import Enum

# === Enums ===
class TravelType(str, Enum):
    BEACH = "beach"
    CITY = "city"
    ADVENTURE = "adventure"
    CULTURE = "culture"
    NATURE = "nature"

class BookingStatus(str, Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"
    FAILED = "failed"

class BookingType(str, Enum):
    HOTEL = "hotel"
    FLIGHT = "flight"
    ACTIVITY = "activity"


# === Request Models ===
class PlanRequest(BaseModel):
    user_id: str = "user_1"
    destination: str = Field(..., example="Yogyakarta")
    start_date: date = Field(..., example="2025-12-20")
    end_date: date = Field(..., example="2025-12-24")
    budget_idr: int = Field(..., ge=500000, le=50000000, example=5000000)
    travel_type: TravelType = TravelType.CULTURE
    travelers: int = Field(default=1, ge=1, le=10)
    preferences: Optional[str] = Field(None, example="prefer homestay, local food")

class BookingConfirmRequest(BaseModel):
    plan_id: str
    user_id: str = "user_1"
    payment_token: str = Field(..., example="tok_valid_123")
    confirmed: bool = True

# === Response Models ===
class Activity(BaseModel):
    time: str
    name: str
    description: str
    estimated_cost: int

class DayPlan(BaseModel):
    date: str
    activities: list[Activity]
    lodging: Optional[dict] = None
    transport: Optional[dict] = None
    daily_cost: int

class Itinerary(BaseModel):
    trip_name: str
    destination: str
    start_date: str
    end_date: str
    days: list[DayPlan]
    total_estimated_cost: int
    recommended_hotels: list[dict]
    recommended_flights: Optional[list[dict]] = None

class PlanResponse(BaseModel):
    plan_id: str
    status: str
    user_id: str
    created_at: datetime
    itinerary: Optional[Itinerary] = None
    message: Optional[str] = None

class BookingResponse(BaseModel):
    booking_id: str
    plan_id: str
    booking_type: BookingType
    provider_ref: str
    status: BookingStatus
    amount_idr: int
    created_at: datetime

class BookingConfirmResponse(BaseModel):
    success: bool
    plan_id: str
    bookings: list[BookingResponse]
    total_charged: int
    message: str