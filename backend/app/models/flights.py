# app/models/flights.py
from __future__ import annotations
from typing import List, Optional
from pydantic import BaseModel, Field
from pydantic import ConfigDict

# Pydantic v2 style config (recommended)
class BaseModelV2(BaseModel):
    model_config = ConfigDict(populate_by_name=True)  # allow alias "from" → from_

class Seat(BaseModelV2):
    seat_no: str
    type: str
    available: bool
    price: float

class Flight(BaseModelV2):
    id: str
    mode: str
    
    # alias from → from_
    from_: str = Field(..., alias="from")
    
    to: str
    date: str
    departure: Optional[str] = None
    arrival: Optional[str] = None
    
    price: float
    airline: Optional[str] = None
    flight_number: Optional[str] = None
    
    stops: Optional[int] = 0
    layovers: Optional[List[Optional[str]]] = []
    total_time: Optional[str] = None
    
    seats: List[Seat] = []

# Seat selection
class SeatSelection(BaseModelV2):
    flight_id: str = Field(..., alias="flight_id")
    seat_no: str

# Hold request
class HoldRequest(BaseModelV2):
    flight_id: str
    seat_no: str
    session_id: Optional[str] = None
    hold_ttl_seconds: Optional[int] = 600

class HoldResponse(BaseModelV2):
    hold_id: str
    status: str
    expires_at: Optional[str] = None

class SeatHoldResponse(BaseModelV2):
    hold_id: str
    flight_id: str
    seat_no: str
    expires_at: int
    status: str



