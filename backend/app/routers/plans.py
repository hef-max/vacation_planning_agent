"""
API endpoints untuk vacation planning.
"""
import uuid
import json
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session

from app.models.schemas import (
    PlanRequest, PlanResponse, BookingConfirmRequest, 
    BookingConfirmResponse, BookingResponse, BookingStatus, BookingType
)
from app.database import get_db, PlanDB, BookingDB
from app.agents.planner import generate_itinerary, generate_itinerary_fallback
from app.tools.booking import process_payment, book_hotel, validate_booking_request
from app.utils.logger import audit, logger

router = APIRouter(prefix="/api/v1/plan", tags=["Plans"])

# === HELPER: Pemeriksaan Biaya Ganda ===
def _recalculate_cost_mock(itinerary: dict) -> int:
    """
    Menghitung ulang total biaya berdasarkan struktur itinerary (Guardrail).
    Digunakan untuk verifikasi terhadap biaya yang dilaporkan oleh Agen LLM.
    """
    total_recalculated = 0
    days = itinerary.get("days", [])
    
    # Hitung biaya aktivitas, transportasi, dan lodging dari setiap hari
    for day in days:
        # Biaya Aktivitas
        for activity in day.get("activities", []):
            total_recalculated += activity.get("estimated_cost", 0)
        
        # Biaya Transportasi
        total_recalculated += day.get("transport", {}).get("estimated_cost", 0)
        
        # Biaya Penginapan (hanya jika ada, biasanya kecuali hari terakhir)
        if day.get("lodging"):
            # Harga lodging harus dihitung per hari (asumsi harga sudah per malam)
            total_recalculated += day["lodging"].get("price", 0)
    
    return total_recalculated

# === POST /api/v1/plan - Create new itinerary ===
@router.post("", response_model=PlanResponse)
async def create_plan(request: PlanRequest, db: Session = Depends(get_db)):
    """
    Generate a new vacation itinerary based on user preferences.
    """
    plan_id = f"plan_{uuid.uuid4().hex[:12]}"
    
    logger.info(f"Creating plan {plan_id} for user {request.user_id}")
    
    # Try LLM agent first
    try:
        result = generate_itinerary(
            user_id=request.user_id,
            destination=request.destination,
            start_date=request.start_date.isoformat(),
            end_date=request.end_date.isoformat(),
            budget_idr=request.budget_idr,
            travel_type=request.travel_type.value,
            travelers=request.travelers,
            preferences=request.preferences or ""
        )

    except Exception as e:
        logger.warning(f"LLM agent failed (exception), using fallback: {e}")
        # FALLBACK KARENA EXCEPTION
        result = generate_itinerary_fallback(
            user_id=request.user_id,
            destination=request.destination,
            start_date=request.start_date.isoformat(),
            end_date=request.end_date.isoformat(),
            budget_idr=request.budget_idr,
            travel_type=request.travel_type.value,
            travelers=request.travelers,
            preferences=request.preferences or ""
        )
    
    # Save to database
    plan_record = PlanDB(
        id=plan_id,
        user_id=request.user_id,
        status="draft",
        destination=request.destination,
        start_date=request.start_date.isoformat(),
        end_date=request.end_date.isoformat(),
        budget_idr=request.budget_idr,
        itinerary_json=json.dumps(result.get("itinerary")) if result.get("itinerary") else None
    )
    db.add(plan_record)
    db.commit()
    
    # Audit log
    audit.log_plan_created(request.user_id, plan_id, request.destination, request.budget_idr)
    
    return PlanResponse(
        plan_id=plan_id,
        status="draft",
        user_id=request.user_id,
        created_at=datetime.utcnow(),
        itinerary=result.get("itinerary"),
        message="Itinerary generated successfully" if result["success"] else result.get("error")
    )

# === GET /api/v1/plan/{plan_id} - Get plan details ===
@router.get("/{plan_id}", response_model=PlanResponse)
async def get_plan(plan_id: str, db: Session = Depends(get_db)):
    """Get details of an existing plan."""
    plan = db.query(PlanDB).filter(PlanDB.id == plan_id).first()
    
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    
    itinerary = None
    if plan.itinerary_json:
        try:
            itinerary = json.loads(plan.itinerary_json)
        except json.JSONDecodeError:
            pass
    
    return PlanResponse(
        plan_id=plan.id,
        status=plan.status,
        user_id=plan.user_id,
        created_at=plan.created_at,
        itinerary=itinerary
    )

