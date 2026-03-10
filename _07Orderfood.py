from enum import Enum
from abc import ABC, abstractmethod
import copy
from fastapi import HTTPException
from datetime import datetime, timedelta

# ==========================================
# Enums
# ==========================================

class BookingStatus(Enum):
    PENDING = "Pending"
    CONFIRMED = "Confirmed"
    CANCELLED = "Cancelled"
    CHECKDIN = "Checkedin"
    NOSHOW = "Noshow"

class PaymentStatus(Enum):
    PAID = "Paid"
    UNPAID = "Unpaid"
    REFUNDED = "Refunded"

class FlightStatus(Enum):
    SCHEDULED = "Scheduled"
    CHECKINOPEN = "Checkinopen"
    BOARDING = "Boarding"
    DEPARTED = "Departed"
    ARRIVED = "Arrived"
    CANCELLED = "Cancelled"

# ==========================================
# Core Models
# ==========================================

class Booking:
    def __init__(self, pnr: str, passenger: 'Passenger', flight_instance: 'FlightInstance', seat_type: str, seat_amount: int) -> None:
        self.__pnr: str = pnr
        self.__passenger: 'Passenger' = passenger
        self.__flight: 'FlightInstance' = flight_instance
        self.__seat_type: str = seat_type
        self.__seat_amout: int = seat_amount
        self.__payment_status: PaymentStatus = PaymentStatus.PAID
        self.__booking_status: BookingStatus = BookingStatus.CHECKDIN
        self.__booking_date: datetime = datetime.now()
        self.__transaction: 'Transaction' = Transaction("Booking", "PayByCard", 5000)  # เซ็ตค่าไว้เฉยๆ เพราะต้องไดรับมาจากการเงินบุ๊กกิ้ง

    def update_status(self, booking_status: BookingStatus, payment_status: PaymentStatus) -> None:
        self.__booking_status = booking_status
        self.__payment_status = payment_status
        print(f"Booking status updated to {booking_status.value}", end=", ")
        print(f"Payment status updated to {payment_status.value}")

    @property
    def pnr(self) -> str:
        return self.__pnr

    #สำหรับทำ Transaction ของการ Refund
    def get_status_str(self) -> str:
        # TODO: ชื่อฟังชั้นแย่มาก (ควรพิจารณาเปลี่ยนชื่อ)
        return "Booking: " + self.__booking_status.value + ", Payment: " + self.__payment_status.value  

    @property
    def seat_type(self) -> str:
        return self.__seat_type

    def add_flight(self, flight: 'FlightInstance') -> None:
        self.__flight = flight

    @property
    def flight(self) -> 'FlightInstance':
        return self.__flight

    def check_status(self, booking_status: BookingStatus, payment_status: PaymentStatus) -> bool:
        return self.__booking_status == booking_status and self.__payment_status == payment_status

    @property
    def transaction(self) -> 'Transaction':
        return self.__transaction

    def get_food_transaction_list(self) -> list: # แก้ไขชื่อ Method
        return self.transaction.get_food_transaction_list()  


class Passenger(ABC):
    def __init__(self, passenger_id: str, name: str, email: str, card: 'Card') -> None:
        self.__passenger_id: str = passenger_id
        self.__name: str = name
        self.__email: str = email
        self.__card: 'Card' = card
        self.__booking_list: list['Booking'] = [] # แก้ไข Attribute
        self.__refunded_total: int = 0
        self.__is_blacklisted: bool = False
        self.__blacklist_time: timedelta | None = None
        self.__notification_list: list[str] = [] # แก้ไข Attribute

    def add_booking(self, booking: Booking) -> None:
        self.__booking_list.append(booking)

    @property
    def booking_list(self) -> list['Booking']: # แก้ไขชื่อ Method
        return self.__booking_list

    @property
    def refunded_total(self) -> int:
        return self.__refunded_total

    def add_refunded_total(self) -> None:
        self.__refunded_total += 1

    def booking_request(self) -> None:
        pass

    def check_refunded_total(self) -> bool:
        return 0 <= self.__refunded_total < 3

    @property
    def card(self) -> 'Card':
        return self.__card
    
    @property
    def name(self) -> str:
        return self.__name

    @property
    def id(self) -> str:
        return self.__passenger_id

    def find_booking(self, pnr: str) -> Booking:
        for booking in self.__booking_list: 
            id = booking.pnr
            if id == pnr:
                return booking
        raise ValueError("unfound")
    
    def make_blacklist(self) -> None:
        self.__is_blacklisted = True
        self.__blacklist_time = timedelta(days=180)

