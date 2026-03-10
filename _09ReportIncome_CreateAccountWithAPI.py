from datetime import datetime
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn
import random
from enum import Enum


app = FastAPI()

class BookingStatus(Enum):
    PENDING = "Pending"
    CONFIRMED = "Confirmed"
    CANCELLED = "Cancelled"
    CHECKED_IN = "Checkedin"
    NO_SHOW = "Noshow"

class PaymentStatus(Enum):
    PAID = "Paid"
    UNPAID = "Unpaid"
    REFUNDED = "Refunded"

class FlightStatus(Enum):
    SCHEDULED = "Scheduled"
    CHECKIN_OPEN = "Checkinopen"
    BOARDING = "Boarding"
    DEPARTED = "Departed"
    ARRIVED = "Arrived"
    CANCELLED = "Cancelled"

class Passenger:
    id = 1
    def __init__(self, name: str, Email: str):
        self.__passenger_id = f"{Passenger.id:05d}" 
        self.__name = name
        self.__email = Email
        self.__card = None
        self.__booking = []
        self.__refunded_total = 0
        self.__is_blacklisted = False
        self.__blacklist_time = None
        self.__notification = []
        Passenger.id += 1

    def add_book(self,book):
        self.__booking.append(book)
    
    def add_card(self,card):
        self.__card = card

    def get_passenger_id(self):
        return self.__passenger_id

    def get_passenger_name(self):
        return self.__name
    
    def get_passenger_email(self):
        return self.__email
    
    def get_card(self):
        return self.__card
    
    def get_refunded_total(self):
        return self.__refunded_total
    
    def get_is_blacklisted(self):
        return self.__is_blacklisted
    
    def get_blacklist_time(self):
        return self.__blacklist_time
    
    def get_book_by_pnr(self, pnr):
        for b in self.__booking:
            if b.get_pnr() == pnr:
                return b
        raise HTTPException(
            status_code=404, 
            detail=f"Did not find book with pnr {pnr} in id {self.__passenger_id}"
        )
    
    def get_data(self):
        return {
                "passenger_id": self.__passenger_id,
                "name": self.__name,                
                "email": self.__email,
                "card_pin": self.__card.get_money(),
                "refunded_total": self.__refunded_total,
                "is_blacklisted": self.__is_blacklisted,
                "blacklist_time": self.__blacklist_time
                }
    
    def get_booking(self):
        count = 1
        all_book = {}
        for b in self.__booking:
            all_book[count] = b.get_data()
            count+=1
        return all_book

    
class Member(Passenger):
    def __init__(self, name: str, Email: str):
        super().__init__(name, Email)
        self.__point = 0

    def get_point(self):
        return self.__point
    
    def change_point(self, point):
        self.__point += point
    
class Card:
    def __init__(self,pin: str,money: float):
        self.__pin = pin
        self.__money = money
    
    def get_pin(self):
        return self.__pin
    
    def get_money(self):
        return self.__money
    
    def pay_money(self, money):
        self.__money -= money
    
class Guest(Passenger):
    identifier = "Guest"
    def __init__(self, name: str, Email:str):
        super().__init__(name, Email)
        self.__discount = 1
        self.__extra_weight = 0
        self.__annual_fee = 0
    
    def get_discount(self):
        return self.__discount

    def get_extra_weight(self):
        return self.__extra_weight
    
    def get_annual_fee(self):
        return self.__annual_fee
    
class Silver(Member):
    identifier = "Silver"
    def __init__(self, name: str, Email:str):
        super().__init__(name, Email)
        self.__discount = 0.95
        self.__extra_weight = 5
        self.__annual_fee = 200
    
    def get_discount(self):
        return self.__discount

    def get_extra_weight(self):
        return self.__extra_weight
    
    def get_annual_fee(self):
        return self.__annual_fee

class Gold(Member):
    identifier = "Gold"
    def __init__(self, name: str, Email:str):
        super().__init__(name, Email)
        self.__discount = 0.9
        self.__extra_weight = 10
        self.__annual_fee = 300
    
    def get_discount(self):
        return self.__discount

    def get_extra_weight(self):
        return self.__extra_weight
    
    def get_annual_fee(self):
        return self.__annual_fee
    
