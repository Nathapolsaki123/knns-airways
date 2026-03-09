from enum import Enum
from datetime import datetime


# =========================
# ENUMS
# =========================

class BookingStatus(Enum):
    PENDING = "PENDING"
    CONFIRMED = "CONFIRMED"
    CHECKEDIN = "CHECKEDIN"
    CANCELED = "CANCELED"
    NOSHOW = "NOSHOW"
    COMPLETED = "COMPLETED"


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
# SEAT
# =========================

class Seat:
    def __init__(self, seat_no):
        self.__seat_no = seat_no

    @property
    def seat_no(self):
        return self.__seat_no


class Economy(Seat):
    def __init__(self, seat_no):
        super().__init__(seat_no)
        self.__luggage_limit = 20.0
        self.__seat_price = 300.0
        self.__type_seat = "Economy"

    @property
    def type_seat(self):
        return self.__type_seat


class Business(Seat):
    def __init__(self, seat_no):
        super().__init__(seat_no)
        self.__luggage_limit = 40.0
        self.__seat_price = 500.0
        self.__type_seat = "Business"

    @property
    def type_seat(self):
        return self.__type_seat



class Passenger:

    def __init__(self, passenger_id, name, email):
        self.__passenger_id = passenger_id
        self.__name = name
        self.__email = email
        self.__card = None
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

    def add_booking(self, booking):
        self.__booking_list.append(booking)

    def booking_request(self):
        pass

    def search_booking_by_pnr(self, pnr):
        for b in self.__booking_list:
            if b.pnr == pnr:
                return b
        return None


# =========================
# MEMBERSHIP
# =========================

class Guest:
    def __init__(self):
        self.__discount = 0.0
        self.__extra_weight = 0.0
        self.__annual_fee = 0.0


class Member:
    def __init__(self, point, discount, extra_weight, annual_fee):
        self.__point = point
        self.__discount = discount
        self.__extra_weight = extra_weight
        self.__annual_fee = annual_fee


class Silver(Member):
    def __init__(self, point):
        super().__init__(point, 0.05, 5, 200)


class Gold(Member):
    def __init__(self, point):
        super().__init__(point, 0.1, 10, 300)


class Platinum(Member):
    def __init__(self, point):
        super().__init__(point, 0.15, 20, 500)


# =========================
# FLIGHT
# =========================

class Flight:

    def __init__(self, flight_no, origin, destination):
        self.__flight_no = flight_no
        self.__origin = origin
        self.__destination = destination
        self.__flight_instance_list = []


class FlightSeat:

    def __init__(self, passenger, seat):
        self.__passenger = passenger
        self.__seat = seat
        self.__food_list = []
        self.__extra_weight = 0


class FlightInstance:

    def __init__(self, flight_no, origin, destination,airplane, departure_time, arrival_time, price):
        self.__flight_no = flight_no
        self.__origin = origin
        self.__destination = destination
        self.__airplane = airplane
        self.__departure_time = departure_time
        self.__arrival_time = arrival_time
        self.__remaining_seat_list = []
        self.__assigned_seat_list = []
        self.__food_list = []
        self.__total_income = 0
        self.__price = price
        self.__status = FlightStatus.SCHEDULED

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
    def departure_time(self):
        return self.__departure_time

    @property
    def remaining_seat_list(self):
        return self.__remaining_seat_list
    
    @property
    def assigned_seat_list(self):
        return self.__assigned_seat_list
    
    @property
    def status(self):
        return self.__status

    def add_seat(self, seat):
        self.__remaining_seat_list.append(seat)

    def add_assigned_seat(self, flight_seat):
        self.__assigned_seat_list.append(flight_seat)

    def check_availability(self):
        return len(self.__remaining_seat_list) > 0

    def openCheckIn(self):
        self.__status = FlightStatus.CHECKINOPEN

    def closeCheckIn(self):
        self.__status = FlightStatus.BOARDING

    def cancelFlight(self):
        self.__status = FlightStatus.CANCELLED

    def get_available_seat(self, seat_class):
        result = []
        for seat in self.__remaining_seat_list:
            if seat.type_seat == seat_class:
                result.append(seat)
        return result
    
    def update_status(self, status):
        self.__status = status


# =========================
# TICKET
# =========================

class Ticket:

    def __init__(self, passenger, flight, seat):
        self.__passenger = passenger
        self.__flight_no = flight.flight_no
        self.__origin = flight.origin
        self.__destination = flight.destination
        self.__departure_time = flight.departure_time
        self.__seat = seat

    def __str__(self):
        return (
            f"\n------ TICKET ------\n"
            f"Flight No : {self.__flight_no}\n"
            f"Passenger : {self.__passenger.passenger_id}\n"
            f"Route     : {self.__origin} -> {self.__destination}\n"
            f"Departure : {self.__departure_time}\n"
            f"Seat      : {self.__seat.seat_no}\n"
            f"--------------------"
        )

