# backend/app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes.flights import router as flights_router
from app.routes.booking import router as booking_router
from app.routes.seats import router as seat_router

app = FastAPI(title="Flight Booking API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # change to allowed origins in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# include routers with prefixes
app.include_router(flights_router, prefix="/flights")
app.include_router(booking_router, prefix="/booking")
app.include_router(seat_router, prefix="/seat")


@app.get("/")
def health():
    return {"status": "ok"}
