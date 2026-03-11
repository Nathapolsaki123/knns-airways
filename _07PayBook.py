# from datetime import datetime
# from fastapi import FastAPI, HTTPException
# from pydantic import BaseModel
# import uvicorn
# import random


# app = FastAPI()

# class Passenger:
#     def __init__(self, passenger_id: str, first_name: str, last_name: str):
#         self.__passenger_id = passenger_id
#         self.__first_name = first_name
#         self.__last_name = last_name
#         self.__book_list = []
#         self.__card = None

#     def get_passenger_id(self):
#         return self.__passenger_id

#     def add_book(self,book):
#         self.__book_list.append(book)
    
#     def add_card(self,card):
#         self.__card = card

#     def get_passenger_name(self):
#         return self.__first_name
    
#     def get_book_by_pnr(self, pnr):
#         for b in self.__book_list:
#             if b.get_pnr() == pnr:
#                 return b
#         raise HTTPException(
#             status_code=404, 
#             detail=f"Did not find book with pnr {pnr} in id {self.__passenger_id}"
#         )
    
#     def get_book_list(self):
#         count = 1
#         all_book = {}
#         for b in self.__book_list:
#             all_book[count] = b.get_data()
#             count+=1
#         return all_book
    
# class Member(Passenger):
#     def __init__(self, passenger_id: str, first_name: str, last_name: str):
#         super().__init__(passenger_id, first_name, last_name)
#         self.__point = 0


# class Card:
#     def __init__(self,pin,amount):
#         self.__pin = pin
#         self.__amount = amount
    
#     def get_pin(self):
#         return self.__pin
    
#     def get_amount(self):
#         return self.__amount
    
# class Guest(Passenger):
#     def __init__(self, passenger_id: str, first_name: str, last_name: str):
#         super().__init__(passenger_id, first_name, last_name)
#         self.__discount = 1
#         self.__max_weight = 10
    
#     def get_discount(self):
#         return self.__discount

#     def get_max_weight(self):
#         return self.__max_weight
    
# class Silver(Member):
#     def __init__(self, passenger_id: str, first_name: str, last_name: str):
#         super().__init__(passenger_id, first_name, last_name)
#         self.__discount = 0.9
#         self.__max_weight = 20
    
#     def get_discount(self):
#         return self.__discount

#     def get_max_weight(self):
#         return self.__max_weight
    


# class Gold(Member):
#     def __init__(self, passenger_id: str, first_name: str, last_name: str):
#         super().__init__(passenger_id, first_name, last_name)
#         self.__discount = 0.8
#         self.__max_weight = 30
    
#     def get_discount(self):
#         return self.__discount

#     def get_max_weight(self):
#         return self.__max_weight
    
# class Payment:
#     def get_payment_type(self, payment_type):
#         for cls in Payment.__subclasses__():
#             if cls.identifier == payment_type:
#                 return cls() # Instantiate and return
            
#         raise HTTPException(
#             status_code=404,
#             detail=f"Payment method invalid"
#             )

# class PayByCard(Payment):
#     identifier = "PayByCard"
#     def validate(self,received_book, validate_object=None):
#         received_book.get

# class PayBypoint(Payment):
#     identifier = "PayByPoint"
#     def validate(self,received_book, validate_object=None):
#         pass
#         #unfinish
        

# class Transaction:
#     def __init__(self):
#         self.__sub_transaction = []

# class Flight:
#     def __init__(self, flight_no: str):
#         self.__flight_no = flight_no
#         self.__flight_status = "Scheduled"
#         self.__flight_instance_list = []
        
#     def get_flight_no(self):
#         return self.__flight_no
    
#     def get_flight_instance_list(self):
#         return self.__flight_instance_list
    
#     def create_flight_instance(self, airplane: Airplane ,origin: str, destination: str, arrival_time: datetime, departure_time: datetime, price: int):
#         new_flight = FlightInstance(self.__flight_no,airplane ,origin, destination, arrival_time, departure_time, price)
#         self.__flight_instance_list.append(new_flight)

# class FlightInstance():
#     def __init__(self, flight_no: str, airplane: Airplane ,origin: str, destination: str, arrival_time: datetime, departure_time: datetime, price: int):
#         self.__flight_no = flight_no
#         self.__airplane = airplane
#         self.__origin = origin 
#         self.__destination = destination
#         self.__arrival_time = arrival_time
#         self.__departure_time = departure_time
#         self.__price = price