# =========================
# BOOKING
# =========================

class Booking:

    def __init__(self, pnr, passenger, flight,seat_type, seat_amount):
        self.__pnr = pnr
        self.__passenger = passenger
        self.__flight_instance = flight
        self.__seat_class = seat_type
        self.__seat_amount = seat_amount
        self.__booking_status = BookingStatus.PENDING
        self.__payment_status = PaymentStatus.UNPAID
        self.__booking_date = datetime.now()
        self.__ticket_list = []
        self.__transaction_list = []

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
    def seat_class(self):
        return self.__seat_class
    
    @property
    def seat_amount(self):
        return self.__seat_amount
    
    @property
    def booking_status(self):
        return self.__booking_status
    
    @property
    def payment_status(self):
        return self.__payment_status
    
    def add_ticket(self,ticket):
        self.__ticket_list.append(ticket)

    def confirmBooking(self):
        self.__booking_status = BookingStatus.CONFIRMED

    def cancelBooking(self):
        self.__booking_status = BookingStatus.CANCELED

    def update_booking_status(self,status):
        self.__booking_status = status

    def update_payment_status(self,status):
        self.__payment_status = status


# =========================
# AIRLINE
# =========================

class Airline:

    def __init__(self, airline_name):
        self.__airline_name = airline_name
        self.__passenger_list = []
        self.__booking_list = []
        self.__airplane_list = []
        self.__flight_list = []
        self.__blacklist_list = []

    def add_airplane(self, airplane):
        self.__airplane_list.append(airplane)

    def add_booking(self, booking):
        self.__booking_list.append(booking)

    def add_flight(self, flight):
        self.__flight_list.append(flight)

    def add_passenger(self, passenger):
        self.__passenger_list.append(passenger)

    def check_in_passenger(self,passenger_id,pnr):
        current_passenger = self.search_passenger_by_id(passenger_id)
        if current_passenger == None:
            raise Exception("Invalid Passenger ID.")
        
        current_booking = current_passenger.search_booking_by_pnr(pnr)
        if current_booking == None:
            raise Exception("Invalid Booking PNR.")
        
        if current_booking.booking_status == BookingStatus.CHECKEDIN:
            raise Exception("You have already checked in.")
        elif current_booking.booking_status == BookingStatus.PENDING:
            raise Exception("Your booking has not been paid yet.")
        elif current_booking.booking_status == BookingStatus.CANCELED or current_booking.booking_status == BookingStatus.NOSHOW:
            raise Exception("This booking cannot check in.")
        elif current_booking.booking_status == BookingStatus.CONFIRMED:
            current_flight = current_booking.flight_instance
            if current_flight == None:
                raise Exception("Invalid Booking (Booking doesn't had flight)")
            if current_flight.status != FlightStatus.CHECKINOPEN:
                raise Exception("Check-in is not open yet.")
            current_booking.update_booking_status(BookingStatus.CHECKEDIN)
        else:
            raise Exception("Invalid Booking Status")

        
        available_seat_list = current_flight.get_available_seat(current_booking.seat_class)
        if not available_seat_list:
            raise Exception("Error not founded any available seat. Please contact customer service.")
        else:
            print(f"available seat: {[ s.seat_no for s in available_seat_list]}")
            return True
            
    def search_passenger_by_id(self, passenger_id):
        for p in self.__passenger_list:
            if p.passenger_id == passenger_id:
                return p
        return None

    def choose_seat(self,passenger_id,pnr,chosen_seat:str):
        
        current_passenger = self.search_passenger_by_id(passenger_id)
        if current_passenger == None:
            raise Exception("Invalid Passenger ID.")
        
        current_booking = current_passenger.search_booking_by_pnr(pnr)
        if current_booking == None:
            raise Exception("Invalid Booking PNR.")
        
        if current_booking.booking_status == BookingStatus.CONFIRMED:
            raise Exception("Please check-in first.")
        elif current_booking.booking_status == BookingStatus.COMPLETED:
            raise Exception("You have already chosen seats.")
        elif current_booking.booking_status == BookingStatus.PENDING:
            raise Exception("Your booking has not been paid yet.")
        elif current_booking.booking_status == BookingStatus.CANCELED or current_booking.booking_status == BookingStatus.NOSHOW:
            raise Exception("This booking cannot check in.")
        elif current_booking.booking_status == BookingStatus.CHECKEDIN:
            current_flight = current_booking.flight_instance
            if current_flight == None:
                raise Exception("Invalid Booking (Booking doesn't had flight)")
            
            valid, invalid, duplicates, chosen_seat_obj = self.parse_seats(chosen_seat,current_flight.get_available_seat(current_booking.seat_class))
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
                ticket = Ticket(current_passenger,current_flight,seat)
                current_booking.add_ticket(ticket)
                created_tickets.append(ticket)
            current_booking.update_booking_status(BookingStatus.COMPLETED)
            return created_tickets
        else:
            raise Exception("Invalid Booking Status")

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
    






