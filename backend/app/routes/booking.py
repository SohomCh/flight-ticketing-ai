"""
Routes for booking confirmation and getting booking details.
Drop this file into backend/app/routes/booking.py
"""

from fastapi import APIRouter, HTTPException, Body
from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime
import uuid

router = APIRouter()

# In-memory bookings store (demo)
BOOKINGS: Dict[str, Dict[str, Any]] = {}

# Request/Response models
class BookRequest(BaseModel):
    hold_id: Optional[str] = None
    flight_id: Optional[str] = None
    seat_no: Optional[str] = None
    passenger_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    payment_method: Optional[str] = "mock"

class BookResponse(BaseModel):
    booking_id: str
    pnr: str
    flight_id: str
    seat_no: str
    passenger_name: str
    status: str

def generate_pnr():
    # simple 6-char alnum PNR
    return uuid.uuid4().hex[:6].upper()

@router.post("/book", response_model=BookResponse)
def confirm_booking(payload: BookRequest = Body(...)):
    """
    Confirm booking. Accepts either a hold_id (preferred) or flight_id+seat_no.
    Returns booking details with PNR.
    """
    # validate hold if provided
    chosen_flight = None
    chosen_seat = None
    passenger_name = payload.passenger_name or "Passenger"
    if payload.hold_id:
        # try to find hold in flights route in-memory HOLDS if available
        # to avoid circular import, we'll attempt to import the data structure
        try:
            from app.routes.flights import HOLDS
        except Exception:
            raise HTTPException(status_code=500, detail="Hold store not available")
        hold = HOLDS.get(payload.hold_id)
        if not hold:
            raise HTTPException(status_code=404, detail="Hold not found or expired")
        chosen_flight = hold["flight_id"]
        chosen_seat = hold["seat_no"]
        # optional: mark hold consumed
        hold["status"] = "consumed"
    else:
        if not (payload.flight_id and payload.seat_no):
            raise HTTPException(status_code=400, detail="Provide hold_id or flight_id + seat_no")
        chosen_flight = payload.flight_id
        chosen_seat = payload.seat_no

    # Now create booking
    booking_id = str(uuid.uuid4())
    pnr = generate_pnr()
    booking = {
        "booking_id": booking_id,
        "pnr": pnr,
        "flight_id": chosen_flight,
        "seat_no": chosen_seat,
        "passenger_name": passenger_name,
        "email": payload.email,
        "phone": payload.phone,
        "status": "confirmed",
        "created_at": datetime.utcnow().isoformat()
    }
    BOOKINGS[booking_id] = booking

    # Also attempt to mark seat as booked in flights data (in-memory only)
    try:
        from app.routes.flights import find_flight_by_id
        f = find_flight_by_id(chosen_flight)
        if f:
            for s in f.get("seats", []):
                if s.get("seat_no") == chosen_seat:
                    s["available"] = False
                    break
    except Exception:
        pass

    return BookResponse(
        booking_id=booking_id,
        pnr=pnr,
        flight_id=chosen_flight,
        seat_no=chosen_seat,
        passenger_name=passenger_name,
        status="confirmed"
    )

@router.get("/{booking_id}")
def get_booking(booking_id: str):
    b = BOOKINGS.get(booking_id)
    if not b:
        raise HTTPException(status_code=404, detail="Booking not found")
    return b
