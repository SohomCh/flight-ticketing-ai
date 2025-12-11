# app/models/booking.py
from __future__ import annotations
from typing import Optional
from pydantic import BaseModel, Field
from pydantic import ConfigDict

class BaseModelV2(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

class Passenger(BaseModelV2):
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    age: Optional[int] = None

class BookingRequest(BaseModelV2):
    flight_id: str
    seat_no: str
    passenger: Passenger
    payment_method: Optional[str] = None

class BookingResponse(BaseModelV2):
    booking_id: str
    pnr: str
    status: str
    flight_id: str
    seat_no: str
