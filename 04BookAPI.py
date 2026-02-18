from datetime import datetime
from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn

app = FastAPI()

class Passenger:
    def __init__(self, passenger_id: str, first_name: str, last_name: str):
        self.__passenger_id = passenger_id
        self.__first_name = first_name
        self.__last_name = last_name
        self.__bookList = []
        self.__point = 0

    def get_passenger_id(self):
        return self.__passenger_id

    def add_book(self,book):
        self.__bookList.append(book)
    
    def add_point(self,point):     
        self.__point += point
    
    def find_book_by_pnr(self,pnr):
        for b in self.__bookList:
            if pnr == b.get_pnr():
                return b
        return False
    
class Flight:
    def __init__(self, flight_no: str, origin: str, destination: str, datetime: str):
        self.__flight_no = flight_no
        self.__origin = origin
        self.__destination = destination
        self.__datetime = datetime
        self.__BseatAmount = 50
        self.__EseatAmount = 50

    def new_seat_amount(self,seatType):
        if seatType == "Business":
            self.__BseatAmount -= 1
        elif seatType == "Economy":
            self.__EseatAmount -= 1

    def check_seat_availability(self,seatType):
        if seatType == "Business":
            return self.__BseatAmount > 0
        elif seatType == "Economy":
            return self.__EseatAmount > 0
        
    def get_id(self):
        return self.__flight_no


class Payment:
    def __init__(self):
        self.__status = "Pending"

    def pay(self,amount):
        if amount <= 0:
            self.__status = "Unpaid"
            return False
        else:
            self.__status = "Paid"
            return True


class Book:
    def __init__(self, pnr: str, passenger: str, flight: Flight, seatType: str, seatAmount: int, dateTime: str, price: int):
        self.__pnr = pnr
        self.__passenger = passenger
        self.__flight = flight
        self.__seatType = None
        self.__seatAmount = 0
        self.__status = "Pending"
        self.__booking_date = dateTime
        self.__maxWeight = 0
        self.__fare = 0

    def get_pnr(self):
        return self.__pnr

    def confirm(self):
        self.__status = "Confirmed"

    def cancel(self):
        self.__status = "Cancelled"


class AirlineController:
    def __init__(self, name: str):
        self.__name = name
        self.__currentPassenger = None
        self.__passengers = []
        self.__flights = []

    def add_passenger(self, passenger: Passenger):
        self.__passengers.append(passenger)
    
    def add_Flight(self, Flight: Flight):
        self.__flights.append(Flight)

    # Login
    def login(self, passenger_id: str) -> bool:
        for p in self.__passengers:
            if p.get_passenger_id() == passenger_id:
                self.__currentPassenger = p
                return True
        return False

    def find_flight(self, flight_no: str):
        for f in self.__flights:
            if f.get_id() == flight_no:
                return f
        return False
    
    def calculate_fare(self,seatType):
        if seatType == "Economy":
            return 100
        elif seatType == "Business":
            return 200
        else:
            return False
    

    def booking(self,pnr: str, name: str, flight_no: str, seatType: str, seatAmount: int, dateTime: str):
        received_flight = self.find_flight(flight_no)
        if received_flight == False:
            raise Exception("No flight")
        else:
            if received_flight.check_seat_availability(seatType) == False:
                raise Exception("No available")
            else:
                price = self.calculate_fare(seatType)
                if price == False:
                    raise Exception("Can't calculate Price")
                else:
                    self.__currentPassenger.add_book(Book(pnr,name, received_flight, seatType, seatAmount, dateTime, price))
                    currentBook = self.__currentPassenger.find_book_by_pnr(pnr)
                    ValidatePayment = payment.pay(price)
                    if ValidatePayment == False:
                        currentBook.cancel()
                    else:
                        currentBook.confirm()
                        self.__currentPassenger.add_point(100)

airline_system = AirlineController("Thai Airways")
payment = Payment()

# 2. Create Dummy Data
flight1 = Flight("TG101", "Bangkok", "Tokyo", "2024-05-20")
passenger1 = Passenger("12345", "Somsak", "Jaidee")

# 3. Add Data to Controller
airline_system.add_Flight(flight1)
airline_system.add_passenger(passenger1)

# 4. Simulate Login (Required because booking() uses self.__currentPassenger)
airline_system.login("12345")

@app.post("/booking/{pnr}/{name}/{flight_no}/{seatType}/{seatAmount}/{dateTime}")
def bookings(pnr:str, name:str, flight_no:str, seatType:str, seatAmount:str, dateTime:str):
    try :
        airline_system.booking(pnr, name, flight_no, seatType, seatAmount, dateTime)
        return {"name" : name,"flight_no" : flight_no, "seatType" : seatType, "seatAmount" : seatAmount, "dateTime" : dateTime}
    except Exception as e :
        return f"error {e} "

payment = Payment()


if __name__ == "__main__":
    uvicorn.run("04BookAPI:app", host="127.0.0.1", port=8000, log_level="info")