# ==========================================
# Main Execution (Test Cases)
# ==========================================
if __name__ == "__main__":

    print("========== AIRLINE SYSTEM TEST ==========")

    # Create airline
    airline = Airline("Tempest Airways")

    # Passenger
    p1 = Passenger("P001","John Smith","john@email.com")
    p2 = Passenger("P002","Alice","alice@email.com")

    airline.add_passenger(p1)
    airline.add_passenger(p2)

    # Flight
    flight = FlightInstance(
        "TG101",
        "BKK",
        "NRT",
        "Boeing777",
        datetime(2026,3,10,10,30),
        datetime(2026,3,10,18,30),
        15000
    )

    airline.add_flight(flight)

    # Add seats
    for i in range(1,6):
        flight.add_seat(Economy(f"A{i:02d}"))

    flight.add_seat(Business("B01"))
    flight.add_seat(Business("B02"))

    print("\nSeats created")

    # Booking
    booking = Booking("PNR001",p1,flight,"Economy",2)
    p1.add_booking(booking)
    airline.add_booking(booking)

    booking.confirmBooking()

    print("\nBooking confirmed")

    # ==========================================
    # TEST 1 : Check-in before open
    # ==========================================

    print("\nTEST1 : Check-in before open")

    try:
        airline.check_in_passenger("P001","PNR001")
    except Exception as e:
        print("Expected Error:",e)

    # ==========================================
    # Open Check-in
    # ==========================================

    flight.openCheckIn()
    print("\nCheck-in opened")

    # ==========================================
    # TEST 2 : Wrong Passenger ID
    # ==========================================

    print("\nTEST2 : Invalid passenger")

    try:
        airline.check_in_passenger("P999","PNR001")
    except Exception as e:
        print("Expected Error:",e)

    # ==========================================
    # TEST 3 : Wrong PNR
    # ==========================================

    print("\nTEST3 : Invalid PNR")

    try:
        airline.check_in_passenger("P001","PNR999")
    except Exception as e:
        print("Expected Error:",e)

    # ==========================================
    # TEST 4 : Correct Check-in
    # ==========================================

    print("\nTEST4 : Correct Check-in")

    airline.check_in_passenger("P001","PNR001")

    # ==========================================
    # TEST 5 : Check-in twice
    # ==========================================

    print("\nTEST5 : Check-in again")

    try:
        airline.check_in_passenger("P001","PNR001")
    except Exception as e:
        print("Expected Error:",e)

    # ==========================================
    # TEST 6 : Seat amount mismatch
    # ==========================================

    print("\nTEST6 : Seat amount mismatch")

    try:
        airline.choose_seat("P001","PNR001","A01")
    except Exception as e:
        print("Expected Error:",e)

    # ==========================================
    # TEST 7 : Invalid seat
    # ==========================================

    print("\nTEST7 : Invalid seat")

    try:
        airline.choose_seat("P001","PNR001","A01,A99")
    except Exception as e:
        print("Expected Error:",e)

    # ==========================================
    # TEST 8 : Seat wrong class
    # ==========================================

    print("\nTEST8 : Seat wrong class")

    try:
        airline.choose_seat("P001","PNR001","B01,B02")
    except Exception as e:
        print("Expected Error:",e)

    # ==========================================
    # TEST 9 : Seat duplicate
    # ==========================================

    print("\nTEST9 : Seat duplicate")

    try:
        airline.choose_seat("P001","PNR001","A01,A01")
    except Exception as e:
        print("Expected Error:",e)

    # ==========================================
    # TEST 10 : Correct seat selection
    # ==========================================

    print("\nTEST10 : Correct seat selection")

    tickets = airline.choose_seat("P001","PNR001","A01,A02")

    for t in tickets:
        print(t)

    # ==========================================
    # TEST 11 : Choose seat again after completed
    # ==========================================

    print("\nTEST11 : Choose seat again after completed")

    try:
        airline.choose_seat("P001","PNR001","A03,A04")
    except Exception as e:
        print("Expected Error:",e)

    # ==========================================
    # TEST 12 : Seat already taken
    # ==========================================

    print("\nTEST12 : Seat already taken")

    booking2 = Booking("PNR002",p2,flight,"Economy",1)
    p2.add_booking(booking2)
    airline.add_booking(booking2)

    booking2.confirmBooking()

    airline.check_in_passenger("P002","PNR002")

    try:
        airline.choose_seat("P002","PNR002","A01")
    except Exception as e:
        print("Expected Error:",e)

    # ==========================================
    # TEST 13 : Valid seat for second passenger
    # ==========================================

    print("\nTEST13 : Valid seat for passenger2")

    tickets = airline.choose_seat("P002","PNR002","A03")

    for t in tickets:
        print(t)

    print("\n========== TEST COMPLETE ==========")