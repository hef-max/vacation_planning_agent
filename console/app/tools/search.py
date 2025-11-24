"""
Mock search tools untuk hotels, flights, dan activities.
Untuk PoC, return data dummy yang realistis.
"""
from typing import Optional
import random

# === Mock Data ===
MOCK_HOTELS = {
    "yogyakarta": [
        {"id": "htl_001", "name": "The Phoenix Hotel Yogyakarta", "type": "hotel", "price_per_night": 850000, "rating": 4.7, "amenities": ["wifi", "pool", "breakfast"]},
        {"id": "htl_002", "name": "Greenhost Boutique Hotel", "type": "hotel", "price_per_night": 650000, "rating": 4.5, "amenities": ["wifi", "eco-friendly", "restaurant"]},
        {"id": "htl_003", "name": "Rumah Palagan Homestay", "type": "homestay", "price_per_night": 350000, "rating": 4.8, "amenities": ["wifi", "local breakfast", "garden"]},
        {"id": "htl_004", "name": "Omah Pakem Guesthouse", "type": "homestay", "price_per_night": 280000, "rating": 4.6, "amenities": ["wifi", "mountain view", "parking"]},
        {"id": "htl_005", "name": "RedDoorz near Malioboro", "type": "budget", "price_per_night": 200000, "rating": 4.0, "amenities": ["wifi", "ac"]},
    ],
    "bali": [
        {"id": "htl_101", "name": "Alila Seminyak", "type": "resort", "price_per_night": 2500000, "rating": 4.9, "amenities": ["wifi", "pool", "spa", "beach"]},
        {"id": "htl_102", "name": "Kuta Paradiso Hotel", "type": "hotel", "price_per_night": 900000, "rating": 4.4, "amenities": ["wifi", "pool", "breakfast"]},
        {"id": "htl_103", "name": "Ubud Village Homestay", "type": "homestay", "price_per_night": 400000, "rating": 4.7, "amenities": ["wifi", "rice field view", "yoga"]},
    ],
    "default": [
        {"id": "htl_999", "name": "Standard City Hotel", "type": "hotel", "price_per_night": 500000, "rating": 4.0, "amenities": ["wifi", "ac"]},
    ]
}

MOCK_ACTIVITIES = {
    "yogyakarta": [
        {"id": "act_001", "name": "Sunrise at Borobudur Temple", "duration": "4 hours", "price": 450000, "type": "culture", "description": "Watch sunrise at the world's largest Buddhist temple"},
        {"id": "act_002", "name": "Prambanan Temple Visit", "duration": "3 hours", "price": 350000, "type": "culture", "description": "Explore the magnificent Hindu temple complex"},
        {"id": "act_003", "name": "Malioboro Street Walking Tour", "duration": "2 hours", "price": 0, "type": "culture", "description": "Free walking tour of the famous shopping street"},
        {"id": "act_004", "name": "Batik Workshop", "duration": "3 hours", "price": 200000, "type": "culture", "description": "Learn traditional Javanese batik making"},
        {"id": "act_005", "name": "Jomblang Cave Adventure", "duration": "5 hours", "price": 500000, "type": "adventure", "description": "Rappelling into cave with heavenly light beam"},
        {"id": "act_006", "name": "Sultan Palace (Kraton) Tour", "duration": "2 hours", "price": 25000, "type": "culture", "description": "Visit the living palace of Yogyakarta Sultan"},
        {"id": "act_007", "name": "Traditional Ramayana Ballet", "duration": "2 hours", "price": 150000, "type": "culture", "description": "Watch epic dance performance at Prambanan"},
        {"id": "act_008", "name": "Mount Merapi Jeep Tour", "duration": "4 hours", "price": 450000, "type": "adventure", "description": "4x4 jeep tour around active volcano"},
    ],
    "bali": [
        {"id": "act_101", "name": "Tegallalang Rice Terrace", "duration": "2 hours", "price": 50000, "type": "nature", "description": "Walk through iconic rice terraces"},
        {"id": "act_102", "name": "Uluwatu Temple Sunset", "duration": "3 hours", "price": 100000, "type": "culture", "description": "Watch sunset and Kecak dance"},
        {"id": "act_103", "name": "Snorkeling at Nusa Penida", "duration": "full day", "price": 800000, "type": "beach", "description": "Swim with manta rays"},
    ],
    "default": [
        {"id": "act_999", "name": "City Walking Tour", "duration": "2 hours", "price": 100000, "type": "culture", "description": "Explore local highlights"},
    ]
}

