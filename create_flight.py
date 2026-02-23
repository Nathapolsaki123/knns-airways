from fastapi import FastAPI,HTTPException
import uvicorn
from datetime import date,datetime,timedelta

app = FastAPI()

class Airline:
    def __init__(self):
        self.__flight_list:list = []
        self.__airplane_list:list = []

    def add_flight(self,flight):
        self.__flight_list.append(flight)

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
    
    def create_flight(self,flight_no,airplane_no,origin,target,depart_time,arrive_time):
        try:
            datetime.strptime(depart_time,'%d/%m/%Y %H:%M')
            datetime.strptime(arrive_time,'%d/%m/%Y %H:%M')
        except:
            raise HTTPException(status_code=404,detail="Invalid Time")
        
        flight = self.search_flight(flight_no)
        if not(flight):
            flight = Flight(flight_no)
            self.__flight_list.append(flight)

        airplane = self.search_airplane(airplane_no)
        if not(airplane):
            raise HTTPException(status_code=404,detail="Airplane Not Found")
        
        if not(airplane.get_status()):
            raise HTTPException(status_code=404,detail="Airplane Unavailable")
        
        flight.create_flight_instance(airplane,origin,target,depart_time,arrive_time)
        airplane.set_status(False)
        return "Create Flight Success"
class Airplane:
    def __init__(self,airplane_no):
        self.__airplane_no = airplane_no
        self.__status = True

    def get_airplane_no(self):
        return self.__airplane_no
    
    def get_status(self):
        return self.__status
    
    def set_status(self,status:bool):
        self.__status = status


class Flight:
    def __init__(self,flight_no:str):
        self.__flight_no = flight_no
        self.__instance_list:list = []

    def create_flight_instance(self,airplane,origin,target,depart_time,arrive_time):
        flight_instance = Flight_instance(self.__flight_no,origin,target,depart_time,arrive_time)
        flight_instance.add_airplane(airplane)
        self.__instance_list.append(flight_instance)

    def get_flight_no(self):
        return self.__flight_no
    
    def get_flight_instance_list(self):
        return self.__instance_list

class Flight_instance:
    def __init__(self,flight_no,origin,target,depart_time,arrive_time):
        self.__flight_no = flight_no
        self.__airplane = None
        self.__origin = origin
        self.__target = target
        self.__depart_time = depart_time
        self.__arrive_time = arrive_time
    
    def add_airplane(self,airplane:Airplane):
        self.__airplane = airplane
    
    def calculate_flight_time(self):
        start = datetime.strptime(self.__depart_time,'%d/%m/%Y %H:%M')
        end = datetime.strptime(self.__arrive_time,'%d/%m/%Y %H:%M')
        time_diff = end-start
        if start>end:
            raise HTTPException(status_code=404,detail="Negative Time")
        return str(time_diff)
    

    def get_flight_data(self):
        return {"Flight_no":self.__flight_no,
                "Origin":self.__origin,
                "Target":self.__target,
                "Depart_time":self.__depart_time,
                "Arrive_time":self.__arrive_time,
                "Flight_time":self.calculate_flight_time()
                }
    
    def get_depart_time(self):
        return self.__depart_time
    

airline = Airline()
airplane = Airplane("AB1234")
flight = Flight("TG911")
airline.add_flight(flight)
airline.add_airplane(airplane)

# result = airline.create_flight("TG911","AB1234","BKK","CNX","23/02/2026 12:00","23/02/2026 13:20")
# print(result)
# print(airline.search_flight_instance("TG911","23/02/2026 12:00").get_flight_data())

@app.get("/")
def home():
    return {"message":"Welcome to KNNS Airways"}

@app.post("/create_flight")
def create_flight(flight_no,airplane_no,origin,target,depart_time,arrive_time):
    result = airline.create_flight(flight_no,airplane_no,origin,target,depart_time,arrive_time)
    return {"message":result,"info":airline.search_flight_instance(flight_no,depart_time).get_flight_data()}

if __name__ == "__main__":
    uvicorn.run("create_flight:app", host = "127.0.0.1" ,port=8000, log_level="info")