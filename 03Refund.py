
from enum import Enum
from datetime import datetime


class BookingStatus(Enum):
    CONFIRMED = "Confirmed"
    CANCELLED = "Cancelled"
    REFUNDED = "Refunded"


class Transaction:
    def __init__(self, transaction_id: str, amount: float, type_: str):
        self.__transaction_id = transaction_id
        self.__amount = amount
        self.__type = type_
        self.__created_at = datetime.now()

    def print_transaction(self):
        print(f"[{self.__type}] Amount: {self.__amount}")


class Passenger:
    def __init__(self, first_name: str, last_name: str):
        self.__first_name = first_name
        self.__last_name = last_name
        self.__transactions: list[Transaction] = []

    def add_transaction(self, transaction: Transaction):
        self.__transactions.append(transaction)
        print("Passenger: transaction added")

    def get_transactions(self):
        return self.__transactions


class Booking:
    def __init__(self, pnr: str, amount: float):
        self.__pnr = pnr
        self.__amount = amount
        self.__status = BookingStatus.CONFIRMED

    def validate(self) -> bool:
        return self.__status == BookingStatus.CONFIRMED

    def update_status(self, status: BookingStatus):
        self.__status = status
        print(f"Booking status updated to {status.value}")

    def get_amount(self) -> float:
        return self.__amount

    def get_pnr(self) -> str:
        return self.__pnr


class Payment:
    def process_refund(self, amount: float, method: str) -> bool:
        print(f"Processing refund {amount} via {method}")
        return True


class FinanceOfficer:
    def validate_booking(self, booking: Booking) -> bool:
        return booking.validate()

    def approve_refund(self, booking: Booking, amount: float) -> bool:
        print("FinanceOfficer: refund approved")
        return True


class Airline:
    def __init__(self):
        self.__payment = Payment()
        self.__finance_officer = FinanceOfficer()

    def request_refund(self, passenger: Passenger, booking: Booking):
        print("Airline: refund requested")

        # 1. Validate booking
        if not booking.validate():
            raise Exception("Invalid or non-refundable booking")

        # 2. Finance approval
        if not self.__finance_officer.validate_booking(booking):
            raise Exception("Finance validation failed")

        if not self.__finance_officer.approve_refund(
            booking, booking.get_amount()
        ):
            raise Exception("Refund rejected by finance")

        # 3. Process refund
        if not self.__payment.process_refund(
            booking.get_amount(), "Original Method"
        ):
            raise Exception("Refund failed")

        # 4. Create transaction
        transaction = Transaction(
            transaction_id="TRX-REF-001",
            amount=booking.get_amount(),
            type_="REFUND"
        )

        passenger.add_transaction(transaction)

        # 5. Update booking status
        booking.update_status(BookingStatus.REFUNDED)

        print(f"Refund confirmed for PNR {booking.get_pnr()}")


passenger = Passenger("John", "Doe")
booking = Booking("PNR123", 5000.0)

airline = Airline()
airline.request_refund(passenger, booking)