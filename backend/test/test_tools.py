# tests/test_tools.py
"""
Unit tests for tools (search, calendar, booking).
"""
import pytest
from datetime import datetime, timedelta

class TestSearchTools:
    """Tests for search tools."""
    
    def test_search_hotels_yogyakarta(self):
        from app.tools.search import search_hotels
        results = search_hotels("Yogyakarta", "2025-12-20", "2025-12-24")
        
        assert len(results) > 0
        assert all("id" in h for h in results)
        assert all("name" in h for h in results)
        assert all("price_per_night" in h for h in results)
    
    def test_search_hotels_with_preferences(self):
        from app.tools.search import search_hotels
        results = search_hotels("Yogyakarta", "2025-12-20", "2025-12-24", preferences="homestay")
        
        assert len(results) > 0
        # Should prioritize homestays
        homestays = [h for h in results if h.get("type") == "homestay"]
        assert len(homestays) > 0
    
    def test_search_hotels_with_max_price(self):
        from app.tools.search import search_hotels
        max_price = 400000
        results = search_hotels("Yogyakarta", "2025-12-20", "2025-12-24", max_price=max_price)
        
        # At least some results should be under max price
        under_budget = [h for h in results if h["price_per_night"] <= max_price]
        assert len(under_budget) > 0
    
    def test_search_hotels_unknown_destination(self):
        from app.tools.search import search_hotels
        results = search_hotels("UnknownCity", "2025-12-20", "2025-12-24")
        
        # Should return default hotels
        assert len(results) > 0
    
    def test_search_flights(self):
        from app.tools.search import search_flights
        results = search_flights("Yogyakarta", "2025-12-20")
        
        assert len(results) > 0
        assert all("airline" in f for f in results)
        assert all("price" in f for f in results)
    
    def test_search_flights_custom_origin(self):
        from app.tools.search import search_flights
        results = search_flights("Bali", "2025-12-20", origin="Surabaya")
        
        assert len(results) > 0
        assert all(f["origin"] == "Surabaya" for f in results)
    
    def test_search_activities(self):
        from app.tools.search import search_activities
        results = search_activities("Yogyakarta")
        
        assert len(results) > 0
        assert all("name" in a for a in results)
        assert all("price" in a for a in results)
    
    def test_search_activities_by_type(self):
        from app.tools.search import search_activities
        results = search_activities("Yogyakarta", travel_type="adventure")
        
        assert len(results) > 0
        # Adventure activities should be prioritized
        adventure = [a for a in results if a.get("type") == "adventure"]
        assert len(adventure) > 0
    
    def test_get_destination_info(self):
        from app.tools.search import get_destination_info
        info = get_destination_info("Yogyakarta")
        
        assert info["name"] == "Yogyakarta"
        assert "highlights" in info
        assert "avg_daily_budget" in info


class TestCalendarTools:
    """Tests for calendar tools."""
    
    def test_get_busy_dates(self):
        from app.tools.calendar import get_busy_dates
        busy = get_busy_dates("user_1", "2025-12-20", "2025-12-30")
        
        assert isinstance(busy, list)
        # user_1 has events on 22nd and 25-26th
        assert "2025-12-22" in busy
        assert "2025-12-25" in busy
    
    def test_get_free_dates(self):
        from app.tools.calendar import get_free_dates
        free = get_free_dates("user_1", "2025-12-20", "2025-12-24")
        
        assert isinstance(free, list)
        assert "2025-12-20" in free
        assert "2025-12-21" in free
        # 22nd should NOT be free (Team Meeting)
        assert "2025-12-22" not in free
    
    def test_get_free_dates_empty_calendar(self):
        from app.tools.calendar import get_free_dates
        free = get_free_dates("user_3", "2025-12-20", "2025-12-24")
        
        # All dates should be free
        assert len(free) == 5
    
    def test_check_date_availability(self):
        from app.tools.calendar import check_date_availability
        
        # Free date
        result = check_date_availability("user_1", "2025-12-20")
        assert result["available"] == True
        
        # Busy date
        result = check_date_availability("user_1", "2025-12-22")
        assert result["available"] == False
    
    def test_find_best_travel_window_all_clear(self):
        from app.tools.calendar import find_best_travel_window
        result = find_best_travel_window("user_3", "2025-12-20", "2025-12-24", min_days=3)
        
        assert result["status"] == "all_clear"
    
    def test_find_best_travel_window_partial_conflict(self):
        from app.tools.calendar import find_best_travel_window
        result = find_best_travel_window("user_1", "2025-12-20", "2025-12-26", min_days=3)
        
        # Should suggest alternative window
        assert result["status"] in ["all_clear", "partial_conflict"]


