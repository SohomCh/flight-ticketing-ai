# backend/app/routes/flights.py
from fastapi import APIRouter, HTTPException, Body
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from pathlib import Path
import uuid
import json
from datetime import datetime, timedelta

router = APIRouter()

DATA_DIR = Path(__file__).resolve().parents[1] / "data"
FLIGHTS_FILE = DATA_DIR / "flights.json"

# In-memory stores for demo/dev
HOLDS: Dict[str, Dict[str, Any]] = {}      # hold_id -> hold info
HOLDS_EXPIRY: Dict[str, datetime] = {}     # hold_id -> expiry timestamp

# ---------- Pydantic models (match your JSON) ----------
class Seat(BaseModel):
    seat_no: str
    type: Optional[str] = None
    available: bool
    price: Optional[float] = None

class Flight(BaseModel):
    id: str
    mode: Optional[str] = None
    from_: str = Field(..., alias="from")   # incoming JSON key "from"
    to: str
    date: str
    departure: Optional[str] = None
    arrival: Optional[str] = None
    price: Optional[float] = None
    airline: Optional[str] = None
    flight_number: Optional[str] = None
    stops: Optional[int] = 0
    layovers: Optional[List[Optional[str]]] = None
    total_time: Optional[str] = None
    seats: List[Seat] = []

    model_config = {"populate_by_name": True}  # pydantic v2 field alias handling

# ---------- helpers ----------
def load_raw_flights() -> List[dict]:
    if not FLIGHTS_FILE.exists():
        return []
    return json.loads(FLIGHTS_FILE.read_text(encoding="utf-8"))

def find_flight_by_id(flight_id: str) -> Optional[dict]:
    raw = load_raw_flights()
    for f in raw:
        if f.get("id") == flight_id:
            return f
    return None

def validate_and_update_availability(flight_dict: dict):
    # ensure seats are boolean and normalized
    for s in flight_dict.get("seats", []):
        s["available"] = bool(s.get("available", False))

# --------- Routes ----------

@router.get("/search")
def search_flights(origin: str, destination: str, date: str):
    """
    Example: GET /flights/search?origin=Dubai&destination=Kolkata&date=2020-02-06
    Returns list of flights matching origin/destination/date (case-insensitive).
    """
    raw = load_raw_flights()
    origin = origin.lower()
    destination = destination.lower()
    results = []
    for f in raw:
        if (f.get("from", "").lower() == origin and
            f.get("to", "").lower() == destination and
            f.get("date", "") == date):
            # validate and include
            validate_and_update_availability(f)
            results.append(f)
    return {"flights": results}


@router.get("/{flight_id}")
def get_flight(flight_id: str):
    flight = find_flight_by_id(flight_id)
    if not flight:
        raise HTTPException(status_code=404, detail="Flight not found")
    validate_and_update_availability(flight)
    return flight


@router.get("/{flight_id}/seatmap")
def get_seatmap(flight_id: str):
    """
    Returns the seat list for a flight. (You can transform to grid in frontend.)
    """
    flight = find_flight_by_id(flight_id)
    if not flight:
        raise HTTPException(status_code=404, detail="Flight not found")
    seats = flight.get("seats", [])
    return {"flight_id": flight_id, "seats": seats}


# Hold request model
class HoldRequest(BaseModel):
    seat_no: str
    session_id: Optional[str] = None
    hold_minutes: Optional[int] = 10
    passenger_name: Optional[str] = None

class HoldResponse(BaseModel):
    hold_id: str
    flight_id: str
    seat_no: str
    expires_at: str
    status: str

@router.post("/{flight_id}/hold", response_model=HoldResponse)
def hold_seat(flight_id: str, payload: HoldRequest = Body(...)):
    """
    Hold a seat for short TTL (default 10 minutes).
    POST /flights/{flight_id}/hold
    body: { "seat_no": "1C", "session_id": "sess123", "passenger_name": "Astha" }
    """
    flight = find_flight_by_id(flight_id)
    if not flight:
        raise HTTPException(status_code=404, detail="Flight not found")

    # find seat
    seat_no = payload.seat_no
    seat_obj = None
    for s in flight.get("seats", []):
        if s.get("seat_no") == seat_no:
            seat_obj = s
            break

    if not seat_obj:
        raise HTTPException(status_code=404, detail="Seat not found")

    if not seat_obj.get("available", False):
        raise HTTPException(status_code=400, detail="Seat not available")

    # reserve in-memory (for demo)
    hold_id = str(uuid.uuid4())
    expires_at = datetime.utcnow() + timedelta(minutes=payload.hold_minutes or 10)

    HOLDS[hold_id] = {
        "hold_id": hold_id,
        "flight_id": flight_id,
        "seat_no": seat_no,
        "session_id": payload.session_id,
        "passenger_name": payload.passenger_name,
        "expires_at": expires_at.isoformat(),
        "status": "held"
    }
    HOLDS_EXPIRY[hold_id] = expires_at

    # mark seat temporarily unavailable in in-memory structure
    # Note: this does not persist to flights.json; for demo purposes only.
    seat_obj["available"] = False

    return HoldResponse(
        hold_id=hold_id,
        flight_id=flight_id,
        seat_no=seat_no,
        expires_at=expires_at.isoformat(),
        status="held"
    )

# optional: free expired holds (simple sweep)
@router.post("/sweep-expired")
def sweep_expired():
    now = datetime.utcnow()
    removed = []
    for hid, exp in list(HOLDS_EXPIRY.items()):
        if exp < now:
            # free seat in flight
            hold = HOLDS.get(hid)
            if hold:
                f = find_flight_by_id(hold["flight_id"])
                if f:
                    for s in f.get("seats", []):
                        if s.get("seat_no") == hold["seat_no"]:
                            s["available"] = True
                            break
            HOLDS.pop(hid, None)
            HOLDS_EXPIRY.pop(hid, None)
            removed.append(hid)
    return {"removed": removed}
