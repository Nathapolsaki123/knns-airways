from enum import Enum
from datetime import date, datetime, timedelta
from abc import ABC, abstractmethod
from fastapi import FastAPI, HTTPException


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

    def __init__(self, pin: str, money: float) -> None:
        # [ดัก Error] เช็ค Type และดักค่าว่าง/ติดลบ
        if not isinstance(pin, str) or not pin.strip().isdigit() or len(pin.strip()) != 6:
            raise HTTPException(status_code=400, detail="Pin must be a 6-digit number string")
        if not isinstance(money, (int, float)) or money < 0:
            raise HTTPException(status_code=400, detail="Money cannot be negative")
            
        self.__pin = pin.strip()
        self.__money = float(money)

    @property
    def pin(self) -> str:
        return self.__pin

    @property
    def money(self) -> float:
        return self.__money
    
    def change_money(self, money: float) -> None:
        if not isinstance(money, (int, float)):
            raise HTTPException(status_code=400, detail="Money amount must be a number")
        if self.__money + money < 0:
            raise HTTPException(status_code=400, detail="Card balance cannot be negative")
        self.__money += money


# =========================
# PASSENGER
# =========================

class Passenger:

    id: int = 1

    DISCOUNT: float = 0.0
    EXTRA_WEIGHT: float = 0.0
    ANNUAL_FEE: float = 0.0

    def __init__(self, name: str, email: str) -> None:
        # [ดัก Error] เช็คการกด Spacebar ผ่านๆ หรือส่งค่าว่าง
        if not isinstance(name, str) or not name.strip():
            raise HTTPException(status_code=400, detail="Name cannot be empty")
        if not isinstance(email, str) or not email.strip():
            raise HTTPException(status_code=400, detail="Email cannot be empty")
            
        self.__passenger_id: str = f"{Passenger.id:05d}"
        Passenger.id += 1
        self.__name: str = name.strip()
        self.__email: str = email.strip()
        self.__card: Card | None = None
        self.__booking_list: list['Booking'] = []
        self.__refunded_total: int = 0
        self.__is_blacklisted: bool = False
        self.__blacklist_time: timedelta | None = None
        self.__notification_list: list[str] = []
        self.__luggage_weight: float = 0.0

    @property
    def passenger_id(self) -> str:
        return self.__passenger_id

    @property
    def name(self) -> str:
        return self.__name

    @property
    def email(self) -> str:
        return self.__email

    @property
    def card(self) -> 'Card':
        return self.__card # type: ignore

    @property
    def booking_list(self) -> list['Booking']:
        return self.__booking_list

    @property
    def refunded_total(self) -> int:
        return self.__refunded_total

    @property
    def is_blacklisted(self) -> bool:
        return self.__is_blacklisted

    @property
    def notification_list(self) -> list[str]:
        return self.__notification_list
    
    @property
    def luggage_weight(self) -> float:
        return self.__luggage_weight

    def add_booking(self, booking: 'Booking') -> None:
        self.__booking_list.append(booking)

    def add_card(self, card: 'Card') -> None:
        self.__card = card

    def add_notification(self, notification: str) -> None:
        self.__notification_list.append(notification.strip())

    def read_notification(self) -> None:
        for n in self.__notification_list:
            print(n)

    def set_weight(self, weight: float) -> None:
        if not isinstance(weight, (int, float)) or weight < 0:
            raise HTTPException(status_code=400, detail="Luggage weight must be a number >= 0")
        self.__luggage_weight = float(weight)

    def find_booking(self, pnr: str) -> 'Booking':
        # [ดัก Error] PNR Case Sensitivity
        if not isinstance(pnr, str):
            raise HTTPException(status_code=400, detail="PNR must be a string")
        pnr = pnr.strip().upper()
        
        for booking in self.__booking_list: 
            if booking.pnr == pnr:
                return booking
        raise HTTPException(
            status_code=404,
            detail=f"Booking PNR '{pnr}' not found for passenger '{self.__name}'"
        )
    
    def get_data(self) -> dict:
        return {
                "passenger_id": self.__passenger_id,
                "name": self.__name,                
                "email": self.__email,
                "has_card": self.__card is not None,
                "card_balance": self.__card.money if self.__card else None,
                "refunded_total": self.__refunded_total,
                "is_blacklisted": self.__is_blacklisted,
                }
    
    def get_booking(self) -> dict:
        count = 1
        all_book = {}
        for b in self.__booking_list:
            all_book[count] = b.get_data()
            count += 1
        return all_book
    
    def check_refunded_total(self) -> bool:
        return 0 <= self.__refunded_total < 3
    
    def add_refunded_total(self) -> None:
        self.__refunded_total += 1

    def make_blacklist(self) -> None:
        self.__is_blacklisted = True
        self.__blacklist_time = timedelta(days=180)

# =========================
# MEMBERSHIP
# =========================

class Guest(Passenger):

    DISCOUNT: float = 0.0  # แก้จาก 1.0 เป็น 0.0
    EXTRA_WEIGHT: float = 0.0
    ANNUAL_FEE: float = 0.0

    identifier: str = "Guest"
    def __init__(self, name: str, email: str) -> None:
        super().__init__(name, email)


class Member(Passenger):

    def __init__(self, name: str, email: str) -> None:
        super().__init__(name, email)
        self.__point: int = 0

    @property
    def point(self) -> int:
        return self.__point

    def change_point(self, point: int) -> None:
        if not isinstance(point, int):
            raise HTTPException(status_code=400, detail="Points must be an integer")
        if self.__point + point < 0:
            raise HTTPException(status_code=400, detail="Member points cannot be negative")
        self.__point += point


class Silver(Member):

    DISCOUNT: float = 0.05
    EXTRA_WEIGHT: float = 5.0
    ANNUAL_FEE: float = 200.0

    identifier: str = "Silver"
    def __init__(self, name: str, email: str) -> None:
        super().__init__(name, email)
    

class Gold(Member):
    
    DISCOUNT: float = 0.1
    EXTRA_WEIGHT: float = 10.0
    ANNUAL_FEE: float = 300.0

    identifier: str = "Gold"
    def __init__(self, name: str, email: str) -> None:
        super().__init__(name, email)


class Platinum(Member):
    
    DISCOUNT: float = 0.15
    EXTRA_WEIGHT: float = 20.0
    ANNUAL_FEE: float = 500.0

    identifier: str = "Platinum"
    def __init__(self, name: str, email: str) -> None:
        super().__init__(name, email)

# =========================
# SEAT
# =========================

