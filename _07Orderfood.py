from enum import Enum
from datetime import datetime
from abc import ABC, abstractmethod
import copy

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

class Booking:
    def __init__(self,passenger_name:str, pnr: str, fare: float, seat_class :str ,flight):
        self.__passenger = passenger_name
        self.__pnr = pnr        
        self.__fare = fare #### ชื่อยังไม่ตรง
        self.__flight_no = None
        self.__seat_class = seat_class
        self.__payment_status = PaymentStatus.PAID 
        self.__booking_status = BookingStatus.CHECKDIN ###ชื่อยังไม่ตรง
        self.__date_time = None
        self.__max_weight= None
        self.__payment = Payment() ## เพิ่มข่องทางการชำระเงิน
        self.__flight = flight ##FlightInstance
        self.__transaction = Transaction()


    def check_status(self) -> bool:
        return self.__booking_status == BookingStatus.CONFIRMED and self.__payment_status == PaymentStatus.PAID

    def update_status(self, booking_status: BookingStatus, payment_status : PaymentStatus):
        self.__booking_status = booking_status
        self.__payment_status = payment_status
        print(f"Booking status updated to {booking_status.value}", end = ", ")
        print(f"Payment status updated to {payment_status.value}") 

    def get_amount(self) -> float: return self.__fare
    def get_pnr(self) -> str: return self.__pnr
    def get_payment(self) : return self.__payment #Payment
    def get_status(self): return "Booking: " + self.__booking_status.value + ", Payment: " + self.__payment_status.value
    def get_seat_type (self): return self.__seat_class
    def add_flight (self,flight): self.__flight = flight
    def get_flight (self): return self.__flight
    def check_checked_in (self): return self.__booking_status == BookingStatus.CHECKDIN and self.__payment_status == PaymentStatus.PAID
    def get_transaction (self) : return self.__transaction
    def get_food_transaction(self) : 
        return self.__transaction.get_food_transaction() 

class Passenger:
    def __init__(self, first_name: str, last_name: str):
        self.__first_name = first_name
        self.__last_name = last_name
        self.__passport_no = None
        self.__nationality = None
        self.__phone = None
        self.__email = None
        self.__refund_total = 0
        self.__bookings = []
        self.__booking_times = 0
        self.__payment = []
    
    def add_booking(self,booking: Booking): self.__bookings.append (booking)
    def get_booking(self): return self.__bookings
    def get_refund_total(self): return self.__refund_total
    def add_refund_total (self): self.__refund_total+=1
    def booking_request(self):pass
    def check_refund_total(self): return 0 <= self.__refund_total < 3
    def add_payment (self,payment): self.__payment.append (payment)
    def get_name (self): return f"{self.__first_name} {self.__last_name}"

    def find_payment_by_type (self,payment_type):
        for payment in self.__payment :
            type = payment.get_type ()
            if type == payment_type :
                return payment
        raise ValueError ("unfound")

class Payment:
    #init

    def refund(self, amount: float, method: str) -> bool:
        if self.validate ():
            print(f"Processing refund {amount} via {method}")
            return True
        return False


    @staticmethod
    @abstractmethod
    def get_type()->str:
        return "Original Method"
    
    def validate(self,password)->bool:
        return True

class CardPayment (Payment):
    def __init__ (self, balance:float,pin) :
        self.__balance = balance
        self.__pin = pin
    
    @staticmethod
    def get_type() :
        return "Card"
    
    def pay (self,pin,price : float):
        self.validate_pin(pin)
        if 0 <= self.__balance >= price : self.decrease_money (price)
        else : raise ValueError("PaymentFailed")
    
    def validate_pin (self,pin): return self.__pin == pin
    def decrease_money (self,price):self.__balance -= price

class PointPayment (Payment):
    def __init__ (self, point):
        self.__point = point
 
    @staticmethod
    def get_type():
        return "Point"

    def pay(self,pin,price):
        self.validate_pin()
        if 0 <= self.__point >= price : self.decrease_money (price)
        else : raise ValueError("PaymentFailed")

    def validate_pin (self,pin=None): return True
    def decrease_money (self,price):self.__point -= price
        

class Airplane : 
    pass
    
class Flight :
    def __init__ (self,airplane : str,flight_no : str, origin : str, destination : str):
        self.__airplane = airplane
        self.__flight_no = flight_no
        self.__origin = origin
        self.__destination = destination
        self.__seat_economyclass = 25
        self.__seat_bussinessclass = 25
        self.__flight_instance = []
        self.__seat = []
        self.__food = []

        self.__departure_time = None
        self.__arrival_time = None
        self.__flight_status = None

    def updateSeat(self,seatType,amount) :
        if (seatType == "Bussiness") : self.__seat_bussinessclass += amount
        elif (seatType == "Economy") : self.__seat_economyclass += amount

    def add_flight_instance (self,flight_instance): self.__flight_instance.append (flight_instance)
    def add_flight_seat (self,flight_seat): self.__seat.append (flight_seat)
    def add_flight_food (self,flight_food): self.__food.append (flight_food)
    def open_checkin (self):pass
    def close_checkin (self):pass
    def cancel_flight (self):pass
    def get_available_seat(self):pass
    def check_availabillity (self): pass
    def crete_flight_instance (self):pass #note อาจจะต้องมี และตอนนี้สับสน


