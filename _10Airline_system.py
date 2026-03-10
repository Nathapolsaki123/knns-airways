from enum import Enum
from datetime import date,datetime,timedelta
from abc import ABC,abstractmethod
import random
import uuid



# =========================
# ENUMS
# =========================

class BookingStatus(Enum):
    PENDING = "PENDING"
    CONFIRMED = "CONFIRMED"
    CHECKEDIN = "CHECKEDIN"
    COMPLETED = "COMPLETED"
    CANCELED = "CANCELED"
    NOSHOW = "NOSHOW"


class PaymentStatus(Enum):
    PAID = "PAID"
    UNPAID = "UNPAID"
    REFUNDED = "REFUNDED"


class FlightStatus(Enum):
    SCHEDULED = "SCHEDULED"
    CHECKINOPEN = "CHECKINOPEN"
    BOARDING = "BOARDING"
    DEPARTED = "DEPARTED"
    ARRIVED = "ARRIVED"
    CANCELLED = "CANCELLED"


# =========================
# CARD
# =========================

class Card:

    def __init__(self, pin, money):
        self.__pin = pin
        self.__money = money

    @property
    def pin(self):
        return self.__pin

    @property
    def money(self):
        return self.__money
    
    def pay_money(self, money):
        self.__money -= money


# =========================
# PASSENGER
# =========================

class Passenger:
    id = 1
    def __init__(self, name, email, card=None):
        self.__passenger_id = f"{Passenger.id:05d}"
        Passenger.id += 1
        self.__name = name
        self.__email = email
        self.__card = card
        self.__booking_list = []
        self.__refunded_total = 0
        self.__is_blacklisted = False
        self.__blacklist_time = None
        self.__notification_list = []

    @property
    def passenger_id(self):
        return self.__passenger_id

    @property
    def name(self):
        return self.__name

    @property
    def email(self):
        return self.__email

    @property
    def card(self):
        return self.__card

    @property
    def booking_list(self):
        return self.__booking_list

    @property
    def refunded_total(self):
        return self.__refunded_total

    @property
    def is_blacklisted(self):
        return self.__is_blacklisted

    @property
    def blacklist_time(self):
        return self.__blacklist_time

    @property
    def notification_list(self):
        return self.__notification_list

    def add_booking(self, booking):
        self.__booking_list.append(booking)

    def add_card(self,card):
        self.__card = card

    def add_notification(self, notification):
        self.__notification_list.append(notification)

    def booking_request(self):
        pass

    def search_booking_by_pnr(self, pnr):
        for b in self.__booking_list:
            if b.pnr == pnr:
                return b
        return None
    
    def get_data(self):
        return {
                "passenger_id": self.__passenger_id,
                "name": self.__name,                
                "email": self.__email,
                "has_card": self.__card is not None,
                "card_balance": self.__card.money if self.__card else None,
                "refunded_total": self.__refunded_total,
                "is_blacklisted": self.__is_blacklisted,
                "blacklist_time": self.__blacklist_time
                }
    
    def get_booking(self):
        count = 1
        all_book = {}
        for b in self.__booking_list:
            all_book[count] = b.get_data()
            count+=1
        return all_book

# =========================
# MEMBERSHIP
# =========================

class Guest(Passenger):
    identifier = "Guest"
    def __init__(self, name, email, card=None):
        super().__init__(name, email, card)
        self.__discount = 1
        self.__extra_weight = 0
        self.__annual_fee = 0

    @property
    def discount(self):
        return self.__discount

    @property
    def extra_weight(self):
        return self.__extra_weight

    @property
    def annual_fee(self):
        return self.__annual_fee


class Member(Passenger):

    def __init__(self, name, email, card=None):
        super().__init__(name, email, card)
        self.__point = 0

    @property
    def point(self):
        return self.__point

    def change_point(self, point):
        self.__point += point


class Silver(Member):
    identifier = "Silver"
    def __init__(self, name, email, card=None):
        super().__init__(name, email, card)
        self.__discount = 0.95
        self.__extra_weight = 5.0
        self.__annual_fee = 200.0

    @property
    def discount(self):
        return self.__discount

    @property
    def extra_weight(self):
        return self.__extra_weight

    @property
    def annual_fee(self):
        return self.__annual_fee
    

