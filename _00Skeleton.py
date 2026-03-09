from enum import Enum
from datetime import datetime
from abc import ABC, abstractmethod
import copy
from fastapi import HTTPException
from typing import List, Optional, Any

# ==========================================
# Enums
# ==========================================

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

# ==========================================
# Core Models
# ==========================================

class Booking:
    def __init__(self, pnr: str, passenger: 'Passenger', flight_instance: 'FlightInstance', seat_type: 'Seat', seat_amount: int):
        self.__pnr: str = pnr
        self.__passenger: 'Passenger' = passenger
        self.__flight: 'FlightInstance' = flight_instance
        self.__seat_type: 'Seat' = seat_type
        self.__seat_amount: int = seat_amount
        self.__payment_status: PaymentStatus = PaymentStatus.PAID
        self.__booking_status: BookingStatus = BookingStatus.CHECKED_IN
        self.__booking_date: datetime = datetime.now()
        self.__transaction: 'Transaction' = Transaction("Booking", "Original Method", 0)

    def update_status(self, booking_status: BookingStatus, payment_status: PaymentStatus) -> None:
        self.__booking_status = booking_status
        self.__payment_status = payment_status
        print(f"Booking status updated to {booking_status.value}", end=", ")
        print(f"Payment status updated to {payment_status.value}")

    def get_pnr(self) -> str:
        return self.__pnr

    def get_status_str(self) -> str:
        return "Booking: " + self.__booking_status.value + ", Payment: " + self.__payment_status.value  

    def get_seat_type(self) -> str:
        return self.__seat_type.get_type()

    def add_flight(self, flight: 'FlightInstance') -> None:
        self.__flight = flight

    def get_flight(self) -> 'FlightInstance':
        return self.__flight

    def check_status(self, booking_status: BookingStatus, payment_status: PaymentStatus) -> bool:
        return self.__booking_status == booking_status and self.__payment_status == payment_status

    def get_transaction(self) -> 'Transaction':
        return self.__transaction

    def get_food_transaction_list(self) -> List[list]:
        return self.__transaction.get_food_transaction_list()  


class Passenger(ABC):
    def __init__(self, passenger_id: str, name: str, email: str, card: 'Card'):
        self.__passenger_id: str = passenger_id
        self.__name: str = name
        self.__email: str = email
        self.__card: 'Card' = card
        self.__booking_list: List['Booking'] = []
        self.__refunded_total: int = 0
        self.__is_blacklisted: bool = False
        self.__blacklist_time: Optional[datetime] = None
        self.__notification_list: List[str] = []

    def add_booking(self, booking: Booking) -> None:
        self.__booking_list.append(booking)

    def get_booking_list(self) -> List[Booking]:
        return self.__booking_list

    def get_refunded_total(self) -> int:
        return self.__refunded_total

    def add_refunded_total(self) -> None:
        self.__refunded_total += 1

    def booking_request(self) -> None:
        pass

    def check_refunded_total(self) -> bool:
        return 0 <= self.__refunded_total < 3

    def get_card(self) -> 'Card':
        return self.__card

    def get_name(self) -> str:
        return self.__name

    def get_id(self) -> str:
        return self.__passenger_id

    def search_booking_by_pnr(self, pnr: str) -> Booking:
        for booking in self.__booking_list:
            if booking.get_pnr() == pnr:
                return booking
        raise ValueError("unfound")


class Guest(Passenger):
    def __init__(self, passenger_id: str, name: str, email: str, card: 'Card'):
        super().__init__(passenger_id, name, email, card)
        self.__discount: float = 0.0
        self.__extra_weight: int = 0
        self.__annual_fee: int = 0


class Member(Passenger):
    def __init__(self, passenger_id: str, name: str, email: str, card: 'Card', point: int = 0):
        super().__init__(passenger_id, name, email, card)
        self.__point: int = point
        self.__discount: float = 0.0
        self.__extra_weight: int = 0
        self.__annual_fee: int = 0


class Silver(Member):
    def __init__(self, passenger_id: str, name: str, email: str, card: 'Card', point: int = 0):
        super().__init__(passenger_id, name, email, card, point)
        self.__discount: float = 0.05
        self.__extra_weight: int = 5
        self.__annual_fee: int = 200


class Gold(Member):
    def __init__(self, passenger_id: str, name: str, email: str, card: 'Card', point: int = 0):
        super().__init__(passenger_id, name, email, card, point)
        self.__discount: float = 0.10
        self.__extra_weight: int = 10
        self.__annual_fee: int = 300