class Guest(Passenger):
    def __init__(self, passenger_id: str, name: str, email: str, card: 'Card') -> None:
        super().__init__(passenger_id, name, email, card)
        self.__discount: float = 0.0
        self.__extra_weight: int = 0
        self.__annual_fee: int = 0


class Member(Passenger):
    def __init__(self, passenger_id: str, name: str, email: str, card: 'Card', point: int = 0) -> None:
        super().__init__(passenger_id, name, email, card)
        self.__point: int = point
        self.__discount: float = 0.0
        self.__extra_weight: int = 0
        self.__annual_fee: int = 0

    @property
    def point(self) -> int:
        return self.__point
    
    def change_point(self, point: int) -> None:
        self.__point += point

class Silver(Member):
    def __init__(self, passenger_id: str, name: str, email: str, card: 'Card', point: int = 0) -> None:
        super().__init__(passenger_id, name, email, card, point)
        self.__discount: float = 0.05
        self.__extra_weight: int = 5
        self.__annual_fee: int = 200


class Gold(Member):
    def __init__(self, passenger_id: str, name: str, email: str, card: 'Card', point: int = 0) -> None:
        super().__init__(passenger_id, name, email, card, point)
        self.__discount: float = 0.10
        self.__extra_weight: int = 10
        self.__annual_fee: int = 300


class Platinum(Member):
    def __init__(self, passenger_id: str, name: str, email: str, card: 'Card', point: int = 0) -> None:
        super().__init__(passenger_id, name, email, card, point)
        self.__discount: float = 0.15
        self.__extra_weight: int = 20
        self.__annual_fee: int = 500


# ==========================================
# Payment System
# ==========================================
class Payment:
    
    def get_payment_type(self, payment_type: str):
        for cls in Payment.__subclasses__():
            if getattr(cls, "identifier", None) == payment_type:
                return cls
            
        raise HTTPException(
            status_code=404,
            detail=f"Payment method invalid"
            )
    
    @classmethod
    def validate (cls, received_passenger: Passenger,  validate_object: str | None = None) -> bool | None:
        pass
    
    @classmethod
    def pay(cls, received_passenger: Passenger, price: float) -> bool | None:
        pass

    @classmethod
    @abstractmethod
    def refund(cls, received_passenger: Passenger, price: float) -> None:
        pass

