from fastapi import FastAPI,HTTPException
import uvicorn
from datetime import date,datetime,timedelta
from abc import ABC,abstractmethod
import random

app = FastAPI()

class Seat(ABC):

    @abstractmethod
    def get_seat_type(self):
        pass

    @abstractmethod
    def get_seat_no(self):
        pass



class EconomySeat(Seat):
    def __init__(self,seat_no):
        self.__seat_no = seat_no
        self.__seat_type = "Economy"

    def get_seat_type(self):
        return self.__seat_type
    
    def get_seat_no(self):
        return self.__seat_no
    


class BusinessSeat(Seat):
    def __init__(self,seat_no):
        self.__seat_no = seat_no
        self.__seat_type = "Business"

    def get_seat_type(self):
        return self.__seat_type
    
    def get_seat_no(self):
        return self.__seat_no



class Airline:
    def __init__(self,name):
        self.__name = name
        self.__passenger_list:list = []
        self.__booking_list:list = []
        self.__airplane_list:list = []
        self.__flight_list:list = []
        self.__blacklist:list = []
        self.__flightfood_list:list = []

    def add_airplane(self,airplane):
        self.__airplane_list.append(airplane)

    def search_flight(self,flight_no) ->bool:
        for flight in self.__flight_list:
            if flight.get_flight_no() == flight_no:
                return flight
        return False
    
    def search_airplane(self,airplane_no) ->bool :
        for airplane in self.__airplane_list:
            if airplane.get_airplane_no() == airplane_no:
                return airplane
        return False
    
    def search_flight_instance(self,flight_no,depart_time):
        for flight in self.__flight_list:
            if flight.get_flight_no() == flight_no:
                for instance in flight.get_flight_instance_list():
                    if instance.get_depart_time() == depart_time:
                        return instance
                raise HTTPException(status_code=404,detail="Instance Not Found")
        raise HTTPException(status_code=404,detail="Flight Not Found")
    
    def create_flight(self,flight_no,origin,target):
        flight = Flight(flight_no ,origin,target)
        self.__flight_list.append(flight)
    
    def create_flight_instance(self,flight_no,airplane_no,depart_time,arrive_time):
        try:
            datetime.strptime(depart_time,'%d-%m-%Y %H:%M')
            datetime.strptime(arrive_time,'%d-%m-%Y %H:%M')
        except:
            raise HTTPException(status_code=404,detail="Invalid Time")
        
        flight = self.search_flight(flight_no)
        if not(flight):
            raise HTTPException(status_code=404,detail="Flight Number Not Found")
        
        airplane = self.search_airplane(airplane_no)
        if not(airplane):
            raise HTTPException(status_code=404,detail="Airplane Not Found")
        
        if not(airplane.get_status()):
            raise HTTPException(status_code=404,detail="Airplane Unavailable")
        
        flight_instance = flight.create_flight_instance(airplane,depart_time,arrive_time)
        airplane.set_status(False)

        self.add_flightfood_to_flight_instance(flight_instance)

        return "Create Flight Success"
    
    def add_flightfood_to_flight_instance(self,flight_instance):

        foodlen = len(self.__flightfood_list)
        if foodlen <1 :
            raise HTTPException(status_code=404,detail="FlightFood Not Found")
        
        while(len(flight_instance.get_food_list())<flight_instance.FOOD_IN_FLIGHT):
            index = random.randint(0,foodlen-1)
            if not (self.__flightfood_list[index] in flight_instance.get_food_list()):
                flight_instance.add_flightfood(self.__flightfood_list[index])
    
    def create_flightfood(self,name,price):
        food = FlightFood(name,price)
        self.__flightfood_list.append(food)

    def update_flight(self,flight_no,old_depart_time,depart_time,arrive_time):
        try:
            datetime.strptime(depart_time,'%d-%m-%Y %H:%M')
            datetime.strptime(arrive_time,'%d-%m-%Y %H:%M')
            datetime.strptime(old_depart_time,'%d-%m-%Y %H:%M')
        except:
            raise HTTPException(status_code=404,detail="Invalid Time")
        
        instance = self.search_flight_instance(flight_no,old_depart_time)
        instance.edit_time(depart_time,arrive_time)
        return instance
    


