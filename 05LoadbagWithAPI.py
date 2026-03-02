from fastapi import FastAPI,HTTPException
import uvicorn
from abc import ABC,abstractmethod

app = FastAPI()

class Payment(ABC):

    @abstractmethod
    def pay(self):
        pass

class Booking:
    def __init__(self, pnr: str, seat_class :str):
        self.__pnr = pnr
        self.__seat_class = seat_class
        self.__transaction = None
    
    def get_seat_class(self):
        return self.__seat_class
    
    def get_pnr(self):
        return self.__pnr
    
    def get_transaction(self):
        return self.__transaction
    
    def add_transaction(self,transaction):
        self.__transaction = transaction

class Transaction:
    def __init__(self,name,amount):
        self.__name = name
        self.__amount = amount
        self.__subtransaction_list:list = []

    def add_subtransaction(self,subtransaction):
        self.__subtransaction_list.append(subtransaction)

    def get_all_subtransaction(self):
        sub_list = [{self.__name:self.__amount}]
        for sub in self.__subtransaction_list:
            sub_list.append(sub.get_data())
        return sub_list


class Subtransaction:
    def __init__(self,name,amount):
        self.__name = name
        self.__amount = amount

    def get_data(self):
        return {self.__name:self.__amount}

class Card(Payment):
    def __init__(self,card_no:str,amount:float):
        self.__card_no = card_no
        self.__amount = amount

    def get_card_no(self):
        return self.__card_no
    
    def pay(self,fee):
        if fee <0:
            raise HTTPException(status_code=404,detail="Fee must be more than 0")
        if fee > self.__amount:
            raise HTTPException(status_code=404,detail="Not enought money")
        self.__amount-=fee

class Passenger:
    def __init__(self, first_name: str,luggage_weight: int):
        self.__first_name = first_name
        self.__booking_list:list = []
        self.__tier = "Gold"
        if(luggage_weight<0):
            raise HTTPException(status_code=404,detail="Luggage weight must be more than 0")
        self.__luggage_weight = luggage_weight
        self.__card = None

    def get_weight(self) -> int:
        return self.__luggage_weight
    def set_weight(self,weight):
        if(weight<0):
            raise HTTPException(status_code=404,detail="Luggage weight must be more than 0")
        self.__luggage_weight = weight
    
    def get_name(self):
        return self.__first_name
    
    def get_tier(self):
        return self.__tier
    
    def get_booking_list(self):
        return self.__booking_list
    
    def get_card(self):
        return self.__card
    
    def add_booking(self,booking:Booking):
        self.__booking_list.append(booking)

    def add_card(self,card:Card):
        self.__card = card

class Airline:
    ECONOMYCLASS_LIMIT_WEIGHT = 15
    BUSSINESSCLASS_LIMIT_WEIGHT = 30
    def __init__(self):
        self.__extra_fee_per_kg = 250  # บาท / กิโล
        self.__passenger_list:list = []

    def add_passenger(self,passenger:Passenger):
        self.__passenger_list.append(passenger)

    def get_data_by_pnr(self,pnr:str):
        for passenger in self.__passenger_list:
            for booking in passenger.get_booking_list():
                if(booking.get_pnr() == pnr):
                    return passenger,booking
        raise HTTPException(status_code=404,detail="Data Not Found")
    
    def get_weight_limit(self,pnr:str)->int:
        current_data = self.get_data_by_pnr(pnr)
        seat_class = current_data[1].get_seat_class()
        passenger_tier = current_data[0].get_tier()
        weight_limit_before_tier = self.ECONOMYCLASS_LIMIT_WEIGHT if(seat_class == "Economy") else self.BUSSINESSCLASS_LIMIT_WEIGHT

        if(passenger_tier == "Silver"): return weight_limit_before_tier
        if(passenger_tier == "Gold"): return weight_limit_before_tier*1.5
        if(passenger_tier == "Platinum"): return weight_limit_before_tier*2


    def verify_weight(self,weight_limit:int,passenger:Passenger) -> bool:
        if(passenger.get_weight()<=weight_limit):
            return True
        return False

    def load_luggage(self, pnr: str):
        
        weight_limit = self.get_weight_limit(pnr)
        passenger = self.get_data_by_pnr(pnr)[0]
        booking = self.get_data_by_pnr(pnr)[1]
        card = passenger.get_card()

        # verify luggage weight
        if self.verify_weight(weight_limit,passenger):
            return {"name":passenger.get_name(),
           "luggage_weight":passenger.get_weight(),
           "weight_limit":weight_limit,
        "message":f"Luggage loaded (WithinLimit)"
        }

        # calculate extra fee
        extra_weight = passenger.get_weight() -weight_limit
        extra_fee = self.__calculate_extra_weight_fee(extra_weight)

        # payment
        payment_result = self.payment_process(card,extra_fee)
        if not payment_result:
            return "Error: Extra baggage payment failed"
        
        # create_subtransaction
        subtransaction = Subtransaction("Load_luggage_fee",extra_fee)
        transaction = booking.get_transaction()
        transaction.add_subtransaction(subtransaction)

        return {"name":passenger.get_name(),
           "luggage_weight":passenger.get_weight(),
           "weight_limit":weight_limit,
        "message":f"Luggage loaded (Extra Fee :{extra_weight} X {self.__extra_fee_per_kg} = {extra_fee})",
        "transaction":booking.get_transaction().get_all_subtransaction()
        }
    
    def __calculate_extra_weight_fee(self, extra_weight: int) -> int:
        return extra_weight * self.__extra_fee_per_kg
    
    def payment_process(self,channel,fee:int):
        channel.pay(fee)
        return True


airline = Airline()
booking = Booking(pnr="ABC123",seat_class="Business")
passenger = Passenger(first_name="John", luggage_weight=50)
card = Card("1234-5678-9101-1121",10000)
transaction = Transaction("Booking",10000)

passenger.add_booking(booking)
passenger.add_card(card)
airline.add_passenger(passenger)
booking.add_transaction(transaction)
# airline.load_luggage("ABC123")

@app.get("/")
def home():
    return {"message":"Welcome to KNNS Airways"}

@app.post("/loadluggage")
def Loadluggage(pnr:str):
    message = airline.load_luggage(pnr)
    return message

if __name__ == "__main__":
    uvicorn.run("05LoadbagWithAPI:app", host="127.0.0.1", port=8000, log_level="info")