class Platinum(Member):
    def __init__(self, passenger_id: str, name: str, email: str, card: 'Card', point: int = 0):
        super().__init__(passenger_id, name, email, card, point)
        self.__discount: float = 0.15
        self.__extra_weight: int = 20
        self.__annual_fee: int = 500

# ==========================================
# Payment System
# ==========================================

class Payment(ABC):

    identifier: str
    
    @staticmethod
    def get_payment_type(payment_type: str) -> 'Payment':
        for cls in Payment.__subclasses__():
            if getattr(cls, 'identifier', None) == payment_type:
                return cls()
            
        raise HTTPException(
            status_code=404,
            detail=f"Payment method invalid"
            )
    
    @abstractmethod
    def pay(self, passenger: Passenger, amount: float, pin: str) -> None:
        pass
    
    @staticmethod
    @abstractmethod
    def refund(amount: float, method: str) -> None:
        print(f"Processing refund {amount} via {method}")

    @abstractmethod
    def decrease_money(self, price: float) -> None:
        pass


class PayByCard(Payment):
    identifier = "PayByCard"
    def validate(self, received_book: Booking, validate_object: Any = None) -> None:
        pass

    def pay(self, passenger: Passenger = None, amount: float = 0, pin: str = "") -> None:
        pass
    
    @staticmethod
    def refund(amount: float, method: str) -> None:
        print(f"Processing refund {amount} via {method}")

    def decrease_money(self, price: float) -> None:
        pass


class PayBypoint(Payment):
    identifier = "PayByPoint"
    def validate(self, received_book: Booking, validate_object: Any = None) -> None:
        pass

    @staticmethod
    def refund(amount: float, method: str) -> None:
        print(f"Processing refund {amount} via {method}")

    def decrease_money(self, price: float) -> None:
        pass

    def pay(self, passenger: Passenger = None, amount: float = 0, pin: str = "") -> None:
        pass


class Card:
    def __init__(self, pin: str, money: float):
        self.__pin: str = pin
        self.__money: float = money

    @staticmethod
    def refund(amount: float, method: str) -> None:
        print(f"Processing refund {amount} via {method}")

    def pay(self) -> None:
        pass

    def decrease_money(self, price: float) -> None:
        pass

# ==========================================
# Flight Models
# ==========================================

class Airplane:
    def __init__(self, model_number: str, registration_no: str, economy_seat_amount: int, business_seat_amount: int):
        self.__model_number: str = model_number
        self.__registration_no: str = registration_no
        self.__economy_seat_amount: int = economy_seat_amount
        self.__business_seat_amount: int = business_seat_amount
        self.__seat_list: List['Seat'] = []

    def get_economy_seat_amount (self)->int:
        return self.__economy_seat_amount
    
    def get_business_seat_amount (self)->int:
        return self.__business_seat_amount

class Flight:
    def __init__(self, flight_no: str, origin: str, destination: str):
        self.__flight_no: str = flight_no
        self.__origin: str = origin
        self.__destination: str = destination
        self.__flight_instance_list: List['FlightInstance'] = []

    def create_flight_instance(self, airplane: Airplane, departure_time: datetime, arrival_time: datetime, price: int, status: FlightStatus) -> 'FlightInstance':
        instance = FlightInstance(
            self.__flight_no, 
            self.__origin, 
            self.__destination, 
            airplane, 
            departure_time, 
            arrival_time, 
            price, 
            status
        )
        self.add_flight(instance) 
        return instance

    def add_flight(self, flight_instance: 'FlightInstance') -> None:
        self.__flight_instance_list.append(flight_instance)


class FlightInstance(Flight):
    def __init__(self, flight_no: str, origin: str, destination: str,
        airplane: Airplane, departure_time: datetime, arrival_time: datetime,
        price: int, status: FlightStatus):

        super().__init__(flight_no, origin, destination)
        self.__airplane: Airplane = airplane
        self.__departure_time: datetime = departure_time
        self.__arrival_time: datetime = arrival_time

        self.__remaining_seat_list: List['FlightSeat'] = []
        self.__assigned_seat_list: List['FlightSeat'] = []

        self.__economy_seat_avaliable :int = airplane.get_economy_seat_amount()
        self.__business_seat_avaliable :int = airplane.get_business_seat_amount()

        self.__food_list: List['FlightFood'] = []
        self.__total_income: int = 0
        self.__price: int = price
        self.__status: FlightStatus = status

    def find_flight_seat_by_passenger_id(self, passenger_id: str) -> 'FlightSeat':
        for seat in self.__assigned_seat_list:
            if seat.get_passenger_id() == passenger_id:
                return seat
        raise ValueError("unfound")

    def find_flight_food_by_food_name(self, food_name: str) -> 'FlightFood':
        for food in self.__food_list:
            if food.get_name() == food_name:
                return food
        raise ValueError("unfound")

    def add_assigned_seat(self, flight_seat: 'FlightSeat') -> None:
        self.__assigned_seat_list.append(flight_seat)

    def add_flight_food(self, food_menu: 'FlightFood') -> None:
        self.__food_list.append(food_menu)

    def updateSeat(self, seat: 'FlightSeat') -> None:
        self.__assigned_seat_list.remove(seat)
        raw_seat = seat.get_seat()
        self.__remaining_seat_list.append(seat)

    def open_checkin(self) -> None: pass
    def close_checkin(self) -> None: pass
    def cancel_flight(self) -> None: pass
    def get_available_seat_list(self) -> List['FlightSeat']: pass
    def check_availabillity(self) -> bool: pass


