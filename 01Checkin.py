class Passenger:
    def __init__(self, first_name: str, last_name: str, passport_no: str):
        self.__first_name = first_name
        self.__last_name = last_name
        self.__passport_no = passport_no

    def get_passport_no(self):
        return self.__passport_no


class Seat:
    def __init__(self, seat_no: str):
        self.__seat_no = seat_no
        self.__status = "Available"

    def update_status(self, status: str):
        self.__status = status

    def get_status(self):
        return self.__status


class Booking:
    def __init__(self, pnr: str, passenger: Passenger, seat: Seat):
        self.__pnr = pnr
        self.__passenger = passenger
        self.__seat = seat
        self.__status = "Booked"

    def validate_booking(self, pnr: str) -> bool:
        return self.__pnr == pnr and self.__status == "Booked"

    def update_status(self, status: str):
        self.__status = status

    def get_seat(self):
        return self.__seat


class Airline:
    def __init__(self):
        self.__bookings = []

    def add_booking(self, booking: Booking):
        self.__bookings.append(booking)

    def check_in(self, pnr: str, passenger: Passenger) -> bool:
        for booking in self.__bookings:
            if booking.validate_booking(pnr):
                booking.update_status("Checked-in")

                seat = booking.get_seat()
                seat.update_status("Occupied")

                return True
        return False


class Counter:
    def __init__(self, airline: Airline):
        self.__airline = airline

    def provide_checkin_info(self, pnr: str, passenger: Passenger):
        success = self.__airline.check_in(pnr, passenger)

        if success:
            print("Check-in confirmed")
            print("Boarding pass issued")
        else:
            print("Error: Invalid booking")


# CREATE OBJECTS
airline = Airline()
counter = Counter(airline)

passenger = Passenger("John", "Doe", "P123456")
seat = Seat("12A")
booking = Booking("PNR001", passenger, seat)

airline.add_booking(booking)

# USER CHECK-IN
counter.provide_checkin_info("PNR001", passenger)