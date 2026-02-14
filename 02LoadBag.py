from datetime import datetime
from typing import List


class Transaction:
    def __init__(self, transaction_id: str, amount: float):
        self.__transaction_id = transaction_id
        self.__amount = amount
        self.__created_at = datetime.now()

    def print_transaction(self):
        return {
            "transaction_id": self.__transaction_id,
            "amount": self.__amount,
            "created_at": self.__created_at
        }


class Payment:
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


class Passenger:
    def __init__(self, first_name: str, luggage_limit: int):
        self.__first_name = first_name
        self.__luggage_limit = luggage_limit
        self.__transactions: List[Transaction] = []

    def verify_weight(self, weight: int) -> bool:
        return weight <= self.__luggage_limit

    def add_transaction(self, transaction: Transaction):
        self.__transactions.append(transaction)

    def get_luggage_limit(self):
        return self.__luggage_limit


class Booking:
    def __init__(self, pnr: str, is_valid: bool = True):
        self.__pnr = pnr
        self.__is_valid = is_valid

    def validate_booking(self, pnr: str) -> bool:
        return self.__pnr == pnr and self.__is_valid


class Airline:
    def __init__(self):
        self.__extra_fee_per_kg = 500  # บาท / กิโล

    def load_luggage(self, pnr: str, weight: int,
                     booking: Booking,
                     passenger: Passenger,
                     payment: Payment):
        # 1. validate booking
        if not booking.validate_booking(pnr):
            return "Error: Invalid booking"

        # 2. verify luggage weight
        if passenger.verify_weight(weight):
            return "Luggage loaded (within limit)"

        # 3. calculate extra fee
        extra_weight = weight - passenger.get_luggage_limit()
        extra_fee = self.__calculate_extra_weight_fee(extra_weight)

        # 4. payment
        payment_result = payment.process_payment(extra_fee)
        if not payment_result:
            return "Error: Extra baggage payment failed"

        # 5. create transaction
        transaction = Transaction(
            transaction_id=f"TXN-{pnr}",
            amount=extra_fee
        )

        passenger.add_transaction(transaction)

        return {
            "message": "Luggage loaded with extra fee",
            "extra_fee": extra_fee,
            "transaction": transaction.print_transaction()
        }

    def __calculate_extra_weight_fee(self, extra_weight: int) -> float:
        return extra_weight * self.__extra_fee_per_kg


airline = Airline()
booking = Booking(pnr="ABC123", is_valid=True)
passenger = Passenger(first_name="John", luggage_limit=20)
payment = Payment()

result = airline.load_luggage(
    pnr="ABC123",
    weight=25,
    booking=booking,
    passenger=passenger,
    payment=payment
)

print(result)