# app/tools/__init__.py
"""
Tools for the vacation planner agent.
Includes search, calendar, and booking tools.
"""
from .search import (
    search_hotels,
    search_flights,
    search_activities,
    get_destination_info
)

from .calendar import (
    get_free_dates,
    get_busy_dates,
    check_date_availability,
    find_best_travel_window
)

from .booking import (
    process_payment,
    book_hotel,
    book_flight,
    book_activity,
    cancel_booking,
    validate_booking_request
)

__all__ = [
    # Search
    "search_hotels",
    "search_flights", 
    "search_activities",
    "get_destination_info",
    # Calendar
    "get_free_dates",
    "get_busy_dates",
    "check_date_availability",
    "find_best_travel_window",
    # Booking
    "process_payment",
    "book_hotel",
    "book_flight",
    "book_activity",
    "cancel_booking",
    "validate_booking_request"
]