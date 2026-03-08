from enum import Enum
from datetime import datetime
from abc import ABC,abstractmethod
from fastapi import HTTPException
import copy

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
    def __init__(self, pnr: str, passenger, flight_instance, seat_type, seat_amount):
        self.__pnr = pnr
        self.__passenger = passenger
        self.__flight = flight_instance
        self.__seat_type = seat_type
        self.__seat_amout = seat_amount
        self.__payment_status = PaymentStatus.PAID
        self.__booking_status = BookingStatus.CHECKDIN
        self.__booking_date = datetime.now()
        self.__transaction = Transaction("Booking", "Original Method", 5000)  # เซ็ตค่าไว้เฉยๆ

    def update_status(self, booking_status: BookingStatus, payment_status: PaymentStatus):
        self.__booking_status = booking_status
        self.__payment_status = payment_status
        print(f"Booking status updated to {booking_status.value}", end=", ")
        print(f"Payment status updated to {payment_status.value}")

    # TODO: ต้องแก้ให้อยุ่ในทรานเซคชัน Transaction
    # def get_amount(self) -> float: return self.__fare  

    def get_pnr(self) -> str:
        return self.__pnr

    # TODO: ต้องแก้ให้อยู่ในทรานเซึคชัน
    # def get_payment(self) : return self.__payment #Payment 

    #สำหรับทำ Transaction ของการ Refund
    def get_status_str(self):
        # TODO: ชื่อฟังชั้นแย่มาก (ควรพิจารณาเปลี่ยนชื่อ)
        return "Booking: " + self.__booking_status.value + ", Payment: " + self.__payment_status.value  

    def get_seat_type(self):
        return self.__seat_type.get_type()

    def add_flight(self, flight):
        self.__flight = flight

    def get_flight (self):
        return self.__flight

    def check_status(self, booking_status, payment_status) -> bool:
        return self.__booking_status == booking_status and self.__payment_status == payment_status

    def get_transaction(self):
        return self.__transaction

    def get_food_transaction(self):
        return self.__transaction.get_food_transaction()  


class Passenger(ABC):
    def __init__(self, passenger_id: str, name: str, email: str, card):
        self.__passenger_id = passenger_id
        self.__name = name
        self.__email = email
        self.__card = card
        self.__bookings = []
        self.__refunded_total = 0
        self.__is_blacklisted = False
        self.__blacklist_time = None
        self.__notification = []

    def add_booking(self, booking: Booking):
        self.__bookings.append(booking)

    def get_booking(self):
        return self.__bookings

    def get_refunded_total(self):
        return self.__refunded_total

    def add_refunded_total(self):
        self.__refunded_total += 1

    def booking_request(self):
        pass

    def check_refunded_total(self):
        return 0 <= self.__refunded_total < 3

    def get_card(self):
        return self.__card

    # TODO: กูว่าควรมีนะแต่มันไม่มี wtf (พิจารณาเพิ่มเมธอด add_payment)
    # def add_payment (self,payment): self.__payment.append (payment) 

    def get_name(self):
        return self.__name

    def get_id(self):
        return self.__passenger_id

    # TODO: ต้องรอไอ้ขุน (รอประสานงานเรื่อง Payment search)
    # ควรอยู่ใน payment โดยส่ง paramitor ของผู้โดยสาร 
    # def find_payment_by_type (self,payment_type):
    #     for payment in self.__payment :
    #         type = payment.get_type ()
    #         if type == payment_type :
    #             return payment
    #     raise ValueError ("unfound")

    def search_booking_by_pnr(self, pnr):
        for booking in self.__bookings:
            id = booking.get_pnr()
            if id == pnr:
                return booking
        raise ValueError("unfound")


class Guest(Passenger):
    def __init__(self, passenger_id: str, name: str, email: str, card):
        super().__init__(passenger_id, name, email, card)
        self.__discount: float = 0.0
        self.__extra_weight: int = 0
        self.__annual_fee: int = 0


class Member(Passenger):
    def __init__(self, passenger_id: str, name: str, email: str, card, point: int = 0):
        super().__init__(passenger_id, name, email, card)
        self.__point: int = point
        self.__discount: float = 0.0
        self.__extra_weight: int = 0
        self.__annual_fee: int = 0


class Silver(Member):
    def __init__(self, passenger_id: str, name: str, email: str, card, point: int = 0):
        super().__init__(passenger_id, name, email, card, point)
        self.__discount: float = 0.05
        self.__extra_weight: int = 5
        self.__annual_fee: int = 200


