from  fastapi import FastAPI
import uvicorn
import webbrowser
from _03Refund import *

app = FastAPI()
airline = Airline("KNNS airways","Thailand")

@app.post ("/requestRefund/{pnr}")
def requestRefund (pnr:str):
    airline.request_refund (pnr)
    return "Refund Booking: " +pnr+ " Is Complete"

@app.get ("/getBookkingStatus/{pnr}")
def getBookkingStatus (pnr:str):
    bookings = airline.find_booking_by_pnr(pnr)
    return "Booking: " + pnr + ", Status --> " + bookings.get_status()

def create_system () :
    passenger = Passenger("John", "Doe")
    booking = Booking("PNR123", 5000.0)
    passenger.add_booking (booking)
    airline.add_passenger (passenger)

create_system ()

if __name__ == "__main__" :
    webbrowser.open ("http://127.0.0.1:8000/docs")
    uvicorn.run ("06Refund:app",host = "127.0.0.1",port = 8000, reload=True )