import asyncio
from mcp.server.fastmcp import FastMCP
from datetime import datetime, timedelta
from enum import Enum
from datetime import date, datetime, timedelta
from abc import ABC, abstractmethod
from fastapi import FastAPI, HTTPException

import random
import uuid

# นำเข้า Logic ทั้งหมดจากไฟล์ของคุณ (ต้องชื่อไฟล์ airline_logic.py)
from _12Test import *

# สร้าง MCP Server
mcp = FastMCP("KNNS-Airline-Ultimate-Test")

# สร้าง Instance ของสายการบินไว้เป็น Global State
airline_sys = Airline("KNNS Global Airways")

# ========================================================
# 🚀 12 TEST CASES - MCP TOOLS
# ========================================================

# @mcp.tool()
# def admin_setup_system():
#     """[Admin]Setup ระบบพื้นฐาน สร้างเครื่องบิน, เส้นทางบิน และเมนูอาหาร"""
#     from _12Test import Airplane
airline_sys.create_flightfood("Premium Steak", 500.0)
airline_sys.create_flightfood("Bibimbap", 250.0)

@mcp.tool()
def create_flight(flight_no: str, origin: str, target: str):
    """
    สร้างเส้นทางการบินหลัก (Flight Route) โดยยังไม่ได้ระบุเวลาหรือเครื่องบิน
    - flight_no: รหัสเที่ยวบิน (เช่น 'TG911')
    - origin: สนามบินต้นทาง (เช่น 'BKK')
    - target: สนามบินปลายทาง (เช่น 'HKT')
    ต้องสร้างเส้นทางบินก่อนเสมอ ถึงจะไปสร้าง Flight Instance (ตารางบินจริง) ได้
    """
    flight : Flight = airline_sys.create_flight(flight_no, origin, target)
    return flight.get_flight_data()

@mcp.tool()
def create_flight_instance(flight_no: str, airplane_no: str, depart_time: str, arrive_time: str):
    """
    สร้างตารางบินจริง (Flight Instance) โดยการจับคู่เส้นทางบินกับเครื่องบินและกำหนดเวลา
    - flight_no: รหัสเที่ยวบินที่เคยสร้างไว้แล้ว
    - airplane_no: เลขทะเบียนเครื่องบินที่ต้องการใช้
    - depart_time: เวลาออกเดินทาง รูปแบบ 'DD-MM-YYYY HH:MM' (เช่น '15-03-2024 10:30')
    - arrive_time: เวลาถึงปลายทาง รูปแบบ 'DD-MM-YYYY HH:MM'
    ใช้เครื่องมือนี้เพื่อกำหนดวันและเวลาที่จะบินจริง
    """
    result = airline_sys.create_flight_instance(flight_no, airplane_no, depart_time, arrive_time)
    flight_instance = airline_sys.search_flight_instance(flight_no, depart_time)
    return {
        "Message": result,
        "Info": flight_instance.get_flight_instance_data(),
        "Amount_seat": {
            "Economy": flight_instance.get_amount_seat("Economy"),
            "Business": flight_instance.get_amount_seat("Business")
        },
        "FlightFood": flight_instance.show_flightfood(),
        "seat_layout": flight_instance.get_available_seat()
    }

@mcp.tool()
def user_create_account(name: str, email: str, pin: str, money: float, tier: str):
    """[Passenger]สมัครสมาชิกใหม่ (รองรับ Guest, Silver, Gold, Platinum)"""
    user = airline_sys.create_account(name, email, pin, money, tier)
    return f"Account Created: {user.name} (ID: {user.passenger_id}) Tier: {tier}"

# @mcp.tool()
# def user_search_flight_instance(flight_no: str):
#     """[Passenger]ค้นหาข้อมูลเที่ยวบินและเส้นทาง"""
#     f = airline_sys.search_flight(flight_no)
#     return f.get_flight_data() if f else "Flight not found."

@mcp.tool()
def user_request_booking(passenger_id: str, flight_no: str, depart_time: str, seat_type: str, amount: int):
    """[Passenger]ทำการจองที่นั่ง (Request Booking)"""
    book = airline_sys.booking(passenger_id, flight_no, depart_time, seat_type, amount)
    return f"Booking Success: PNR {book.pnr}, Total Fare: {book.fare} THB"

@mcp.tool()
def user_payment(passenger_id: str, pnr: str, method: str, pin: str = None):
    """[Passenger]ชำระเงิน (PayByCard หรือ PayByPoint) เพื่อยืนยันการจอง"""
    airline_sys.pay_book(passenger_id, pnr, method, pin)
    return f"Payment Success for PNR {pnr}. Status: CONFIRMED"

