import json
from pathlib import Path
from app.models.flights import Flight

DATA_PATH = Path(__file__).parent / "flights.json"

with open(DATA_PATH, "r", encoding="utf-8") as f:
    raw_flights = json.load(f)

# Validate + normalize JSON into Pydantic models
flights: list[Flight] = [
    Flight.model_validate(f) for f in raw_flights
]