class Gold(Member):
    def __init__(self, passenger_id: str, name: str, email: str, card, point: int = 0):
        super().__init__(passenger_id, name, email, card, point)
        self.__discount: float = 0.10
        self.__extra_weight: int = 10
        self.__annual_fee: int = 300


class Platinum(Member):
    def __init__(self, passenger_id: str, name: str, email: str, card, point: int = 0):
        super().__init__(passenger_id, name, email, card, point)
        self.__discount: float = 0.15
        self.__extra_weight: int = 20
        self.__annual_fee: int = 500


# ==========================================
# Payment System
# ==========================================

class Payment(ABC):
    @staticmethod
    def pay():
        pass

    @staticmethod
    def refund(amount: float, method: str):
        print(f"Processing refund {amount} via {method}")
        # TODO: แก้ process ไม่ต้องมีหรอก validate แต่มีการคืนเงินจริงๆ แทน

    @staticmethod
    @abstractmethod
    def get_type() -> str:
        return "Original Method"


class CardPayment(Payment):
    def __init__(self, balance: float, pin):
        self.__balance = balance
        self.__pin = pin

    @staticmethod
    def get_type():
        return "Card"

    def pay(self, pin, price: float):
        self.validate_pin(pin)
        if 0 <= self.__balance >= price:
            self.decrease_money(price)
        else:
            raise ValueError("PaymentFailed")

    def validate_pin(self, pin):
        return self.__pin == pin

    def decrease_money(self, price):
        self.__balance -= price


class PointPayment(Payment):
    def __init__(self, point):
        self.__point = point

    @staticmethod
    def get_type():
        return "Point"

    def pay(self, pin, price):
        self.validate_pin()
        if 0 <= self.__point >= price:
            self.decrease_money(price)
        else:
            raise ValueError("PaymentFailed")

    def validate_pin(self, pin=None):
        return True

    def decrease_money(self, price):
        self.__point -= price

class Card :
    def __init__(self,pin,money):
        self.__pin = pin
        self.__money = money
    #---------------------------------------------------------#
    #                      ส่วนการแก้ไขขุน                      #
    #---------------------------------------------------------#
# class Payment(ABC):

#     identifier: str
    
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

    #---------------------------------------------------------#
    #                      ส่วนการแก้ไขขุน                      #
    #---------------------------------------------------------#

# ==========================================
# Flight Models
# ==========================================

class Airplane:
    def __init__(self, model_number: str, registration_no: str, economy_seat_amount: int, business_seat_amount: int):
        self.__model_number: str = model_number
        self.__registration_no: str = registration_no
        self.__economy_seat_amount: int = economy_seat_amount
        self.__business_seat_amount: int = business_seat_amount
        self.__seats = []


class Flight:
    def __init__(self, flight_no: str, origin: str, destination: str):
        self.__flight_no: str = flight_no
        self.__origin: str = origin
        self.__destination: str = destination
        self.__flights = []

    def crete_flight_instance(self, airplane, departure_time, arrival_time, price, status):
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

    def add_flight(self, flight_instance):
        # TODO: ชื่อฟังก์ชั้นหรือชื่อแอดทรีบิวที่กาก (ควรตั้งชื่อให้สื่อสารกว่านี้) #อาจจะผ่านการแก้แล้ว
        self.__flights.append(flight_instance)  


class FlightInstance(Flight):
    def __init__(self, flight_no: str, origin: str, destination: str,
        airplane: Airplane, departure_time: datetime, arrival_time: datetime,
        price: int, status: FlightStatus):

        self.__flight_no: str = flight_no
        self.__origin: str = origin
        self.__destination: str = destination
        self.__airplane: Airplane = airplane
        self.__departure_time: datetime = departure_time
        self.__arrival_time: datetime = arrival_time

        self.__remaining_seats = []
        self.__assigned_seats = []
        self.__food = []
        self.__total_income: int = 0
        self.__price: int = price
        self.__status: FlightStatus = status

    def find_flight_seat_by_passenger_id(self, passenger_id: str):
        for seat in self.__assigned_seats:
            id = seat.get_passenger_id()
            if id == passenger_id:
                return seat
        raise ValueError("unfound")

    def find_flight_food_by_food_name(self, food_name: str):
        for food in self.__food:
            name = food.get_name()
            if food_name == name:
                return food
        raise ValueError("unfound")

    def add_assigned_seat(self, flight_seat):
        # TODO: ใช่ โลจิคนี้หรอวะ (ตรวจสอบความถูกต้องของการ assign seat) # เหมือนจะโอเครอถามเพื่อน
        self.__assigned_seats.append(flight_seat)  

    def add_flight_food(self, food_menu):
        self.__food.append(food_menu)

    # TODO: ต้องแก้โลจิค (สำหรับการอัปเดตจำนวนที่นั่ง) #อาจจะถูกแล้ว
    def updateSeat(self,seat) :

        self.__assigned_seats.remove(seat)
        raw_seat = seat.get_seat ()
        self.__remaining_seats.append(seat)

    def open_checkin(self): pass
    def close_checkin(self): pass
    def cancel_flight(self): pass
    def get_available_seat(self): pass
    def check_availabillity(self): pass


