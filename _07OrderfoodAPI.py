from _07Orderfood import *
from fastapi import FastAPI
import webbrowser
import uvicorn

app = FastAPI()

def create_system ():
    print("--- 1. Setting up Environment ---")
    airline = Airline("Thai Airways", "Thailand")
    food_menu = FlightFood("Pad Thai", 150.0, "Economy")
    seat = Economy("12A")
    flight_seat = FlightSeat(seat)
    flight_seat.assigh_passenger("John Doe")  # ชื่อต้องตรงกับ passenger ด้านล่าง
    
    # บัตรเครดิตมีเงิน 1000 บาท รหัส "1234"
    payment = CardPayment(1000.0, "1234") 

    flight = FlightInstance("Boeing 777", "TG123", "BKK", "CNX")
    flight.add_flight_food(food_menu)
    flight.add_flight_seat(flight_seat)

    print("--- 2. Setting up Passenger & Booking ---")
    booking = Booking("John Doe","PNR12345", 2500.0, "Economy", flight)
    
    # อัปเดตสถานะเป็น CHECKDIN และ PAID เพื่อให้สั่งอาหารได้
    booking.update_status(BookingStatus.CHECKDIN, PaymentStatus.PAID)

    passenger = Passenger("John", "Doe")
    passenger.add_booking(booking)
    passenger.add_payment(payment)
    
    airline.add_passenger(passenger)
    return airline



@app.post ("/buyfood/{passenger_name}/{pnr}/{food_name}/{quantity}/{payment_type}/{pin}")
def buy_food (passenger_name:str,pnr:str, food_name:str, quantity:int, payment_type:str, pin:str) :
    try: 
        airline.buy_food(passenger_name,pnr, food_name, quantity, payment_type, pin)
        return f"{passenger_name} order {food_name} success!"
    except Exception as e : return f"Fail : {e}"


@app.get ("/getfoodtransaction/{pnr}/")
def get_food_transaction (pnr) :
    try: return airline.get_food_transaction (pnr)
    except Exception as e : return f"Fail : {e}"

airline = create_system ()

if __name__ == "__main__" :
    print (type(airline))
    webbrowser.open("http://127.0.0.1:8000/docs")
    uvicorn.run ("_07OrderfoodAPI:app",host = "127.0.0.1", port = 8000,reload = True)
    