class Platinum(Member):
    identifier = "Platinum"
    def __init__(self, name: str, Email:str):
        super().__init__(name, Email)
        self.__discount = 0.85
        self.__extra_weight = 20
        self.__annual_fee = 500
    
    def get_discount(self):
        return self.__discount

    def get_extra_weight(self):
        return self.__extra_weight
    
    def get_annual_fee(self):
        return self.__annual_fee
    
class Payment:
    def get_payment_type(self, payment_type):
        for cls in Payment.__subclasses__():
            if getattr(cls, "identifier", None) == payment_type:
                return cls
            
        raise HTTPException(
            status_code=404,
            detail=f"Payment method invalid"
            )

class PayByCard(Payment):
    identifier = "PayByCard"

    @classmethod
    def validate(cls,received_passenger,  validate_object=None):
        card = received_passenger.get_card()
        if card.get_pin() != validate_object:
            raise HTTPException(
            status_code=404,
            detail=f"Incorrect Pin"
            )
        else:
            return True

    @classmethod  
    def pay(cls, received_passenger, price):
        card = received_passenger.get_card()
        if price > card.get_money():
                raise HTTPException(
                status_code=404,
                detail=f"Not enough money"
                )
        else:
            card = received_passenger.get_card()
            card.pay_money(price)
            is_member = issubclass(type(received_passenger), Member)
            if is_member == True:
                received_passenger.change_point(price/25)
            return True
        



class PayByPoint(Payment):
    identifier = "PayByPoint"

    @classmethod
    def validate(cls,received_passenger, validate_object=None):
        is_member = issubclass(type(received_passenger), Member)

        if is_member == False:
            raise HTTPException(
                status_code=404,
                detail=f"You cannot pay by point if you are not a member"
                )
        else:
            return True
        
    @classmethod       
    def pay(cls, received_passenger, price):
        if price > received_passenger.get_point():
                raise HTTPException(
                status_code=404,
                detail=f"Not enough point"
                )
        else:
            received_passenger.change_point(-price)
            return True

class Transaction:
    def __init__(self, name: str, payment_type: str, amount: float):
        self.__sub_transaction = []
        self.__name = name
        self.__payment_type = payment_type
        self.__amount = amount

class SubTransaction:
    def __init__(self,name: str,payment_type: str, amount: float):
        self.__name = name
        self.__payment_type = payment_type
        self.__amount = amount

class Flight:
    def __init__(self, flight_no: str,origin: str, destination: str):
        self.__flight_no = flight_no
        self.__flight_instance_list = []
        self.__origin = origin 
        self.__destination = destination
        
        
    def get_flight_no(self):
        return self.__flight_no
    
    def get_flight_instance_list(self):
        return self.__flight_instance_list
    
    def get_origin(self):
        return self.__origin
    
    def get_destination(self):
        return self.__destination
    
    def create_flight_instance(self, airplane: Airplane , arrival_time: datetime, departure_time: datetime, price: float):
        new_flight = FlightInstance(self.__flight_no,airplane ,self.__origin, self.__destination, arrival_time, departure_time, price)
        self.__flight_instance_list.append(new_flight)

class FlightInstance():
    def __init__(self, flight_no: str, airplane: Airplane ,origin: str, destination: str, arrival_time: datetime, departure_time: datetime, price: float):
        self.__flight_no = flight_no
        self.__airplane = airplane
        self.__origin = origin 
        self.__destination = destination
        self.__arrival_time = arrival_time
        self.__departure_time = departure_time
        self.__economy_seat_available = airplane.get_economy_seat()
        self.__business_seat_available = airplane.get_business_seat()
        self.__remaining_seat_list = []
        self.__assigned_seat_list = []
        self.__food_list = []
        self.__price = price
        self.__total_income = 0
        self.__flight_status = FlightStatus.SCHEDULED

    def get_origin(self):
        return self.__origin
    
    def get_destination(self):
        return self.__destination

    def get_arrival_time(self):
        return self.__arrival_time

    def get_departure_time(self):
        return self.__departure_time
    
    def get_airplane(self):
        return self.__airplane

    def get_price(self):
        return self.__price
    
    def get_flight_no(self):
        return self.__flight_no

    def get_total_income(self):
        return self.__total_income
    
    def update_total_income(self, amount):
        self.__total_income += amount
    
    def new_seat_amount(self,seat_type,seat_amount):
        if seat_type == "Business":
            return self.__business_seat_available - seat_amount
        elif seat_type == "Economy":
            return self.__economy_seat_available - seat_amount

    def check_seat_availability(self,seat_type,seat_amount):
        if seat_type == "Business":
            check =  self.__business_seat_available >= seat_amount
        elif seat_type == "Economy":
            check =  self.__economy_seat_available >= seat_amount
        else:
            check = False
        
        if check == False:
            raise HTTPException(
                    status_code=404,
                    detail=f"There is no seat_type {seat_type} that is still available for {seat_amount} seat"
                    )
        

