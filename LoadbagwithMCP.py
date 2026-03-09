from fastapi import FastAPI,HTTPException
import uvicorn
from abc import ABC,abstractmethod
from fastmcp import FastMCP

mcp = FastMCP("Loadbag")

app = FastAPI()

class Payment_Method(ABC):

    @abstractmethod
    def pay(self):
        pass

class Booking:
    def __init__(self, pnr: str, passenger,flight_in, seat_type :str):
        self.__pnr = pnr
        self.__passenger = passenger
        self.__flight_instance = flight_in
        self.__seat_type = seat_type
        self.__booking_status = None
        self.__payment_status = None
        self.__booking_date = None
        self.__transaction = None
    
    def get_seat_type(self):
        return self.__seat_type
    
    def get_pnr(self):
        return self.__pnr
    
    def get_transaction(self):
        return self.__transaction
    
    def add_transaction(self,transaction):
        self.__transaction = transaction

class Transaction:
    def __init__(self,name,amount,payment_type):
        self.__name = name
        self.__amount = amount
        self.__subtrans_list:list = []
        self.__payment_type = payment_type

    def add_subtransaction(self,subtransaction):
        self.__subtrans_list.append(subtransaction)

    def get_all_subtransaction(self):
        sub_list = [{self.__name:self.__amount}]
        for sub in self.__subtrans_list:
            sub_list.append(sub.get_data())
        return sub_list


class Subtransaction:
    def __init__(self,name,amount,payment_type):
        self.__name = name
        self.__amount = amount
        self.__payment_type = payment_type

    def get_data(self):
        return {self.__name:self.__amount,"Payment_type":self.__payment_type.get_name()}


class Card:
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


class Pay_By_Card(Payment_Method):

    def pay(self,card:Card,fee):
        card.pay(fee)

    def get_name(self):
        return "Card"

class Passenger:
    def __init__(self, passenger_id:str, name: str,email,luggage_weight: int):
        self.__passenger_id = passenger_id
        self.__name = name
        self.__email = email
        self.__booking_list:list = []
        self.__total_refunded:int = 0
        self.__is_blacklisted:bool = False
        self.__blacklist_time = None
        self.__notification:list = []
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
        return self.__name
    
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


class Member(Passenger):

    def __init__(self, passenger_id, name, email, luggage_weight):
        super().__init__(passenger_id, name, email, luggage_weight)
        self.__point = 0

    def add_point(self,point):
        self.__point+=point


class Silver(Member):

    DISCOUNT = 0.05
    EXTRA_WEIGHT = 5
    ANNUAL_FEE = 200

    def get_weight(self) -> int:
        return super().get_weight()
    def set_weight(self,weight):
        if(weight<0):
            raise HTTPException(status_code=404,detail="Luggage weight must be more than 0")
        super().set_weight(weight)
    
    def get_name(self):
        return super().get_name()
    
    def get_tier(self):
        return "Gold"
    
    def get_booking_list(self):
        return super().get_booking_list()
    
    def get_card(self):
        return super().get_card()
    
    def add_booking(self,booking:Booking):
        super().add_booking(booking)

    def add_card(self,card:Card):
        super().add_card(card)

    def add_point(self,point):
        super().add_point(point)



class Gold(Member):

    DISCOUNT = 0.1
    EXTRA_WEIGHT = 10
    ANNUAL_FEE = 300

    def get_weight(self) -> int:
        return super().get_weight()
    def set_weight(self,weight):
        if(weight<0):
            raise HTTPException(status_code=404,detail="Luggage weight must be more than 0")
        super().set_weight(weight)
    
    def get_name(self):
        return super().get_name()
    
    def get_tier(self):
        return "Gold"
    
    def get_booking_list(self):
        return super().get_booking_list()
    
    def get_card(self):
        return super().get_card()
    
    def add_booking(self,booking:Booking):
        super().add_booking(booking)

    def add_card(self,card:Card):
        super().add_card(card)

    def add_point(self,point):
        super().add_point(point)


class Platinum(Member):

    DISCOUNT = 0.15
    EXTRA_WEIGHT = 20
    ANNUAL_FEE = 500

    def get_weight(self) -> int:
        return super().get_weight()
    def set_weight(self,weight):
        if(weight<0):
            raise HTTPException(status_code=404,detail="Luggage weight must be more than 0")
        super().set_weight(weight)
    
    def get_name(self):
        return super().get_name()
    
    def get_tier(self):
        return "Platinum"
    
    def get_booking_list(self):
        return super().get_booking_list()
    
    def get_card(self):
        return super().get_card()
    
    def add_booking(self,booking:Booking):
        super().add_booking(booking)

    def add_card(self,card:Card):
        super().add_card(card)

    def add_point(self,point):
        super().add_point(point)