class Seat(ABC):
    def __init__(self, seat_no: str) -> None:
        self.__seat_no = seat_no.strip().upper() # ป้องกัน Case Sensitive เรื่องเบาะที่นั่ง

    @property
    def seat_no(self) -> str:
        return self.__seat_no
    
    @property
    @abstractmethod
    def identifier(self) -> str:
        pass
    

class Economy(Seat):
    SEAT_PRICE: float = 300.0
    LUGGAGE_LIMIT: float = 20.0 

    def __init__(self, seat_no: str) -> None:
        super().__init__(seat_no)
        self.__identifier: str = "Economy"
        self.__luggage_limit = self.LUGGAGE_LIMIT

    @property
    def luggage_limit(self) -> float:
        return self.__luggage_limit
    
    @property
    def identifier(self) -> str:
        return self.__identifier
    

class Business(Seat):
    SEAT_PRICE: float = 500.0
    LUGGAGE_LIMIT: float = 40.0 

    def __init__(self, seat_no: str) -> None:
        super().__init__(seat_no)
        self.__identifier: str = "Business"
        self.__luggage_limit = self.LUGGAGE_LIMIT

    @property
    def luggage_limit(self) -> float:
        return self.__luggage_limit
    
    @property
    def identifier(self) -> str:
        return self.__identifier
    

# =========================
# AIRPLANE
# =========================

class Airplane:

    def __init__(self, model_number: str, registration_no: str, eco: int, bus: int) -> None:
        self.__model_number = model_number.strip().upper()
        self.__registration_no = registration_no.strip().upper()
        self.__status: bool = True
        self.__economy_seat_amount = int(eco)
        self.__business_seat_amount = int(bus)
        self.__seat_layout_list: list['Seat'] = []
        self.add_seat_for_new_plane(self.__economy_seat_amount, self.__business_seat_amount)

    @property
    def model_number(self) -> str:
        return self.__model_number

    @property
    def registration_no(self) -> str:
        return self.__registration_no

    @property
    def status(self) -> bool:
        return self.__status
    
    def set_status(self, status: bool) -> None:
        self.__status = status

    @property
    def economy_seat_amount(self) -> int:
        return self.__economy_seat_amount

    @property
    def business_seat_amount(self) -> int:
        return self.__business_seat_amount

    @property
    def seat_layout_list(self) -> list['Seat']:
        return self.__seat_layout_list
    
    def get_data(self):
        return {"Model":self.__model_number,
                "Airplane_no":self.__registration_no,
                "Seat":{"Economy":self.__economy_seat_amount,"Business":self.__business_seat_amount},
                }

    
    def add_seat_for_new_plane(self, economy_seat: int, business_seat: int) -> None:
        self.__seat_layout_list.clear()
        for b in range(1, business_seat + 1):
            if b < 10:
                temp_seat_bus = self.create_business_seat(f"B0{b}")
                self.__seat_layout_list.append(temp_seat_bus)
            else:
                temp_seat_bus = self.create_business_seat(f"B{b}")
                self.__seat_layout_list.append(temp_seat_bus)

        for e in range(1, economy_seat + 1):
            if e < 10:
                temp_seat_eco = self.create_economy_seat(f"E0{e}")
                self.__seat_layout_list.append(temp_seat_eco)
            else:
                temp_seat_eco = self.create_economy_seat(f"E{e}")
                self.__seat_layout_list.append(temp_seat_eco)

    def create_economy_seat(self, seat_no: str) -> Economy:
        return Economy(seat_no)
    
    def create_business_seat(self, seat_no: str) -> Business:
        return Business(seat_no)


# =========================
# FOOD
# =========================

class FlightFood:

    def __init__(self, name: str, price: float) -> None:
        if not name.strip():
            raise HTTPException(status_code=400, detail="Food name cannot be empty")
        if not isinstance(price, (int, float)) or price < 0:
            raise HTTPException(status_code=400, detail="Food price cannot be negative")
            
        self.__name = name.strip()
        self.__price = float(price)

    @property
    def name(self) -> str:
        return self.__name

    @property
    def price(self) -> float:
        return self.__price
    
    def calculate_price(self, quantity: int) -> float:
        # [ดัก Error] Mismatch + Negative
        if not isinstance(quantity, int) or quantity <= 0:
            raise HTTPException(status_code=400, detail="Quantity must be a positive integer")
        return self.__price * quantity

    

# =========================
# FLIGHT
# =========================

class Flight:

    def __init__(self, flight_no: str, origin: str, destination: str) -> None:
        # [ดัก Error] Case Sensitivity
        self.__flight_no = flight_no.strip().upper()
        self.__origin = origin.strip().upper()
        self.__destination = destination.strip().upper()
        self.__flight_instance_list: list['FlightInstance'] = []

    @property
    def flight_no(self) -> str:
        return self.__flight_no
    
    @property
    def origin(self) -> str:
        return self.__origin
    
    @property
    def destination(self) -> str:
        return self.__destination
    
    @property
    def flight_instance_list(self) -> list['FlightInstance']:
        return self.__flight_instance_list
    
    def add_flight_instance(self, flight_instance: 'FlightInstance') -> None:
        self.__flight_instance_list.append(flight_instance)

    def create_flight_instance(self, airplane: Airplane, depart_time: str | datetime, arrive_time: str | datetime) -> 'FlightInstance':
        flight_instance = FlightInstance(self.__flight_no, self.__origin, self.__destination, depart_time, arrive_time)
        flight_instance.add_airplane(airplane)
        self.__flight_instance_list.append(flight_instance)
        return flight_instance
    
    def get_flight_data(self) -> dict:
        return {"Flight_no": self.__flight_no,
                "Origin": self.__origin,
                "Destination": self.__destination
                }
    
# =========================
# FLIGHT SEAT
# =========================

class FlightSeat:

    def __init__(self, passenger: Passenger, seat: Seat) -> None:
        self.__passenger = passenger
        self.__seat = seat
        self.__food_list: list[FlightFood] = []
        self.__extra_weight: float = 0.0

    @property
    def passenger(self) -> Passenger:
        return self.__passenger

    @property
    def seat(self) -> Seat:
        return self.__seat

    @property
    def food_list(self) -> list[FlightFood]:
        return self.__food_list

    @property
    def extra_weight(self) -> float:
        return self.__extra_weight
    
    def add_food(self, food: FlightFood) -> None:
        self.__food_list.append(food)

    def add_extra_weight(self, weight: float) -> None:
        if not isinstance(weight, (int, float)) or weight < 0:
            raise HTTPException(status_code=400, detail="Extra weight must be >= 0")
        self.__extra_weight += weight


# =========================
# FLIGHT INSTANCE
# =========================