class Airplane:
    def __init__(self, model: str, economy_seat_amount: int, business_seat_amount: int):
        self.__model = model
        self.__economy_seat_amount = economy_seat_amount
        self.__business_seat_amount = business_seat_amount

    def get_economy_seat(self):
        return self.__economy_seat_amount
    
    def get_business_seat(self):
        return self.__business_seat_amount
    

class Book:

    _used_pnr = set()

    def __init__(self, passenger: Passenger, flight_instance: FlightInstance, seat_type: str, seat_amount: int, max_weight: int, price: float):
        self.__pnr = self.generate_pnr()
        self.__passenger = passenger
        self.__flight_instance = flight_instance
        self.__seat_type = seat_type
        self.__seat_amount = seat_amount
        self.__status = BookingStatus.PENDING
        self.__payment_status = PaymentStatus.UNPAID
        self.__booking_date = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
        self.__max_weight = max_weight
        self.__fare = price
        self.__transaction = None

    def get_data(self):
        return {
                "pnr": self.__pnr,
                "passenger": self.__passenger.get_passenger_name(),                
                "flight_no": self.__flight_instance.get_flight_no(),
                "seat_type": self.__seat_type,
                "seat_amount": self.__seat_amount,
                "status": self.__status,
                "payment_status": self.__payment_status,
                "booking_date": self.__booking_date,
                "max_weight": self.__max_weight,
                "fare": self.__fare
                }

    def generate_pnr(self):
        chars = "ABCDEFGHJKMNPQRSTUVWXYZ23456789"
        
        while True:
            candidate_pnr = ''.join(random.choices(chars, k=6))
            
            if candidate_pnr not in Book._used_pnr:
                
                Book._used_pnr.add(candidate_pnr)
                return candidate_pnr

    def get_pnr(self):
        return self.__pnr

    def get_passenger(self):
        return self.__passenger
    
    def get_flight_instance(self):
        return self.__flight_instance

    def change_status(self, status):
        self.__status = status

    def change_payment_status(self, status):
        self.__payment_status = status

    def get_payment_status(self):
        return self.__payment_status

    def get_fare(self):
        return self.__fare

    def add_transaction(self, name: str, payment_type: str, amount: float):
        new_transaction = Transaction(name,payment_type,amount)
        self.__transaction = new_transaction

    def validate_bookb(self):
        if self.get_payment_status() != PaymentStatus.UNPAID:
            raise HTTPException(
            status_code=404,
            detail=f"You can't paid what you already paid or cancel"
            )
        else:
            return True