class FlightInstance(Flight) :
    def __init__ (self,airplane : str ,flight_no : str, origin : str, destination : str):
        super().__init__(airplane ,flight_no , origin , destination)
        self.__seat_economyclass = 25
        self.__seat_bussinessclass = 25
        self.__seat = []
        self.__food = []
    
    def find_flight_seat_by_passenger_name (self,passenger_name:str):
        for seat in self.__seat :
            name = seat.get_passenger_name ()
            if name == passenger_name :
                return seat
        raise ValueError ("unfound")
    
    def find_flight_food_by_food_name(self,food_name:str):
        for food in self.__food :
            name = food.get_name()
            if food_name == name :
                return food
        raise ValueError ("unfound")

    def add_flight_seat(self,flight_seat):self.__seat.append (flight_seat)
    def add_flight_food(self,food_menu):self.__food.append (food_menu)


class Seat(ABC) :
    def __init__(self,seat_no):
        self.__seat_no = seat_no

    @abstractmethod
    def get_type (self): pass

    def get_seat_no (self): return self.__seat_no

class Economy(Seat) :
    def __init__(self,seat_no):
        super().__init__ (seat_no)
        self.__luggage_limit = 20
        self.__price_multiplier = 1.0

    def get_type (self): return "Economy"

class Bussiness(Seat):
    def __init__(self,seat_no):
        super().__init__ (seat_no)
        self.__luggage_limit = 40
        self.__price_multiplier = 2.5

    def get_type (self): return "Bussiness" 

class FlightSeat :
    def __init__(self,seat_no):
        self.__passenger_name = None
        self.__seat_no = seat_no
        self.__food = []
    
    def assigh_passenger(self,passenger_name): self.__passenger_name = passenger_name
    def assigh_seat_no(self,seat :Seat): self.__seat_no = seat #จริงอาจจะไม่ต้องมี
    def get_seat_no (self) : return self.__seat_no.get_seat_no()
    def is_available(): return self.__passenger_name == None
    def add_food(self,food,quantity): 
        for i in range(0,quantity,1): 
            new_food_instance = copy.deepcopy(food) 
            self.__food.append(new_food_instance)

    def get_passenger_name (self): return self.__passenger_name

class FlightFood :
    def __init__(self,name:str,price:float,teir_type:str):
        self.__name = name
        self.__price = price
        self.__teir_type = teir_type
    
    def get_name (self): return self.__name
    def get_type (self): return self.__name
    def calculate_price (self, quantity : int): return self.__price * quantity

class Transaction :
    def __init__(self):
        self.__food_transaction = []
        self.__loadluggage_transaction = []
    
    def add_sub_transaction_food (self,sub_transaction) : self.__food_transaction.append(sub_transaction)
    def get_food_transaction(self): 
        msg = []
        for T in self.__food_transaction:
            sub_msg = [T.get_flight_seat().get_seat_no(),T.get_passenger().get_name(),T.get_type().get_type(),str(T.get_quantity()),T.get_payment_type()]
            msg.append (sub_msg)
        return msg

class SubTransaction : 
    def __init__(self,flight_seat,passenger,type,quantity,payment_type):
        self.__flight_seat = flight_seat
        self.__passenger = passenger
        self.__type = type
        self.__quantity = quantity
        self.__payment_type = payment_type
    
    def get_flight_seat (self):return self.__flight_seat
    def get_passenger (self):return self.__passenger
    def get_type (self):return self.__type
    def get_quantity (self):return self.__quantity
    def get_payment_type (self):return self.__payment_type