class Gold(Member):
    identifier = "Gold"
    def __init__(self, name, email, card=None):
        super().__init__(name, email, card)
        self.__discount = 0.9
        self.__extra_weight = 10.0
        self.__annual_fee = 300.0
    
    @property
    def discount(self):
        return self.__discount

    @property
    def extra_weight(self):
        return self.__extra_weight

    @property
    def annual_fee(self):
        return self.__annual_fee


class Platinum(Member):
    identifier = "Platinum"
    def __init__(self, name, email, card=None):
        super().__init__(name, email, card)
        self.__discount = 0.85
        self.__extra_weight = 20.0
        self.__annual_fee = 500.0

    @property
    def discount(self):
        return self.__discount

    @property
    def extra_weight(self):
        return self.__extra_weight

    @property
    def annual_fee(self):
        return self.__annual_fee

# =========================
# SEAT
# =========================

class Seat(ABC):
    def __init__(self, seat_no):
        self.__seat_no = seat_no

    @property
    def seat_no(self):
        return self.__seat_no

    @property
    @abstractmethod
    def type_seat(self):
        pass

class Economy(Seat):

    def __init__(self, seat_no):
        super().__init__(seat_no)
        self.__luggage_limit = 20.0
        self.__seat_price = 300
        self.__type_seat = "Economy"


    @property
    def luggage_limit(self):
        return self.__luggage_limit

    @property
    def seat_price(self):
        return self.__seat_price
    
    @property
    def type_seat(self):
        return self.__type_seat


class Business(Seat):

    def __init__(self, seat_no):
        super().__init__(seat_no)
        self.__luggage_limit = 40.0
        self.__seat_price = 500
        self.__type_seat = "Business"


    @property
    def luggage_limit(self):
        return self.__luggage_limit

    @property
    def seat_price(self):
        return self.__seat_price
    
    @property
    def type_seat(self):
        return self.__type_seat


# =========================
# AIRPLANE
# =========================

class Airplane:

    def __init__(self, model_number, registration_no, eco, bus):
        self.__model_number = model_number
        self.__registration_no = registration_no
        self.__status = True
        self.__economy_seat_amount = eco
        self.__business_seat_amount = bus
        self.__seat_layout_list = []
        self.add_seat_for_new_plane(eco,bus)

    @property
    def model_number(self):
        return self.__model_number

    @property
    def registration_no(self):
        return self.__registration_no

    @property
    def status(self):
        return self.__status
    
    def set_status(self,status:bool):
        self.__status = status

    @property
    def economy_seat_amount(self):
        return self.__economy_seat_amount

    @property
    def business_seat_amount(self):
        return self.__business_seat_amount

    @property
    def seat_layout_list(self):
        return self.__seat_layout_list
    
    def add_seat_for_new_plane(self,economy_seat,business_seat):
        self.__seat_layout_list.clear()
        for b in range(1,business_seat+1):
            if b<10:
                temp_seat = self.create_business_seat(f"B0{b}")
                self.__seat_layout_list.append(temp_seat)
            else:
                temp_seat = self.create_business_seat(f"B{b}")
                self.__seat_layout_list.append(temp_seat)

        for e in range(1,economy_seat+1):
            if e<10:
                temp_seat = self.create_economy_seat(f"E0{e}")
                self.__seat_layout_list.append(temp_seat)
            else:
                temp_seat = self.create_economy_seat(f"E{e}")
                self.__seat_layout_list.append(temp_seat)

    def create_economy_seat(self,seat_no):
        return Economy(seat_no)
    
    def create_business_seat(self,seat_no):
        return Business(seat_no)


# =========================
# FOOD
# =========================

class FlightFood:

    def __init__(self, name, price):
        self.__name = name
        self.__price = price

    @property
    def name(self):
        return self.__name

    @property
    def price(self):
        return self.__price


# =========================
# FLIGHT
# =========================

class Flight:

    def __init__(self, flight_no, origin, destination):
        self.__flight_no = flight_no
        self.__origin = origin
        self.__destination = destination
        self.__flight_instance_list = []

    @property
    def flight_no(self):
        return self.__flight_no
    
    @property
    def origin(self):
        return self.__origin
    
    @property
    def destination(self):
        return self.__destination
    
    @property
    def flight_instance_list(self):
        return self.__flight_instance_list
    
    def add_flight_instance(self,flight_instance):
        self.__flight_instance_list.append(flight_instance)

    def create_flight_instance(self, airplane, depart_time, arrive_time):
        flight_instance = FlightInstance(self.__flight_no,self.__origin,self.__destination, depart_time, arrive_time)
        flight_instance.add_airplane(airplane)
        self.__flight_instance_list.append(flight_instance)
        return flight_instance

    
    def get_flight_data(self):
        return {"Flight_no":self.__flight_no
                ,"Origin":self.__origin
                ,"Destination":self.__destination
                }
    
