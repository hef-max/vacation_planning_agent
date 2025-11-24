"""
Mock calendar integration.
Untuk PoC, simulasi calendar user dengan busy dates.
"""
from datetime import date, datetime, timedelta
from typing import Optional

# Mock calendar events per user
MOCK_CALENDAR = {
    "user_1": [
        {"title": "Team Meeting", "start": "2025-12-22", "end": "2025-12-22"},
        {"title": "Project Deadline", "start": "2025-12-15", "end": "2025-12-15"},
        {"title": "Family Event", "start": "2025-12-25", "end": "2025-12-26"},
        {"title": "Work Conference", "start": "2026-01-05", "end": "2026-01-07"},
    ],
    "user_2": [
        {"title": "Dentist Appointment", "start": "2025-12-18", "end": "2025-12-18"},
    ]
}

def get_busy_dates(user_id: str, range_start: str, range_end: str) -> list[str]:
    """
    Get list of busy dates untuk user dalam range tertentu.
    Returns list of date strings yang TIDAK available.
    """
    events = MOCK_CALENDAR.get(user_id, [])
    busy_dates = set()
    
    start = datetime.strptime(range_start, "%Y-%m-%d").date()
    end = datetime.strptime(range_end, "%Y-%m-%d").date()
    
    for event in events:
        event_start = datetime.strptime(event["start"], "%Y-%m-%d").date()
        event_end = datetime.strptime(event["end"], "%Y-%m-%d").date()
        
        # Check overlap with requested range
        current = event_start
        while current <= event_end:
            if start <= current <= end:
                busy_dates.add(current.strftime("%Y-%m-%d"))
            current += timedelta(days=1)
    
    return sorted(list(busy_dates))

def get_free_dates(user_id: str, range_start: str, range_end: str) -> list[str]:
    """
    Get list of FREE dates untuk user dalam range tertentu.
    Ini yang akan digunakan agent untuk planning.
    """
    busy = set(get_busy_dates(user_id, range_start, range_end))
    
    start = datetime.strptime(range_start, "%Y-%m-%d").date()
    end = datetime.strptime(range_end, "%Y-%m-%d").date()
    
    free_dates = []
    current = start
    while current <= end:
        date_str = current.strftime("%Y-%m-%d")
        if date_str not in busy:
            free_dates.append(date_str)
        current += timedelta(days=1)
    
    return free_dates

def check_date_availability(user_id: str, check_date: str) -> dict:
    """Check apakah tanggal tertentu available."""
    # Extend range sedikit untuk context
    dt = datetime.strptime(check_date, "%Y-%m-%d").date()
    range_start = (dt - timedelta(days=1)).strftime("%Y-%m-%d")
    range_end = (dt + timedelta(days=1)).strftime("%Y-%m-%d")
    
    busy = get_busy_dates(user_id, range_start, range_end)
    is_available = check_date not in busy
    
    return {
        "date": check_date,
        "available": is_available,
        "conflict": None if is_available else "User has existing event"
    }

def find_best_travel_window(user_id: str, preferred_start: str, preferred_end: str, min_days: int = 3) -> Optional[dict]:
    """
    Cari window terbaik untuk travel berdasarkan calendar.
    Returns suggested dates jika ada conflict.
    """
    free = get_free_dates(user_id, preferred_start, preferred_end)
    
    # Check if all requested dates are free
    start = datetime.strptime(preferred_start, "%Y-%m-%d").date()
    end = datetime.strptime(preferred_end, "%Y-%m-%d").date()
    total_days = (end - start).days + 1
    
    if len(free) == total_days:
        return {
            "status": "all_clear",
            "start_date": preferred_start,
            "end_date": preferred_end,
            "free_days": total_days,
            "message": "All requested dates are available"
        }
    
    # Find longest consecutive free window
    if len(free) >= min_days:
        longest_start = free[0]
        longest_len = 1
        current_start = free[0]
        current_len = 1
        
        for i in range(1, len(free)):
            prev = datetime.strptime(free[i-1], "%Y-%m-%d").date()
            curr = datetime.strptime(free[i], "%Y-%m-%d").date()
            
            if (curr - prev).days == 1:
                current_len += 1
            else:
                if current_len > longest_len:
                    longest_start = current_start
                    longest_len = current_len
                current_start = free[i]
                current_len = 1
        
        if current_len > longest_len:
            longest_start = current_start
            longest_len = current_len
        
        if longest_len >= min_days:
            suggested_end = (datetime.strptime(longest_start, "%Y-%m-%d").date() + timedelta(days=longest_len-1)).strftime("%Y-%m-%d")
            return {
                "status": "partial_conflict",
                "suggested_start": longest_start,
                "suggested_end": suggested_end,
                "free_days": longest_len,
                "original_free_days": len(free),
                "message": f"Some dates have conflicts. Suggested window: {longest_start} to {suggested_end}"
            }
    
    return {
        "status": "insufficient_free_days",
        "free_days": len(free),
        "required_days": min_days,
        "message": f"Not enough consecutive free days. Found {len(free)} free days, need at least {min_days}"
    }