class Seat(ABC):
    def __init__(self, seat_no: str):
        self.__seat_no: str = seat_no

    @abstractmethod
    def get_type(self) -> str: pass

    def get_seat_no(self) -> str:
        return self.__seat_no


class Economy(Seat):
    def __init__(self, seat_no: str):
        super().__init__(seat_no)
        self.__luggage_limit: int = 20
        self.__price_multiplier: float = 1.0

    def get_type(self) -> str:
        return "Economy"


class Business(Seat):
    def __init__(self, seat_no: str):
        super().__init__(seat_no)
        self.__luggage_limit: int = 40
        self.__price_multiplier: float = 2.5

    def get_type(self) -> str:
        return "Business"


class FlightSeat:
    def __init__(self, seat: Seat):
        self.__passenger: Optional[Passenger] = None
        self.__seat: Seat = seat
        self.__food_list: List['FlightFood'] = []
        self.__extra_weight: int = 0

    def assign_passenger(self, passenger: Passenger) -> None:
        self.__passenger = passenger

    def assign_seat(self, seat: Seat) -> None:
        self.__seat = seat
    
    def get_seat(self) -> Seat:
        return self.__seat

    def get_seat_no(self) -> str:
        return self.__seat.get_seat_no()

    def is_available(self) -> bool:
        return self.__passenger is None

    def add_food(self, food: 'FlightFood', quantity: int) -> None:
        for _ in range(0, quantity, 1):
            new_food_instance = copy.deepcopy(food)
            self.__food_list.append(new_food_instance)

    def get_passenger_name(self) -> str:
        if self.__passenger is not None:
            return self.__passenger.get_name()
        return "Unknown"

    def get_passenger_id(self) -> str:
        if self.__passenger is not None:
            return self.__passenger.get_id()
        return "Unknown"


class FlightFood:
    def __init__(self, name: str, price: float, teir_type: str):
        self.__name: str = name
        self.__price: float = price

    def get_name(self) -> str:
        return self.__name
    
    def calculate_price(self, quantity: int) -> float:
        return self.__price * quantity

# ==========================================
# Transaction models
# ==========================================

class Transaction:
    def __init__(self, name: str, payment_type: str, amount: float):
        self.__name: str = name
        self.__sub_tran_list: List['SubTransaction'] = []
        self.__payment_type: str = payment_type
        self.__amount: float = amount

    def add_sub_transaction(self, sub_transaction: 'SubTransaction') -> None:
        self.__sub_tran_list.append(sub_transaction)

    def get_food_transaction_list(self) -> List[list]:
        msg = []
        for T in self.__sub_tran_list:
            if T.get_name() != "LoadLuggage":
                sub_msg = [T.get_name(), T.get_payment_type(), T.get_amount()]
                msg.append(sub_msg)
        return msg
    
    def get_amount(self) -> float:
        return self.__amount

    def get_payment_type(self) -> str:
        return self.__payment_type


class SubTransaction:
    def __init__(self, name: str, payment_type: str, amount: float):
        self.__name: str = name
        self.__payment_type: str = payment_type
        self.__amount: float = amount

    def get_name(self) -> str: return self.__name
    def get_amount(self) -> float: return self.__amount
    def get_payment_type(self) -> str: return self.__payment_type

# ==========================================
# Ticket Part
# ==========================================

class Ticket:
    def __init__(self, passenger: Passenger, flight: FlightInstance, 
        origin: str, destination: str, 
        departure_time: datetime, seat: FlightSeat):

        self.__passenger: Passenger = passenger
        self.__flight: FlightInstance = flight
        self.__origin: str = origin
        self.__destination: str = destination
        self.__departure_time: datetime = departure_time
        self.__seat: FlightSeat = seat