class PayByCard(Payment):
    identifier: str = "PayByCard"

    @classmethod
    def validate(cls, received_passenger: Passenger, validate_object: str | None = None) -> bool:
        card = received_passenger.card
        if card.pin != validate_object:
            raise HTTPException(
            status_code=404,
            detail=f"Incorrect Pin"
            )
        else:
            return True

    @classmethod  
    def pay(cls, received_passenger: Passenger | Member, price: float) -> bool:
        card = received_passenger.card
        if price > card.money:
                raise HTTPException(
                status_code=404,
                detail=f"Not enough money"
                )
        else:
            card = received_passenger.card
            card.change_money(-price)
            is_member = issubclass(type(received_passenger), Member)
            if is_member == True:
                received_passenger.change_point(int(price // 25)) # type: ignore
            return True
    
    @classmethod
    def refund(cls, received_passenger: Passenger, price: float) -> None:
        card = received_passenger.card
        card.change_money (price)


class PayBypoint(Payment):
    identifier: str = "PayByPoint"

    @classmethod
    def validate(cls, received_passenger: Passenger, validate_object: str | None = None) -> bool:
        is_member = issubclass(type(received_passenger), Member)

        if is_member == False:
            raise HTTPException(
                status_code=404,
                detail=f"You cannot pay by point if you are not a member"
                )
        else:
            return True
        
    @classmethod       
    def pay(cls, received_passenger: Member, price: float) -> bool:
        if price > received_passenger.point:
                raise HTTPException(
                status_code=404,
                detail=f"Not enough point"
                )
        else:
            received_passenger.change_point(int(-price))
            return True


    @classmethod
    def refund(cls, received_passenger: Member, price: float) -> None:
        received_passenger.change_point(int(price))


class Card :
    def __init__(self, pin: str, money: float) -> None:
        self.__pin: str = pin
        self.__money: float = money

    @staticmethod
    def refund(amount: float, method: str) -> None:
        print(f"Processing refund {amount} via {method}")
        # TODO: แก้ process ไม่ต้องมีหรอก validate แต่มีการคืนเงินจริงๆ แทน

    @property
    def pin(self) -> str:
        return self.__pin
    
    @property
    def money(self) -> float:
        return self.__money
    
    def change_money(self, money: float) -> None:
        self.__money += money


# ==========================================
# Flight Models
# ==========================================

class Airplane:
    def __init__(self, model_number: str, registration_no: str, economy_seat_amount: int, business_seat_amount: int) -> None:
        self.__model_number: str = model_number
        self.__registration_no: str = registration_no
        self.__economy_seat_amount: int = economy_seat_amount
        self.__business_seat_amount: int = business_seat_amount
        self.__seat_list: list['Seat'] = [] # แก้ไข Attribute

    @property
    def economy_seat_amount(self) -> int:
        return self.__economy_seat_amount
    
    @property
    def business_seat_amount(self) -> int:
        return self.__business_seat_amount


class Flight:
    def __init__(self, flight_no: str, origin: str, destination: str) -> None:
        self.__flight_no: str = flight_no
        self.__origin: str = origin
        self.__destination: str = destination
        self.__flight_instance_list: list['FlightInstance'] = [] # แก้ไข Attribute

    def crete_flight_instance(self, airplane: Airplane, departure_time: datetime, arrival_time: datetime, price: int, status: FlightStatus) -> 'FlightInstance':
        # สร้าง Instance ใหม่โดยดึงข้อมูลชื่อไฟล์ทและเส้นทางจากตัวเอง (Blueprint)
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
        
        # บันทึก Instance ที่สร้างขึ้นลงในลิสต์ของ Blueprint นี้ (ถ้ามีเมธอด add_flight)
        self.add_flight(instance) 
        return instance

    def add_flight(self, flight_instance: 'FlightInstance') -> None:
        # TODO: ชื่อฟังก์ชั้นหรือชื่อแอดทรีบิวที่กาก (ควรตั้งชื่อให้สื่อสารกว่านี้) #อาจจะผ่านการแก้แล้ว
        self.__flight_instance_list.append(flight_instance) # อ้างอิงชื่อ Attribute ใหม่


class FlightInstance(Flight):
    def __init__(self, flight_no: str, origin: str, destination: str,
        airplane: Airplane, departure_time: datetime, arrival_time: datetime,
        price: int, status: FlightStatus) -> None:

        self.__flight_no: str = flight_no
        self.__origin: str = origin
        self.__destination: str = destination
        self.__airplane: Airplane = airplane
        self.__departure_time: datetime = departure_time
        self.__arrival_time: datetime = arrival_time

        self.__economy_seat_avaliable: int = airplane.economy_seat_amount
        self.__business_seat_avaliable: int = airplane.business_seat_amount

        self.__remaining_seat_list: list['Seat'] = [] # แก้ไข Attribute
        self.__assigned_seat_list: list['FlightSeat'] = [] # แก้ไข Attribute
        self.__food_list: list['FlightFood'] = [] # แก้ไข Attribute
        self.__total_income: int = 0
        self.__price: int = price
        self.__status: FlightStatus = status

    def find_flight_seat_by_passenger_id(self, passenger_id: str) -> 'FlightSeat':
        for seat in self.__assigned_seat_list: # อ้างอิงชื่อ Attribute ใหม่
            id = seat.passenger_id
            if id == passenger_id:
                return seat
        raise ValueError("unfound")

    def find_flight_food_by_food_name(self, food_name: str) -> 'FlightFood':
        for food in self.__food_list: # อ้างอิงชื่อ Attribute ใหม่
            name = food.name
            if food_name == name:
                return food
        raise ValueError("unfound")

    def add_assigned_seat(self, flight_seat: 'FlightSeat') -> None:
        # TODO: ใช่ โลจิคนี้หรอวะ (ตรวจสอบความถูกต้องของการ assign seat) # เหมือนจะโอเครอถามเพื่อน
        self.__assigned_seat_list.append(flight_seat) # อ้างอิงชื่อ Attribute ใหม่

    def add_flight_food(self, food_menu: 'FlightFood') -> None:
        self.__food_list.append(food_menu) # อ้างอิงชื่อ Attribute ใหม่

    def updateSeat(self, seat_type: str, amount: int) -> None:
        if seat_type == "Economy" : 
            self.__economy_seat_avaliable += amount
        elif seat_type == "Bussiness":
            self.__business_seat_avaliable += amount

    @property
    def departure_time(self) -> datetime:
        return self.__departure_time

    def is_refundable_time(self) -> bool:
        # คำนวณเวลาที่เหลือก่อนเครื่องออก
        time_until_departure = self.departure_time - datetime.now()
        # ถ้าเวลาเหลือมากกว่าหรือเท่ากับ 24 ชั่วโมง จะ return True (คืนเงินได้)
        return time_until_departure >= timedelta(hours=24)

    def open_checkin(self) -> None: pass
    def close_checkin(self) -> None: pass
    def cancel_flight(self) -> None: pass
    def get_available_seat_list(self) -> None: pass # แก้ไขชื่อ Method
    def check_availabillity(self) -> None: pass


class Seat(ABC):
    def __init__(self, seat_no: str) -> None:
        self.__seat_no: str = seat_no

    @property
    @abstractmethod
    def type(self) -> str: pass

    @property
    def seat_no(self) -> str:
        return self.__seat_no


class Economy(Seat):
    def __init__(self, seat_no: str) -> None:
        super().__init__(seat_no)
        self.__luggage_limit: float = 20.0
        self.__price_multiplier: float = 1.0

    @property
    def type(self) -> str:
        return "Economy"


class Bussiness(Seat):
    def __init__(self, seat_no: str) -> None:
        super().__init__(seat_no)
        self.__luggage_limit: float = 40.0
        self.__price_multiplier: float = 2.5

    @property
    def type(self) -> str:
        return "Bussiness"


class FlightSeat:
    def __init__(self, seat: Seat) -> None:
        self.__passenger: Passenger | None = None
        self.__seat: Seat = seat
        self.__food_list: list['FlightFood'] = [] # แก้ไข Attribute
        self.__extra_weight: float = 0.0

    def assigh_passenger(self, passenger: Passenger) -> None:
        self.__passenger = passenger

    def assigh_seat(self, seat: Seat) -> None:
        # TODO: จริงอาจจะไม่ต้องมี (เพราะมีใน Seat object อยู่แล้ว) #เหมือนจะแก้ แล้วแต่ยังไม่ชัวร์ว่าต้องมีไหม
        self.__seat = seat
    
    @property
    def seat(self) -> Seat:
        return self.__seat

    @property
    def seat_no(self) -> str:
        return self.__seat.seat_no

    def is_available(self) -> bool:
        return self.__passenger is None

    def add_food(self, food: 'FlightFood', quantity: int) -> None:
        for i in range(0, quantity, 1):
            new_food_instance = copy.deepcopy(food)
            self.__food_list.append(new_food_instance) # อ้างอิงชื่อ Attribute ใหม่

    @property
    def passenger_name(self) -> str:
        if self.__passenger is not None:
            return self.__passenger.name
        return "Unknown"

    @property
    def passenger_id(self) -> str:
        if self.__passenger is not None:
            return self.__passenger.id
        return "Unknown"


class FlightFood:
    def __init__(self, name: str, price: float, teir_type: str) -> None:
        self.__name: str = name
        self.__price: float = price

    @property
    def name(self) -> str:
        return self.__name
    
    def calculate_price(self, quantity: int) -> float:
        return self.__price * quantity


# ==========================================
# Transaction models
# ==========================================

class Transaction:
    def __init__(self, name: str, payment_type: str, amount: float) -> None:
        self.__name: str = name
        self.__sub_tran_list: list['SubTransaction'] = [] # แก้ไข Attribute
        self.__payment_type: str = payment_type
        self.__amount: float = amount

    def add_sub_transaction(self, sub_transaction: 'SubTransaction') -> None:
        self.__sub_tran_list.append(sub_transaction) # อ้างอิงชื่อ Attribute ใหม่

    def get_food_transaction_list(self) -> list[list]: # แก้ไขชื่อ Method
        msg = []
        for T in self.__sub_tran_list: # อ้างอิงชื่อ Attribute ใหม่
            if T.name != "LoadLuggage":
                sub_msg = [T.name, T.payment_type, T.amount]
                msg.append(sub_msg)
        return msg
    
    @property
    def amount(self) -> float:
        return self.__amount

    @property
    def payment_type(self) -> str:
        return self.__payment_type


class SubTransaction:
    def __init__(self, name: str, payment_type: str, amount: float) -> None:
        self.__name: str = name
        self.__payment_type: str = payment_type
        self.__amount: float = amount

    @property
    def name(self) -> str: return self.__name
    
    @property
    def amount(self) -> float: return self.__amount
    
    @property
    def payment_type(self) -> str: return self.__payment_type

# ==========================================
# Ticket Part
# ==========================================

class Ticket:
    def __init__(self, passenger: Passenger, flight: FlightInstance, 
        origin: str, destination: str, 
        departure_time: datetime, seat: FlightSeat) -> None:

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
    def __init__(self, airline_name: str) -> None:
        self.__airline_name: str = airline_name
        self.__passenger_list: list[Passenger] = [] # แก้ไข Attribute
        self.__booking_list: list[Booking] = [] # แก้ไข Attribute
        self.__airplane_list: list[Airplane] = [] # แก้ไข Attribute
        self.__flight_list: list[Flight] = [] # แก้ไข Attribute
        self.__blacklist_list: list[Passenger] = [] # แก้ไข Attribute

    def request_refund(self, pnr: str, passenger_id: str) -> str:
        print("Airline: refund requested")

        passenger = self.find_passenger_by_id(passenger_id)
        booking = passenger.find_booking(pnr)

        if not booking.check_status(BookingStatus.CONFIRMED, PaymentStatus.PAID):
            raise Exception("Status Invalid")

        if not passenger.check_refunded_total():
            raise Exception("Reach Maximum Refund or System Error")
        
        flight_instance = booking.flight
        if not flight_instance.is_refundable_time():
            raise Exception("Cannot refund: Flight departure is in less than 24 hours.")

        T = booking.transaction
        payment_type = T.payment_type
        price = T.amount

        payment_system = Payment()
        payment = payment_system.get_payment_type(payment_type)
        payment.refund(passenger, price)       

        booking.update_status(BookingStatus.CANCELLED, PaymentStatus.REFUNDED)
        passenger.add_refunded_total()

        flight_instance.updateSeat(booking.seat_type, 1)

        if passenger.refunded_total == 3:
            self.__blacklist_list.append(passenger)
            passenger.make_blacklist()

        print(f"Refund confirmed for PNR {booking.pnr}")
        return f"Refund confirmed for PNR {booking.pnr}"


    def buy_food(self, passenger_id: str, pnr: str, food_name: str, quantity: int, payment_type: str, pin: str) -> str:
        # [1] Identification
        passenger = self.find_passenger_by_id(passenger_id)
        booking = passenger.find_booking(pnr)

        # [2] Validation
        booking.check_status(BookingStatus.CHECKDIN, PaymentStatus.PAID)

        # [3] Location Retrieval
        flight_instance = booking.flight
        flight_seat = self.get_flight_seat(flight_instance, passenger_id)

        # [4] Menu & Pricing
        food = self.get_food(flight_instance, food_name)
        price = food.calculate_price(quantity)

        # [5] Payment Processing
        # TODO: ตรวจสอบ/แก้ไขกระบวนการดึง Payment Object ตรงนี้
        payment_system = Payment()
        payment = payment_system.get_payment_type(payment_type)
        if payment is not None:
            payment.validate(passenger, pin)
            payment.pay(received_passenger=passenger, price=price)

        # [6] Finalizing & Records
        sub_transaction = self.create_sub_transaction(food_name, payment_type, price)
        transaction = booking.transaction
        transaction.add_sub_transaction(sub_transaction)

        flight_seat.add_food(food, quantity)

        return "Order Food Success"

    def add_passenger(self, passenger: Passenger) -> None:
        self.__passenger_list.append(passenger) # อ้างอิงชื่อ Attribute ใหม่

    def search_booking_by_pnr(self, pnr: str) -> Booking:
        for passenger in self.__passenger_list: # อ้างอิงชื่อ Attribute ใหม่
            booking_list = passenger.booking_list # เรียกชื่อ Method ใหม่
            for booking in booking_list:
                if booking.pnr == pnr:
                    return booking
        raise ValueError("unfounded")

    def find_passenger_by_id(self, passenger_id: str) -> Passenger:
        for passenger in self.__passenger_list: # อ้างอิงชื่อ Attribute ใหม่
            if passenger.id == passenger_id:
                return passenger
        raise ValueError("unfounded")

    def find_flight_by_pnr(self, pnr: str) -> FlightInstance:
        for passenger in self.__passenger_list: # อ้างอิงชื่อ Attribute ใหม่
            booking_list = passenger.booking_list # เรียกชื่อ Method ใหม่
            for booking in booking_list:
                if booking.pnr == pnr:
                    return booking.flight
        raise ValueError("unfounded")

    def get_flight_seat(self, flight: FlightInstance, passenger_id: str) -> FlightSeat:
        return flight.find_flight_seat_by_passenger_id(passenger_id)

    # def get_payment (self, passenger : Passenger, payment_type : str): return passenger.find_payment_by_type(payment_type)

    def get_food(self, flight: FlightInstance, food_name: str) -> FlightFood:
        return flight.find_flight_food_by_food_name(food_name)

    def create_sub_transaction(self, name: str, payment_type: str, amount: float) -> SubTransaction:
        return SubTransaction(name, payment_type, amount)

    def get_food_transaction_list(self, pnr: str) -> list: # แก้ไขชื่อ Method
        booking = self.search_booking_by_pnr(pnr)
        msg = booking.get_food_transaction_list() # เรียกชื่อ Method ใหม่
        return msg

    def add_airplane(self, airplane: Airplane) -> None: self.__airplane_list.append(airplane)
    def add_booking(self, booking: Booking) -> None: self.__booking_list.append(booking) 
    def add_flight(self, flight: Flight) -> None: self.__flight_list.append(flight) 
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
    print("--- 1. Setting up Environment ---")
    airline = Airline("Thai Airways")
    food_menu = FlightFood("Pad Thai", 150.0, "Economy")

    #ตรงนี้น่าจะต้องแก้ไข เปลี่ยนเป็นการ์ดเลย
    card = Card("1234", 1000.0 )  
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


    booking = Booking("PNR12345", passenger, flight_instance, "Economy", 1)

    booking.update_status(BookingStatus.CHECKDIN, PaymentStatus.PAID)
    passenger.add_booking(booking)
    airline.add_passenger(passenger)

    print("\n--- 3. Testing buy_food Method ---")
    try:
        airline.buy_food(
            passenger_id="1234",
            pnr="PNR12345",
            food_name="Pad Thai",
            quantity=2,
            payment_type="PayByCard",
            pin="1234"
        )
        print("Order Food Success !")
        print(booking.transaction.get_food_transaction_list()) # เรียกชื่อ Method ใหม่
    except Exception as e:
        print(f"FAILED: {str(e)}")