# =========================
# FLIGHT SEAT
# =========================

class FlightSeat:

    def __init__(self, passenger, seat):
        self.__passenger = passenger
        self.__seat = seat
        self.__food_list = []
        self.__extra_weight = 0

    @property
    def passenger(self):
        return self.__passenger

    @property
    def seat(self):
        return self.__seat

    @property
    def food_list(self):
        return self.__food_list

    @property
    def extra_weight(self):
        return self.__extra_weight
    
    def add_food(self,food:FlightFood):
        self.__food_list.append(food)

    def add_extra_weight(self,weight):
        self.__extra_weight += weight


# =========================
# FLIGHT INSTANCE
# =========================

class FlightInstance:

    FOOD_IN_FLIGHT = 3

    def __init__(self, flight_no, origin, destination, departure_time, arrival_time):

        self.__flight_no = flight_no
        self.__airplane = None

        if isinstance(departure_time, str):
            departure_time = datetime.strptime(departure_time, '%d-%m-%Y %H:%M')
        if isinstance(arrival_time, str):
            arrival_time = datetime.strptime(arrival_time, '%d-%m-%Y %H:%M')

        self.__origin = origin
        self.__destination = destination
        self.__departure_time = departure_time
        self.__arrival_time = arrival_time
        self.__economy_seat_available = 0
        self.__business_seat_available = 0
        self.__remaining_seat_list = []
        self.__assigned_seat_list = []
        self.__food_list = []
        self.__total_income = 0
        self.__price = 10000
        self.__status = FlightStatus.SCHEDULED

    @property
    def flight_no(self):
        return self.__flight_no

    @property
    def airplane(self):
        return self.__airplane
    
    @property
    def origin(self):
        return self.__origin

    @property
    def destination(self):
        return self.__destination

    @property
    def departure_time(self):
        return self.__departure_time

    @property
    def arrival_time(self):
        return self.__arrival_time
    
    @property
    def economy_seat_available(self):
        return self.__economy_seat_available
    
    @property
    def business_seat_available(self):
        return self.__business_seat_available
    
    @property
    def remaining_seat_list(self):
        return self.__remaining_seat_list
    
    @property
    def assigned_seat_list(self):
        return self.__assigned_seat_list
    
    @property
    def food_list(self):
        return self.__food_list
    
    @property
    def total_income(self):
        return self.__total_income
    
    def update_total_income(self, amount):
        self.__total_income += amount

    def check_seat_availability(self,seat_type,seat_amount):
        if seat_type == "Business":
            if self.__business_seat_available < seat_amount:
                raise Exception("Not enough Business seats")

        elif seat_type == "Economy":
            if self.__economy_seat_available < seat_amount:
                raise Exception("Not enough Economy seats")

        else:
            raise Exception("Invalid seat type")

    @property
    def price(self):
        return self.__price

    @property
    def status(self):
        return self.__status
    
    def add_airplane(self,airplane:Airplane):
        self.__airplane = airplane
        self.__remaining_seat_list = self.__airplane.seat_layout_list.copy()
        self.__economy_seat_available = len([s for s in self.__remaining_seat_list if s.type_seat == "Economy"])
        self.__business_seat_available = len([s for s in self.__remaining_seat_list if s.type_seat == "Business"])

    def add_flightfood(self,flightfood):
        self.__food_list.append(flightfood)

    def reserve_seat(self, type):
        if type not in ["Economy","Business"]:
            raise Exception("Invalid seat type")
        if type == "Economy":
            if self.__economy_seat_available <= 0:
                raise Exception("No economy seats available to reserve")
            self.__economy_seat_available -= 1
        elif type == "Business":
            if self.__business_seat_available <= 0:
                raise Exception("No business seats available to reserve")
            self.__business_seat_available -= 1

    def release_seat(self, seat_type, seat_amount):
        if seat_type == "Economy":
            self.__economy_seat_available += seat_amount
        elif seat_type == "Business":
            self.__business_seat_available += seat_amount

    def add_assigned_seat(self, flightseat):
        self.__assigned_seat_list.append(flightseat)
    
    def get_available_seat(self, seat_class):
        result = []
        for seat in self.__remaining_seat_list:
            if seat.type_seat == seat_class:
                result.append(seat)
        return result
    
    def get_amount_seat(self,seat_type):
        if seat_type == "Economy":
            return self.__economy_seat_available
        elif seat_type == "Business":
            return self.__business_seat_available
        else:
            raise Exception("Invalid seat type")
        
    def show_flightfood(self):
        return [food.name for food in self.__food_list]
    
    def change_flight_status(self,status):
        self.__status = status

    def calculate_flight_time(self):
        start = self.__departure_time
        end = self.__arrival_time
        if start > end:
            raise Exception("Negative Time")
        time_diff = end - start
        return str(time_diff)
    
    def get_flight_data(self):
        return {"Flight_no":self.__flight_no,
                "Origin":self.__origin,
                "Destination":self.__destination,
                "Depart_time":self.__departure_time,
                "Arrive_time":self.__arrival_time,
                "Flight_time":self.calculate_flight_time()
                }
    
    def edit_time(self, depart_time, arrive_time):
        # accept either datetime or str
        if isinstance(depart_time, str):
            depart_time = datetime.strptime(depart_time, '%d-%m-%Y %H:%M')
        if isinstance(arrive_time, str):
            arrive_time = datetime.strptime(arrive_time, '%d-%m-%Y %H:%M')
        self.__departure_time = depart_time
        self.__arrival_time = arrive_time

    def open_check_in(self):
        self.__status = FlightStatus.CHECKINOPEN

    def close_check_in(self):
        self.__status = FlightStatus.BOARDING

    def cancel_flight(self):
        self.__status = FlightStatus.CANCELLED