class Airplane:
    def __init__(self,model, airplane_no,economy_seat,business_seat):
        self.__model_number = model
        self.__registration_no = airplane_no
        self.__status = True
        self.__economy_seat_amount = economy_seat
        self.__business_seat_amount =business_seat
        self.__seat_layout:list = []
        self.add_seat_for_new_plane(economy_seat,business_seat)

    def get_airplane_no(self):
        return self.__registration_no
    
    def get_status(self):
        return self.__status
    
    def set_status(self,status:bool):
        self.__status = status

    def get_seat_layout(self):
        return self.__seat_layout

    def add_seat_for_new_plane(self,economy_seat,business_seat):
        self.__seat_layout.clear()
        for b in range(1,business_seat+1):
            if b<10:
                temp_seat = self.create_business_seat(f"B0{b}")
                self.__seat_layout.append(temp_seat)
            else:
                temp_seat = self.create_business_seat(f"B{b}")
                self.__seat_layout.append(temp_seat)

        for e in range(1,economy_seat+1):
            if e<10:
                temp_seat = self.create_economy_seat(f"E0{e}")
                self.__seat_layout.append(temp_seat)
            else:
                temp_seat = self.create_economy_seat(f"E{e}")
                self.__seat_layout.append(temp_seat)
    def create_economy_seat(self,seat_no):
        return EconomySeat(seat_no)
    
    def create_business_seat(self,seat_no):
        return BusinessSeat(seat_no)



class Flight:
    def __init__(self,flight_no:str, origin:str, target:str):
        self.__flight_no = flight_no
        self.__target = target
        self.__origin = origin
        self.__instance_list:list = []

    def create_flight_instance(self,airplane,depart_time,arrive_time):
        flight_instance = FlightInstance(self.__flight_no,depart_time,arrive_time)
        flight_instance.add_airplane(airplane)
        self.__instance_list.append(flight_instance)
        return flight_instance

    def get_flight_no(self):
        return self.__flight_no
    
    def get_flight_instance_list(self):
        return self.__instance_list
    
    def get_flight_data(self):
        return {"Flight_no":self.__flight_no
                ,"Origin":self.__origin
                ,"Target":self.__target
                }


class FlightInstance:

    FOOD_IN_FLIGHT = 3

    def __init__(self,flight_no,depart_time,arrive_time):
        self.__flight_no = flight_no
        self.__airplane = None
        self.__price = 10000
        self.__depart_time = depart_time
        self.__arrive_time = arrive_time
        self.__economy_seat_available = 0
        self.__business_seat_available = 0
        self.__remaining_seat:list = []
        self.__assigned_seat:list = []
        self.__food_list:list = []
        self.__flight_status = None
    
    def add_airplane(self,airplane:Airplane):
        self.__airplane = airplane
        self.__remaining_seat = self.__airplane.get_seat_layout()
        self.__economy_seat_available = len(self.get_remaining_seat("Economy"))
        self.__business_seat_available = len(self.get_remaining_seat("Business"))

    def add_flightfood(self,flightfood):
        self.__food_list.append(flightfood)

    def edit_time(self,depart_time,arrive_time):
        self.__depart_time = depart_time
        self.__arrive_time = arrive_time

    def reserve_seat(self,type):
        if type == "Economy":
            self.__economy_seat_available-=1
        elif type == "Business":
            self.__business_seat_available-=1

    def get_amount_seat(self,type):
        if type == "Economy":
            return self.__economy_seat_available
        elif type == "Business":
            return self.__business_seat_available
        
    def get_food_list(self):
        return self.__food_list
        
    def show_flightfood(self):
        foodlist = []
        for food in self.__food_list:
            foodlist.append(food.get_name())
        return foodlist

    def change_flight_status(self,status):
        self.__flight_status = status
    
    def calculate_flight_time(self):
        start = datetime.strptime(self.__depart_time,'%d-%m-%Y %H:%M')
        end = datetime.strptime(self.__arrive_time,'%d-%m-%Y %H:%M')
        time_diff = end-start
        if start>end:
            raise HTTPException(status_code=404,detail="Negative Time")
        return str(time_diff)
    

    def get_flight_data(self):
        return {"Flight_data":airline.search_flight(self.__flight_no).get_flight_data(),
                "Depart_time":self.__depart_time,
                "Arrive_time":self.__arrive_time,
                "Flight_time":self.calculate_flight_time()
                }
    
    def get_depart_time(self):
        return self.__depart_time
    
    def get_assigned_seat(self):
        return self.__assigned_seat
    

    def get_remaining_seat(self,seat_type=None)->list:
        seat_list = []
        if seat_type == None:
            for seat in self.__remaining_seat:
                seat_list.append(seat.get_seat_no())
            return seat_list
        if seat_type == "Economy":
            for seat in self.__remaining_seat:
                if seat.get_seat_type() == "Economy":
                    seat_list.append(seat.get_seat_no())
            return seat_list
        if seat_type == "Business":
            for seat in self.__remaining_seat:
                if seat.get_seat_type() == "Business":
                    seat_list.append(seat.get_seat_no())
            return seat_list
        raise HTTPException(status_code=404,detail="Seat Type Error")