class TestBookingTools:
    """Tests for booking and payment tools."""
    
    def test_process_payment_valid_token(self):
        from app.tools.booking import process_payment
        result = process_payment(1000000, "tok_valid_abc123")
        
        assert result["success"] == True
        assert "transaction_id" in result
        assert result["amount_idr"] == 1000000
    
    def test_process_payment_fail_token(self):
        from app.tools.booking import process_payment
        result = process_payment(1000000, "tok_fail_abc123")
        
        assert result["success"] == False
        assert result["error"] == "payment_declined"
    
    def test_process_payment_invalid_format(self):
        from app.tools.booking import process_payment
        result = process_payment(1000000, "invalid_token")
        
        assert result["success"] == False
        assert result["error"] == "invalid_token_format"
    
    def test_process_payment_zero_amount(self):
        from app.tools.booking import process_payment
        result = process_payment(0, "tok_valid_123")
        
        assert result["success"] == False
        assert result["error"] == "invalid_amount"
    
    def test_process_payment_exceeds_limit(self):
        from app.tools.booking import process_payment
        result = process_payment(100_000_000, "tok_valid_123")  # 100 juta
        
        assert result["success"] == False
        assert result["error"] == "amount_exceeds_limit"
    
    def test_book_hotel_success(self):
        from app.tools.booking import book_hotel, process_payment
        
        payment = process_payment(1000000, "tok_valid_123")
        result = book_hotel("htl_001", "user_1", "2025-12-20", "2025-12-24", payment)
        
        assert result["success"] == True
        assert "booking_ref" in result
        assert result["booking_ref"].startswith("HTL-")
    
    def test_book_hotel_without_payment(self):
        from app.tools.booking import book_hotel
        
        fake_payment = {"success": False}
        result = book_hotel("htl_001", "user_1", "2025-12-20", "2025-12-24", fake_payment)
        
        assert result["success"] == False
        assert result["error"] == "payment_required"
    
    def test_book_flight_success(self):
        from app.tools.booking import book_flight, process_payment
        
        payment = process_payment(500000, "tok_valid_123")
        result = book_flight("flt_001", "user_1", "2025-12-20", 2, payment)
        
        assert result["success"] == True
        assert result["booking_ref"].startswith("FLT-")
    
    def test_cancel_booking(self):
        from app.tools.booking import cancel_booking
        
        result = cancel_booking("HTL-ABC123", "Changed plans")
        
        assert result["success"] == True
        assert result["status"] == "cancelled"
    
    def test_validate_booking_request_valid(self):
        from app.tools.booking import validate_booking_request
        
        result = validate_booking_request("user_1", "tok_valid_123", True)
        assert result["valid"] == True
    
    def test_validate_booking_request_no_confirmation(self):
        from app.tools.booking import validate_booking_request
        
        result = validate_booking_request("user_1", "tok_valid_123", False)
        assert result["valid"] == False
        assert "confirmation" in str(result["errors"]).lower()
    
    def test_validate_booking_request_no_token(self):
        from app.tools.booking import validate_booking_request
        
        result = validate_booking_request("user_1", "", True)
        assert result["valid"] == False