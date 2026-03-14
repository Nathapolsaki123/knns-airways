import asyncio
from mcp.server.fastmcp import FastMCP
from datetime import datetime, timedelta
from enum import Enum
from datetime import date, datetime, timedelta
from abc import ABC, abstractmethod
from fastapi import FastAPI, HTTPException
import copy
import random
import uuid

# นำเข้า Logic ทั้งหมดจากไฟล์ของคุณ (ต้องชื่อไฟล์ airline_logic.py)
from _12Test import *

# สร้าง MCP Server
mcp = FastMCP("KNNS-Airline-Ultimate-Test")

# สร้าง Instance ของสายการบินไว้เป็น Global State
airline_sys = Airline("KNNS Global Airways")


def crete_system():
    airline_sys.create_flightfood("Premium Steak", 500.0)
    airline_sys.create_flightfood("Bibimbap", 250.0)
    airline_sys.create_flightfood("Padthai", 150.0)
    airline_sys.create_flightfood("Pizza", 800.0)

crete_system() #-->> สร้างระบบ

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
    flight_instance = airline_sys.find_flight_instance(flight_no, depart_time)
    return {
        "Message": result,
        "Info": flight_instance.get_flight_instance_data(),
        "Amount_seat": {
            "Economy": flight_instance.get_amount_seat("Economy"),
            "Business": flight_instance.get_amount_seat("Business")
        },
        "FlightFood": flight_instance.show_flightfood(),
        "seat_layout": {
            "Economy": flight_instance.get_available_seat("Economy"),
            "Business": flight_instance.get_available_seat("Business")
        }
    }


@mcp.tool()
def user_create_account(name: str, email: str, pin: str, money: float, tier: str):
    """
    สร้างบัญชีผู้โดยสารหรือสมัครสมาชิกใหม่ในระบบ
    - name: ชื่อ-นามสกุลของผู้โดยสาร
    - email: อีเมลสำหรับติดต่อและใช้เข้าสู่ระบบ
    - pin: รหัสผ่านหรือ PIN สำหรับยืนยันตัวตน
    - money: ยอดเงินเริ่มต้นในบัญชี
    - tier: ระดับสมาชิก (รองรับ 'Guest', 'Silver', 'Gold', 'Platinum')
    ใช้เครื่องมือนี้เมื่อมีผู้ใช้งานใหม่ต้องการลงทะเบียนเพื่อจองตั๋ว
    """
    user = airline_sys.create_account(name, email, pin, money, tier)
    return f"Account Created: {user.name} (ID: {user.passenger_id}) Tier: {tier}"


@mcp.tool()
def user_search_flight_instance(flight_no: str, depart_time: str):
    """
    ค้นหาข้อมูลเที่ยวบินและเส้นทางบินแบบเจาะจง
    - flight_no: รหัสเที่ยวบินที่ต้องการค้นหา (เช่น 'TG911')
    - depart_time: เวลาออกเดินทาง รูปแบบ 'DD-MM-YYYY HH:MM'
    ใช้เครื่องมือนี้เพื่อดูรายละเอียดของเที่ยวบิน จำนวนที่นั่งที่เหลือ และเมนูอาหารบนเครื่อง
    """
    flight_instance = airline_sys.find_flight_instance(flight_no,depart_time)
    return {
        "Info": flight_instance.get_flight_instance_data(),
        "Amount_seat": {
            "Economy": flight_instance.get_amount_seat("Economy"),
            "Business": flight_instance.get_amount_seat("Business")
        },
        "FlightFood": flight_instance.show_flightfood(),
        "seat_layout": {
            "Economy": flight_instance.get_available_seat("Economy"),
            "Business": flight_instance.get_available_seat("Business")
        }
    }


@mcp.tool()
def user_request_booking(passenger_id: str, flight_no: str, depart_time: str, seat_type: str, amount: int):
    """
    ทำการจองที่นั่งสำหรับผู้โดยสาร (Request Booking)
    - passenger_id: รหัสผู้โดยสารที่ทำการจอง
    - flight_no: รหัสเที่ยวบินที่ต้องการจอง
    - depart_time: เวลาออกเดินทาง รูปแบบ 'DD-MM-YYYY HH:MM'
    - seat_type: ประเภทที่นั่ง (เช่น 'Economy' หรือ 'Business')
    - amount: จำนวนผู้โดยสารหรือจำนวนที่นั่งที่ต้องการจอง
    ใช้เครื่องมือนี้เพื่อสร้างรหัส PNR ใหม่ในสถานะ PENDING เพื่อรอการชำระเงินต่อไป
    """
    book = airline_sys.booking(passenger_id, flight_no, depart_time, seat_type, amount)
    return f"Booking Success: PNR {book.pnr}, Total Fare: {book.fare} THB"