class Seat(ABC):
    def __init__(self, seat_no):
        self.__seat_no = seat_no

    @abstractmethod
    def get_type(self): pass

    def get_seat_no(self):
        return self.__seat_no


class Economy(Seat):
    def __init__(self, seat_no):
        super().__init__(seat_no)
        self.__luggage_limit = 20
        self.__price_multiplier = 1.0

    def get_type(self):
        return "Economy"


class Bussiness(Seat):
    def __init__(self, seat_no):
        super().__init__(seat_no)
        self.__luggage_limit = 40
        self.__price_multiplier = 2.5

    def get_type(self):
        return "Bussiness"


class FlightSeat:
    def __init__(self, seat: Seat):
        self.__passenger = None
        self.__seat = seat
        self.__foods = []
        self.__extra_weight = 0

    def assigh_passenger(self, passenger):
        self.__passenger = passenger

    def assigh_seat(self, seat: Seat):
        # TODO: จริงอาจจะไม่ต้องมี (เพราะมีใน Seat object อยู่แล้ว) #เหมือนจะแก้ แล้วแต่ยังไม่ชัวร์ว่าต้องมีไหม
        self.__seat = seat
    
    def get_seat (self):
        return self.__seat

    def get_seat_no(self):
        return self.__seat.get_seat_no()

    def is_available(self):
        return self.__passenger is None

    def add_food(self, food, quantity):
        for i in range(0, quantity, 1):
            new_food_instance = copy.deepcopy(food)
            self.__foods.append(new_food_instance)

    def get_passenger_name(self):
        if self.__passenger is not None:
            return self.__passenger.get_name()
        return "Unknown"

    def get_passenger_id(self):
        if self.__passenger is not None:
            return self.__passenger.get_id()
        return "Unknown"


class FlightFood:
    def __init__(self, name: str, price: float, teir_type: str):
        self.__name = name
        self.__price = price

    def get_name(self):
        return self.__name
    
    def calculate_price(self, quantity: int):
        return self.__price * quantity


# ==========================================
# Transaction models
# ==========================================

class Transaction:
    def __init__(self, name: str, payment_type: str, amount: float):
        self.__name = name
        self.__sub_trans = []
        self.__payment_type = payment_type
        self.__amount = amount

    def add_sub_transaction(self, sub_transaction):
        self.__sub_trans.append(sub_transaction)

    def get_food_transaction(self):
        msg = []
        for T in self.__sub_trans:
            if T.get_name() != "LoadLuggage":
                sub_msg = [T.get_name(), T.get_payment_type(), T.get_amount()]
                msg.append(sub_msg)
        return msg
    
    def get_amount(self):
        return self.__amount

    def get_payment_type(self):
        return self.__payment_type


