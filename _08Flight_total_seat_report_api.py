from fastapi import FastAPI, HTTPException
from datetime import datetime

# import class จากไฟล์หลัก
from _08Flight_total_seat_report import *

app = FastAPI(title="Airline API")

# =========================
# SYSTEM INIT (เหมือน __main__)
# =========================

airline = Airline("Tempest Airways")

airplane1 = Airplane("B737", "HS-TST", 10, 4)
airline.add_airplane(airplane1)

flight1 = Flight("TG100", "Bangkok", "Tokyo")
airline.add_flight(flight1)

fi1 = FlightInstance(
    "TG100",
    "Bangkok",
    "Tokyo",
    airplane1,
    datetime(2026,3,10,8,0),
    datetime(2026,3,10,16,0),
    15000
)

fi2 = FlightInstance(
    "TG100",
    "Bangkok",
    "Tokyo",
    airplane1,
    datetime(2026,3,11,8,0),
    datetime(2026,3,11,16,0),
    15000
)

flight1.flight_instance_list.append(fi1)
flight1.flight_instance_list.append(fi2)

for i in range(1,11):
    fi1.add_seat(Economy(f"E{i}"))
    fi2.add_seat(Economy(f"E{i}"))

for i in range(1,5):
    fi1.add_seat(Business(f"B{i}"))
    fi2.add_seat(Business(f"B{i}"))

fi1._FlightInstance__economy_seat_available -= 4
fi1._FlightInstance__business_seat_available -= 1

fi2._FlightInstance__economy_seat_available -= 6
fi2._FlightInstance__business_seat_available -= 2


# =========================
# ENDPOINTS
# =========================

@app.get("/")
def root():
    return {"message": "Airline API Running"}


@app.get("/flight/{flight_no}/seat-report")
def seat_report(flight_no: str):

    try:
        report = airline.create_flight_seat_report(flight_no)
        return {
            "flight_no": flight_no,
            "report": report
        }

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))