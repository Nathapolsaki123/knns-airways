from _07Orderfood import *
from fastapi import FastAPI
import webbrowser
import uvicorn

app = FastAPI()

def create_system ():
    print("--- 1. Setting up Environment ---")
    airline = Airline("Thai Airways")
    food_menu = FlightFood("Pad Thai", 150.0, "Economy")

    #ตรงนี้น่าจะต้องแก้ไข เปลี่ยนเป็นการ์ดเลย
    card = Card("1234",1000.0 )  
    passenger = Guest("1234", "John", "john@email.com", card)

    eco_seat = Economy("12A")  
    flight_seat = FlightSeat(eco_seat)
    flight_seat.assigh_passenger(passenger)  

    airplane = Airplane("Boeing 777", "B777-123", 200, 50)  

    flight_blueprint = Flight("TG123", "BKK", "CNX")
    
    flight_instance = flight_blueprint.crete_flight_instance(
        airplane, 
        datetime.now(), 
        datetime.now(), 
        5000, 
        FlightStatus.SCHEDULED
    )

    flight_instance.add_flight_food(food_menu)
    flight_instance.add_assigned_seat(flight_seat)

    print("--- 2. Setting up Passenger & Booking ---")
    booking = Booking("PNR12345", passenger, flight_instance,"Economy", 1)

    booking.update_status(BookingStatus.CHECKDIN, PaymentStatus.PAID)
    passenger.add_booking(booking)
    airline.add_passenger(passenger)
    airline.add_airplane(airplane)
    return airline



@app.post ("/buyfood/{passenger_id}/{pnr}/{food_name}/{quantity}/{payment_type}/{pin}")
def buy_food (passenger_id:str,pnr:str, food_name:str, quantity:int, payment_type:str, pin:str) :
    try: 
        airline.buy_food(passenger_id,pnr, food_name, quantity, payment_type, pin)
        return f"{passenger_id} order {food_name} success!"
    except Exception as e : return f"Fail : {e}"


@app.get ("/getfoodtransaction/{pnr}/")
def get_food_transaction_list (pnr) :
    try: return airline.get_food_transaction_list (pnr)
    except Exception as e : return f"Fail : {e}"

airline = create_system ()

if __name__ == "__main__" :
    print (type(airline))
    webbrowser.open("http://127.0.0.1:8000/docs")
    uvicorn.run ("_07OrderfoodAPI:app",host = "127.0.0.1", port = 8000,reload = True)
    