class FlightFood:
    def __init__(self,name,price):
        self.__name = name
        self.__price = price

    def get_price(self):
        return self.__price
    
    def get_name(self):
        return self.__name
    
# --- เริ่มการจำลองข้อมูล (Mock Data) ---
airline = Airline("KNNS Airways")
# 1. สร้างเครื่องบิน (รุ่น, ทะเบียน, ที่นั่งประหยัด, ที่นั่งธุรกิจ)
airplane1 = Airplane("Airbus A320", "AB1234", 10, 5)
airplane2 = Airplane("Boeing 737", "B737-88", 20, 10)
airplane3 = Airplane("Airbus A350", "A350-99", 50, 20)

airline.add_airplane(airplane1)
airline.add_airplane(airplane2)
airline.add_airplane(airplane3)

# 2. สร้างเส้นทางบินหลัก (Flight)
airline.create_flight("TG911", "BKK", "HKT")  # กรุงเทพ - ภูเก็ต
airline.create_flight("TG912", "HKT", "BKK")  # ภูเก็ต - กรุงเทพ
airline.create_flight("KN001", "BKK", "ICN")  # กรุงเทพ - อินชอน (เกาหลี)

# 3. สร้างรายการอาหารเข้าระบบ (เพื่อสุ่มลง Flight Instance)
food_items = [
    ("Premium Wagyu Steak", 1200),
    ("Pad Thai Shrimp", 250),
    ("Salmon Salad", 450),
    ("Club Sandwich", 180),
    ("Green Curry Rice", 300),
    ("Chocolate Mousse", 150),
    ("Orange Juice", 80)
]

for name, price in food_items:
    airline.create_flightfood(name, price)

# 4. ทดลองสร้าง Flight Instance ไว้ล่วงหน้า 1 รายการ
airline.create_flight_instance("TG911", "AB1234", "15-03-2026 10:00", "15-03-2026 11:30")

# --- จบการจำลองข้อมูล ---

@app.get("/")
def home():
    return {"message":"Welcome to KNNS Airways"}

@app.post("/create_flight")
def create_flight(flight_no,airplane_no,depart_time,arrive_time):
    result = airline.create_flight_instance(flight_no,airplane_no,depart_time,arrive_time)
    flight_instance = airline.search_flight_instance(flight_no,depart_time)
    return {"Message":result
            ,"Info":flight_instance.get_flight_data()
            ,"Amount_seat":{"Economy":flight_instance.get_amount_seat("Economy"),"Business":flight_instance.get_amount_seat("Business")}
            ,"FlightFood":flight_instance.show_flightfood()
            ,"seat_layout":flight_instance.get_remaining_seat()}

@app.post("/edit_flight")
def edit_flight(flight_no,old_depart_time,depart_time,arrive_time):
    instance = airline.update_flight(flight_no,old_depart_time,depart_time,arrive_time)
    return {"Info":instance.get_flight_data()}

if __name__ == "__main__":
    uvicorn.run("create_flight:app", host = "127.0.0.1" ,port=8000, log_level="info")