from fastapi import FastAPI
from typing import Dict, Any
import json
import os

app = FastAPI(title="Flight Ticketing MCP Server")

TOOLS_DIR = os.path.join(os.path.dirname(__file__), "tools")

# -----------------------------
# Utility: Load Tool Schemas
# -----------------------------

def load_tool_schema(tool_name: str) -> Dict[str, Any]:
    path = os.path.join(TOOLS_DIR, f"{tool_name}.json")
    with open(path, "r") as f:
        return json.load(f)

# -----------------------------
# MCP Tool Endpoints
# -----------------------------

@app.post("/searchFlights")
def search_flights(payload: Dict[str, Any]):
    """
    Mock flight search tool
    """
    return {
        "status": "success",
        "flights": [
            {
                "offerId": "FLIGHT123",
                "origin": payload.get("origin"),
                "destination": payload.get("destination"),
                "price": 5200,
                "currency": "USD",
                "cabinClass": payload.get("cabinClass", "economy")
            }
        ]
    }


@app.post("/getSeatMap")
def get_seat_map(payload: Dict[str, Any]):
    return {
        "status": "success",
        "offerId": payload.get("offerId"),
        "seats": [
            {"seat": "12A", "available": True},
            {"seat": "12B", "available": False},
            {"seat": "12C", "available": True}
        ]
    }


@app.post("/selectSeat")
def select_seat(payload: Dict[str, Any]):
    return {
        "status": "success",
        "message": f"Seat {payload.get('seatNumber')} reserved for passenger {payload.get('passengerId')}"
    }


@app.post("/holdFlight")
def hold_flight(payload: Dict[str, Any]):
    return {
        "status": "success",
        "offerId": payload.get("offerId"),
        "holdExpiresIn": payload.get("expireSeconds", 900)
    }


@app.post("/bookFlight")
def book_flight(payload: Dict[str, Any]):
    return {
        "status": "success",
        "bookingId": "BOOKING789",
        "offerId": payload.get("offerId"),
        "passengers": payload.get("passengers"),
        "message": "Flight booked successfully"
    }


@app.get("/tools")
def list_tools():
    """Expose tool schemas for MCP clients"""
    tools = {}
    for file in os.listdir(TOOLS_DIR):
        if file.endswith(".json"):
            name = file.replace(".json", "")
            tools[name] = load_tool_schema(name)
    return tools
