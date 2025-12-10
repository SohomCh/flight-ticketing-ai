
# backend/app/models/flights.py
from typing import List, Optional, Literal
from pydantic import BaseModel, Field


class Seat(BaseModel):
    seat_no: str
    type: Literal["window", "middle", "aisle"]
    available: bool
    price: int


class Flight(BaseModel):
    id: str
    mode: Literal["flight"]

    # "from" and "to" are reserved-ish in Python, so we use aliases
    origin: str = Field(alias="from")
    destination: str = Field(alias="to")

    date: str            # you can later change to datetime.date
    departure: str       # or time
    arrival: str

    price: int
    airline: str
    flight_number: str

    stops: int
    layovers: List[Optional[str]]
    total_time: str

    seats: List[Seat]

    class Config:
        populate_by_name = True  # allows using origin/destination in code, "from"/"to" in JSON