@mcp.tool()
def user_payment(passenger_id: str, pnr: str, method: str, pin: str|None = None):
    """
    ชำระเงินเพื่อยืนยันการจองตั๋วเครื่องบิน
    - passenger_id: รหัสผู้โดยสารที่เป็นเจ้าของการจอง
    - pnr: รหัสการจอง (PNR)
    - method: วิธีการชำระเงิน (เช่น 'PayByCard' หรือ 'PayByPoint')
    - pin: รหัส PIN ยืนยันการชำระเงิน (ถ้ามี/ถ้าจำเป็น)
    ใช้เครื่องมือนี้เพื่อเปลี่ยนสถานะการจองจาก PENDING เป็น CONFIRMED
    """
    airline_sys.pay_book(passenger_id, pnr, method, pin)
    return f"Payment Success for PNR {pnr}. Status: CONFIRMED"


@mcp.tool()
def user_cancel_booking(passenger_id: str, pnr: str):
    """
    ยกเลิกการจองตั๋วเครื่องบินขณะที่สถานะยังเป็น PENDING
    - passenger_id: รหัสผู้โดยสารที่เป็นเจ้าของการจอง
    - pnr: รหัสการจอง (PNR) ที่ต้องการยกเลิก
    ใช้เครื่องมือนี้เพื่อยกเลิกการจองที่ยังไม่ได้ทำการชำระเงิน
    """
    return airline_sys.cancel_booking(passenger_id, pnr)


@mcp.tool()
def member_request_refund(pnr: str, passenger_id: str):
    """
    ขอคืนเงินค่าตั๋ว (Refund) สำหรับสมาชิก
    - pnr: รหัสการจอง (PNR) ที่ต้องการขอคืนเงิน
    - passenger_id: รหัสผู้โดยสารที่เป็นเจ้าของการจอง
    ใช้เครื่องมือนี้เมื่อสมาชิกต้องการยกเลิกเที่ยวบินที่ชำระเงินแล้ว ระบบจะตรวจสอบเงื่อนไขและ Blacklist
    """
    return airline_sys.request_refund(pnr, passenger_id)


@mcp.tool()
def admin_update_status_and_notify(flight_no: str, depart_time: str, status_str: str):
    """
    อัปเดตสถานะของเที่ยวบินและส่งการแจ้งเตือน (Notification) ไปยังผู้โดยสาร
    - flight_no: รหัสเที่ยวบินที่ต้องการอัปเดต
    - depart_time: เวลาออกเดินทาง รูปแบบ 'DD-MM-YYYY HH:MM'
    - status_str: สถานะเที่ยวบิน (เช่น 'BOARDING', 'DELAYED', 'CANCELLED', 'ARRIVED')
    ใช้เครื่องมือนี้สำหรับเจ้าหน้าที่ (Admin) ในการจัดการและประกาศสถานะของเที่ยวบิน
    """
    status = FlightStatus[status_str.upper()]
    airline_sys.update_flight_status(flight_no, depart_time, status)
    return f"Flight {flight_no} is now {status_str}. Passengers notified."


@mcp.tool()
def counter_user_check_in(passenger_id: str, pnr: str):
    """
    ผู้โดยสารทำการเช็คอิน
    - passenger_id: รหัสผู้โดยสารที่ทำการเช็คอิน
    - pnr: รหัสการจอง (PNR) ที่ชำระเงินแล้ว
    ใช้เครื่องมือนี้เพื่อยืนยันตัวตนให้ผู้โดยสาร
    """
    
    airline_sys.check_in_passenger(passenger_id, pnr)
    return f"Check-in Success."


@mcp.tool()
def counter_user_choose_seat(passenger_id: str, pnr: str, seat_no: str):
    """
    เลือกที่นั่งบนเที่ยวบิน
    - passenger_id: รหัสผู้โดยสารที่ทำเลือกที่นั่ง
    - pnr: รหัสการจอง (PNR) ที่เช็กอินแล้ว
    - seat_no: หมายเลขที่นั่งที่ต้องการเลือก (เช่น 'E1', 'B12')
    ใช้เครื่องมือนี้ออกตั๋ว (Ticket Issued) และล็อกที่นั่งให้ผู้โดยสาร
    """
    tickets = airline_sys.choose_seat(passenger_id, pnr, seat_no)
    return f"Choose seat Success. Seat {seat_no} assigned. Ticket Issued."


@mcp.tool()
def counter_load_luggage(pnr: str, weight: float):
    """
    โหลดสัมภาระหน้าเคาน์เตอร์เช็คอิน
    - pnr: รหัสการจอง (PNR) ของผู้โดยสาร
    - weight: น้ำหนักสัมภาระรวมที่ต้องการโหลด (กิโลกรัม)
    ใช้เครื่องมือนี้เพื่อบันทึกน้ำหนักสัมภาระและคำนวณค่าธรรมเนียมน้ำหนักเกินหากมี
    """
    passenger, booking = airline_sys.get_data_by_pnr(pnr)
    passenger.set_weight(weight)
    return airline_sys.load_luggage(pnr)


