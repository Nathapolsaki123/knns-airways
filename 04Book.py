from datetime import datetime
import uuid


class Passenger:
    def __init__(self, passenger_id: str, first_name: str, last_name: str):
        self.__passenger_id = passenger_id
        self.__first_name = first_name
        self.__last_name = last_name
        self.__transactions = []

    def get_passenger_id(self):
        return self.__passenger_id

    def add_transaction(self, transaction):
        self.__transactions.append(transaction)


class Seat:
    def __init__(self, seat_no: str):
        self.__seat_no = seat_no
        self.__status = "Available"

    def get_seat_no(self):
        return self.__seat_no

    def is_available(self):
        return self.__status == "Available"

    def reserve(self):
        if self.__status != "Available":
            raise Exception("Seat not available")
        self.__status = "Reserved"

    def release(self):
        self.__status = "Available"


class Flight:
    def __init__(self, flight_no: str, origin: str, destination: str):
        self.__flight_no = flight_no
        self.__origin = origin
        self.__destination = destination
        self.__seats = []

    def add_seat(self, seat: Seat):
        self.__seats.append(seat)

    def check_availability(self):
        return any(seat.is_available() for seat in self.__seats)

    def get_available_seat(self) :  ##-> Seat
        for seat in self.__seats:
            if seat.is_available():
                return seat
        raise Exception("No seats available")


class Payment:
    def __init__(self, amount: float):
        self.__amount = amount
        self.__status = "Pending"

    def pay(self) -> bool:
        self.__status = "Success"
        return True

    def refund(self):
        self.__status = "Refunded"


class Transaction:
    def __init__(self, amount: float, method: str):
        self.__transaction_id = str(uuid.uuid4())
        self.__amount = amount
        self.__method = method
        self.__created_at = datetime.now()


class Booking:
    def __init__(self, passenger: Passenger, flight: Flight, seat: Seat):
        self.__pnr = str(uuid.uuid4())[:8]
        self.__passenger = passenger
        self.__flight = flight
        self.__seat = seat
        self.__status = "Pending"
        self.__booking_date = datetime.now()

    def get_pnr(self):
        return self.__pnr

    def confirm(self):
        self.__status = "Confirmed"

    def cancel(self):
        self.__status = "Cancelled"
        self.__seat.release()


class Airline:
    def __init__(self, name: str):
        self.__name = name
        self.__current_passenger = None
        self.__passengers = []

    def add_passenger(self, passenger: Passenger):
        self.__passengers.append(passenger)

    # ===== LOGIN =====
    def login(self, passenger_id: str) -> bool:
        for p in self.__passengers:
            if p.get_passenger_id() == passenger_id:
                self.__current_passenger = p
                return True
        return False

    # ===== BOOKING FLOW =====
    def book_ticket(self, flight: Flight, payment_method: str) -> Booking:
        if not self.__current_passenger:
            raise Exception("User not logged in")

        if not flight.check_availability():
            raise Exception("Flight full")

        seat = flight.get_available_seat()
        seat.reserve()

        fare = self.calculate_fare()

        payment = Payment(fare)
        if not payment.pay():
            seat.release()
            raise Exception("Payment failed")

        transaction = Transaction(fare, payment_method)
        self.__current_passenger.add_transaction(transaction)

        booking = Booking(self.__current_passenger, flight, seat)
        booking.confirm()

        return booking

    def calculate_fare(self) -> float:
        return 100.0



if __name__ == "__main__":
    airline = Airline("Demo Airline")

    passenger = Passenger("P001", "John", "Doe")
    airline.add_passenger(passenger)

    flight = Flight("TG101", "BKK", "CNX")
    flight.add_seat(Seat("1A"))
    flight.add_seat(Seat("1B"))

    if airline.login("P001"):
        booking = airline.book_ticket(flight, "Credit Card")
        print("✅ Booking Confirmed")
        print("PNR:", booking.get_pnr())