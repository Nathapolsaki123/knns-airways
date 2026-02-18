from enum import Enum
from datetime import datetime

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
    def __init__(self, pnr: str, fare: float, seat_class :str):
        self.__pnr = pnr
        self.__fare = fare #### ชื่อยังไม่ตรง
        self.__flight_no = None
        self.__seat_class = seat_class
        self.__payment_status = PaymentStatus.PAID 
        self.__booking_status = BookingStatus.CONFIRMED ###ชื่อยังไม่ตรง
        self.__date_time = None
        self.__max_weight= None
        self.__payment = Payment() ## เพิ่มข่องทางการชำระเงิน
        self.__flight = None ##Flight

    def validate(self) -> bool:
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
    
    def add_booking(self,booking: Booking): self.__bookings.append (booking)
    def get_booking(self): return self.__bookings
    def get_refund_total(self): return self.__refund_total
    def add_refund_total (self): self.__refund_total+=1
    def booking_request(self):pass


class Payment:
    #init

    def refund(self, amount: float, method: str) -> bool:
        if self.validate ():
            print(f"Processing refund {amount} via {method}")
            return True
        return False
    
    @staticmethod
    def get_method()->str:
        return "Original Method"
    
    def validate(self)->bool:
        return True


class FinanceOfficer:
    #init
    def __init__(self):
        self.__staff_id = None
        self.__name = None
        self.__position = None
 
    def approve_refund(self,passenger:Passenger, booking: Booking, amount: float) -> bool:
        if self.validate (passenger): 
            print("FinanceOfficer: refund approved") 
            return True
        return False
    
    def validate(self,passenger) -> bool:
        return passenger.get_refund_total() <3 and passenger.get_refund_total() >= 0
    
class Flight :
    def __init__ (self,airplane : str,flight_no : str, oirgin : str, destination : str):
        self.__airplane = airplane
        self.__flight_no = flight_no
        self.__origin = oirgin
        self.__destination = destination
        self.__seat_firstclass = 25
        self.__seat_bussinessclass = 24
    
    def updateSeat(self,seatType,amount) :
        if (seatType == "Bussiness") : self.__seat_bussinessclass += amount
        elif (seatType == "First") : self.__seat_firstclass += amount


class Airline:
    def __init__(self,name : str, country : str):
        self.__name = name #str       
        self.__country = country
        self.__airplane = None #[]
        self.__is_active = None #bool
        self.__passenger = []
        self.__finance_officer = FinanceOfficer() #ควรแยกเป็น starf start ไหม
        self.__blacklist = []
        self.__flight = []

    def request_refund(self, pnr:str):
        print("Airline: refund requested")

        # 0. Find value
        booking = self.find_booking_by_pnr (pnr)
        passenger = self.find_passenger_by_pnr (pnr)

        # 1. Validate booking
        if not booking.validate():
            raise Exception("Invalid or non-refundable booking")

        # 2. Finance approval

        if not self.__finance_officer.approve_refund(
            passenger, booking, booking.get_amount()
        ):
            raise Exception("Refund rejected by finance")

        # 3. Process refund
        if not booking.get_payment().refund(
            booking.get_amount(), booking.get_payment().get_method()
        ):
            raise Exception("Refund failed")

        # 5. Update booking status
        booking.update_status(BookingStatus.CANCELLED,PaymentStatus.REFUNDED)
        passenger.add_refund_total ()
        booking.get_flight().updateSeat(booking.get_seat_type(),1)

        if passenger.get_refund_total() == 3 : self.__blacklist.append (passenger)

        print(f"Refund confirmed for PNR {booking.get_pnr()}")
    
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

airline = Airline("KNNS airways","Thailand")
passenger = Passenger("John", "Doe")
booking = Booking("PNR123", 5000.0, "Bussiness" )
flight = Flight("Boeig747","123","Bangkok","Chaingmai")
booking.add_flight (flight)
passenger.add_booking (booking)
airline.add_passenger (passenger)
airline.request_refund("PNR123")