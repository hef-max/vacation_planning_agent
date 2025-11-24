"""
Booking dan Payment tools (Mock).
Includes safety checks dan audit logging.
"""
import uuid
from datetime import datetime
from typing import Optional
from loguru import logger

# === Mock Payment Processing ===
# Rules: token yang dimulai dengan "tok_valid" akan sukses
#        token yang dimulai dengan "tok_fail" akan gagal
#        token lainnya akan gagal dengan "invalid token"

def process_payment(amount_idr: int, payment_token: str, description: str = "") -> dict:
    """
    Process payment (mock).
    PENTING: Fungsi ini HARUS dipanggil dengan explicit user confirmation.
    """
    # Validate token format
    if not payment_token or not payment_token.startswith("tok_"):
        logger.warning(f"Invalid payment token format: {payment_token[:10]}...")
        return {
            "success": False,
            "error": "invalid_token_format",
            "message": "Payment token must start with 'tok_'"
        }
    
    # Check amount limits
    if amount_idr <= 0:
        return {
            "success": False,
            "error": "invalid_amount",
            "message": "Amount must be positive"
        }
    
    if amount_idr > 50_000_000:  # 50 juta limit
        return {
            "success": False,
            "error": "amount_exceeds_limit",
            "message": "Amount exceeds maximum limit of 50,000,000 IDR"
        }
    
    # Simulate payment processing
    if payment_token.startswith("tok_valid"):
        transaction_id = f"txn_{uuid.uuid4().hex[:12]}"
        logger.info(f"Payment SUCCESS: {transaction_id} - {amount_idr} IDR")
        return {
            "success": True,
            "transaction_id": transaction_id,
            "amount_idr": amount_idr,
            "status": "completed",
            "timestamp": datetime.utcnow().isoformat(),
            "message": "Payment processed successfully"
        }
    
    elif payment_token.startswith("tok_fail"):
        logger.warning(f"Payment FAILED: simulated failure for token {payment_token[:15]}...")
        return {
            "success": False,
            "error": "payment_declined",
            "message": "Payment was declined by the provider"
        }
    
    else:
        logger.warning(f"Payment FAILED: unrecognized token {payment_token[:15]}...")
        return {
            "success": False,
            "error": "invalid_token",
            "message": "Payment token is not recognized"
        }

# === Booking Functions ===
def book_hotel(hotel_id: str, user_id: str, checkin: str, checkout: str, payment_result: dict) -> dict:
    """
    Book hotel setelah payment berhasil.
    """
    if not payment_result.get("success"):
        return {
            "success": False,
            "error": "payment_required",
            "message": "Cannot book hotel without successful payment"
        }
    
    booking_ref = f"HTL-{uuid.uuid4().hex[:8].upper()}"
    logger.info(f"Hotel BOOKED: {booking_ref} for user {user_id}")
    
    return {
        "success": True,
        "booking_ref": booking_ref,
        "hotel_id": hotel_id,
        "user_id": user_id,
        "checkin": checkin,
        "checkout": checkout,
        "status": "confirmed",
        "transaction_id": payment_result.get("transaction_id"),
        "created_at": datetime.utcnow().isoformat()
    }

def book_flight(flight_id: str, user_id: str, travel_date: str, passengers: int, payment_result: dict) -> dict:
    """
    Book flight setelah payment berhasil.
    """
    if not payment_result.get("success"):
        return {
            "success": False,
            "error": "payment_required", 
            "message": "Cannot book flight without successful payment"
        }
    
    booking_ref = f"FLT-{uuid.uuid4().hex[:8].upper()}"
    logger.info(f"Flight BOOKED: {booking_ref} for user {user_id}")
    
    return {
        "success": True,
        "booking_ref": booking_ref,
        "flight_id": flight_id,
        "user_id": user_id,
        "travel_date": travel_date,
        "passengers": passengers,
        "status": "confirmed",
        "transaction_id": payment_result.get("transaction_id"),
        "created_at": datetime.utcnow().isoformat()
    }

def book_activity(activity_id: str, user_id: str, activity_date: str, participants: int, payment_result: dict) -> dict:
    """
    Book aktivitas setelah payment berhasil.
    """
    if not payment_result.get("success"):
        return {
            "success": False,
            "error": "payment_required",
            "message": "Cannot book activity without successful payment"
        }
    
    booking_ref = f"ACT-{uuid.uuid4().hex[:8].upper()}"
    logger.info(f"Activity BOOKED: {booking_ref} for user {user_id}")
    
    return {
        "success": True,
        "booking_ref": booking_ref,
        "activity_id": activity_id,
        "user_id": user_id,
        "activity_date": activity_date,
        "participants": participants,
        "status": "confirmed",
        "transaction_id": payment_result.get("transaction_id"),
        "created_at": datetime.utcnow().isoformat()
    }

# === Cancellation ===
def cancel_booking(booking_ref: str, reason: str = "") -> dict:
    """Cancel a booking (mock - always succeeds for PoC)."""
    logger.info(f"Booking CANCELLED: {booking_ref} - Reason: {reason}")
    
    return {
        "success": True,
        "booking_ref": booking_ref,
        "status": "cancelled",
        "refund_status": "processing",
        "cancelled_at": datetime.utcnow().isoformat()
    }

# === Validation Helpers ===
def validate_booking_request(user_id: str, payment_token: str, confirmed: bool) -> dict:
    """
    Validate bahwa booking request memenuhi safety requirements.
    """
    errors = []
    
    if not user_id:
        errors.append("user_id is required")
    
    if not payment_token:
        errors.append("payment_token is required")
    
    if not confirmed:
        errors.append("explicit confirmation (confirmed=True) is required")
    
    if errors:
        return {"valid": False, "errors": errors}
    
    return {"valid": True, "errors": []}