# =========================
# TICKET
# =========================

class Ticket:

    def __init__(self, passenger, flight_instance, flight_seat):
        self.__passenger = passenger
        self.__flight_instance = flight_instance
        self.__origin = flight_instance.origin
        self.__destination = flight_instance.destination
        self.__departure_time = flight_instance.departure_time
        self.__seat = flight_seat

    @property
    def passenger(self):
        return self.__passenger

    @property
    def flight_instance(self):
        return self.__flight_instance
    
    @property
    def seat(self):
        return self.__seat
    
    def __str__(self):
        return (
            f"\n------ TICKET ------\n"
            f"Flight No : {self.__flight_instance.flight_no}\n"
            f"Passenger : {self.__passenger.name}\n"
            f"Route     : {self.__origin} -> {self.__destination}\n"
            f"Departure : {self.__departure_time}\n"
            f"Seat      : {self.__seat.seat.seat_no}\n"
            f"Class     : {self.__seat.seat.type_seat}\n"
            f"--------------------"
        )


# =========================
# TRANSACTION
# =========================

class Transaction:

    def __init__(self, name, payment_type, amount):
        self.__sub_transaction_list = []
        self.__name = name
        self.__payment_type = payment_type
        self.__amount = amount

    @property
    def sub_transaction_list(self):
        return self.__sub_transaction_list

    def add_sub_trans(self, sub):
        self.__sub_transaction_list.append(sub)

class SubTransaction:

    def __init__(self, name, payment_type, amount):
        self.__name = name
        self.__payment_type = payment_type
        self.__amount = amount

    @property
    def name(self):
        return self.__name

    @property
    def payment_type(self):
        return self.__payment_type

    @property
    def amount(self):
        return self.__amount




# =========================
# PAYMENT
# =========================

class Payment(ABC):
    @classmethod
    def get_payment_type(cls, payment_type):
        for sub in cls.__subclasses__():
            if getattr(sub, "identifier", None) == payment_type:
                return sub
        raise Exception("Payment method invalid")
                    
    @abstractmethod
    def validate(self):
        pass


