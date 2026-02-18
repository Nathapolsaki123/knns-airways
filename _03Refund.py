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
    def __init__(self, pnr: str, fare: float):
        self.__pnr = pnr
        self.__fare = fare #### ชื่อยังไม่ตรง
        self.__flight_no = None
        self.__seat = None
        self.__payment_status = PaymentStatus.PAID 
        self.__booking_status = BookingStatus.CONFIRMED ###ชื่อยังไม่ตรง
        self.__date_time = None
        self.__max_weight= None
        self.__payment = Payment() ## เพิ่มข่องทางการชำระเงิน

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

class Passenger:
    def __init__(self, first_name: str, last_name: str):
        self.__first_name = first_name
        self.__last_name = last_name
        self.__passport_no = None
        self.__nationality = None
        self.__phone = None
        self.__email = None
        self.__bookings = []
        self.__booking_times = 0
    
    def add_booking(self,booking: Booking): self.__bookings.append (booking)
    def get_booking(self): return self.__bookings
    def booking_request(self):pass

class Payment:
    #init

    def refund(self, amount: float, method: str) -> bool:
        print(f"Processing refund {amount} via {method}")
        return True
    
    @staticmethod
    def get_method()->str:
        return "Original Method"


class FinanceOfficer:
    #init
    def __init__(self):
        self.__staff_id = None
        self.__name = None
        self.__position = None

    def approve_refund(self, booking: Booking, amount: float) -> bool:
        print("FinanceOfficer: refund approved")
        return True

class Airline:
    def __init__(self,name : str, country : str):
        self.__name = name #str       
        self.__country = country
        self.__airplane = None #[]
        self.__is_active = None #bool
        self.__passenger = []
        self.__finance_officer = FinanceOfficer() #ควรแยกเป็น starf start ไหม

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
            booking, booking.get_amount()
        ):
            raise Exception("Refund rejected by finance")

        # 3. Process refund
        if not booking.get_payment().refund(
            booking.get_amount(), booking.get_payment().get_method()
        ):
            raise Exception("Refund failed")

        # 5. Update booking status
        booking.update_status(BookingStatus.CANCELLED,PaymentStatus.REFUNDED)

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

#airline = Airline("KNNS airways","Thailand")
# passenger = Passenger("John", "Doe")
# booking = Booking("PNR123", 5000.0)
# passenger.add_booking (booking)
# airline.add_passenger (passenger)
#airline.request_refund("PNR123")