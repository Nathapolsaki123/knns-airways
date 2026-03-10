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
        self.__transaction: 'Transaction' = Transaction("Booking", "PayByCard", 5000)  

    def update_status(self, booking_status: BookingStatus, payment_status: PaymentStatus) -> None:
        self.__booking_status = booking_status
        self.__payment_status = payment_status
        print(f"Booking status updated to {booking_status.value}", end=", ")
        print(f"Payment status updated to {payment_status.value}")

    @property
    def pnr(self) -> str:
        return self.__pnr

    def get_status_str(self) -> str:
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

    def get_food_transaction_list(self) -> list: 
        return self.transaction.get_food_transaction_list()  


class Passenger(ABC):
    def __init__(self, passenger_id: str, name: str, email: str, card: 'Card') -> None:
        self.__passenger_id: str = passenger_id
        self.__name: str = name
        self.__email: str = email
        self.__card: 'Card' = card
        self.__booking_list: list['Booking'] = [] 
        self.__refunded_total: int = 0
        self.__is_blacklisted: bool = False
        self.__blacklist_time: timedelta | None = None
        self.__notification_list: list[str] = [] 

    def add_booking(self, booking: Booking) -> None:
        self.__booking_list.append(booking)

    @property
    def booking_list(self) -> list['Booking']: 
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
        # [Error Handling] กรณีหา PNR ไม่เจอ
        raise HTTPException(
            status_code=404,
            detail=f"Booking PNR '{pnr}' not found for passenger '{self.__name}'"
        )
    
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
        # [Error Handling] ป้องกัน Point ติดลบ
        if self.__point + point < 0:
            raise HTTPException(status_code=400, detail="Member points cannot be negative")
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
    def pay(cls, received_passenger: Passenger, price: float) -> bool:
        # [Error Handling] ป้องกันยอดเงินจ่ายติดลบหรือ 0
        if price <= 0:
            raise HTTPException(status_code=400, detail="Payment price must be strictly positive")

        card = received_passenger.card
        if price > card.money:
                raise HTTPException(
                status_code=404,
                detail=f"Not enough money"
                )
        else:
            card.change_money(-price)
            if isinstance(received_passenger, Member):
                received_passenger.change_point(int(price // 25))
            return True
    
    @classmethod
    def refund(cls, received_passenger: Passenger, price: float) -> None:
        # [Error Handling] ป้องกันยอดคืนเงินติดลบหรือ 0
        if price <= 0:
            raise HTTPException(status_code=400, detail="Refund amount must be strictly positive")

        card = received_passenger.card
        card.change_money (price)


class PayBypoint(Payment):
    identifier: str = "PayByPoint"

    @classmethod
    def validate(cls, received_passenger: Passenger, validate_object: str | None = None) -> bool:
        is_member = isinstance(received_passenger, Member)

        if is_member == False:
            raise HTTPException(
                status_code=404,
                detail=f"You cannot pay by point if you are not a member"
                )
        else:
            return True
        
    @classmethod       
    def pay(cls, received_passenger: Member, price: float) -> bool:
        # [Error Handling] ป้องกันยอดจ่ายพ้อยท์ติดลบหรือ 0
        if price <= 0:
            raise HTTPException(status_code=400, detail="Payment point amount must be strictly positive")

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
        # [Error Handling] ป้องกันยอดคืนพ้อยท์ติดลบหรือ 0
        if price <= 0:
            raise HTTPException(status_code=400, detail="Refund point amount must be strictly positive")

        received_passenger.change_point(int(price))


class Card :
    def __init__(self, pin: str, money: float) -> None:
        self.__pin: str = pin
        self.__money: float = money

    @staticmethod
    def refund(amount: float, method: str) -> None:
        print(f"Processing refund {amount} via {method}")

    @property
    def pin(self) -> str:
        return self.__pin
    
    @property
    def money(self) -> float:
        return self.__money
    
    def change_money(self, money: float) -> None:
        # [Error Handling] ป้องกันเงินในบัตรทะลุติดลบ
        if self.__money + money < 0:
            raise HTTPException(status_code=400, detail="Card balance cannot be negative")
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
        self.__seat_list: list['Seat'] = [] 

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
        self.__flight_instance_list: list['FlightInstance'] = [] 

    def crete_flight_instance(self, airplane: Airplane, departure_time: datetime, arrival_time: datetime, price: int, status: FlightStatus) -> 'FlightInstance':
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
        price: int, status: FlightStatus) -> None:

        self.__flight_no: str = flight_no
        self.__origin: str = origin
        self.__destination: str = destination
        self.__airplane: Airplane = airplane
        self.__departure_time: datetime = departure_time
        self.__arrival_time: datetime = arrival_time

        self.__economy_seat_avaliable: int = airplane.economy_seat_amount
        self.__business_seat_avaliable: int = airplane.business_seat_amount

        self.__remaining_seat_list: list['Seat'] = [] 
        self.__assigned_seat_list: list['FlightSeat'] = [] 
        self.__food_list: list['FlightFood'] = [] 
        self.__total_income: int = 0
        self.__price: int = price
        self.__status: FlightStatus = status

    def find_flight_seat_by_passenger_id(self, passenger_id: str) -> 'FlightSeat':
        for seat in self.__assigned_seat_list: 
            id = seat.passenger_id
            if id == passenger_id:
                return seat
        # [Error Handling] 
        raise HTTPException(
            status_code=404,
            detail=f"Seat assigned to passenger ID '{passenger_id}' not found on this flight"
        )

    def find_flight_food_by_food_name(self, food_name: str) -> 'FlightFood':
        for food in self.__food_list: 
            name = food.name
            if food_name == name:
                return food
        # [Error Handling] 
        raise HTTPException(
            status_code=404,
            detail=f"Food menu '{food_name}' not found on this flight"
        )

    def add_assigned_seat(self, flight_seat: 'FlightSeat') -> None:
        self.__assigned_seat_list.append(flight_seat) 

    def add_flight_food(self, food_menu: 'FlightFood') -> None:
        self.__food_list.append(food_menu) 

    def updateSeat(self, seat_type: str, amount: int) -> None:
        if seat_type == "Economy" : 
            self.__economy_seat_avaliable += amount
        elif seat_type == "Bussiness":
            self.__business_seat_avaliable += amount
        else:
            # [Error Handling] กันบัคส่ง seat_type ผิด
            raise HTTPException(
                status_code=400,
                detail=f"Invalid seat type: {seat_type}"
            )

    @property
    def departure_time(self) -> datetime:
        return self.__departure_time

    def is_refundable_time(self) -> bool:
        time_until_departure = self.departure_time - datetime.now()
        return time_until_departure >= timedelta(hours=24)

    def open_checkin(self) -> None: pass
    def close_checkin(self) -> None: pass
    def cancel_flight(self) -> None: pass
    def get_available_seat_list(self) -> None: pass 
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
        self.__food_list: list['FlightFood'] = [] 
        self.__extra_weight: float = 0.0

    def assigh_passenger(self, passenger: Passenger) -> None:
        self.__passenger = passenger

    def assigh_seat(self, seat: Seat) -> None:
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
            self.__food_list.append(new_food_instance) 

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
        # [Error Handling] ป้องกันสั่งอาหารติดลบหรือ 0
        if quantity <= 0:
            raise HTTPException(status_code=400, detail="Quantity must be greater than zero")
        return self.__price * quantity


# ==========================================
# Transaction models
# ==========================================

class Transaction:
    def __init__(self, name: str, payment_type: str, amount: float) -> None:
        self.__name: str = name
        self.__sub_tran_list: list['SubTransaction'] = [] 
        self.__payment_type: str = payment_type
        self.__amount: float = amount

    def add_sub_transaction(self, sub_transaction: 'SubTransaction') -> None:
        self.__sub_tran_list.append(sub_transaction) 

    def get_food_transaction_list(self) -> list[list]: 
        msg = []
        for T in self.__sub_tran_list: 
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
        self.__passenger_list: list[Passenger] = [] 
        self.__booking_list: list[Booking] = [] 
        self.__airplane_list: list[Airplane] = [] 
        self.__flight_list: list[Flight] = [] 
        self.__blacklist_list: list[Passenger] = [] 

    def request_refund(self, pnr: str, passenger_id: str) -> str:
        print("Airline: refund requested")

        passenger = self.find_passenger_by_id(passenger_id)
        booking = passenger.find_booking(pnr)

        if not booking.check_status(BookingStatus.CONFIRMED, PaymentStatus.PAID):
            # [Error Handling]
            raise HTTPException(
                status_code=400,
                detail="Booking Status or Payment Status Invalid for refund"
            )

        if not passenger.check_refunded_total():
            # [Error Handling]
            raise HTTPException(
                status_code=403,
                detail="Reach Maximum Refund Limit or System Error"
            )
        
        flight_instance = booking.flight
        if not flight_instance.is_refundable_time():
            # [Error Handling]
            raise HTTPException(
                status_code=400,
                detail="Cannot refund: Flight departure is in less than 24 hours."
            )

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
        # [Error Handling] ดักไม่ให้ผ่านถ้าสถานะไม่ถูก (ของเดิมไม่มี if ดัก)
        if not booking.check_status(BookingStatus.CHECKDIN, PaymentStatus.PAID):
            raise HTTPException(
                status_code=400,
                detail="Booking must be Checked-in and Paid to buy food"
            )

        # [3] Location Retrieval
        flight_instance = booking.flight
        flight_seat = self.get_flight_seat(flight_instance, passenger_id)

        # [4] Menu & Pricing
        food = self.get_food(flight_instance, food_name)
        price = food.calculate_price(quantity)

        # [5] Payment Processing
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
        self.__passenger_list.append(passenger) 

    def search_booking_by_pnr(self, pnr: str) -> Booking:
        for passenger in self.__passenger_list: 
            booking_list = passenger.booking_list 
            for booking in booking_list:
                if booking.pnr == pnr:
                    return booking
        # [Error Handling]
        raise HTTPException(
            status_code=404,
            detail=f"Booking PNR '{pnr}' not found in system"
        )

    def find_passenger_by_id(self, passenger_id: str) -> Passenger:
        for passenger in self.__passenger_list: 
            if passenger.id == passenger_id:
                return passenger
        # [Error Handling]
        raise HTTPException(
            status_code=404,
            detail=f"Passenger ID '{passenger_id}' not found"
        )

    def find_flight_by_pnr(self, pnr: str) -> FlightInstance:
        for passenger in self.__passenger_list: 
            booking_list = passenger.booking_list 
            for booking in booking_list:
                if booking.pnr == pnr:
                    return booking.flight
        # [Error Handling]
        raise HTTPException(
            status_code=404,
            detail=f"Flight instance not found for PNR '{pnr}'"
        )

    def get_flight_seat(self, flight: FlightInstance, passenger_id: str) -> FlightSeat:
        return flight.find_flight_seat_by_passenger_id(passenger_id)

    def get_food(self, flight: FlightInstance, food_name: str) -> FlightFood:
        return flight.find_flight_food_by_food_name(food_name)

    def create_sub_transaction(self, name: str, payment_type: str, amount: float) -> SubTransaction:
        return SubTransaction(name, payment_type, amount)

    def get_food_transaction_list(self, pnr: str) -> list: 
        booking = self.search_booking_by_pnr(pnr)
        msg = booking.get_food_transaction_list() 
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
    # 1. สร้างสายการบิน (Airline)
    airline = Airline("KNNS Airways")

    # 2. สร้างโครงสร้างพื้นฐาน: เครื่องบิน (Airplane) และเส้นทางบิน (Flight)
    boeing747 = Airplane(
        model_number="Boeing 747", 
        registration_no="HS-KMITL", 
        economy_seat_amount=300, 
        business_seat_amount=50
    )
    
    # สร้าง Blueprint ของเที่ยวบิน
    flight_blueprint = Flight("KNNS001", "Bangkok (BKK)", "Chiang Mai (CNX)")
    
    # สร้าง Instance ของเที่ยวบินจริง (FlightInstance)
    june_flight = flight_blueprint.crete_flight_instance(
        airplane=boeing747,
        departure_time=datetime(2026, 6, 23, 13, 0),
        arrival_time=datetime(2026, 6, 23, 14, 30),
        price=5000,
        status=FlightStatus.SCHEDULED
    )

    # 3. สร้างข้อมูลผู้โดยสาร (เลือกใช้ Silver Member เนื่องจาก Passenger เป็น Abstract Class)
    # ต้องมี Card เพราะใน Passenger __init__ รับพารามิเตอร์ card
    my_card = Card(pin="1234", money=20000)
    passenger = Silver(
        passenger_id="STD68011671", 
        name="John", 
        email="john@kmitl.ac.th", 
        card=my_card
    )

    # 4. การสร้างการจอง (Booking)
    # ต้องสร้าง Seat Object ก่อน (ใช้ Bussiness ตามที่ระบุใน Class)
    my_seat_type = "Bussiness"

    booking = Booking(
        pnr="PNR747", 
        passenger=passenger, 
        flight_instance=june_flight, 
        seat_type=my_seat_type, 
        seat_amount=1
    )
    
    # เพิ่มผู้โดยสารลงในระบบสายการบิน
    airline.add_passenger(passenger)
    airline.add_booking(booking)
    airline.add_flight(flight_blueprint)
    airline.add_airplane(boeing747)


    # ---------------------------------------------------------
    # ส่วนสำคัญ: การทำให้ Logic Refund ทำงานได้
    # ---------------------------------------------------------
    
    # [A] เพิ่ม Booking เข้าไปในตัว Passenger (เพื่อให้ search_booking_by_pnr หาเจอ)
    passenger.add_booking(booking)

    # [B] อัปเดตสถานะให้เป็น CONFIRMED และ PAID 
    # เพราะ Logic ใน airline.request_refund เช็ค: booking.check_status(BookingStatus.CONFIRMED, PaymentStatus.PAID)
    booking.update_status(BookingStatus.CONFIRMED, PaymentStatus.PAID)

    # 5. รันการขอคืนเงิน (Refund)
    print("--- ระบบเริ่มต้นการขอคืนเงิน (Refund Process) ---")
    try:
        # เรียกใช้ Method ตาม Signature: request_refund(self, pnr, passenger_id)
        result = airline.request_refund(pnr="PNR747", passenger_id="STD68011671")
        
        print(f"ผลลัพธ์: {result}")
        print(f"สถานะปัจจุบันของ Booking: {booking.get_status_str()}")
        print(f"จำนวนครั้งที่ Refund ไปแล้ว: {passenger.refunded_total} ครั้ง")
        
    except Exception as e:
        print(f"เกิดข้อผิดพลาดในการ Refund: {e}")