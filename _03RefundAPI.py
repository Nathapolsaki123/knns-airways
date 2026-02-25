from  fastapi import FastAPI
import uvicorn
import webbrowser
from _03Refund import *

app = FastAPI()
airline = Airline("KNNS airways","Thailand")

@app.post ("/requestRefund/{pnr}")
def requestRefund (pnr:str):
    if len(pnr)!=6 : return f"Error occurred: Wrong Len"
    try :
        airline.request_refund (pnr)
        return "Refund Booking: " +pnr+ " Is Complete"
    except Exception as e:
        return f"Error occurred: {e}"

@app.get ("/getBookkingStatus/{pnr}")
def getBookkingStatus (pnr:str):
    if len(pnr)!=6 : return f"Error occurred: Wrong Len"
    try :
        bookings = airline.find_booking_by_pnr(pnr)
        return "Booking: " + pnr + ", Status --> " + bookings.get_status()
    except Exception as e:
        return f"Error occurred: {e}"

def create_system () :
    airline = Airline("KNNS airways","Thailand")
    passenger = Passenger("John", "Doe")
    booking = Booking("PNR123", 5000.0, "Bussiness" )
    flight = Flight("Boeig747","123","Bangkok","Chaingmai")
    booking.add_flight (flight)
    passenger.add_booking (booking)
    airline.add_passenger (passenger)
    airline.request_refund("PNR123")

create_system ()

if __name__ == "__main__" :
    webbrowser.open ("http://127.0.0.1:8000/docs")
    uvicorn.run ("06Refund:app",host = "127.0.0.1",port = 8000, reload=True )