@mcp.tool()
def admin_generate_reports(flight_no: str):
    """
    ดูรายงานสรุปรายได้และสถิติการครองที่นั่งของเที่ยวบิน
    - flight_no: รหัสเที่ยวบินที่ต้องการดูรายงาน
    ใช้เครื่องมือนี้สำหรับเจ้าหน้าที่ (Admin) เพื่อดูภาพรวมรายได้และที่นั่งของเที่ยวบินนั้นๆ
    """
    income = airline_sys.create_income_report(flight_no)
    seats = airline_sys.create_flight_seat_report(flight_no)
    return {"income": income, "occupancy": seats}


@mcp.tool()
def admin_create_airplane(model: str, no: str, economy_seat: int, business_seat: int):
    """
    สร้างเครื่องบินลำใหม่ (Airplane) และลงทะเบียนเข้าสู่ระบบ
    - model: ชื่อรุ่นเครื่องบิน (เช่น 'Airbus A350-800')
    - no: เลขทะเบียนเครื่องบิน (Registration number เช่น 'AB350-8')
    - economy_seat: จำนวนที่นั่งชั้นประหยัด
    - business_seat: จำนวนที่นั่งชั้นธุรกิจ
    ใช้เครื่องมือนี้เมื่อต้องการเพิ่มเครื่องบินใหม่เข้าระบบก่อนนำไปกำหนดในเที่ยวบิน
    """
    airplane = Airplane(model, no, economy_seat, business_seat)
    airline_sys.add_airplane(airplane)
    return airplane.get_data()


@mcp.tool()
def user_read_inbox(passenger_id: str):
    """
    ตรวจสอบกล่องข้อความของผู้โดยสาร
    - passenger_id: รหัสผู้โดยสารที่ต้องการตรวจสอบ
    ใช้เครื่องมือนี้เพื่ออ่านประกาศ แจ้งเตือนสถานะเที่ยวบิน หรือแจ้งเตือนการคืนเงิน
    """
    u = airline_sys.search_passenger_by_id(passenger_id)  
    return {"notifications": u.notification_list} if u.notification_list else "Inbox Empty." 


@mcp.tool()
def user_show_all_flight_instance():
    """
    แสดงตารางเที่ยวบิน (Flight Instances) ทั้งหมดในระบบ
    ไม่มีตัวแปรที่ต้องระบุ
    ใช้เครื่องมือนี้เพื่อดูภาพรวมของเที่ยวบินทั้งหมด เวลาเดินทาง และระยะเวลาบิน
    """
    data = airline_sys.show_flight_instance()
    return data


@mcp.tool()
def admin_edit_flight(flight_no: str, old_depart_time: str, depart_time: str, arrive_time: str):
    """
    แก้ไขเวลาเดินทางของเที่ยวบินที่มีอยู่ในระบบ
    - flight_no: รหัสเที่ยวบินที่ต้องการแก้ไข
    - old_depart_time: เวลาออกเดินทางเดิมที่ต้องการเปลี่ยน (ใช้เพื่อระบุตัวเที่ยวบิน)
    - depart_time: เวลาออกเดินทางใหม่ รูปแบบ 'DD-MM-YYYY HH:MM'
    - arrive_time: เวลาถึงปลายทางใหม่ รูปแบบ 'DD-MM-YYYY HH:MM'
    ใช้เครื่องมือนี้เมื่อต้องการเลื่อนเวลาบิน (Reschedule) หรือปรับตารางเวลาใหม่
    """
    instance = airline_sys.update_flight(flight_no, old_depart_time, depart_time, arrive_time)
    return {"Info": instance.get_flight_instance_data()}


@mcp.tool()
def user_order_food(passenger_id: str, pnr: str, food_name: str, quantity: int, payment_type: str, pin: str):
    """
    สั่งซื้ออาหารล่วงหน้าสำหรับผู้โดยสารในเที่ยวบิน
    - passenger_id: รหัสผู้โดยสารที่ทำการสั่งอาหาร
    - pnr: รหัสการจอง (PNR)
    - food_name: ชื่ออาหารที่ต้องการสั่งซื้อ (เช่น 'Premium Steak')
    - quantity: จำนวนอาหารที่ต้องการสั่ง 
    - payment_type: วิธีการชำระเงิน (เช่น 'PayByCard' หรือ 'PayByPoint')
    - pin: รหัส PIN ยืนยันการชำระเงิน
    ใช้เครื่องมือนี้เพื่อให้ผู้โดยสารซื้ออาหารเพิ่มหลังจากเช็กอินแล้ว
    """
    msg = airline_sys.buy_food(passenger_id, pnr, food_name, quantity, payment_type, pin)
    return msg

if __name__ == "__main__":
    mcp.run()