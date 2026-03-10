
from fastapi import FastAPI, HTTPException
from datetime import datetime
from _01Checkin import *

app = FastAPI(title="Airline Check-in API")

# =========================
# SYSTEM INIT
# =========================

airline = Airline("Tempest Airways")

p1 = Passenger("P001","John Smith","john@email.com")
p2 = Passenger("P002","Alice","alice@email.com")

airline.add_passenger(p1)
airline.add_passenger(p2)

flight = FlightInstance(
    "TG101",
    "BKK",
    "NRT",
    "Boeing777",
    datetime(2026,3,10,10,30),
    datetime(2026,3,10,18,30),
    15000
)

airline.add_flight(flight)

for i in range(1,6):
    flight.add_seat(Economy(f"A{i:02d}"))

flight.add_seat(Business("B01"))
flight.add_seat(Business("B02"))

booking = Booking("PNR001",p1,flight,"Economy",2)

p1.add_booking(booking)
airline.add_booking(booking)

booking.confirmBooking()

# =========================
# API
# =========================

@app.get("/")
def root():
    return {"message":"Airline API running"}

# เปิด check-in
@app.post("/flight/open-checkin")
def open_checkin():
    flight.openCheckIn()
    return {"message":"Check-in opened"}

# ดูที่นั่งว่าง
@app.get("/flight/seats")
def available_seats(seat_class:str=None):

    if seat_class:
        seats = flight.get_available_seat(seat_class)
    else:
        seats = flight.remaining_seat_list

    return {
        "available_seats":[s.seat_no for s in seats]
    }

# check-in
@app.post("/checkin")
def checkin(passenger_id:str, pnr:str):

    try:
        airline.check_in_passenger(passenger_id,pnr)

        seats = flight.get_available_seat("Economy")

        return {
            "message":"Check-in success",
            "available_seats":[s.seat_no for s in seats]
        }

    except Exception as e:
        raise HTTPException(status_code=400,detail=str(e))

# เลือกที่นั่ง
@app.post("/choose-seat")
def choose_seat(passenger_id:str, pnr:str, seats:str):
    try:
        tickets = airline.choose_seat(passenger_id,pnr,seats)
        return {
            "tickets":[
                {
                    "flight":t._Ticket__flight_no,
                    "passenger":t._Ticket__passenger.name,
                    "origin":t._Ticket__origin,
                    "destination":t._Ticket__destination,
                    "departure":t._Ticket__departure_time,
                    "seat":t._Ticket__seat.seat_no
                }
                for t in tickets
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=400,detail=str(e))


# สร้าง booking (ใช้ใน testcase 11,12)
@app.post("/booking")
def create_booking(passenger_id:str,pnr:str,seat_class:str,seat_amount:int):

    passenger = airline.search_passenger_by_id(passenger_id)

    if passenger is None:
        raise HTTPException(status_code=404,detail="Passenger not found")

    booking = Booking(pnr,passenger,flight,seat_class,seat_amount)

    passenger.add_booking(booking)
    airline.add_booking(booking)

    booking.confirmBooking()

    return {
        "message":"Booking created",
        "pnr":pnr
    }
