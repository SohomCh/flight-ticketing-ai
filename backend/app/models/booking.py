
# backend/app/models/booking.py
from typing import Literal, Optional
from pydantic import BaseModel, EmailStr


class Passenger(BaseModel):
    full_name: str
    email: EmailStr
    phone: Optional[str] = None


class BookingCreate(BaseModel):
    flight_id: str
    seat_no: str
    passenger: Passenger


class Booking(BaseModel):
    booking_id: str
    flight_id: str
    seat_no: str
    passenger: Passenger

    status: Literal["HOLD", "CONFIRMED", "CANCELLED"]
    pnr: str
    total_price: int
