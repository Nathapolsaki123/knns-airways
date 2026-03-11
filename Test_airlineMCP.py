import asyncio
from mcp.server.fastmcp import FastMCP
from datetime import datetime, timedelta

# นำเข้า Logic ทั้งหมดจากไฟล์หลักของคุณ 
from _10Airline_system import (
    Airline, FlightStatus, BookingStatus, Passenger, Member, 
    Payment, PayByCard, PayByPoint, FlightStatus, PaymentStatus,Airplane
)

# สร้าง MCP Server
mcp = FastMCP("KNNS-Airline-Full-Management")

# สร้าง Instance ของสายการบิน [cite: 17]
airline_sys = Airline("KNNS Global Airways")

# ========================================================
# 🔧 [ADMIN TOOLS - 6 CASES]
# ========================================================

# @mcp.tool()
# def admin_tc01_setup_infrastructure():
#     """[TC-01] Setup Infrastructure: เตรียมเครื่องบินและเมนูอาหารในคลังระบบ """
#     from _10Airline_system import Airplane
#     airline_sys.add_airplane(Airplane("Airbus A350", "HS-MAX", 20, 5)) 
#     airline_sys.create_flightfood("Premium Beef", 500.0)  
#     airline_sys.create_flightfood("Vegetarian Pasta", 300.0)  
#     airline_sys.create_flightfood("Special Dessert", 150.0)  
#     return "Infrastructure is ready with Airplanes and Food Database."

airline_sys = Airline("k")
airline_sys.create_flightfood("Premium Beef", 500.0)  
airline_sys.create_flightfood("Vegetarian Pasta", 300.0)  
airline_sys.create_flightfood("Special Dessert", 150.0)  

@mcp.tool()
def admin_tc03_update_flight_hybrid(flight_no: str, old_depart: str, new_depart: str = None, new_arrive: str = None, status: str = None):
    """[TC-03] Update Flight: อัปเดตทั้งเวลาและสถานะไฟลท์ (เช่น SCHEDULED -> BOARDING) """
    flight_no = flight_no.strip().upper()
    old_dt = datetime.strptime(old_depart, '%d-%m-%Y %H:%M')
    res = []
    if new_depart and new_arrive:
        airline_sys.update_flight(flight_no, old_depart, new_depart, new_arrive)  
        res.append("Time Changed")
    if status:
        stat_enum = FlightStatus[status.upper()]
        airline_sys.update_flight_status(flight_no, old_dt, stat_enum)  
        res.append(f"Status set to {status}")
    return " & ".join(res) if res else "No changes."

@mcp.tool()
def admin_tc04_broadcast_msg(flight_no: str, depart_time: str, message: str):
    """[TC-04] Send Notification: แจ้งประกาศสำคัญไปยังผู้โดยสารทุกคนในไฟลท์ """
    dt = datetime.strptime(depart_time, '%d-%m-%Y %H:%M')
    instance = airline_sys.find_flight_instance(flight_no, dt)  
    count = 0
    for p in airline_sys._Airline__passenger_list:
        for b in p.booking_list:
            if b.flight_instance == instance:
                p.add_notification(f"AIRLINE NEWS: {message}")  
                count += 1
    return f"Broadcasted to {count} passengers."

@mcp.tool()
def admin_tc05_business_report(flight_no: str):
    """[TC-05] Report: สรุปรายงานรายได้และจำนวนผู้โดยสาร """
    return {"Income": airline_sys.create_income_report(flight_no), "Seats": airline_sys.create_flight_seat_report(flight_no)}  

# ========================================================
# 👤 [PASSENGER & COUNTER TOOLS - 8 CASES]
# ========================================================

@mcp.tool()
def user_tc06_register(name: str, email: str, pin: str, money: float, tier: str):
    """[TC-06] Create Account: สมัครสมาชิกใหม่ """
    u = airline_sys.create_account(name, email, pin, money, tier)  
    return f"Account {u.passenger_id} Created."

@mcp.tool()
def user_tc07_search(flight_no: str):
    """[TC-07] Search Flight: ตรวจสอบตารางบิน """
    f = airline_sys.search_flight(flight_no)  
    return f.get_flight_data() if f else "Not found."

@mcp.tool()
def user_tc08_booking(passenger_id: str, flight_no: str, depart: str, seat_type: str, amount: int):
    """[TC-08] Request Booking: จองที่นั่งในระบบ """
    b = airline_sys.booking(passenger_id, flight_no, depart, seat_type, amount)  
    return f"PNR: {b.pnr} | Total: {b.fare} THB"

@mcp.tool()
def user_tc09_pay(passenger_id: str, pnr: str, method: str, pin: str = None):
    """[TC-09] Pay: ชำระเงินยืนยันการเดินทาง """
    airline_sys.pay_book(passenger_id, pnr, method, pin)  
    return f"Payment Success for {pnr}."

@mcp.tool()
def user_tc10_cancel(passenger_id: str, pnr: str):
    """[TC-10] Cancel Booking: ยกเลิกการจองก่อนจ่ายเงิน """
    return airline_sys.cancel_booking(passenger_id, pnr)  

@mcp.tool()
def user_tc11_refund(pnr: str, passenger_id: str):
    """[TC-11] Request Refund: ขอคืนเงิน (สำหรับสมาชิก) """
    return airline_sys.request_refund(pnr, passenger_id)  

@mcp.tool()
def user_tc12_counter_ops(passenger_id: str, pnr: str, seat_no: str, luggage_kg: float = 0.0):
    """[TC-12] Check-in & Load Luggage: ดำเนินการที่เคาน์เตอร์สนามบิน [cite: 10, 18, 19]"""
    p, b = airline_sys.get_data_by_pnr(pnr)  
    b.flight_instance.open_check_in()  
    airline_sys.check_in_passenger(passenger_id, pnr)  
    airline_sys.choose_seat(passenger_id, pnr, seat_no)  
    if luggage_kg > 0: p.set_weight(luggage_kg)  
    return airline_sys.load_luggage(pnr) if luggage_kg > 0 else "Checked-in Successful."  

@mcp.tool()
def user_tc13_read_inbox(passenger_id: str):
    """[TC-13] Read Notification: ผู้โดยสารอ่านประกาศและการแจ้งเตือน """
    u = airline_sys.search_passenger_by_id(passenger_id)  
    return {"notifications": u.notification_list} if u.notification_list else "Inbox Empty." 


@mcp.tool()
def create_airplane(model: str, no: str, economy_seat: int, business_seat: int):
    """
    สร้างเครื่องบินลำใหม่ (Airplane) และลงทะเบียนเข้าสู่ระบบของสายการบิน
    - model: ชื่อรุ่นเครื่องบิน (เช่น 'Airbus A350-800')
    - no: เลขทะเบียนเครื่องบิน (Registration number เช่น 'AB350-8')
    - economy_seat: จำนวนที่นั่งชั้นประหยัด
    - business_seat: จำนวนที่นั่งชั้นธุรกิจ
    ใช้เครื่องมือนี้เมื่อต้องการเพิ่มเครื่องบินใหม่เข้าระบบก่อนที่จะนำไปสร้างเที่ยวบิน
    """
    airplane = Airplane(model, no, economy_seat, business_seat)
    airline_sys.add_airplane(airplane)
    return airplane.get_data()



if __name__ == "__main__":
    mcp.run()