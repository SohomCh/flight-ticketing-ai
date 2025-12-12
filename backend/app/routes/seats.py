# backend/app/routes/seats.py
from fastapi import APIRouter, HTTPException, Body
from typing import Optional
import time
import uuid
from datetime import datetime, timedelta

from app.routes.flights import find_flight_by_id, HOLDS, HOLDS_EXPIRY  # reuse flights in-memory stores

router = APIRouter()

# in-memory holds if you want a seat-specific interface
# we use the same HOLDS store from flights module to avoid duplication

class SeatHoldRequestModel:
    # simple container - the flights route already has a HoldRequest model,
    # but for a self-contained route we accept simple JSON body:
    pass

@router.get("/seatmap/{flight_id}")
def get_seatmap(flight_id: str):
    flight = find_flight_by_id(flight_id)
    if not flight:
        raise HTTPException(status_code=404, detail="Flight not found")
    return {"flight_id": flight_id, "seats": flight.get("seats", [])}

@router.post("/hold-seat")
def hold_seat(payload: dict = Body(...)):
    """
    Body expected: {"flight_id":"FL-XXX","seat_no":"1C","session_id":"sess123"}
    """
    flight_id = payload.get("flight_id")
    seat_no = payload.get("seat_no")
    session_id = payload.get("session_id")

    if not flight_id or not seat_no:
        raise HTTPException(status_code=400, detail="flight_id and seat_no required")

    flight = find_flight_by_id(flight_id)
    if not flight:
        raise HTTPException(status_code=404, detail="Flight not found")

    seat = next((s for s in flight.get("seats", []) if s.get("seat_no") == seat_no), None)
    if not seat:
        raise HTTPException(status_code=404, detail="Seat not found")
    if not seat.get("available", False):
        raise HTTPException(status_code=400, detail="Seat already booked/held")

    # create hold
    hold_id = str(uuid.uuid4())
    expiry = datetime.utcnow() + timedelta(seconds=600)  # default TTL 10 minutes
    HOLDS[hold_id] = {
        "hold_id": hold_id,
        "flight_id": flight_id,
        "seat_no": seat_no,
        "session_id": session_id,
        "expires_at": expiry.isoformat(),
        "status": "held"
    }
    HOLDS_EXPIRY[hold_id] = expiry

    # mark seat temporarily unavailable
    seat["available"] = False

    return {
        "hold_id": hold_id,
        "flight_id": flight_id,
        "seat_no": seat_no,
        "expires_at": expiry.isoformat(),
        "status": "held"
    }