#     def get_arrival_time(self):
#         return self.__arrival_time

#     def get_departure_time(self):
#         return self.__departure_time
    
#     def get_airplane(self):
#         return self.__airplane

#     def get_price(self):
#         return self.__price
    
#     def get_flight_no(self):
#         return self.__flight_no
        

# class Airplane:
#     def __init__(self, model: str, economy_seat_amount: int, business_seat_amount: int):
#         self.__model = model
#         self.__economy_seat_amount = economy_seat_amount
#         self.__business_seat_amount = business_seat_amount
    
#     def new_seat_amount(self,seat_type,seat_amount):
#         if seat_type == "Business":
#             return self.__business_seat_amount - seat_amount
#         elif seat_type == "Economy":
#             return self.__economy_seat_amount - seat_amount

#     def check_seat_availability(self,seat_type,seat_amount):
#         if seat_type == "Business":
#             check =  self.__business_seat_amount >= seat_amount
#         elif seat_type == "Economy":
#             check =  self.__economy_seat_amount >= seat_amount
#         else:
#             check = False
        
#         if check == False:
#             raise HTTPException(
#                     status_code=404,
#                     detail=f"There is no seat_type {seat_type} that is still available for {seat_amount} seat"
#                     )

# class Book:

#     _used_pnr = set()

#     def __init__(self, passenger: Passenger, flight_instance: FlightInstance, seat_type: str, seat_amount: int, max_weight: int, price: int):
#         self.__pnr = self.generate_pnr()
#         self.__passenger = passenger
#         self.__flight_instance = flight_instance
#         self.__seat_type = seat_type
#         self.__seat_amount = seat_amount
#         self.__status = "Pending"
#         self.__booking_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
#         self.__max_weight = max_weight
#         self.__fare = price
#         self.__Transaction = None

#     def get_data(self):
#         return {
#                 "pnr": self.__pnr,
#                 "passenger": self.__passenger.get_passenger_name(),                
#                 "flight_no": self.__flight_instance.get_flight_no(),
#                 "seat_type": self.__seat_type,
#                 "seat_amount": self.__seat_amount,
#                 "status": self.__status,
#                 "booking_date": self.__booking_date,
#                 "max_weight": self.__max_weight,
#                 "fare": self.__fare
#                 }

#     def generate_pnr(self):
#         chars = "ABCDEFGHJKMNPQRSTUVWXYZ23456789"
        
#         while True:
#             candidate_pnr = ''.join(random.choices(chars, k=6))
            
#             if candidate_pnr not in Book._used_pnr:
                
#                 Book._used_pnr.add(candidate_pnr)
#                 return candidate_pnr

#     def get_pnr(self):
#         return self.__pnr


# class AirlineController:
#     def __init__(self, name: str):
#         self.__name = name
#         self.__passengers = []
#         self.__flights = []

#     def add_passenger(self, passenger: Passenger):
#         self.__passengers.append(passenger)
    
#     def add_Flight(self, Flight: Flight):
#         self.__flights.append(Flight)

#     def find_flight(self, flight_no: str, arrival_time: datetime, departure_time:datetime):
#         for f in self.__flights:
#             if f.get_flight_no() == flight_no:
#                 for ff in f.get_flight_instance_list():
#                     print(f"{ff.get_arrival_time()} is euqal? {arrival_time} and {ff.get_departure_time()} is euqal? {departure_time}")
#                     if ff.get_arrival_time() == arrival_time and ff.get_departure_time() == departure_time:
#                         return ff
#                 raise HTTPException(
#                 status_code=404,
#                 detail=f"Did not found flight {flight_no} that depart at {departure_time} and arrive at {arrival_time}"
#                 )
#         raise HTTPException(
#                 status_code=404,
#                 detail=f"Did not found flight {flight_no}"
#                 )
    
#     def find_passenger(self, id: str):
#         for p in self.__passengers:
#             if p.get_passenger_id() == id:
#                 return p
#         raise HTTPException(
#             status_code=404, 
#             detail=f"Did not find passenger with id {id}"
#         )
    
#     def calculate_fare(self, flight_price: int, seat_type: str, seat_amount: int, discount: float):
#         if seat_type == "Economy":
#             seat_cost = 100
#         elif seat_type == "Business":
#             seat_cost = 300
#         else:
#             raise HTTPException(
#                 status_code=404,
#                 detail=f"Price cannot be calculate"
#                 )

