from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn

app = FastAPI()

class Payment(BaseModel):
    def __init__(self):
        self.__status = "PENDING"

    def process_payment(self, amount: float) -> bool:
        # mock payment logic
        if amount <= 0:
            self.__status = "FAILED"
            return False

        self.__status = "SUCCESS"
        return True

    def get_status(self):
        return self.__status


class Passenger(BaseModel):
    def __init__(self, first_name: str, luggage_weight: int):
        self.__first_name = first_name
        self.__luggage_weight = luggage_weight

    def get_weight(self) -> int:
        return self.__luggage_weight
    def set_weight(self,weight):
        self.__luggage_weight = weight
    def get_name(self):
        return self.__first_name


class Booking(BaseModel):
    def __init__(self, pnr: str, luggage_limit: int, is_valid: bool=True):
        self.__pnr = pnr
        self.__is_valid = is_valid
        self.__luggage_limit = luggage_limit

    def validate_booking(self, pnr: str) -> bool:
        return self.__pnr == pnr and self.__is_valid
    
    def get_luggage_limit(self):
        return self.__luggage_limit


class Airline:
    def __init__(self):
        self.__extra_fee_per_kg = 500  # บาท / กิโล

    def verify_weight(self,booking:Booking,passenger:Passenger):
        if(passenger.get_weight()<=booking.get_luggage_limit()):
            return True
        return False

    def load_luggage(self, pnr: str,
                     booking: Booking,
                     passenger: Passenger,
                     payment: Payment):
        # 1. validate booking
        if not booking.validate_booking(pnr):
            return "Error: Invalid booking"

        # 2. verify luggage weight
        if self.verify_weight(booking,passenger):
            return {"name":passenger.get_name(),
           "luggage_weight":passenger.get_weight(),
           "limitweight":booking.get_luggage_limit(),
        "message":f"Luggage loaded (WithinLimit)"
        }

        # 3. calculate extra fee
        extra_weight = passenger.get_weight() -booking.get_luggage_limit()
        extra_fee = self.__calculate_extra_weight_fee(extra_weight)

        # 4. payment
        payment_result = payment.process_payment(extra_fee)
        if not payment_result:
            return "Error: Extra baggage payment failed"
        
        return {"name":passenger.get_name(),
           "luggage_weight":passenger.get_weight(),
           "limitweight":booking.get_luggage_limit(),
        "message":f"Luggage loaded (Extra Fee :{extra_weight} X {self.__extra_fee_per_kg} = {extra_fee})"
        }
    
    def __calculate_extra_weight_fee(self, extra_weight: int) -> float:
        return extra_weight * self.__extra_fee_per_kg


airline = Airline()
booking = Booking(pnr="ABC123",luggage_limit=50, is_valid=True)
passenger = Passenger(first_name="John", luggage_weight=90)
payment = Payment()

@app.get("/")
def home():
    return {"message":"Welcome to KNNS Airways"}

@app.post("/loadluggage")
def Loadluggage(pnr:str,booking:Booking,passenger:Passenger,payment:Payment):
    message = airline.load_luggage(pnr=pnr,
    booking=booking,
    passenger=passenger,
    payment=payment
    )
    return message

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="info")