class AirlineController:
    def __init__(self, name: str):
        self.__name = name
        self.__passengers = []
        self.__bookings = []
        self.__airplanes = []
        self.__flights = []
        self.__blacklist = []

    def add_passenger(self, passenger: Passenger):
        self.__passengers.append(passenger)
    
    def add_Flight(self, Flight: Flight):
        self.__flights.append(Flight)

    def find_flight(self, flight_no: str):
        for f in self.__flights:
            if f.get_flight_no() == flight_no:
                return f
        raise HTTPException(
                status_code=404,
                detail=f"Did not found flight {flight_no}"
                )
    

    def validate_card_info(self, card_pin: str, money: float):
        if len(card_pin) != 6:
            raise HTTPException(
            status_code=404,
            detail=f"Pin need to be 6 digit, yours is {len(card_pin)} digit"
        )
        if money <= 0:
            raise HTTPException(
            status_code=404,
            detail=f"Your card need to have money more than 0"
        )
        return True


    def find_flight_instance(self, flight_no: str, arrival_time: datetime, departure_time:datetime):
        f = self.find_flight(flight_no)
        for ff in f.get_flight_instance_list():
            if ff.get_arrival_time() == arrival_time and ff.get_departure_time() == departure_time:
                return ff
        raise HTTPException(
        status_code=404,
        detail=f"Did not found flight {flight_no} that depart at {departure_time} and arrive at {arrival_time}"
        )
    
    def find_passenger(self, id: str):
        for p in self.__passengers:
            if p.get_passenger_id() == id:
                return p
        raise HTTPException(
            status_code=404, 
            detail=f"Did not find passenger with id {id}"
        )
    
    def calculate_fare(self, flight_price: int, seat_type: str, seat_amount: int, discount: float):
        if seat_type == "Economy":
            seat_cost = 100
        elif seat_type == "Business":
            seat_cost = 300
        else:
            raise HTTPException(
                status_code=404,
                detail=f"Price cannot be calculate"
                )

        fare = (flight_price+(seat_cost*seat_amount))*discount
        return fare
    
    def pay_book(self,id: str, pnr: str, payment_method: str, validate_object: str = None):
        received_passenger = self.find_passenger(id)
        received_book = received_passenger.get_book_by_pnr(pnr)
        received_flight_instance = received_book.get_flight_instance()
        received_book.validate_book()

        payment_type = payment_system.get_payment_type(payment_method)

        payment_type.validate(received_passenger, validate_object)
        payment_type.pay(received_passenger, received_book.get_fare())
        received_flight_instance.update_total_income(received_book.get_fare())
        received_book.change_status(BookingStatus.CONFIRMED)
        received_book.change_payment_status(PaymentStatus.PAID)
        received_book.add_transaction("pay_for_booking", payment_method, received_book.get_fare())
        return received_book

        


    def booking(self,id: str, flight_no: str, arrival_time: str, departure_time: str, seat_type: str, seat_amount: int, ):
        received_passenger = self.find_passenger(id)
        if received_passenger.get_is_blacklisted():
            raise HTTPException(
                status_code=404,
                detail=f"You on the blacklist and cannot booking on this airline until your blacklist time is over"
                )
        try:
            date_arrival_time = datetime.strptime(arrival_time, "%d-%m-%Y %H:%M")
            date_departure_time = datetime.strptime(departure_time, "%d-%m-%Y %H:%M")
        except:
            raise HTTPException(
                status_code=404,
                detail=f"Date Format is wrong"
                )

        received_flight_instance = self.find_flight_instance(flight_no, date_arrival_time, date_departure_time)

        received_flight_instance.check_seat_availability(seat_type, seat_amount)
            
        received_flight_instance.new_seat_amount(seat_type, seat_amount)
        discount = received_passenger.get_discount()
        price = self.calculate_fare(received_flight_instance.get_price(),seat_type,seat_amount,discount)

        max_weight = received_passenger.get_extra_weight()
        new_book = Book(received_passenger, received_flight_instance, seat_type, seat_amount, max_weight, price)
        received_passenger.add_book(new_book)
        return new_book
        #dont forget to change formula to claculate weight because I used attribute weight in class Book (old patch)
    
    def create_income_report(self, flight_no: str):
        string = []
        total = 0
        f = self.find_flight(flight_no)
        header = f"Income report of flight number:{f.get_flight_no()}(from {f.get_origin()} to {f.get_destination()})"
        print(header)
        string.append(header)
        for ff in f.get_flight_instance_list():
            content = f" Flight that travel from {ff.get_departure_time()} to {ff.get_arrival_time()} has earned income of {ff.get_total_income()}"
            total += ff.get_total_income()
            print(content)
            string.append(content)
        string.append(f"Total income of flight: {f.get_flight_no()} is {total}")
        return string
    
    def get_account(self,tier: str,name: str,email: str):
        classes_to_check = Passenger.__subclasses__()
        
        while classes_to_check:
            # Take the first class out of the list to examine
            cls = classes_to_check.pop(0)
            
            # Check if this class matches our identifier
            # Using getattr is safer in case an intermediate subclass forgot to define 'identifier'
            if getattr(cls, "identifier", None) == tier:
                return cls(name, email) # Instantiate and return
                
            # Add any subclasses of THIS class to the end of our list to check later
            classes_to_check.extend(cls.__subclasses__())
            
        # If the loop finishes and we found nothing, raise the error
        raise HTTPException(
            status_code=404,
            detail=f"There is no {tier} tier in this airline"
        )

    def create_account(self, name: str,email: str,card_pin: str,money: float,tier: str):
        self.validate_card_info(card_pin, money)
        new_card = Card(card_pin, money)
        passenger = self.get_account(tier, name, email)
        passenger.add_card(new_card)
        if passenger.get_annual_fee() > new_card.get_money():#so if the passenger cant afford thier tier,the unique value will not be lost
            Passenger.id -= 1
        PayByCard.pay(passenger, passenger.get_annual_fee())
        self.add_passenger(passenger)
        return passenger
        