# ==========================================
# Airline Service
# ==========================================

class Airline:
    def __init__(self, airline_name: str):
        self.__airline_name: str = airline_name
        self.__passenger_list: List[Passenger] = []
        self.__booking_list: List[Booking] = []
        self.__airplane_list: List[Airplane] = []
        self.__flight_list: List[Flight] = []
        self.__blacklist_list: List[Passenger] = []

    def request_refund(self, pnr: str, passenger_id: str) -> str:
        print("Airline: refund requested")

        booking = self.search_booking_by_pnr(pnr)
        passenger = self.find_passenger_by_id(passenger_id)

        if not booking.check_status(BookingStatus.CONFIRMED, PaymentStatus.PAID):
            raise Exception("Status Invalid")

        if not passenger.check_refunded_total():
            raise Exception("Reach Maximum Refund or System Error")

        booking.update_status(BookingStatus.CANCELLED, PaymentStatus.REFUNDED)
        passenger.add_refunded_total()

        if passenger.get_refunded_total() == 3:
            self.__blacklist_list.append(passenger)

        print(f"Refund confirmed for PNR {booking.get_pnr()}")
        return f"Refund confirmed for PNR {booking.get_pnr()}"

    def buy_food(self, passenger_id: str, pnr: str, food_name: str, quantity: int, payment_type: str, pin: str) -> str:
        passenger = self.find_passenger_by_id(passenger_id)
        booking = self.find_booking(pnr, passenger)

        booking.check_status(BookingStatus.CHECKED_IN, PaymentStatus.PAID)

        flight_instance = booking.get_flight()
        flight_seat = self.get_flight_seat(flight_instance, passenger_id)

        food = self.get_food(flight_instance, food_name)
        price = food.calculate_price(quantity)

        payment = Payment.get_payment_type(payment_type)
        if payment is not None:
            payment.pay(passenger, price, pin)

        sub_transaction = self.create_sub_transaction(food_name, payment_type, price)
        transaction = booking.get_transaction()
        transaction.add_sub_transaction(sub_transaction)

        flight_seat.add_food(food, quantity)

        return "Order Food Success"

    def add_passenger(self, passenger: Passenger) -> None:
        self.__passenger_list.append(passenger)

    def search_booking_by_pnr(self, pnr: str) -> Booking:
        for passenger in self.__passenger_list:
            booking_list = passenger.get_booking_list()
            for booking in booking_list:
                if booking.get_pnr() == pnr:
                    return booking
        raise ValueError("unfounded")

    def find_booking(self, pnr: str, passenger: Passenger) -> Booking:
        return passenger.search_booking_by_pnr(pnr)

    def find_passenger_by_id(self, passenger_id: str) -> Passenger:
        for passenger in self.__passenger_list:
            if passenger.get_id() == passenger_id:
                return passenger
        raise ValueError("unfounded")

    def find_flight_by_pnr(self, pnr: str) -> FlightInstance:
        for passenger in self.__passenger_list:
            booking_list = passenger.get_booking_list()
            for booking in booking_list:
                if booking.get_pnr() == pnr:
                    return booking.get_flight()
        raise ValueError("unfounded")

    def get_flight_seat(self, flight: FlightInstance, passenger_id: str) -> FlightSeat:
        return flight.find_flight_seat_by_passenger_id(passenger_id)

    def get_food(self, flight: FlightInstance, food_name: str) -> FlightFood:
        return flight.find_flight_food_by_food_name(food_name)

    def create_sub_transaction(self, name: str, payment_type: str, amount: float) -> SubTransaction:
        return SubTransaction(name, payment_type, amount)

    def get_food_transaction_list(self, pnr: str) -> List[list]:
        booking = self.search_booking_by_pnr(pnr)
        msg = booking.get_food_transaction_list()
        return msg

    def add_airplane(self) -> None: pass
    def add_booking(self) -> None: pass
    def add_flight(self) -> None: pass
    def booking(self) -> None: pass
    def calculate_extra_weight_fee(self) -> None: pass
    def calculate_fare(self) -> None: pass
    def check_in_passenger(self) -> None: pass
    def choose_seat(self) -> None: pass
    def generate_report(self) -> None: pass
    def remove_flight(self) -> None: pass
    def search_passenger_by_id(self) -> None: pass
    def update_flight(self) -> None: pass
    def verify_weight(self) -> None: pass

# ==========================================
# Main Execution
# ==========================================

if __name__ == "__main__":
    pass