class FlightInstance:

    FOOD_IN_FLIGHT: int = 3

    def __init__(self, flight_no: str, origin: str, destination: str, departure_time: str | datetime, arrival_time: str | datetime) -> None:

        self.__flight_no = flight_no.strip().upper()
        self.__airplane: Airplane | None = None

        if isinstance(departure_time, str):
            departure_time = datetime.strptime(departure_time.strip(), '%d-%m-%Y %H:%M')
        if isinstance(arrival_time, str):
            arrival_time = datetime.strptime(arrival_time.strip(), '%d-%m-%Y %H:%M')

        self.__origin = origin.strip().upper()
        self.__destination = destination.strip().upper()
        self.__departure_time = departure_time
        self.__arrival_time = arrival_time
        
        self.__economy_booking_quota: int = 0
        self.__business_booking_quota: int = 0
        self.__all_seats_list: list[Seat] = []
        self.__assigned_seat_list: list[FlightSeat] = []
        self.__food_list: list[FlightFood] = []
        self.__total_income: float = 0.0
        self.__price: float = 10000.0
        self.__status: FlightStatus = FlightStatus.SCHEDULED

    @property
    def flight_no(self) -> str:
        return self.__flight_no

    @property
    def airplane(self) -> Airplane | None:
        return self.__airplane
    
    @property
    def origin(self) -> str:
        return self.__origin

    @property
    def destination(self) -> str:
        return self.__destination

    @property
    def departure_time(self) -> datetime:
        return self.__departure_time

    @property
    def arrival_time(self) -> datetime:
        return self.__arrival_time
    
    @property
    def economy_booking_quota(self) -> int:
        return self.__economy_booking_quota
    
    @property
    def business_booking_quota(self) -> int:
        return self.__business_booking_quota
    
    @property
    def all_seats_list(self) -> list[Seat]:
        return self.__all_seats_list
    
    @property
    def assigned_seat_list(self) -> list[FlightSeat]:
        return self.__assigned_seat_list
    
    @property
    def food_list(self) -> list[FlightFood]:
        return self.__food_list
    
    @property
    def total_income(self) -> float:
        return self.__total_income
    
    def update_total_income(self, amount: float) -> None:
        if not isinstance(amount, (int, float)):
            raise HTTPException(status_code=400, detail="Amount must be a number")
        self.__total_income += amount

    def check_seat_availability(self, seat_type: str, seat_amount: int) -> None:
        if not isinstance(seat_amount, int) or seat_amount <= 0:
            raise HTTPException(status_code=400, detail="Seat amount must be a positive integer")
            
        seat_type = seat_type.strip().capitalize() # ป้องกันคนพิมพ์ EcOnomy
        
        if seat_type == "Business":
            if self.__business_booking_quota < seat_amount:
                raise HTTPException(status_code=400, detail="Not enough Business seats")

        elif seat_type == "Economy":
            if self.__economy_booking_quota < seat_amount:
                raise HTTPException(status_code=400, detail="Not enough Economy seats")

        else:
            raise HTTPException(status_code=400, detail=f"Invalid seat type: {seat_type}")

    @property
    def price(self) -> float:
        return self.__price

    @property
    def status(self) -> FlightStatus:
        return self.__status
    
    def add_airplane(self, airplane: Airplane) -> None:
        self.__airplane = airplane
        self.__all_seats_list = self.__airplane.seat_layout_list.copy()
        self.__economy_booking_quota = len([s for s in self.__all_seats_list if isinstance(s, Economy)])
        self.__business_booking_quota = len([s for s in self.__all_seats_list if isinstance(s, Business)])

    def add_flightfood(self, flightfood: FlightFood) -> None:
        self.__food_list.append(flightfood)

    def reserve_seat(self, type: str) -> None:
        type = type.strip().capitalize()
        if type not in ["Economy", "Business"]:
            raise HTTPException(status_code=400, detail="Invalid seat type")
        if type == "Economy":
            if self.__economy_booking_quota <= 0:
                raise HTTPException(status_code=400, detail="No economy seats available to reserve")
            self.__economy_booking_quota -= 1
        elif type == "Business":
            if self.__business_booking_quota <= 0:
                raise HTTPException(status_code=400, detail="No business seats available to reserve")
            self.__business_booking_quota -= 1

    def release_seat(self, seat_type: str, seat_amount: int) -> None:
        if not isinstance(seat_amount, int) or seat_amount < 0:
            return # ป้องกัน Error หรือง่ายๆ คือไม่ต้องทำอะไร
        seat_type = seat_type.strip().capitalize()
        if seat_type == "Economy":
            self.__economy_booking_quota += seat_amount
        elif seat_type == "Business":
            self.__business_booking_quota += seat_amount

    def add_assigned_seat(self, flightseat: FlightSeat) -> None:
        self.__assigned_seat_list.append(flightseat)
    
    def get_available_seat(self, seat_class: str) -> list[Seat]:
        seat_class = seat_class.strip().capitalize()
        available_seats = []
        assigned_seat_nos = [assigned.seat.seat_no for assigned in self.__assigned_seat_list]
        for seat in self.__all_seats_list:
            if seat.identifier == seat_class and seat.seat_no not in assigned_seat_nos:
                available_seats.append(seat)
        return available_seats
    
    def get_amount_seat(self, seat_type: str) -> int:
        seat_type = seat_type.strip().capitalize()
        if seat_type == "Economy":
            return self.__economy_booking_quota
        elif seat_type == "Business":
            return self.__business_booking_quota
        else:
            raise HTTPException(status_code=400, detail="Invalid seat type")
        
    def show_flightfood(self) -> list[str]:
        return [food.name for food in self.__food_list]
    
    def change_flight_status(self, status: FlightStatus) -> None:
        self.__status = status

    def calculate_flight_time(self) -> str:
        start = self.__departure_time
        end = self.__arrival_time
        if start > end:
            raise HTTPException(status_code=400, detail="Negative Time: Arrival is before Departure")
        time_diff = end - start
        return str(time_diff)
    
    def find_flight_instance_food_by_food_name(self, food_name: str) -> FlightFood:
        food_name = food_name.strip()
        for food in self.__food_list: 
            if food.name == food_name:
                return food
        raise HTTPException(
            status_code=404,
            detail=f"Food menu '{food_name}' not found on this flight"
        )
    
    def find_flight_seat_by_passenger_id(self, passenger_id: str) -> FlightSeat:
        passenger_id = passenger_id.strip()
        for seat in self.__assigned_seat_list: 
            id = seat.passenger.passenger_id
            if id == passenger_id:
                return seat
        raise HTTPException(
            status_code=404,
            detail=f"Seat assigned to passenger ID '{passenger_id}' not found on this flight"
        )
    
    def get_flight_data(self) -> dict:
        return {"Flight_no": self.__flight_no,
                "Origin": self.__origin,
                "Destination": self.__destination,
                "Depart_time": self.__departure_time.strftime('%d-%m-%Y %H:%M'),
                "Arrive_time": self.__arrival_time.strftime('%d-%m-%Y %H:%M'),
                "Flight_time": self.calculate_flight_time()
                }
    
    def edit_time(self, depart_time: str | datetime, arrive_time: str | datetime) -> None:
        try:
            if isinstance(depart_time, str):
                depart_time = datetime.strptime(depart_time.strip(), '%d-%m-%Y %H:%M')
            if isinstance(arrive_time, str):
                arrive_time = datetime.strptime(arrive_time.strip(), '%d-%m-%Y %H:%M')
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid Datetime format. Expected DD-MM-YYYY HH:MM")
            
        self.__departure_time = depart_time
        self.__arrival_time = arrive_time

    def is_refundable_time(self) -> bool:
        time_until_departure = self.departure_time - datetime.now()
        return time_until_departure >= timedelta(hours=24)

    def open_check_in(self) -> None:
        self.__status = FlightStatus.CHECKINOPEN

    def close_check_in(self) -> None:
        self.__status = FlightStatus.BOARDING

    def cancel_flight(self) -> None:
        self.__status = FlightStatus.CANCELLED