airline_system = AirlineController("Thai Airways")
payment_system = Payment()

# 2. Create Dummy Data
passenger1 = Silver("Somsak", "Jaidee@gmail.com")
card1 = Card("123456",700000)
passenger2 = Gold("Sexski", "taobin@gmail.com")
card2 = Card("456789",2000)
airplane1 = Airplane("B001",20,20)
airplane2 = Airplane("B002",30,10)
airplane3 = Airplane("B003",1,2)
airplane4 = Airplane("B004",10,10)

flight1 = Flight("TG101", "Bangkok", "Tokyo")
flight_instance1 = flight1.create_flight_instance(airplane1,  datetime(2025,1,10,10,0), datetime(2025,1,10,7,0), 3000)
flight_instance2 = flight1.create_flight_instance(airplane2,  datetime(2025,1,10,18,0), datetime(2025,1,10,15,0), 4000)
flight2 = Flight("TG102","Bangkok", "London")
flight_instance3 = flight2.create_flight_instance(airplane3,  datetime(2025,1,10,11,0), datetime(2025,1,10,6,0), 5000)
flight_instance4 = flight2.create_flight_instance(airplane4,  datetime(2025,3,10,19,0), datetime(2025,3,10,14,0), 6000)

# 3. Add Data to Controller
airline_system.add_Flight(flight1)
airline_system.add_Flight(flight2)

airline_system.add_passenger(passenger1)
airline_system.add_passenger(passenger2)

passenger1.add_card(card1)
passenger2.add_card(card2)


@app.post("/booking/{id}/{flight_no}/{arrival_time}/{departure_time}/{seat_type}/{seat_amount}",tags=["booking"])
def bookings(id:str, flight_no:str, arrival_time:str, departure_time:str, seat_type:str, seat_amount:int):
    new_book = airline_system.booking(id, flight_no, arrival_time, departure_time, seat_type, seat_amount)
    info = new_book.get_data()
    return {"Message":"Success","info":info}

@app.get("/get_booking/{id}",tags=["get_info"])
def get_booking(id:str):
    passenger = airline_system.find_passenger(id)
    return {"All Book" : passenger.get_booking()}

@app.post("/pay_book/{id}/{pnr}/{payment_method}/{amount}/{validate_object}",tags=["booking"])
def bookings(id:str, pnr:str, payment_method:str, validate_object:str):
    new_book = airline_system.pay_book(id, pnr, payment_method, validate_object)
    info = new_book.get_data()
    return {"Message":"Success","info":info}

@app.get("/create_income_report/{flight_no}",tags=["get_info"])
def crete_income_report(flight_no:str):
    flight_report = airline_system.create_income_report(flight_no)
    return {"Message":flight_report}

@app.post("/create_account/{name}/{email}/{card_pin}/{money}/{tier}",tags=["passenger"])
def create_account(name: str,email: str,card_pin: str,money: float,tier: str):
    new_passenger = airline_system.create_account(name, email, card_pin, money, tier)
    info = new_passenger.get_data()
    return {"Message":info}




if __name__ == "__main__":
    uvicorn.run("_09ReportIncome_CreateAccountWithAPI:app", host="127.0.0.1", port=8000, log_level="info")