class Airline:
    ECONOMYCLASS_LIMIT_WEIGHT = 15
    BUSSINESSCLASS_LIMIT_WEIGHT = 30
    EXTRA_FEE_PER_KG = 300
    def __init__(self,name):
        self.__name = name
        self.__passenger_list:list = []
        self.__booking_list:list = []
        self.__airplane_list:list = []
        self.__flight_list:list = []
        self.__blacklist:list = []

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
        seat_class = current_data[1].get_seat_type()
        extra_weight = current_data[0].EXTRA_WEIGHT
        weight_limit_before_tier = self.ECONOMYCLASS_LIMIT_WEIGHT if(seat_class == "Economy") else self.BUSSINESSCLASS_LIMIT_WEIGHT

        return weight_limit_before_tier+extra_weight


    def verify_weight(self,weight_limit:int,passenger:Passenger) -> bool:
        if(passenger.get_weight()<=weight_limit):
            return True
        return False

    def load_luggage(self, pnr: str):
        
        weight_limit = self.get_weight_limit(pnr)
        passenger = self.get_data_by_pnr(pnr)[0]
        booking = self.get_data_by_pnr(pnr)[1]
        card = passenger.get_card()
        discount = passenger.DISCOUNT

        # verify luggage weight
        if self.verify_weight(weight_limit,passenger):
            return {"name":passenger.get_name(),
           "luggage_weight":passenger.get_weight(),
           "weight_limit":weight_limit,
        "message":f"Luggage loaded (WithinLimit)"
        }

        # calculate extra fee
        extra_weight = passenger.get_weight() -weight_limit
        extra_fee_before_discount = self.__calculate_extra_weight_fee(extra_weight)
        extra_fee = extra_fee_before_discount*(1-discount)

        # payment
        payment_result = self.payment_process("Card",extra_fee,passenger)  
        if not payment_result:
            return "Error: Extra baggage payment failed"
        
        # create_subtransaction
        transaction = booking.get_transaction()
        transaction.add_subtransaction(payment_result)

        return {"name":passenger.get_name(),
           "luggage_weight":passenger.get_weight(),
           "weight_limit":weight_limit,
        "message":f"Luggage loaded (Extra Fee :[{extra_weight} X {self.EXTRA_FEE_PER_KG}] - {passenger.DISCOUNT*100}% = {extra_fee})",
        "transaction":booking.get_transaction().get_all_subtransaction()
        }
    
    def __calculate_extra_weight_fee(self, extra_weight: int) -> int:
        return extra_weight * self.EXTRA_FEE_PER_KG
    
    def payment_process(self,channel,fee:int,passenger:Passenger) -> Subtransaction:

        try:
            if(channel == "Card"):
                temp_payment_channel = Pay_By_Card()
                card = passenger.get_card()
                temp_payment_channel.pay(card,fee)
                subtransaction = Subtransaction("Load_luggage_fee",fee,temp_payment_channel)
                return subtransaction
        except:
            raise HTTPException(status_code=404,detail="Payment Failed")

# --- ส่วนการจำลองข้อมูล (Mock Data) สำหรับทดสอบ ---

airline = Airline("KNNS-Airways")
payment_method = Pay_By_Card()

# 1. เคส Platinum: น้ำหนักเยอะมาก (60kg) - Business Class
# Limit: 30 (Business) + 20 (Platinum) = 50kg | ส่วนเกิน 10kg
p_platinum = Platinum("PL-001", "Somchai Platinum", "somchai@email.com", luggage_weight=60)
card_platinum = Card("1111-2222", 50000)
p_platinum.add_card(card_platinum)
booking_platinum = Booking("PLAT123", p_platinum, "FL-001", "Business")
trans_platinum = Transaction("Initial Booking", 15000, payment_method)
booking_platinum.add_transaction(trans_platinum)
p_platinum.add_booking(booking_platinum)
airline.add_passenger(p_platinum)

# 2. เคส Gold: น้ำหนักเกินเล็กน้อย (45kg) - Business Class
# Limit: 30 (Business) + 10 (Gold) = 40kg | ส่วนเกิน 5kg
p_gold = Gold("GD-001", "Jane Gold", "jane@email.com", luggage_weight=45)
card_gold = Card("3333-4444", 20000)
p_gold.add_card(card_gold)
booking_gold = Booking("GOLD456", p_gold, "FL-002", "Business")
trans_gold = Transaction("Initial Booking", 12000, payment_method)
booking_gold.add_transaction(trans_gold)
p_gold.add_booking(booking_gold)
airline.add_passenger(p_gold)

# 3. เคส Silver: น้ำหนักพอดีเป๊ะ (20kg) - Economy Class
# Limit: 15 (Economy) + 5 (Silver) = 20kg | ไม่เสียเงินเพิ่ม
p_silver = Silver("SV-001", "Siri Silver", "siri@email.com", luggage_weight=20)
card_silver = Card("5555-6666", 10000)
p_silver.add_card(card_silver)
booking_silver = Booking("SILV789", p_silver, "FL-003", "Economy")
trans_silver = Transaction("Initial Booking", 5000, payment_method)
booking_silver.add_transaction(trans_silver)
p_silver.add_booking(booking_silver)
airline.add_passenger(p_silver)

# 4. เคส Error: เงินในบัตรไม่พอ (Poor Member)
# ส่วนเกินเยอะแต่เงินน้อย เพื่อเทส HTTPException
p_poor = Silver("SV-002", "Poor Guy", "poor@email.com", luggage_weight=40)
card_poor = Card("0000-0000", 100) # มีเงินแค่ 100
p_poor.add_card(card_poor)
booking_poor = Booking("POOR000", p_poor, "FL-004", "Economy")
trans_poor = Transaction("Initial Booking", 3000, payment_method)
booking_poor.add_transaction(trans_poor)
p_poor.add_booking(booking_poor)
airline.add_passenger(p_poor)


@mcp.tool()
def Loadluggage(pnr:str):
    """โหลดกระเป๋า"""
    message = airline.load_luggage(pnr)
    return message

if __name__ == "__main__":
    mcp.run()