# =========================
# TICKET
# =========================

class Ticket:

    def __init__(self, passenger: Passenger, flight_instance: FlightInstance, flight_seat: FlightSeat) -> None:
        self.__passenger = passenger
        self.__flight_instance = flight_instance
        self.__origin = flight_instance.origin
        self.__destination = flight_instance.destination
        self.__departure_time = flight_instance.departure_time
        self.__seat = flight_seat

    @property
    def passenger(self) -> Passenger:
        return self.__passenger

    @property
    def flight_instance(self) -> FlightInstance:
        return self.__flight_instance
    
    @property
    def seat(self) -> FlightSeat:
        return self.__seat
    
    def __str__(self) -> str:
        return (
            f"\n------ TICKET ------\n"
            f"Flight No : {self.__flight_instance.flight_no}\n"
            f"Passenger : {self.__passenger.name}\n"
            f"Route     : {self.__origin} -> {self.__destination}\n"
            f"Departure : {self.__departure_time.strftime('%d-%m-%Y %H:%M')}\n"
            f"Seat      : {self.__seat.seat.seat_no}\n"
            f"Class     : {self.__seat.seat.identifier}\n"
            f"--------------------"
        )


# =========================
# TRANSACTION
# =========================

class Transaction:

    def __init__(self, name: str, amount: float, payment_type: str) -> None:
        self.__sub_transaction_list: list['SubTransaction'] = []
        self.__name = name.strip()
        self.__payment_type = payment_type.strip()
        self.__amount = float(amount)

    @property
    def payment_type(self) -> str:
        return self.__payment_type
    
    @property
    def amount(self) -> float:
        return self.__amount

    @property
    def sub_transaction_list(self) -> list['SubTransaction']:
        return self.__sub_transaction_list

    def get_all_subtransaction(self) -> list[dict]:
        sub_list: list[dict] = [{self.__name: self.__amount}]
        for sub in self.__sub_transaction_list:
            sub_list.append(sub.get_data())
        return sub_list
    
    def add_sub_transaction(self, subtransaction: 'SubTransaction') -> None:
        self.__sub_transaction_list.append(subtransaction)


class SubTransaction:

    def __init__(self, name: str, amount: float, payment_type: str) -> None:
        self.__name = name.strip()
        self.__payment_type = payment_type.strip()
        self.__amount = float(amount)

    @property
    def name(self) -> str:
        return self.__name

    @property
    def payment_type(self) -> str:
        return self.__payment_type

    @property
    def amount(self) -> float:
        return self.__amount
    
    def get_data(self) -> dict:
        return {self.__name: self.__amount, "Payment_type": self.__payment_type}






# =========================
# PAYMENT
# =========================

class Payment(ABC):

    @classmethod
    def get_payment_type(cls, payment_type: str) -> type['Payment']:
        if not isinstance(payment_type, str) or not payment_type.strip():
            raise HTTPException(status_code=400, detail="Payment method invalid")
        target = payment_type.strip()
        for sub in cls.__subclasses__():
            ident = getattr(sub, "identifier", None)
            if ident is not None and ident.strip().lower() == target.lower():
                return sub
        raise HTTPException(status_code=400, detail="Payment method invalid")
    
    @classmethod                    
    @abstractmethod
    def validate(cls, received_passenger: Passenger, validate_object: str | None = None) -> bool | None:
        pass

    @classmethod
    @abstractmethod
    def refund(cls, received_passenger: Passenger, price: float) -> None:
        pass

    @classmethod
    @abstractmethod
    def pay(cls, received_passenger: Passenger, price: float) -> bool | None:
        pass