#         fare = (flight_price+(seat_cost*seat_amount))*discount
#         return fare
    
#     def pay_book(self,id: str, pnr: str, payment_method: str, validate_object: str = None):
#         received_passenger = self.find_passenger(id)
#         received_book = received_passenger.find_book_by_pnr(pnr)

#         is_member = issubclass(received_passenger, Member)

#         if (not is_member and payment_method == "PayByPoint") == True:
#             raise HTTPException(
#                 status_code=404,
#                 detail=f"You cannot pay by point if you are not a member"
#                 )

#         payment_type = payment_system.get_payment_type(payment_method)

#         payment_type.validate(received_book, validate_object)



#     def booking(self,id: str, flight_no: str, arrival_time: str, departure_time: str, seat_type: str, seat_amount: int, ):
#         received_passenger = self.find_passenger(id)
        
#         date_arrival_time = datetime.strptime(arrival_time, "%Y-%m-%d %H:%M")
#         date_departure_time = datetime.strptime(departure_time, "%Y-%m-%d %H:%M")

#         received_flight_instance = self.find_flight(flight_no, date_arrival_time, date_departure_time)

#         received_airplane = received_flight_instance.get_airplane()
#         received_airplane.check_seat_availability(seat_type, seat_amount)
            
#         received_airplane.new_seat_amount(seat_type, seat_amount)
#         discount = received_passenger.get_discount()
#         price = self.calculate_fare(received_flight_instance.get_price(),seat_type,seat_amount,discount)

#         max_weight = received_passenger.get_max_weight()
#         new_book = Book(received_passenger, received_flight_instance, seat_type, seat_amount, max_weight, price)
#         received_passenger.add_book(new_book)
#         return new_book

# airline_system = AirlineController("Thai Airways")
# payment_system = Payment()

# # 2. Create Dummy Data
# passenger1 = Silver("12345", "Somsak", "Jaidee")
# card1 = Card(123,1000)
# passenger2 = Gold("54321", "Sexski", "taobin")
# card2 = Card(456,2000)
# airplane1 = Airplane("B001",20,20)
# airplane2 = Airplane("B002",30,10)
# airplane3 = Airplane("B003",1,2)
# airplane4 = Airplane("B004",10,10)

# flight1 = Flight("TG101")
# flight_instance1 = flight1.create_flight_instance(airplane1, "Bangkok", "Tokyo", datetime(2025,1,10,10,0), datetime(2025,1,10,7,0), 3000)
# flight_instance2 = flight1.create_flight_instance(airplane2, "Bangkok", "Tokyo", datetime(2025,2,10,18,0), datetime(2025,2,10,15,0), 4000)
# flight2 = Flight("TG102")
# flight_instance3 = flight2.create_flight_instance(airplane3, "Bangkok", "London", datetime(2025,1,10,11,0), datetime(2025,1,10,6,0), 5000)
# flight_instance4 = flight2.create_flight_instance(airplane4, "Bangkok", "London", datetime(2025,3,10,19,0), datetime(2025,3,10,14,0), 6000)

# # 3. Add Data to Controller
# airline_system.add_Flight(flight1)
# airline_system.add_Flight(flight2)

# airline_system.add_passenger(passenger1)
# airline_system.add_passenger(passenger2)

# passenger1.add_card(card1)
# passenger2.add_card(card2)


# @app.post("/booking/{id}/{flight_no}/{arrival_time}/{departure_time}/{seat_type}/{seat_amount}")
# def bookings(id:str, flight_no:str, arrival_time:str, departure_time:str, seat_type:str, seat_amount:int):
#     new_book = airline_system.booking(id, flight_no, arrival_time, departure_time, seat_type, seat_amount)
#     info = new_book.get_data()
#     return {"Message":"Success","info":info}

# @app.get("/get_book_list/{id}")
# def get_book_list(id:str):
#     passenger = airline_system.find_passenger(id)
#     return {"All Book" : passenger.get_book_list()}

# @app.post("/pay_book/{id}/{pnr}/{payment_method}/{amount}/{validate_object}")
# def bookings(id:str, pnr:str, payment_method:str, validate_object:str):
#     airline_system.pay_book(id, pnr, payment_method, validate_object)
#     # info = new_book.get_data()
#     return {"Message":"Success","info":info}


# if __name__ == "__main__":
#     uvicorn.run("07PayBook:app", host="127.0.0.1", port=8000, log_level="info")

