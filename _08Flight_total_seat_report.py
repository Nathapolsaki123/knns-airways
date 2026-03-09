from enum import Enum
from datetime import datetime


# =========================
# ENUMS
# =========================



class FlightStatus(Enum):
    SCHEDULED = "SCHEDULED"
    CHECKINOPEN = "CHECKINOPEN"
    BOARDING = "BOARDING"
    DEPARTED = "DEPARTED"
    ARRIVED = "ARRIVED"
    CANCELLED = "CANCELLED"



# =========================
# AIRPLANE
# =========================

class Airplane:

    def __init__(self, model_number, registration_no,economy_seat_amount, business_seat_amount):

        self.__model_number = model_number
        self.__registration_no = registration_no
        self.__total_economy_seat_amount = economy_seat_amount
        self.__total_business_seat_amount = business_seat_amount
        self.__layout_seat_list = []

    @property
    def total_economy_seat_amount(self):
        return self.__total_economy_seat_amount
    
    @property
    def total_business_seat_amount(self):
        return self.__total_business_seat_amount

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
    
# =========================
# FLIGHT
# =========================

class Flight:

    def __init__(self, flight_no, origin, destination):
        self.__flight_no = flight_no
        self.__origin = origin
        self.__destination = destination
        self.__flight_instance_list = []
    
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
    def flight_instance_list(self):
        return self.__flight_instance_list


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
        self.__economy_seat_available = airplane.total_economy_seat_amount
        self.__business_seat_available = airplane.total_business_seat_amount
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
    def airplane(self):
        return self.__airplane
    
    @property
    def departure_time(self):
        return self.__departure_time
    
    @property
    def arrival_time(self):
        return self.__arrival_time
    
    @property
    def economy_seat_available(self):
        return self.__economy_seat_available
    
    @property
    def business_seat_available(self):
        return self.__business_seat_available

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

    def add_flight(self, flight):
        self.__flight_list.append(flight)

    def find_flight(self,flight_no):
        for f in self.__flight_list:
            if f.flight_no == flight_no:
                return f
        raise ValueError("Flight not found")
    
    def create_flight_seat_report(self, flight_no: str):
        string = []
        total_economy = 0
        total_business = 0
        count = 0

        f = self.find_flight(flight_no)

        header = f"Report of occupied seat in flight:{f.flight_no}(from {f.origin} to {f.destination} in percentage)"
        string.append(header)

        for ff in f.flight_instance_list:
            a = ff.airplane

            eco_percent = (a.total_economy_seat_amount - ff.economy_seat_available) / a.total_economy_seat_amount * 100
            bus_percent = (a.total_business_seat_amount - ff.business_seat_available) / a.total_business_seat_amount * 100

            content1 = f" Flight that travel from {ff.departure_time} to {ff.arrival_time} has {eco_percent:.2f}% of Economy seat that has been chosen"
            content2 = f" Flight that travel from {ff.departure_time} to {ff.arrival_time} has {bus_percent:.2f}% of Business seat that has been chosen"

            string.append(content1)
            string.append(content2)

            total_economy += eco_percent
            total_business += bus_percent
            count += 1

        total_occupied_economy = total_economy / count if count > 0 else 0
        total_occupied_business = total_business / count if count > 0 else 0

        string.append(f"Total percentage of occupied economy seat in flight: {f.flight_no} is {total_occupied_economy}%")
        string.append(f"Total percentage of occupied business seat in flight: {f.flight_no} is {total_occupied_business}%")

        return string

if __name__ == "__main__":

    airline = Airline("Tempest Airways")

    # airplane
    airplane1 = Airplane("B737", "HS-TST", 10, 4)
    airline.add_airplane(airplane1)

    # flight
    flight1 = Flight("TG100", "Bangkok", "Tokyo")
    airline.add_flight(flight1)

    # flight instances
    fi1 = FlightInstance(
        "TG100",
        "Bangkok",
        "Tokyo",
        airplane1,
        datetime(2026,3,10,8,0),
        datetime(2026,3,10,16,0),
        15000
    )

    fi2 = FlightInstance(
        "TG100",
        "Bangkok",
        "Tokyo",
        airplane1,
        datetime(2026,3,11,8,0),
        datetime(2026,3,11,16,0),
        15000
    )

    flight1.flight_instance_list.append(fi1)
    flight1.flight_instance_list.append(fi2)

    # add economy seats
    for i in range(1,11):
        fi1.add_seat(Economy(f"E{i}"))
        fi2.add_seat(Economy(f"E{i}"))

    # add business seats
    for i in range(1,5):
        fi1.add_seat(Business(f"B{i}"))
        fi2.add_seat(Business(f"B{i}"))

    # simulate booked seats
    fi1._FlightInstance__economy_seat_available -= 4
    fi1._FlightInstance__business_seat_available -= 1

    fi2._FlightInstance__economy_seat_available -= 6
    fi2._FlightInstance__business_seat_available -= 2

    # run report
    report = airline.create_flight_seat_report("TG100")

    for r in report:
        print(r)