# === POST /api/v1/plan/{plan_id}/confirm - Confirm and book ===
@router.post("/{plan_id}/confirm", response_model=BookingConfirmResponse)
async def confirm_and_book(
    plan_id: str, 
    request: BookingConfirmRequest, 
    db: Session = Depends(get_db)
):
    """
    Confirm a plan and process bookings.
    REQUIRES explicit user confirmation and valid payment token.
    """
    # 1. VALIDASI SAFETY
    validation = validate_booking_request(
        user_id=request.user_id,
        payment_token=request.payment_token,
        confirmed=request.confirmed
    )
    
    if not validation["valid"]:
        raise HTTPException(status_code=400, detail={"errors": validation["errors"]})
    
    # 2. GET DAN PARSE DATA
    plan = db.query(PlanDB).filter(PlanDB.id == plan_id).first()
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    
    if plan.status == "confirmed":
        raise HTTPException(status_code=400, detail="Plan already confirmed")
    
    itinerary = json.loads(plan.itinerary_json) if plan.itinerary_json else None
    if not itinerary:
        raise HTTPException(status_code=400, detail="Plan has no itinerary")
    
    # 3. GUARDRAIL: PEMERIKSAAN BIAYA GANDA
    total_amount_reported = itinerary.get("total_estimated_cost", 0)
    total_amount_recalculated = _recalculate_cost_mock(itinerary)
    
    # Toleransi 5% untuk perbedaan harga (karena LLM mungkin salah hitung sedikit)
    TOLERANCE_PERCENT = 0.05 
    cost_difference = abs(total_amount_reported - total_amount_recalculated)

    if cost_difference > total_amount_recalculated * TOLERANCE_PERCENT:
        audit.log_booking_failed(
            request.user_id,
            plan_id,
            "halucination_risk",
            f"Agen reported {total_amount_reported} but recalculated cost is {total_amount_recalculated}"
        )
        raise HTTPException(
            status_code=400,
            detail={
                "error": "cost_mismatch",
                "message": "Cost validation failed. Reported cost does not match detailed itinerary costs. Please regenerate plan."
            }
        )
    
    # Gunakan biaya Agen yang sudah divalidasi
    total_amount = total_amount_reported
    
    # Log booking attempt
    audit.log_booking_attempt(request.user_id, plan_id, "full_trip", total_amount)
    
    # 4. PROSES PEMBAYARAN
    audit.log_payment_attempt(request.user_id, total_amount, f"Booking for plan {plan_id}")
    payment_result = process_payment(
        amount_idr=total_amount,
        payment_token=request.payment_token,
        description=f"Vacation booking: {plan.destination}"
    )
    
    if not payment_result["success"]:
        audit.log_booking_failed(request.user_id, plan_id, "payment", payment_result.get("error", "unknown"))
        raise HTTPException(
            status_code=402, 
            detail={
                "error": "payment_failed",
                "message": payment_result.get("message"),
                "code": payment_result.get("error")
            }
        )
    
    # 5. PROSES BOOKING (Hotel/Flight/Activity)
    bookings = []
    recommended_hotels = itinerary.get("recommended_hotels", [])
    
    # Booking Hotel
    if recommended_hotels:
        hotel = recommended_hotels[0]
        # Hitung jumlah malam yang tepat
        try:
            from datetime import date
            start = date.fromisoformat(itinerary.get("start_date"))
            end = date.fromisoformat(itinerary.get("end_date"))
            hotel_nights = (end - start).days
        except Exception:
            hotel_nights = 1 # Fallback
            
        hotel_amount = hotel.get("price_per_night", 0) * hotel_nights
        
        hotel_booking = book_hotel(
            hotel_id=hotel.get("id", "htl_unknown"),
            user_id=request.user_id,
            checkin=itinerary.get("start_date"),
            checkout=itinerary.get("end_date"),
            payment_result=payment_result
        )
        
        if hotel_booking["success"]:
            booking_id = f"bkg_{uuid.uuid4().hex[:12]}"
            booking_record = BookingDB(
                id=booking_id,
                plan_id=plan_id,
                user_id=request.user_id,
                booking_type="hotel",
                provider_ref=hotel_booking["booking_ref"],
                status="confirmed",
                amount_idr=hotel_amount,
                details_json=json.dumps(hotel_booking)
            )
            db.add(booking_record)
            
            bookings.append(BookingResponse(
                booking_id=booking_id,
                plan_id=plan_id,
                booking_type=BookingType.HOTEL,
                provider_ref=hotel_booking["booking_ref"],
                status=BookingStatus.CONFIRMED,
                amount_idr=hotel_amount,
                created_at=datetime.utcnow()
            ))
            
            audit.log_booking_success(
                request.user_id, 
                hotel_booking["booking_ref"], 
                "hotel", 
                hotel_amount,
                payment_result["transaction_id"]
            )
    
    # 6. UPDATE STATUS & COMMIT
    plan.status = "confirmed"
    db.commit()
    
    return BookingConfirmResponse(
        success=True,
        plan_id=plan_id,
        bookings=bookings,
        total_charged=total_amount,
        message=f"Booking confirmed! Transaction ID: {payment_result['transaction_id']}"
    )

# === GET /api/v1/plan/{plan_id}/bookings - List bookings for plan ===
@router.get("/{plan_id}/bookings", response_model=list[BookingResponse])
async def get_plan_bookings(plan_id: str, db: Session = Depends(get_db)):
    """Get all bookings associated with a plan."""
    bookings = db.query(BookingDB).filter(BookingDB.plan_id == plan_id).all()
    
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

# === DELETE /api/v1/plan/{plan_id} - Cancel plan ===
@router.delete("/{plan_id}")
async def cancel_plan(plan_id: str, db: Session = Depends(get_db)):
    """Cancel a plan (only if not yet confirmed)."""
    plan = db.query(PlanDB).filter(PlanDB.id == plan_id).first()
    
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    
    if plan.status == "confirmed":
        raise HTTPException(status_code=400, detail="Cannot cancel confirmed plan. Contact support for refunds.")
    
    plan.status = "cancelled"
    db.commit()
    
    return {"message": "Plan cancelled", "plan_id": plan_id}