class PayByCard(Payment):
    identifier = "PayByCard"

    @classmethod
    def validate(cls,received_passenger,  validate_object=None):
        card = received_passenger.card
        if card is None:
            raise Exception("Passenger has no card")
        if card.pin != validate_object:
            raise Exception("Incorrect Pin")
        else:
            return True

    @classmethod  
    def pay(cls, received_passenger, price):
        card = received_passenger.card
        if price > card.money:
                raise Exception("Not enough money")
        else:
            card.pay_money(price)
            is_member = isinstance(received_passenger, Member)
            if is_member:
                received_passenger.change_point(int(price // 25))
            return True
        



class PayByPoint(Payment):
    identifier = "PayByPoint"

    @classmethod
    def validate(cls,received_passenger, validate_object=None):
        is_member = isinstance(received_passenger, Member)
        if not is_member:
            raise Exception("You cannot pay by point if you are not a member")
        else:
            return True
        
    @classmethod       
    def pay(cls, received_passenger, price):
        if price > received_passenger.point:
                raise Exception("Not enough point")
        else:
            received_passenger.change_point(-price)
            return True


# =========================
# BOOKING
# =========================

class Booking:

    def __init__(self, passenger: Passenger, flight_instance: FlightInstance, seat_type: str, seat_amount: int, max_weight: int, price: float):
        self.__pnr = self.generate_pnr()
        self.__passenger = passenger
        self.__flight_instance = flight_instance
        self.__seat_type = seat_type
        self.__seat_amount = seat_amount
        self.__ticket_list = []
        self.__booking_status = BookingStatus.PENDING
        self.__payment_status = PaymentStatus.UNPAID
        self.__booking_date = datetime.now().strftime('%d-%m-%Y %H:%M:%S')
        self.__max_weight = max_weight
        self.__fare = price
        self.__transaction = None

    @property
    def pnr(self):
        return self.__pnr

    @property
    def passenger(self):
        return self.__passenger

    @property
    def flight_instance(self):
        return self.__flight_instance
    
    @property
    def seat_type(self):
        return self.__seat_type
    
    @property
    def seat_amount(self):
        return self.__seat_amount
    
    @property
    def booking_status(self):
        return self.__booking_status
    
    @property
    def payment_status(self):
        return self.__payment_status
    
    @property
    def booking_date(self):
        return self.__booking_date
    
    @property
    def max_weight(self):
        return self.__max_weight
    
    @property
    def fare(self):
        return self.__fare
    
    @property
    def transaction(self):
        return self.__transaction
    
    def get_data(self):
        return {
                "pnr": self.__pnr,
                "passenger": self.__passenger.name,                
                "flight_no": self.__flight_instance.flight_no,
                "seat_type": self.__seat_type,
                "seat_amount": self.__seat_amount,
                "status": self.__booking_status.value,
                "payment_status": self.__payment_status.value,
                "booking_date": self.__booking_date,
                "max_weight": self.__max_weight,
                "fare": self.__fare
                }
    
    @staticmethod
    def generate_pnr():
        return uuid.uuid4().hex[:6].upper()

    def add_ticket(self,ticket):
        self.__ticket_list.append(ticket)

    def calculate_max_weight(self):
        pass

    def confirm_booking(self):
        self.__booking_status = BookingStatus.CONFIRMED

    def cancel_booking(self):
        self.__booking_status = BookingStatus.CANCELED

    def update_booking_status(self,status):
        self.__booking_status = status

    def update_payment_status(self,status):
        self.__payment_status = status

    def add_transaction(self, name: str, payment_type: str, amount: float):
        new_transaction = Transaction(name,payment_type,amount)
        self.__transaction = new_transaction

    def validate_book(self):
        if self.payment_status != PaymentStatus.UNPAID:
            raise Exception("Booking already paid or canceled")
        else:
            return True


# =========================
# AIRLINE
# =========================

class Airline:

    def __init__(self, name):
        self.__airline_name = name
        self.__passenger_list = []
        self.__booking_list = []
        self.__airplane_list = []
        self.__flight_list = []
        self.__blacklist_list = []
        self.__flight_food_list = []

    @property
    def airline_name(self):
        return self.__airline_name

    def add_passenger(self, p):
        self.__passenger_list.append(p)

    def add_booking(self, b):
        self.__booking_list.append(b)

    def add_airplane(self, a):
        self.__airplane_list.append(a)

    def add_flight(self, f):
        self.__flight_list.append(f)

    def add_blacklist_passenger(self, p):
        self.__blacklist_list.append(p)

    def add_flight_food(self, food):
        self.__flight_food_list.append(food)

    def request_booking(self):
        pass

    def calculate_extra_weight_fee(self):
        pass

    def calculate_fare(self):
        pass

    def check_in_passenger(self,passenger_id,pnr):
        current_passenger = self.search_passenger_by_id(passenger_id)
        if current_passenger is None:
            raise Exception("Invalid Passenger ID.")

        current_booking = current_passenger.search_booking_by_pnr(pnr)
        if current_booking is None:
            raise Exception("Invalid Booking PNR.")

        status = current_booking.booking_status

        if status == BookingStatus.CHECKEDIN:
            raise Exception("You have already checked in.")
        if status == BookingStatus.PENDING:
            raise Exception("Your booking has not been paid yet.")
        if status in [BookingStatus.CANCELED, BookingStatus.NOSHOW]:
            raise Exception("This booking cannot check in.")
        if status != BookingStatus.CONFIRMED:
            raise Exception("Invalid Booking Status")

        current_flight = current_booking.flight_instance

        if current_flight.status != FlightStatus.CHECKINOPEN:
            raise Exception("Check-in is not open yet.")

        current_booking.update_booking_status(BookingStatus.CHECKEDIN)

        available_seat_list = current_flight.get_available_seat(current_booking.seat_type)
        return [s.seat_no for s in available_seat_list]
    

    def choose_seat(self,passenger_id,pnr,chosen_seat:str):
        
        current_passenger = self.search_passenger_by_id(passenger_id)
        if current_passenger is None:
            raise Exception("Invalid Passenger ID.")

        current_booking = current_passenger.search_booking_by_pnr(pnr)
        if current_booking is None:
            raise Exception("Invalid Booking PNR.")

        status = current_booking.booking_status

        if status == BookingStatus.CONFIRMED:
            raise Exception("Please check in before choosing seat.")
        if status == BookingStatus.PENDING:
            raise Exception("Your booking has not been paid yet.")
        if status in [BookingStatus.CANCELED, BookingStatus.NOSHOW]:
            raise Exception("This booking cannot check in.")
        if status != BookingStatus.CHECKEDIN:
            raise Exception("Invalid Booking Status")

        current_flight = current_booking.flight_instance
        
        valid, invalid, duplicates, chosen_seat_obj = self.parse_seats(chosen_seat,current_flight.get_available_seat(current_booking.seat_type))
        
        if invalid:
            print(f"Valid seats: {valid}")
            print(f"Invalid seats: {invalid}")
            raise Exception(f"Invalid seats: {invalid} \n---Please Choose your seat again.---")

        if duplicates:
            raise Exception(f"Duplicate seat selection: {duplicates}")

        if len(chosen_seat_obj) != current_booking.seat_amount:
            raise Exception("Number of seats chosen does not match booking.")
        
        created_tickets = []
        for seat in chosen_seat_obj:
            current_flight.remaining_seat_list.remove(seat)
            flight_seat = FlightSeat(current_passenger, seat)
            current_flight.add_assigned_seat(flight_seat)
            ticket = Ticket(current_passenger,current_flight,flight_seat)
            current_booking.add_ticket(ticket)
            created_tickets.append(ticket)
        current_booking.update_booking_status(BookingStatus.COMPLETED)
        return created_tickets
        
    def create_flight(self,flight_no,origin,target):
        flight = Flight(flight_no ,origin,target)
        self.__flight_list.append(flight)

    def create_flight_instance(self,flight_no,airplane_no,depart_time,arrive_time):
        try:
            datetime.strptime(depart_time,'%d-%m-%Y %H:%M')
            datetime.strptime(arrive_time,'%d-%m-%Y %H:%M')
        except:
            raise Exception("Invalid Time")
        
        flight = self.search_flight(flight_no)
        if not(flight):
            raise Exception("Flight Number Not Found")
        
        airplane = self.search_airplane(airplane_no)
        if not(airplane):
            raise Exception("Airplane Not Found")
        
        if not(airplane.status):
            raise Exception("Airplane Unavailable")
        
        flight_instance = flight.create_flight_instance(airplane,depart_time,arrive_time)
        airplane.set_status(False)

        self.add_flightfood_to_flight_instance(flight_instance)

        return "Create Flight Success"
    
    def update_flight(self,flight_no,old_depart_time,depart_time,arrive_time):
        try:
            datetime.strptime(depart_time,'%d-%m-%Y %H:%M')
            datetime.strptime(arrive_time,'%d-%m-%Y %H:%M')
            datetime.strptime(old_depart_time,'%d-%m-%Y %H:%M')
        except:
            raise Exception("Invalid Time")
        
        instance = self.search_flight_instance(flight_no,old_depart_time)
        instance.edit_time(depart_time,arrive_time)
        return instance

    def add_flightfood_to_flight_instance(self,flight_instance):

        foodlen = len(self.__flight_food_list)
        if foodlen <1 :
            raise Exception("FlightFood Not Found")
        
        target = min(len(self.__flight_food_list), flight_instance.FOOD_IN_FLIGHT)

        while len(flight_instance.food_list) < target:
            index = random.randint(0,foodlen-1)
            if not (self.__flight_food_list[index] in flight_instance.food_list):
                flight_instance.add_flightfood(self.__flight_food_list[index])
        
    def create_flight_seat_report(self, flight_no: str):
        string = []
        total_economy = 0
        total_business = 0
        count = 0

        f = self.search_flight(flight_no)
        if not f:
            raise Exception("Flight not found")
        if not f.flight_instance_list:
            raise Exception("No flight instance")

        header = f"Report of occupied seat in flight:{f.flight_no}(from {f.origin} to {f.destination} in percentage)"
        string.append(header)

        for ff in f.flight_instance_list:
            a = ff.airplane

            eco_total = a.economy_seat_amount or 0
            bus_total = a.business_seat_amount or 0

            eco_percent = ((eco_total - ff.economy_seat_available) / eco_total * 100) if eco_total else 0
            bus_percent = ((bus_total - ff.business_seat_available) / bus_total * 100) if bus_total else 0

            content1 = f" Flight that travel from {ff.departure_time} to {ff.arrival_time} has {eco_percent:.2f}% of Economy seat that has been chosen"
            content2 = f" Flight that travel from {ff.departure_time} to {ff.arrival_time} has {bus_percent:.2f}% of Business seat that has been chosen"

            string.append(content1)
            string.append(content2)

            total_economy += eco_percent
            total_business += bus_percent
            count += 1

        total_occupied_economy = total_economy / count if count > 0 else 0
        total_occupied_business = total_business / count if count > 0 else 0

        string.append(f"Total percentage of occupied economy seat in flight: {f.flight_no} is {total_occupied_economy:.2f}%")
        string.append(f"Total percentage of occupied business seat in flight: {f.flight_no} is {total_occupied_business:.2f}%")

        return string

    def create_flightfood(self,name,price):
        food = FlightFood(name,price)
        self.__flight_food_list.append(food)

    def generate_report(self):
        pass

    def remove_flight(self):
        pass

    def request_refund(self):
        pass

    def search_flight(self,flight_no):
        for flight in self.__flight_list:
            if flight.flight_no == flight_no:
                return flight
        return None

    def search_airplane(self,airplane_no) :
        for airplane in self.__airplane_list:
            if airplane.registration_no == airplane_no:
                return airplane
        return None

    def search_passenger_by_id(self, pid):
        for p in self.__passenger_list:
            if p.passenger_id == pid:
                return p
        return None
    
    def search_flight_instance(self, flight_no, depart_time):
        flight = self.search_flight(flight_no)
        if not flight:
            raise Exception("Flight Not Found")

        # normalize depart_time to datetime for comparison
        if isinstance(depart_time, str):
            depart_time = datetime.strptime(depart_time, '%d-%m-%Y %H:%M')

        for instance in flight.flight_instance_list:
            if instance.departure_time == depart_time:
                return instance
        raise Exception("Instance Not Found")

    def verify_weight(self):
        pass

    def validate_card_info(self, card_pin: str, money: float):
        if len(card_pin) != 6:
            raise Exception(f"Pin need to be 6 digit, yours is {len(card_pin)} digit")
        if money <= 0:
            raise Exception("Your card need to have money more than 0")
        return True

    def calculate_fare(self, flight_price: int, seat_type: str, seat_amount: int, discount: float):
        if seat_type == "Economy":
            seat_cost = 300
        elif seat_type == "Business":
            seat_cost = 500
        else:
            raise Exception("Price cannot be calculate")

        fare = (flight_price+(seat_cost*seat_amount))*discount
        return fare
    
    def pay_book(self,id: str, pnr: str, payment_method: str, validate_object: str = None):
        received_passenger = self.search_passenger_by_id(id)
        if received_passenger is None:
            raise Exception("Passenger not found")
        received_book = received_passenger.search_booking_by_pnr(pnr)
        if received_book is None:
            raise Exception("Booking not found")
        received_flight_instance = received_book.flight_instance
        received_book.validate_book()

        payment_type = Payment.get_payment_type(payment_method)

        payment_type.validate(received_passenger, validate_object)
        payment_type.pay(received_passenger, received_book.fare)
        received_flight_instance.update_total_income(received_book.fare)
        received_book.update_booking_status(BookingStatus.CONFIRMED)
        received_book.update_payment_status(PaymentStatus.PAID)
        received_book.add_transaction("pay_for_booking", payment_method, received_book.fare)
        return received_book
    
    def booking(self,id: str, flight_no: str, departure_time: str, seat_type: str, seat_amount: int, ):
        received_passenger = self.search_passenger_by_id(id)
        if received_passenger is None:
            raise Exception("Passenger not found")
        if received_passenger.is_blacklisted:
            raise Exception("You on the blacklist and cannot booking on this airline until your blacklist time is over")
        try:
            date_departure_time = datetime.strptime(departure_time, '%d-%m-%Y %H:%M')
        except:
            raise Exception("Date Format is wrong")

        received_flight_instance = self.search_flight_instance(flight_no, date_departure_time)

        received_flight_instance.check_seat_availability(seat_type, seat_amount)
            
        for i in range(seat_amount):
            received_flight_instance.reserve_seat(seat_type)
        discount = received_passenger.discount
        price = self.calculate_fare(received_flight_instance.price,seat_type,seat_amount,discount)

        max_weight = received_passenger.extra_weight
        new_book = Booking(received_passenger, received_flight_instance, seat_type, seat_amount, max_weight, price)
        received_passenger.add_booking(new_book)
        self.add_booking(new_book)
        return new_book

    def cancel_booking(self,id: str, pnr: str):#flight can cancel before paid only
        current_passenger = self.search_passenger_by_id(id)
        if not current_passenger:
            raise Exception("Invalid Passenger ID.")
        
        current_booking = current_passenger.search_booking_by_pnr(pnr)
        if not current_booking:
            raise Exception("Invalid Booking PNR.")
        
        if current_booking.booking_status != BookingStatus.PENDING:
            raise Exception("This booking are not able to cancel")
        
        current_booking.cancel_booking()
        current_flight_instance = current_booking.flight_instance
        current_flight_instance.release_seat(current_booking.seat_type,current_booking.seat_amount)
        return "Canceled booking successful."
    
    def create_income_report(self, flight_no: str):
        string = []
        total = 0
        f = self.search_flight(flight_no)
        if not f:
            raise Exception("Flight not found")
        header = f"Income report of flight number:{f.flight_no}(from {f.origin} to {f.destination})"
        string.append(header)
        for ff in f.flight_instance_list:
            content = f" Flight that travel from {ff.departure_time} to {ff.arrival_time} has earned income of {ff.total_income}"
            total += ff.total_income
            string.append(content)
        string.append(f"Total income of flight: {f.flight_no} is {total}")
        return string
    
    def get_account(self,tier: str,name: str,email: str):
        classes_to_check = Passenger.__subclasses__()
        
        while classes_to_check:
            # Take the first class out of the list to examine
            cls = classes_to_check.pop(0)
            
            # Check if this class matches our identifier
            # Using getattr is safer in case an intermediate subclass forgot to define 'identifier'
            if getattr(cls, "identifier", None) == tier:
                #edit                
                return cls(name, email) # Instantiate and return
                
            # Add any subclasses of THIS class to the end of our list to check later
            classes_to_check.extend(cls.__subclasses__())
            
        # If the loop finishes and we found nothing, raise the error
        raise Exception(f"There is no {tier} tier in this airline")
    
    def create_account(self, name: str,email: str,card_pin: str,money: float,tier: str):
        self.validate_card_info(card_pin, money)
        new_card = Card(card_pin, money)
        passenger = self.get_account(tier, name, email)
        passenger.add_card(new_card)
        if passenger.annual_fee > new_card.money:
            Passenger.id -= 1
            raise Exception("Not enough money to pay annual fee")
        PayByCard.pay(passenger, passenger.annual_fee)
        self.add_passenger(passenger)
        return passenger

    @staticmethod
    def parse_seats(seat_string, available_seats):
        chosen = []
        invalid = []
        duplicates = []
        chosen_seat_obj = []

        for part in seat_string.split(","):

            s = part.strip().upper().replace(" ", "")

            if len(s) < 2:
                invalid.append(part)
                continue

            row = s[0]
            num_part = s[1:]

            if not num_part.isdigit():
                invalid.append(part)
                continue

            seat_code = f"{row}{int(num_part):02d}"

            found = None

            for seat in available_seats:
                if seat.seat_no == seat_code:
                    found = seat
                    break

            if found is None:
                invalid.append(part)
                continue

            # detect duplicate
            if seat_code in chosen:
                duplicates.append(seat_code)
                continue

            chosen.append(seat_code)
            chosen_seat_obj.append(found)

        return chosen, invalid, duplicates, chosen_seat_obj