class Airline:
    def __init__(self,name : str, country : str):
        self.__name = name #str       
        self.__country = country
        self.__airplane = None #[]
        self.__is_active = None #bool
        self.__passenger = []
        self.__blacklist = []
        self.__flight = []

    def request_refund(self, pnr:str):
        print("Airline: refund requested")

        # 0. Find value
        booking = self.find_booking_by_pnr (pnr)
        passenger = self.find_passenger_by_pnr (pnr)

        # 1. Validate booking
        if not booking.check_status():
            raise Exception("Status Invalid")

        # 2. Validate passenger
        if not passenger.check_refund_total():
            raise Exception("Reach Maximum Refund or System Error")

        # 3. Process refund
        if not booking.get_payment().refund(
            booking.get_amount(), booking.get_payment().get_type()
        ):
            raise Exception("Refund failed")

        # 5. Update booking status
        booking.update_status(BookingStatus.CANCELLED,PaymentStatus.REFUNDED)
        passenger.add_refund_total ()
        booking.get_flight().updateSeat(booking.get_seat_type(),1)

        if passenger.get_refund_total() == 3 : self.__blacklist.append (passenger)

        print(f"Refund confirmed for PNR {booking.get_pnr()}")
        return (f"Refund confirmed for PNR {booking.get_pnr()}")
    def buy_food (self,passenger_name:str,pnr:str,food_name:str,quantity:int,payment_type:str,pin:str) :
        booking = self.find_booking_by_pnr (pnr)
        booking.check_checked_in ()
        passenger = self.find_passenger_by_pnr (pnr)
        flight_instance = self.find_flight_by_pnr (pnr)
        flight_seat = self.get_flight_seat (flight_instance,passenger_name)
        payment = self.get_payment (passenger,payment_type)
        food = self.get_food (flight_instance,food_name)
        price = food.calculate_price (quantity)
        payment.pay (pin,price)
        sub_transaction = self.create_sub_transection (flight_seat,passenger,food,quantity,payment_type)
        transaction = booking.get_transaction()
        transaction.add_sub_transaction_food (sub_transaction)
        flight_seat.add_food (food,quantity)
        return "Order Food Success"

    def add_passenger (self, passenger:Passenger): self.__passenger.append (passenger)

    def find_booking_by_pnr (self, pnr :str): 
        for passenger in self.__passenger :
            booking_list = passenger.get_booking()
            for booking in booking_list :
                if booking.get_pnr() == pnr :
                    return booking
        raise ValueError ("unfounded")

    def find_passenger_by_pnr (self, pnr :str):
        for passenger in self.__passenger :
            booking_list = passenger.get_booking()
            for booking in booking_list :
                if booking.get_pnr() == pnr :
                    return passenger
        raise ValueError ("unfounded")
    
    def find_flight_by_pnr (self, pnr :str):
        for passenger in self.__passenger :
            booking_list = passenger.get_booking()
            for booking in booking_list :
                if booking.get_pnr() == pnr :
                    return booking.get_flight()
        raise ValueError ("unfounded")

    def get_flight_seat (self, flight :FlightInstance ,passenger_name : str ): return flight.find_flight_seat_by_passenger_name (passenger_name)
    def get_payment (self, passenger : Passenger, payment_type : str): return passenger.find_payment_by_type(payment_type)
    def get_food (self,flight : FlightInstance, food_name:str): return flight.find_flight_food_by_food_name(food_name)
    def create_sub_transection (self, flight_seat, passenger, type, quantity, payment_type): return SubTransaction (flight_seat, passenger, type, quantity, payment_type)
    def get_food_transaction (self,pnr:str):
        booking = self.find_booking_by_pnr (pnr)
        msg = booking.get_food_transaction()
        return msg


if __name__ == "__main__":
    print("--- 1. Setting up Environment ---")
    airline = Airline("Thai Airways", "Thailand")
    food_menu = FlightFood("Pad Thai", 150.0, "Economy")
    flight_seat = FlightSeat("12A")
    flight_seat.assigh_passenger("John Doe")  # ชื่อต้องตรงกับ passenger ด้านล่าง
    
    # บัตรเครดิตมีเงิน 1000 บาท รหัส "1234"
    payment = CardPayment(1000.0, "1234") 

    flight = FlightInstance("Boeing 777", "TG123", "BKK", "CNX")
    flight.add_flight_food(food_menu)
    flight.add_flight_seat(flight_seat)

    print("--- 2. Setting up Passenger & Booking ---")
    booking = Booking("John Doe","PNR12345", 2500.0, "Economy", flight)  
    
    # อัปเดตสถานะเป็น CHECKDIN และ PAID เพื่อให้สั่งอาหารได้
    booking.update_status(BookingStatus.CHECKDIN, PaymentStatus.PAID)

    passenger = Passenger("John", "Doe")
    passenger.add_booking(booking)
    passenger.add_payment(payment)
    
    airline.add_passenger(passenger)

    print("\n--- 3. Testing buy_food Method ---")
    try:
        # ทดสอบซื้อผัดไทย 2 กล่อง จ่ายด้วยบัตรเครดิต
        airline.buy_food(
            passenger_name="John Doe",
            pnr="PNR12345", 
            food_name="Pad Thai", 
            quantity=2, 
            payment_type="Card", 
            pin="1234"
        )
        print ("success ")
    except Exception as e:
        print(f"FAILED: {str(e)}")