class SubTransaction:
    def __init__(self, name, payment_type, amount):
        self.__name = name
        self.__payment_type = payment_type
        self.__amount = amount

    def get_name(self): return self.__name
    def get_amount(self): return self.__amount
    def get_payment_type(self): return self.__payment_type

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
        self.__passenger = []
        self.__booking = []
        self.__airplane = []
        self.__flight = []
        self.__blacklist = []

    def request_refund(self, pnr: str, passenger_id):
        print("Airline: refund requested")

        booking = self.search_booking_by_pnr(pnr)
        passenger = self.find_passenger_by_id(passenger_id)

        if not booking.check_status(BookingStatus.CONFIRMED, PaymentStatus.PAID):
            raise Exception("Status Invalid")

        if not passenger.check_refunded_total():
            raise Exception("Reach Maximum Refund or System Error")

        # # TODO: แก้ process ไม่ต้องมีหรอก validate แต่มีการคืนเงินจริงๆ แทน (สอดคล้องกับ Class Payment) #รอขุน
        # if not booking.get_payment().refund(
        #     booking.get_amount(), booking.get_payment().get_type()
        # ):
        #     raise Exception("Refund failed")

        booking.update_status(BookingStatus.CANCELLED, PaymentStatus.REFUNDED)
        passenger.add_refunded_total()

        # ต้องแก้กลับเป็นแบบเดืมมั๊ยเนี่ย ####################################################
        #booking.get_flight().updateSeat(booking.get_seat()) รอคุยกับนิวตรอนว่ายังไงตอนจองกับ ตอนที่ออกบอรดดิงพาสมันแยกกันใช่ไหม

        if passenger.get_refunded_total() == 3:
            self.__blacklist.append(passenger)

        print(f"Refund confirmed for PNR {booking.get_pnr()}")
        return f"Refund confirmed for PNR {booking.get_pnr()}"

    def buy_food(self, passenger_id: str, pnr: str, food_name: str, quantity: int, payment_type: str, pin: str):
        # [1] Identification
        passenger = self.find_passenger_by_id(passenger_id)
        booking = self.find_booking(pnr, passenger)

        # [2] Validation
        booking.check_status(BookingStatus.CHECKDIN, PaymentStatus.PAID)

        # [3] Location Retrieval
        flight_instance = booking.get_flight()
        flight_seat = self.get_flight_seat(flight_instance, passenger_id)

        # [4] Menu & Pricing
        food = self.get_food(flight_instance, food_name)
        price = food.calculate_price(quantity)

        # [5] Payment Processing
        # TODO: ตรวจสอบ/แก้ไขกระบวนการดึง Payment Object ตรงนี้
        payment = self.get_payment(passenger, payment_type) 
        payment.pay(pin, price)

        # [6] Finalizing & Records
        sub_transaction = self.create_sub_transaction(food_name, payment_type, price)
        transaction = booking.get_transaction()
        transaction.add_sub_transaction(sub_transaction)

        flight_seat.add_food(food, quantity)

        return "Order Food Success"

    def add_passenger(self, passenger: Passenger):
        self.__passenger.append(passenger)

    def search_booking_by_pnr(self, pnr: str):
        for passenger in self.__passenger:
            booking_list = passenger.get_booking()
            for booking in booking_list:
                if booking.get_pnr() == pnr:
                    return booking
        raise ValueError("unfounded")

    def find_booking(self, pnr: str, passenger: Passenger):
        return passenger.search_booking_by_pnr(pnr)

    def find_passenger_by_id(self, passenger_id: str):
        for passenger in self.__passenger:
            if passenger.get_id() == passenger_id:
                return passenger
        raise ValueError("unfounded")

    def find_flight_by_pnr(self, pnr: str):
        for passenger in self.__passenger:
            booking_list = passenger.get_booking()
            for booking in booking_list:
                if booking.get_pnr() == pnr:
                    return booking.get_flight()
        raise ValueError("unfounded")

    def get_flight_seat(self, flight: FlightInstance, passenger_id: str):
        return flight.find_flight_seat_by_passenger_id(passenger_id)

    # def get_payment (self, passenger : Passenger, payment_type : str): return passenger.find_payment_by_type(payment_type)

    def get_food(self, flight: FlightInstance, food_name: str):
        return flight.find_flight_food_by_food_name(food_name)

    def create_sub_transaction(self, name, payment_type, amount):
        return SubTransaction(name, payment_type, amount)

    def get_food_transaction(self, pnr: str):
        booking = self.search_booking_by_pnr(pnr)
        msg = booking.get_food_transaction()
        return msg

    def add_airplane(self,airplane): self.__airplane.append(airplane)
    def add_booking(self,booking): self.__booking.append(booking)
    def add_flight(self,flight): self.__flight.append(flight)
    def booking(self): pass
    def calculate_extra_weight_fee(self): pass
    def calculate_fare(self): pass
    def check_in_passenger(self): pass
    def choose_seat(self): pass
    def generate_report(self): pass
    def remove_flight(self): pass
    def search_passenger_by_id(self): pass
    def update_flight(self): pass
    def verify_weight(self): pass

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
    my_seat_type = Bussiness("12A")
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
        print(f"จำนวนครั้งที่ Refund ไปแล้ว: {passenger.get_refunded_total()} ครั้ง")
        
    except Exception as e:
        print(f"เกิดข้อผิดพลาดในการ Refund: {e}")