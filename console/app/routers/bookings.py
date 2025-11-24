"""
API endpoints untuk booking management.
"""
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session

from app.models.schemas import BookingResponse, BookingStatus, BookingType
from app.database import get_db, BookingDB
from app.tools.booking import cancel_booking
from app.utils.logger import audit, logger

router = APIRouter(prefix="/api/v1/bookings", tags=["Bookings"])

# === GET /api/v1/bookings - List all bookings ===
@router.get("", response_model=list[BookingResponse])
async def list_bookings(
    user_id: Optional[str] = Query(None, description="Filter by user ID"),
    status: Optional[BookingStatus] = Query(None, description="Filter by status"),
    limit: int = Query(50, le=100),
    db: Session = Depends(get_db)
):
    """List bookings with optional filters."""
    query = db.query(BookingDB)
    
    if user_id:
        query = query.filter(BookingDB.user_id == user_id)
    if status:
        query = query.filter(BookingDB.status == status.value)
    
    bookings = query.order_by(BookingDB.created_at.desc()).limit(limit).all()
    
    return [
        BookingResponse(
            booking_id=b.id,
            plan_id=b.plan_id,
            booking_type=BookingType(b.booking_type),
            provider_ref=b.provider_ref,
            status=BookingStatus(b.status),
            amount_idr=b.amount_idr,
            created_at=b.created_at
        )
        for b in bookings
    ]

# === GET /api/v1/bookings/{booking_id} - Get booking details ===
@router.get("/{booking_id}", response_model=BookingResponse)
async def get_booking(booking_id: str, db: Session = Depends(get_db)):
    """Get details of a specific booking."""
    booking = db.query(BookingDB).filter(BookingDB.id == booking_id).first()
    
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    
    return BookingResponse(
        booking_id=booking.id,
        plan_id=booking.plan_id,
        booking_type=BookingType(booking.booking_type),
        provider_ref=booking.provider_ref,
        status=BookingStatus(booking.status),
        amount_idr=booking.amount_idr,
        created_at=booking.created_at
    )

# === POST /api/v1/bookings/{booking_id}/cancel - Cancel booking ===
@router.post("/{booking_id}/cancel")
async def cancel_booking_endpoint(
    booking_id: str, 
    reason: str = Query("User requested cancellation"),
    db: Session = Depends(get_db)
):
    """
    Request cancellation of a booking.
    Note: Refund processing may take 3-5 business days.
    """
    booking = db.query(BookingDB).filter(BookingDB.id == booking_id).first()
    
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    
    if booking.status == "cancelled":
        raise HTTPException(status_code=400, detail="Booking already cancelled")
    
    # Call cancellation (mock)
    result = cancel_booking(booking.provider_ref, reason)
    
    if result["success"]:
        booking.status = "cancelled"
        db.commit()
        
        audit.log_action(
            user_id=booking.user_id,
            action="BOOKING_CANCELLED",
            details={
                "booking_id": booking_id,
                "provider_ref": booking.provider_ref,
                "reason": reason
            }
        )
        
        return {
            "success": True,
            "booking_id": booking_id,
            "status": "cancelled",
            "refund_status": "processing",
            "message": "Booking cancelled. Refund will be processed within 3-5 business days."
        }
    
    raise HTTPException(status_code=500, detail="Failed to cancel booking")

# === GET /api/v1/bookings/user/{user_id}/summary - User booking summary ===
@router.get("/user/{user_id}/summary")
async def get_user_booking_summary(user_id: str, db: Session = Depends(get_db)):
    """Get summary of all bookings for a user."""
    bookings = db.query(BookingDB).filter(BookingDB.user_id == user_id).all()
    
    total_spent = sum(b.amount_idr for b in bookings if b.status == "confirmed")
    
    by_status = {}
    for b in bookings:
        status = b.status
        if status not in by_status:
            by_status[status] = {"count": 0, "total_amount": 0}
        by_status[status]["count"] += 1
        by_status[status]["total_amount"] += b.amount_idr
    
    by_type = {}
    for b in bookings:
        btype = b.booking_type
        if btype not in by_type:
            by_type[btype] = {"count": 0, "total_amount": 0}
        by_type[btype]["count"] += 1
        by_type[btype]["total_amount"] += b.amount_idr
    
    return {
        "user_id": user_id,
        "total_bookings": len(bookings),
        "total_spent_idr": total_spent,
        "by_status": by_status,
        "by_type": by_type
    }