from fastapi import APIRouter, HTTPException
from typing import Optional
import time
import json

from app.models.flights import HoldRequest, SeatHoldResponse
from app.core.redis import redis_client
from app.data.flights import flights  # <-- JSON list

router = APIRouter(prefix="/seat", tags=["Seat Selection"])

HOLD_TTL = 600  # 10 minutes


@router.get("/seatmap/{flight_id}")
def get_seatmap(flight_id: str):
    flight = next((f for f in flights if f["id"] == flight_id), None)

    if not flight:
        raise HTTPException(status_code=404, detail="Flight not found")

    return {
        "flight_id": flight_id,
        "seats": flight["seats"]
    }


@router.post("/hold-seat", response_model=SeatHoldResponse)
def hold_seat(request: HoldRequest):
    flight = next((f for f in flights if f["id"] == request.flight_id), None)

    if not flight:
        raise HTTPException(status_code=404, detail="Flight not found")

    seat = next((s for s in flight["seats"] if s["seat_no"] == request.seat_no), None)

    if not seat:
        raise HTTPException(status_code=404, detail="Seat not found")

    redis_key = f"seat_hold:{request.flight_id}:{request.seat_no}"

    # Seat already held?
    if redis_client.exists(redis_key):
        raise HTTPException(status_code=400, detail="Seat already held")

    # Seat already booked?
    if seat["available"] is False:
        raise HTTPException(status_code=400, detail="Seat already booked")

    # Create Redis hold
    hold_data = {
        "flight_id": request.flight_id,
        "seat_no": request.seat_no,
        "session_id": request.session_id
    }

    redis_client.setex(
        redis_key,
        request.hold_ttl_seconds or HOLD_TTL,
        json.dumps(hold_data)
    )

    expires_at = int(time.time()) + (request.hold_ttl_seconds or HOLD_TTL)

    return SeatHoldResponse(
        hold_id=redis_key,
        flight_id=request.flight_id,
        seat_no=request.seat_no,
        expires_at=expires_at,
        status="held"
    )