@mcp.tool()
def user_cancel_booking(passenger_id: str, pnr: str):
    """[Passenger]ยกเลิกการจองขณะสถานะ PENDING (ก่อนจ่ายเงิน)"""
    return airline_sys.cancel_booking(passenger_id, pnr)

@mcp.tool()
def member_request_refund(pnr: str, passenger_id: str):
    """[Member]ขอคืนเงิน (Refund) และตรวจสอบเงื่อนไข Blacklist"""
    return airline_sys.request_refund(pnr, passenger_id)

@mcp.tool()
def admin_update_status_and_notify(flight_no: str, depart_time: str, status_str: str):
    """[Admin]อัปเดตสถานะไฟลท์ (เช่น BOARDING) และส่ง Notification ไปยังผู้โดยสาร"""
    dt = datetime.strptime(depart_time, '%d-%m-%Y %H:%M')
    status = FlightStatus[status_str.upper()]
    airline_sys.update_flight_status(flight_no, dt, status)
    return f"Flight {flight_no} is now {status_str}. Passengers notified."

@mcp.tool()
def user_check_in_and_choose_seat(passenger_id: str, pnr: str, seat_no: str):
    """[Passenger]เช็คอินและเลือกที่นั่ง (Check-in & Choose Seat)"""
    # จำลองการเปิดเช็คอินในระบบ
    p, b = airline_sys.get_data_by_pnr(pnr)
    b.flight_instance.open_check_in()
    
    airline_sys.check_in_passenger(passenger_id, pnr)
    tickets = airline_sys.choose_seat(passenger_id, pnr, seat_no)
    return f"Check-in Success. Seat {seat_no} assigned. Ticket Issued."

@mcp.tool()
def counter_load_luggage(pnr: str, weight: float):
    """[Counter]โหลดสัมภาระหน้าเคาน์เตอร์ และคำนวณค่าธรรมเนียมน้ำหนักเกิน"""
    passenger, booking = airline_sys.get_data_by_pnr(pnr)
    passenger.set_weight(weight)
    return airline_sys.load_luggage(pnr)

@mcp.tool()
def admin_generate_reports(flight_no: str):
    """[Admin]ดูรายงานรายได้และสถิติการครองที่นั่ง (Report)"""
    income = airline_sys.create_income_report(flight_no)
    seats = airline_sys.create_flight_seat_report(flight_no)
    return {"income": income, "occupancy": seats}

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

@mcp.tool()
def user_read_inbox(passenger_id: str):
    """Read Notification: ผู้โดยสารอ่านประกาศและการแจ้งเตือน """
    u = airline_sys.search_passenger_by_id(passenger_id)  
    return {"notifications": u.notification_list} if u.notification_list else "Inbox Empty." 

@mcp.tool()
def flight_information(flight_no:str,depart_time: str):
    """-flight_no: เลข flight ที่จะหา
    -departure_time: เวลา flight departure"""
    flight = airline_sys.find_flight_instance(flight_no, depart_time)
    return flight.get_flight_instance_data()

@mcp.tool()
def show_all_flight_instance():
    """
    แสดงตารางบิน (Flight Instances) ทั้งหมดที่ถูกสร้างขึ้นในระบบ 
    รวมถึงข้อมูลเวลาเดินทาง และระยะเวลาบิน
    """
    data = airline_sys.show_flight_instance()
    return data

@mcp.tool()
def edit_flight(flight_no: str, old_depart_time: str, depart_time: str, arrive_time: str):
    """
    แก้ไขเวลาเดินทางของเที่ยวบินที่มีอยู่แล้ว
    - flight_no: รหัสเที่ยวบิน
    - old_depart_time: เวลาออกเดินทางเดิมที่ต้องการเปลี่ยน (เพื่อระบุตัวเที่ยวบิน)
    - depart_time: เวลาออกเดินทางใหม่ (DD-MM-YYYY HH:MM)
    - arrive_time: เวลาถึงปลายทางใหม่ (DD-MM-YYYY HH:MM)
    """
    instance = airline_sys.update_flight(flight_no, old_depart_time, depart_time, arrive_time)
    return {"Info": instance.get_flight_instance_data()}

@mcp.tool()
def order_food (passenger_id: str, pnr: str, food_name: str, quantity: int, payment_type: str, pin: str):
    """
    ซื้ออาหาร 
    -passenger_id = รหัสผู้โดยสาร , 
    -pnr = PNR , 
    -food_name = ชื่ออาหาร , 
    -quantity = จำนวน , 
    -payment_type = ช่องทางการจ่ายเงิน , 
    -pin = รหัส
    """
    airline_sys.buy_food (passenger_id, pnr, food_name, quantity, payment_type, pin)
    return f"{food_name} be bought {quantity} amount"

if __name__ == "__main__":
    mcp.run()