MOCK_FLIGHTS = {
    "yogyakarta": [
        {"id": "flt_001", "airline": "Garuda Indonesia", "departure": "06:00", "arrival": "07:10", "price": 850000, "class": "economy"},
        {"id": "flt_002", "airline": "Lion Air", "departure": "08:30", "arrival": "09:40", "price": 550000, "class": "economy"},
        {"id": "flt_003", "airline": "Citilink", "departure": "14:00", "arrival": "15:10", "price": 480000, "class": "economy"},
    ],
    "bali": [
        {"id": "flt_101", "airline": "Garuda Indonesia", "departure": "07:00", "arrival": "08:45", "price": 1200000, "class": "economy"},
        {"id": "flt_102", "airline": "AirAsia", "departure": "10:00", "arrival": "11:50", "price": 650000, "class": "economy"},
    ],
    "default": [
        {"id": "flt_999", "airline": "Generic Air", "departure": "10:00", "arrival": "12:00", "price": 750000, "class": "economy"},
    ]
}

# === Search Functions ===
def search_hotels(destination: str, checkin: str, checkout: str, preferences: Optional[str] = None, max_price: Optional[int] = None) -> list[dict]:
    """Search hotels berdasarkan destinasi dan preferensi."""
    dest_key = destination.lower()
    hotels = MOCK_HOTELS.get(dest_key, MOCK_HOTELS["default"])
    
    # Filter by preferences
    if preferences:
        pref_lower = preferences.lower()
        if "homestay" in pref_lower:
            hotels = [h for h in hotels if h["type"] in ["homestay", "guesthouse"]] or hotels
        elif "budget" in pref_lower:
            hotels = sorted(hotels, key=lambda x: x["price_per_night"])[:3]
    
    # Filter by max price
    if max_price:
        hotels = [h for h in hotels if h["price_per_night"] <= max_price] or hotels[:2]
    
    # Add availability (mock)
    for h in hotels:
        h["available"] = True
        h["checkin"] = checkin
        h["checkout"] = checkout
    
    return hotels

def search_flights(destination: str, departure_date: str, origin: str = "Jakarta") -> list[dict]:
    """Search flights ke destinasi."""
    dest_key = destination.lower()
    flights = MOCK_FLIGHTS.get(dest_key, MOCK_FLIGHTS["default"])
    
    for f in flights:
        f["origin"] = origin
        f["destination"] = destination
        f["date"] = departure_date
        f["available_seats"] = random.randint(5, 50)
    
    return flights

def search_activities(destination: str, travel_type: Optional[str] = None) -> list[dict]:
    """Search aktivitas berdasarkan destinasi dan tipe travel."""
    dest_key = destination.lower()
    activities = MOCK_ACTIVITIES.get(dest_key, MOCK_ACTIVITIES["default"])
    
    # Filter by travel type
    if travel_type:
        type_lower = travel_type.lower()
        filtered = [a for a in activities if a["type"] == type_lower]
        if filtered:
            activities = filtered + [a for a in activities if a["type"] != type_lower][:2]
    
    return activities

def get_destination_info(destination: str) -> dict:
    """Get informasi umum tentang destinasi."""
    info = {
        "yogyakarta": {
            "name": "Yogyakarta",
            "country": "Indonesia",
            "timezone": "WIB (UTC+7)",
            "currency": "IDR",
            "best_time": "April - October",
            "highlights": ["Borobudur", "Prambanan", "Malioboro", "Kraton", "Mount Merapi"],
            "avg_daily_budget": {"budget": 300000, "mid": 600000, "luxury": 1500000}
        },
        "bali": {
            "name": "Bali",
            "country": "Indonesia", 
            "timezone": "WITA (UTC+8)",
            "currency": "IDR",
            "best_time": "April - October",
            "highlights": ["Ubud", "Seminyak", "Uluwatu", "Nusa Penida", "Mount Batur"],
            "avg_daily_budget": {"budget": 500000, "mid": 1000000, "luxury": 3000000}
        }
    }
    return info.get(destination.lower(), {"name": destination, "country": "Indonesia"})