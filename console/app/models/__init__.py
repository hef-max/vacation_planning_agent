# app/models/__init__.py
"""
Pydantic models for request/response schemas.
"""
from .schemas import (
    TravelType,
    BookingStatus,
    BookingType,
    PlanRequest,
    BookingConfirmRequest,
    Activity,
    DayPlan,
    Itinerary,
    PlanResponse,
    BookingResponse,
    BookingConfirmResponse
)

__all__ = [
    "TravelType",
    "BookingStatus", 
    "BookingType",
    "PlanRequest",
    "BookingConfirmRequest",
    "Activity",
    "DayPlan",
    "Itinerary",
    "PlanResponse",
    "BookingResponse",
    "BookingConfirmResponse"
]