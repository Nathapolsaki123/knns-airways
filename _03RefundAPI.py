from  fastapi import FastAPI
import uvicorn
import webbrowser
from _03Refund import *

app = FastAPI()


@app.post ("/requestRefund/{pnr}/{passenger_id}")
def requestRefund (pnr:str,passenger_id:str):
    if len(pnr)!=6 : return f"Error occurred: Wrong Len"
    try :
        airline.request_refund (pnr,passenger_id)
        return "Refund Booking: " +pnr+ " Is Complete"
    except Exception as e:
        return f"Error occurred: {e}"

@app.get ("/getBookkingStatus/{pnr}")
def getBookkingStatus (pnr:str):
    if len(pnr)!=6 : return f"Error occurred: Wrong Len"
    try :
        bookings = airline.search_booking_by_pnr(pnr)
        return "Booking: " + pnr + ", Status --> " + bookings.get_status_str()
    except Exception as e:
        return f"Error occurred: {e}"

def create_system ()-> Airline :
    # 1. สร้างสายการบิน (Airline)
    airline = Airline("KNNS Airways")

    # 2. สร้างโครงสร้างพื้นฐาน: เครื่องบิน (Airplane) และเส้นทางบิน (Flight)
    boeing747 = Airplane(
        model_number="Boeing 747", 
        registration_no="HS-KMITL", 
        economy_seat_amount=300, 
        business_seat_amount=50
    )
    
    # สร้าง Blueprint ของเที่ยวบิน
    flight_blueprint = Flight("KNNS001", "Bangkok (BKK)", "Chiang Mai (CNX)")
    
    # สร้าง Instance ของเที่ยวบินจริง (FlightInstance)
    june_flight = flight_blueprint.crete_flight_instance(
        airplane=boeing747,
        departure_time=datetime(2026, 6, 23, 13, 0),
        arrival_time=datetime(2026, 6, 23, 14, 30),
        price=5000,
        status=FlightStatus.SCHEDULED
    )

    # 3. สร้างข้อมูลผู้โดยสาร (เลือกใช้ Silver Member เนื่องจาก Passenger เป็น Abstract Class)
    # ต้องมี Card เพราะใน Passenger __init__ รับพารามิเตอร์ card
    my_card = Card(pin="1234", money=20000)
    passenger = Silver(
        passenger_id="STD68011671", 
        name="John", 
        email="john@kmitl.ac.th", 
        card=my_card
    )

    # 4. การสร้างการจอง (Booking)
    # ต้องสร้าง Seat Object ก่อน (ใช้ Bussiness ตามที่ระบุใน Class)
    my_seat_type = "Bussiness"
    booking = Booking(
        pnr="PNR747", 
        passenger=passenger, 
        flight_instance=june_flight, 
        seat_type=my_seat_type, 
        seat_amount=1
    )
    
    # เพิ่มผู้โดยสารลงในระบบสายการบิน
    airline.add_passenger(passenger)
    airline.add_booking(booking)
    airline.add_flight(flight_blueprint)

    # ---------------------------------------------------------
    # ส่วนสำคัญ: การทำให้ Logic Refund ทำงานได้
    # ---------------------------------------------------------
    
    # [A] เพิ่ม Booking เข้าไปในตัว Passenger (เพื่อให้ search_booking_by_pnr หาเจอ)
    passenger.add_booking(booking)

    # [B] อัปเดตสถานะให้เป็น CONFIRMED และ PAID 
    # เพราะ Logic ใน airline.request_refund เช็ค: booking.check_status(BookingStatus.CONFIRMED, PaymentStatus.PAID)
    booking.update_status(BookingStatus.CONFIRMED, PaymentStatus.PAID)
    return airline

airline = create_system()

if __name__ == "__main__" :
    webbrowser.open ("http://127.0.0.1:8000/docs")
    uvicorn.run ("_03RefundAPI:app",host = "127.0.0.1",port = 8000, reload=True )