class PayByCard(Payment):
    identifier: str = "PayByCard"

    @classmethod
    def validate(cls, received_passenger: Passenger, validate_object: str | None = None) -> bool:
        card = received_passenger.card
        if card is None:
            raise HTTPException(status_code=400, detail="Passenger has no card")
        if validate_object is None or card.pin != validate_object.strip():
            raise HTTPException(status_code=401, detail="Incorrect Pin")
        else:
            return True

    @classmethod  
    def pay(cls, received_passenger: Passenger, price: float) -> bool:
        if not isinstance(price, (int, float)) or price <= 0:
            raise HTTPException(status_code=400, detail="Payment price must be strictly positive")
            
        card = received_passenger.card
        if price > card.money:
                raise HTTPException(status_code=400, detail="Not enough money")
        else:
            card.change_money(-price)
            is_member = isinstance(received_passenger, Member)
            if is_member:
                received_passenger.change_point(int(price // 25))
            return True
    
    @classmethod
    def refund(cls, received_passenger: Passenger, price: float) -> None:
        if not isinstance(price, (int, float)) or price <= 0:
            raise HTTPException(status_code=400, detail="Refund amount must be strictly positive")
        card = received_passenger.card
        card.change_money(price)
        

class PayByPoint(Payment):
    identifier: str = "PayByPoint"

    @classmethod
    def validate(cls, received_passenger: Passenger, validate_object: str | None = None) -> bool:
        is_member = isinstance(received_passenger, Member)
        if not is_member:
            raise HTTPException(status_code=403, detail="You cannot pay by point if you are not a member")
        else:
            return True
        
    @classmethod       
    def pay(cls, received_passenger: Passenger, price: float) -> bool:
        if not isinstance(received_passenger, Member):
            raise HTTPException(status_code=403, detail="Passenger is not a member")
            
        if not isinstance(price, (int, float)) or price <= 0:
            raise HTTPException(status_code=400, detail="Payment point amount must be strictly positive")
        
        if price > received_passenger.point:
                raise HTTPException(status_code=400, detail="Not enough points")
        else:
            received_passenger.change_point(int(-price))
            return True
        
    @classmethod
    def refund(cls, received_passenger: Passenger, price: float) -> None:
        if not isinstance(received_passenger, Member):
            raise HTTPException(status_code=403, detail="Passenger is not a member")
        if not isinstance(price, (int, float)) or price <= 0:
            raise HTTPException(status_code=400, detail="Refund point amount must be strictly positive")
        received_passenger.change_point(int(price))

# =========================
# BOOKING
# =========================

class Booking:

    def __init__(self, passenger: Passenger, flight_instance: FlightInstance, seat_type: str, seat_amount: int, price: float) -> None:
        self.__pnr = self.generate_pnr()
        self.__passenger = passenger
        self.__flight_instance = flight_instance
        self.__seat_type = seat_type.strip().capitalize()
        self.__seat_amount = int(seat_amount)
        self.__ticket_list: list[Ticket] = []
        self.__booking_status = BookingStatus.PENDING
        self.__payment_status = PaymentStatus.UNPAID
        self.__booking_date = datetime.now().strftime('%d-%m-%Y %H:%M:%S')
        self.__fare = float(price)
        self.__transaction: Transaction | None = None

    @property
    def pnr(self) -> str:
        return self.__pnr

    @property
    def passenger(self) -> Passenger:
        return self.__passenger

    @property
    def flight_instance(self) -> FlightInstance:
        return self.__flight_instance
    
    @property
    def seat_type(self) -> str:
        return self.__seat_type
    
    @property
    def seat_amount(self) -> int:
        return self.__seat_amount
    
    @property
    def booking_status(self) -> BookingStatus:
        return self.__booking_status
    
    @property
    def payment_status(self) -> PaymentStatus:
        return self.__payment_status
    
    @property
    def booking_date(self) -> str:
        return self.__booking_date
    
    @property
    def fare(self) -> float:
        return self.__fare
    
    @property
    def transaction(self) -> Transaction:
        return self.__transaction # type: ignore
    
    def get_data(self) -> dict:
        return {
                "pnr": self.__pnr,
                "passenger": self.__passenger.name,                
                "flight_no": self.__flight_instance.flight_no,
                "seat_type": self.__seat_type,
                "seat_amount": self.__seat_amount,
                "status": self.__booking_status.value,
                "payment_status": self.__payment_status.value,
                "booking_date": self.__booking_date,
                "fare": self.__fare
                }
    
    @staticmethod
    def generate_pnr() -> str:
        return uuid.uuid4().hex[:6].upper()
    
    def change_fare(self, amount: float) -> None:
        if not isinstance(amount, (int, float)):
             raise HTTPException(status_code=400, detail="Amount must be a number")
        self.__fare += amount

    def add_ticket(self, ticket: Ticket) -> None:
        self.__ticket_list.append(ticket)

    def calculate_max_weight(self) -> None:
        pass

    def confirm_booking(self) -> None:
        self.__booking_status = BookingStatus.CONFIRMED

    def cancel_booking(self) -> None:
        self.__booking_status = BookingStatus.CANCELED

    def update_booking_status(self, status: BookingStatus) -> None:
        self.__booking_status = status

    def update_payment_status(self, status: PaymentStatus) -> None:
        self.__payment_status = status

    def add_transaction(self, name: str, payment_type: str, amount: float) -> None:
        new_transaction = Transaction(name, amount, payment_type)
        self.__transaction = new_transaction

    def validate_book(self) -> bool:
        if self.payment_status != PaymentStatus.UNPAID:
            raise HTTPException(status_code=400, detail="Booking already paid or canceled")
        else:
            return True


# =========================
# AIRLINE
# =========================

class Airline:
    
    ECONOMYCLASS_LIMIT_WEIGHT: int = 15
    BUSINESSCLASS_LIMIT_WEIGHT: int = 30
    EXTRA_FEE_PER_KG: float = 300.0

    def __init__(self, name: str) -> None:
        self.__airline_name = name.strip()
        self.__passenger_list: list[Passenger] = []
        self.__booking_list: list[Booking] = []
        self.__airplane_list: list[Airplane] = []
        self.__flight_list: list[Flight] = []
        self.__blacklist_list: list[Passenger] = []
        self.__flight_food_list: list[FlightFood] = []

    @property
    def airline_name(self) -> str:
        return self.__airline_name

    def add_passenger(self, p: Passenger) -> None:
        self.__passenger_list.append(p)

    def add_booking(self, b: Booking) -> None:
        self.__booking_list.append(b)

    def add_airplane(self, a: Airplane) -> None:
        self.__airplane_list.append(a)

    def add_flight(self, f: Flight) -> None:
        self.__flight_list.append(f)

    def add_blacklist_passenger(self, p: Passenger) -> None:
        self.__blacklist_list.append(p)

    def add_flight_food(self, food: FlightFood) -> None:
        self.__flight_food_list.append(food)

    def request_booking(self) -> None:
        pass

    def check_in_passenger(self, passenger_id: str, pnr: str) -> list[str]:
        current_passenger = self.search_passenger_by_id(passenger_id)
        current_booking = current_passenger.find_booking(pnr)

        status = current_booking.booking_status

        if status == BookingStatus.CHECKEDIN:
            raise HTTPException(status_code=400, detail="You have already checked in.")
        if status == BookingStatus.PENDING:
            raise HTTPException(status_code=400, detail="Your booking has not been paid yet.")
        if status in [BookingStatus.CANCELED, BookingStatus.NOSHOW]:
            raise HTTPException(status_code=400, detail="This booking cannot check in.")
        if status != BookingStatus.CONFIRMED:
            raise HTTPException(status_code=400, detail="Invalid Booking Status")

        current_flight = current_booking.flight_instance

        if current_flight.status != FlightStatus.CHECKINOPEN:
            raise HTTPException(status_code=400, detail="Check-in is not open yet.")

        current_booking.update_booking_status(BookingStatus.CHECKEDIN)

        available_seat_list = current_flight.get_available_seat(current_booking.seat_type)
        return [s.seat_no for s in available_seat_list]
    
    def choose_seat(self, passenger_id: str, pnr: str, chosen_seat: str) -> list[Ticket]:
        
        current_passenger = self.search_passenger_by_id(passenger_id)
        current_booking = current_passenger.find_booking(pnr)

        status = current_booking.booking_status

        if status == BookingStatus.CONFIRMED:
            raise HTTPException(status_code=400, detail="Please check in before choosing seat.")
        if status == BookingStatus.PENDING:
            raise HTTPException(status_code=400, detail="Your booking has not been paid yet.")
        if status in [BookingStatus.CANCELED, BookingStatus.NOSHOW]:
            raise HTTPException(status_code=400, detail="This booking cannot check in.")
        if status != BookingStatus.CHECKEDIN:
            raise HTTPException(status_code=400, detail="Invalid Booking Status")

        current_flight = current_booking.flight_instance
        
        valid, invalid, duplicates, chosen_seat_obj = self.parse_seats(chosen_seat, current_flight.get_available_seat(current_booking.seat_type))
        
        if invalid:
            raise HTTPException(status_code=400, detail=f"Invalid seats: {invalid} \n---Please Choose your seat again.---")

        if duplicates:
            raise HTTPException(status_code=400, detail=f"Duplicate seat selection: {duplicates}")

        if len(chosen_seat_obj) != current_booking.seat_amount:
            raise HTTPException(status_code=400, detail="Number of seats chosen does not match booking.")
        
        created_tickets = []
        for seat in chosen_seat_obj:
            flight_seat = FlightSeat(current_passenger, seat)
            current_flight.add_assigned_seat(flight_seat)
            ticket = Ticket(current_passenger, current_flight, flight_seat)
            current_booking.add_ticket(ticket)
            created_tickets.append(ticket)
        current_booking.update_booking_status(BookingStatus.COMPLETED)
        return created_tickets
        
    def create_flight(self, flight_no: str, origin: str, target: str) -> None:
        flight_no = flight_no.strip().upper()
        flight = Flight(flight_no, origin, target)
        self.__flight_list.append(flight)

    def create_flight_instance(self, flight_no: str, airplane_no: str, depart_time: str, arrive_time: str) -> str:
        flight_no = flight_no.strip().upper()
        airplane_no = airplane_no.strip().upper()
        try:
            datetime.strptime(depart_time.strip(), '%d-%m-%Y %H:%M')
            datetime.strptime(arrive_time.strip(), '%d-%m-%Y %H:%M')
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid Time format")
        
        flight = self.find_flight(flight_no) # [ดัก Error] ใช้ find_flight เพื่อให้มันพ่น Error เองถ้าไม่เจอ
        
        airplane = self.search_airplane(airplane_no)
        # [ดัก Error NoneType] ป้องกันการเรียก airplane.status ถัาหาไม่เจอ
        if airplane is None:
            raise HTTPException(status_code=404, detail="Airplane Not Found")
        
        if not airplane.status:
            raise HTTPException(status_code=400, detail="Airplane Unavailable")
        
        flight_instance = flight.create_flight_instance(airplane, depart_time, arrive_time)
        airplane.set_status(False)

        self.add_flightfood_to_flight_instance(flight_instance)

        return "Create Flight Success"
    
    def update_flight_status(self, flight_no: str, departure_time: datetime, status: FlightStatus) -> None:
        flight_no = flight_no.strip().upper()
        flight_instance = self.find_flight_instance(flight_no, departure_time)
        flight_instance.change_flight_status(status)
        for p in self.__passenger_list:
            for b in p.booking_list:
                f = b.flight_instance
                if f.flight_no == flight_no and f.departure_time == departure_time:
                    p.add_notification(f"flight {flight_no} that depart at {departure_time} is now {status.value}")
    
    def update_flight(self, flight_no: str, old_depart_time: str, depart_time: str, arrive_time: str) -> FlightInstance:
        flight_no = flight_no.strip().upper()
        try:
            datetime.strptime(depart_time.strip(), '%d-%m-%Y %H:%M')
            datetime.strptime(arrive_time.strip(), '%d-%m-%Y %H:%M')
            old_dt = datetime.strptime(old_depart_time.strip(), '%d-%m-%Y %H:%M')
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid Time format")
        
        instance = self.find_flight_instance(flight_no, old_dt)
        instance.edit_time(depart_time, arrive_time)
        return instance

    def add_flightfood_to_flight_instance(self, flight_instance: FlightInstance) -> None:
        foodlen = len(self.__flight_food_list)
        if foodlen < 1:
            raise HTTPException(status_code=404, detail="FlightFood Not Found in system")
        
        target = min(len(self.__flight_food_list), flight_instance.FOOD_IN_FLIGHT)

        while len(flight_instance.food_list) < target:
            # [ดัก Error IndexError] จะปลอดภัยเสมอเพราะเราเช็ค foodlen < 1 ไว้ข้างบนแล้ว
            index = random.randint(0, foodlen - 1)
            if not (self.__flight_food_list[index] in flight_instance.food_list):
                flight_instance.add_flightfood(self.__flight_food_list[index])
        
    def create_flight_seat_report(self, flight_no: str) -> list[str]:
        flight_no = flight_no.strip().upper()
        string = []
        total_economy = 0.0
        total_business = 0.0
        count = 0

        f = self.find_flight(flight_no)
        if not f.flight_instance_list:
            raise HTTPException(status_code=404, detail="No flight instance available for this flight")

        header = f"Report of occupied seat in flight:{f.flight_no}(from {f.origin} to {f.destination} in percentage)"
        string.append(header)

        for ff in f.flight_instance_list:
            a = ff.airplane
            if not a: continue

            eco_total = a.economy_seat_amount or 0
            bus_total = a.business_seat_amount or 0

            eco_percent = ((eco_total - ff.economy_booking_quota) / eco_total * 100) if eco_total else 0
            bus_percent = ((bus_total - ff.business_booking_quota) / bus_total * 100) if bus_total else 0

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

    def create_flightfood(self, name: str, price: float) -> None:
        food = FlightFood(name, price)
        self.__flight_food_list.append(food)

    def search_flight(self, flight_no: str) -> Flight | None:
        flight_no = flight_no.strip().upper()
        for flight in self.__flight_list:
            if flight.flight_no == flight_no:
                return flight
        return None
    

    def search_airplane(self, airplane_no: str) -> Airplane | None:
        airplane_no = airplane_no.strip().upper()
        for airplane in self.__airplane_list:
            if airplane.registration_no == airplane_no:
                return airplane
        return None

    def search_passenger_by_id(self, pid: str) -> Passenger:
        pid = pid.strip()
        for p in self.__passenger_list:
            if p.passenger_id == pid:
                return p
        raise HTTPException(
            status_code=404,
            detail=f"Passenger ID {pid} not found"
        )
    
    def find_flight(self, flight_no: str) -> Flight:
        flight_no = flight_no.strip().upper()
        flight = self.search_flight(flight_no)
        if flight is None:
            raise HTTPException(status_code=404, detail=f"Did not found flight {flight_no}")
        return flight
    
    def find_flight_instance(self, flight_no: str, departure_time: datetime) -> FlightInstance:
        flight_no = flight_no.strip().upper()
        f = self.find_flight(flight_no)
        for ff in f.flight_instance_list:
            if ff.departure_time == departure_time:
                return ff
        raise HTTPException(
        status_code=404,
        detail=f"Did not found flight {flight_no} that depart at {departure_time}"
        )
    
    def get_data_by_pnr(self, pnr: str) -> tuple[Passenger, Booking]:
        pnr = pnr.strip().upper()
        for passenger in self.__passenger_list:
            for booking in passenger.booking_list:
                if(booking.pnr == pnr):
                    return passenger, booking
        raise HTTPException(status_code=404, detail="Data Not Found")
    
    def get_weight_limit(self, pnr: str) -> float:
        pnr = pnr.strip().upper()
        passenger, booking = self.get_data_by_pnr(pnr)
        seat_class = booking.seat_type
        extra_weight = passenger.EXTRA_WEIGHT
        
        weight_limit_before_tier = self.ECONOMYCLASS_LIMIT_WEIGHT if(seat_class == "Economy") else self.BUSINESSCLASS_LIMIT_WEIGHT

        return weight_limit_before_tier + extra_weight
    
    def verify_weight(self, weight_limit: float, passenger: Passenger) -> bool:
        if(passenger.luggage_weight <= weight_limit):
            return True
        return False
    
    def verify_status(self, book: Booking) -> bool:
        if book.booking_status == BookingStatus.COMPLETED:
            return True
        else:
            raise HTTPException(status_code=400, detail="You haven't completed your checkin yet")

    def load_luggage(self, pnr: str) -> dict:
        pnr = pnr.strip().upper()
        passenger, booking = self.get_data_by_pnr(pnr)
        flight_instance = booking.flight_instance
        self.verify_status(booking)
        
        weight_limit = self.get_weight_limit(pnr)
        card = passenger.card
        discount = passenger.DISCOUNT

        if self.verify_weight(weight_limit, passenger):
            return {"name": passenger.name,
        "luggage_weight": passenger.luggage_weight,
        "weight_limit": weight_limit,
        "message": f"Luggage loaded (WithinLimit)"
        }

        extra_weight = passenger.luggage_weight - weight_limit
        extra_fee_before_discount = self.__calculate_extra_weight_fee(extra_weight)
        extra_fee = extra_fee_before_discount * (1 - discount)
        booking.change_fare(extra_fee)
        flight_instance.update_total_income(extra_fee)

        PayByCard.pay(passenger, extra_fee)
        
        transaction = booking.transaction
        if transaction is None:
            raise HTTPException(status_code=400, detail="ไม่พบรายการชำระเงิน กรุณาชำระเงินก่อนดำเนินการ")
        
        return {"name": passenger.name,
        "luggage_weight": passenger.luggage_weight,
        "weight_limit": weight_limit,
        "message": f"Luggage loaded (Extra Fee :[{extra_weight} X {self.EXTRA_FEE_PER_KG}] - {passenger.DISCOUNT*100}% = {extra_fee})",
        "transaction": booking.transaction.get_all_subtransaction()
        }
    
    def __calculate_extra_weight_fee(self, extra_weight: float) -> float:
        return extra_weight * self.EXTRA_FEE_PER_KG

    def validate_card_info(self, card_pin: str, money: float) -> bool:
        if not isinstance(card_pin, str) or len(card_pin.strip()) != 6 or not card_pin.strip().isdigit():
            raise HTTPException(status_code=400, detail=f"Pin need to be 6 digit string, yours is {card_pin}")
        if not isinstance(money, (int, float)) or money <= 0:
            raise HTTPException(status_code=400, detail="Your card need to have money more than 0")
        return True

    def calculate_fare(self, flight_price: float, seat_type: str, seat_amount: int, discount: float) -> float:
        seat_type = seat_type.strip().capitalize()
        if not isinstance(seat_amount, int) or seat_amount <= 0:
            raise HTTPException(status_code=400, detail="Seat amount must be a positive integer")
            
        if seat_type == "Business":
            seat_cost = Business.SEAT_PRICE
        elif seat_type == "Economy":
            seat_cost = Economy.SEAT_PRICE
        else:
            raise HTTPException(status_code=400, detail="Invalid seat")

        fare = (flight_price + (seat_cost * seat_amount)) * (1 - discount)
        return fare
    
    def pay_book(self, id: str, pnr: str, payment_method: str, validate_object: str | None = None) -> Booking:
        id = id.strip()
        pnr = pnr.strip().upper()
        
        received_passenger = self.search_passenger_by_id(id)
        received_book = received_passenger.find_booking(pnr)
        
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
    
    def check_flight_status(self,flight_instance, status):
        if flight_instance.status != status:
            raise HTTPException(status_code=400, detail=f"You can't do this because flight status is now {status}")
    
    def booking(self, id: str, flight_no: str, departure_time: str, seat_type: str, seat_amount: int) -> Booking:
        id = id.strip()
        flight_no = flight_no.strip().upper()
        seat_type = seat_type.strip().capitalize()
        
        if not isinstance(seat_amount, int) or seat_amount <= 0:
            raise HTTPException(status_code=400, detail="Seat amount must be a positive integer")
            
        received_passenger = self.search_passenger_by_id(id)
        flight_instance = received_passenger.flight_instance

        self.check_flight_status(self,flight_instance, FlightStatus.SCHEDULED)

        if received_passenger.is_blacklisted:
            raise HTTPException(status_code=403, detail="You are on the blacklist and cannot book until your blacklist time is over")
        try:
            date_departure_time = datetime.strptime(departure_time.strip(), '%d-%m-%Y %H:%M')
        except ValueError:
            raise HTTPException(status_code=400, detail="Date Format is wrong")

        received_flight_instance = self.find_flight_instance(flight_no, date_departure_time)

        received_flight_instance.check_seat_availability(seat_type, seat_amount)
            
        for i in range(seat_amount):
            received_flight_instance.reserve_seat(seat_type)
        discount = received_passenger.DISCOUNT
        price = self.calculate_fare(received_flight_instance.price, seat_type, seat_amount, discount)

        new_book = Booking(received_passenger, received_flight_instance, seat_type, seat_amount, price)
        received_passenger.add_booking(new_book)
        self.add_booking(new_book)
        return new_book

    def cancel_booking(self, id: str, pnr: str) -> str:
        id = id.strip()
        pnr = pnr.strip().upper()
        
        current_passenger = self.search_passenger_by_id(id)
        current_booking = current_passenger.find_booking(pnr)
        
        if current_booking.booking_status != BookingStatus.PENDING:
            raise HTTPException(status_code=400, detail="This booking is not able to be canceled")
        
        current_booking.cancel_booking()
        current_flight_instance = current_booking.flight_instance
        current_flight_instance.release_seat(current_booking.seat_type, current_booking.seat_amount)
        return "Canceled booking successful."
    
    def request_refund(self, pnr: str, passenger_id: str) -> str:
        print("Airline: refund requested")
        pnr = pnr.strip().upper()
        passenger_id = passenger_id.strip()



        passenger: Passenger = self.search_passenger_by_id(passenger_id)
        booking: Booking = passenger.find_booking(pnr)

        if not (booking.booking_status == BookingStatus.CONFIRMED and booking.payment_status == PaymentStatus.PAID):
            raise HTTPException(
                status_code=400,
                detail="Booking Status or Payment Status Invalid for refund"
            )

        if not passenger.check_refunded_total():
            raise HTTPException(
                status_code=403,
                detail="Reach Maximum Refund Limit or System Error"
            )
        
        flight_instance = booking.flight_instance
        if not flight_instance.is_refundable_time():
            raise HTTPException(
                status_code=400,
                detail="Cannot refund: Flight departure is in less than 24 hours."
            )

        T: Transaction = booking.transaction
        payment_type_str = T.payment_type
        price = T.amount

        payment_type = Payment.get_payment_type(payment_type_str)
        payment_type.refund(passenger, price)       

        booking.update_booking_status(BookingStatus.CANCELED)
        booking.update_payment_status(PaymentStatus.REFUNDED)

        flight_instance.update_total_income(-price)
        passenger.add_refunded_total()

        flight_instance.release_seat(booking.seat_type, booking.seat_amount)

        if passenger.refunded_total == 3:
            self.__blacklist_list.append(passenger)
            passenger.make_blacklist()

        print(f"Refund confirmed for PNR {booking.pnr}")
        return f"Refund confirmed for PNR {booking.pnr}"
    
    def buy_food(self, passenger_id: str, pnr: str, food_name: str, quantity: int, payment_type: str, pin: str) -> str:
        passenger_id = passenger_id.strip()
        pnr = pnr.strip().upper()
        food_name = food_name.strip()
        
        flight_instance = booking.flight_instance
        self.check_flight_status(self,flight_instance, FlightStatus.SCHEDULED)

        if not isinstance(quantity, int) or quantity <= 0:
            raise HTTPException(status_code=400, detail="Quantity must be a positive integer")

        passenger = self.search_passenger_by_id(passenger_id)
        booking = passenger.find_booking(pnr)

        # [แก้บัค] ต้องอนุญาตให้สถานะ COMPLETED สั่งอาหารได้ด้วย เพราะต้องเลือกที่นั่งก่อนถึงจะเสิร์ฟอาหารได้
        if booking.booking_status not in [BookingStatus.CHECKEDIN, BookingStatus.COMPLETED] or booking.payment_status != PaymentStatus.PAID:
            raise HTTPException(
                status_code=400,
                detail="Booking must be Checked-in/Completed and Paid to buy food"
            )

        flight_seat = flight_instance.find_flight_seat_by_passenger_id(passenger_id)
        food = flight_instance.find_flight_instance_food_by_food_name(food_name)
        
        price = food.calculate_price(quantity)

        payment = Payment.get_payment_type(payment_type)
        if payment is not None:
            payment.validate(passenger, pin)
            payment.pay(received_passenger=passenger, price=price)
            flight_instance.update_total_income(price)

        sub_transaction = SubTransaction(food_name, price, payment_type)
        transaction = booking.transaction
        transaction.add_sub_transaction(sub_transaction)

        flight_seat.add_food(food)

        return "Order Food Success"
    
    def create_income_report(self, flight_no: str) -> list[str]:
        flight_no = flight_no.strip().upper()
        string = []
        total = 0.0
        f = self.find_flight(flight_no)
        
        header = f"Income report of flight number:{f.flight_no}(from {f.origin} to {f.destination})"
        string.append(header)
        for ff in f.flight_instance_list:
            content = f" Flight that travel from {ff.departure_time} to {ff.arrival_time} has earned income of {ff.total_income}"
            total += ff.total_income
            string.append(content)
        string.append(f"Total income of flight: {f.flight_no} is {total}")
        return string
    
    def get_account(self, tier: str) -> type[Passenger]:
        tier = tier.strip().capitalize()
        classes_to_check = Passenger.__subclasses__()
        
        while classes_to_check:
            cls = classes_to_check.pop(0)
            
            if getattr(cls, "identifier", None) == tier:
                return cls
                
            classes_to_check.extend(cls.__subclasses__())
            
        raise HTTPException(
            status_code=404, 
            detail=f"There is no {tier} tier in this airline"
        )
    
    def create_account(self, name: str, email: str, card_pin: str, money: float, tier: str) -> Passenger:
        name = name.strip()
        email = email.strip()
        
        self.validate_card_info(card_pin, money)
        passenger_class = self.get_account(tier)
        
        if passenger_class.ANNUAL_FEE > money:
            raise HTTPException(
                status_code=400, 
                detail="Not enough money to pay annual fee"
            )
            
        new_card = Card(card_pin, money)
        passenger = passenger_class(name, email)
        passenger.add_card(new_card)
        
        # [แก้บัค] จ่ายเงินเฉพาะกรณีที่คลาสนั้นมีค่าธรรมเนียม (เช่น Guest ไม่ต้องจ่าย)
        if passenger.ANNUAL_FEE > 0:
            PayByCard.pay(passenger, passenger.ANNUAL_FEE)
            
        self.add_passenger(passenger)
        return passenger

    @staticmethod
    def parse_seats(seat_string: str, available_seats: list[Seat]) -> tuple[list[str], list[str], list[str], list[Seat]]:
        chosen = []
        invalid = []
        duplicates = []
        chosen_seat_obj = []

        # [ดัก Error] เช็คก่อนว่า Input ไม่ใช่ค่าว่างล้วนๆ
        if not isinstance(seat_string, str) or not seat_string.strip():
            return chosen, ["EMPTY_INPUT"], duplicates, chosen_seat_obj

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

            if seat_code in chosen:
                duplicates.append(seat_code)
                continue

            chosen.append(seat_code)
            chosen_seat_obj.append(found)

        return chosen, invalid, duplicates, chosen_seat_obj
    
