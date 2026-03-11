import unittest
from datetime import datetime, timedelta
from fastapi import HTTPException

# สมมติว่าไฟล์โค้ดหลักของคุณชื่อ main.py ให้ import คลาสทั้งหมดมาใช้งาน
# หากไฟล์ชื่ออื่น ให้เปลี่ยนจาก main เป็นชื่อไฟล์นั้นครับ
from _10Airline_system import (
    Airline, Airplane, Flight, FlightInstance, FlightFood,
    Card, Passenger, Guest, Member, Silver, Gold, Platinum,
    Booking, BookingStatus, PaymentStatus, FlightStatus,
    Economy, Business, Ticket
)

class TestAirlineSystem(unittest.TestCase):

    def setUp(self):
        # รีเซ็ต ID ผู้โดยสารก่อนเทสทุกครั้ง เพื่อป้องกันเลขรันมั่ว
        Passenger.id = 1 
        
        # 1. สร้างสายการบิน
        self.airline = Airline("Thai Airways")
        
        # 2. สร้างเครื่องบิน (Eco 10 ที่, Bus 5 ที่)
        self.airplane = Airplane("Boeing 777", "B777-123", 10, 5)
        self.airline.add_airplane(self.airplane)
        
        # 3. สร้างเที่ยวบิน (Blueprint)
        self.airline.create_flight("TG123", "BKK", "CNX")
        
        # 4. **เพิ่มอาหารเข้าระบบก่อน** self.airline.create_flightfood("Pad Thai", 150.0)
        self.airline.create_flightfood("Water", 50.0)
        self.airline.create_flightfood("Sandwich", 100.0) # แอดให้ครบ 3 อย่างไปเลย
        
        # 5. สร้างรอบบิน (พอสร้างปุ๊บ ระบบจะสุ่มดึงอาหารจากข้อ 4 มาใส่ได้พอดี)
        self.depart_time = (datetime.now() + timedelta(days=3)).strftime('%d-%m-%Y %H:%M')
        self.arrive_time = (datetime.now() + timedelta(days=3, hours=2)).strftime('%d-%m-%Y %H:%M')
        self.airline.create_flight_instance("TG123", "B777-123", self.depart_time, self.arrive_time)

    # ==========================================
    # 1. Test Core Components (Card & Passenger)
    # ==========================================
    def test_card_creation_and_validation(self):
        # Case: สร้างบัตรปกติ
        card = Card("123456", 1000.0)
        self.assertEqual(card.pin, "123456")
        self.assertEqual(card.money, 1000.0)
        
        # Case: Error พินไม่ครบ 6 หลัก
        with self.assertRaises(HTTPException):
            Card("1234", 1000.0)
            
        # Case: Error เงินติดลบ
        with self.assertRaises(HTTPException):
            Card("123456", -500.0)

    def test_passenger_creation_and_point_system(self):
        # Case: สร้างสมาชิกปกติ
        member = Member("John Doe", "john@email.com")
        self.assertEqual(member.name, "John Doe")
        self.assertEqual(member.point, 0)
        
        # Case: เพิ่ม Point
        member.change_point(100)
        self.assertEqual(member.point, 100)
        
        # Case: Error Point ติดลบ
        with self.assertRaises(HTTPException):
            member.change_point(-200)
            
        # Case: Error ชื่อหรืออีเมลว่าง
        with self.assertRaises(HTTPException):
            Guest("   ", "email@email.com")

    # ==========================================
    # 2. Test Account Creation (Airline Service)
    # ==========================================
    def test_create_account_success(self):
        # Case: สร้างแอคเคาท์ Silver สำเร็จและหักค่าธรรมเนียมถูก
        passenger = self.airline.create_account("Alice", "alice@email.com", "111111", 5000.0, "Silver")
        self.assertIsInstance(passenger, Silver)
        # Silver ค่าธรรมเนียม 200 เงินต้องเหลือ 4800
        self.assertEqual(passenger.card.money, 4800.0)
        # เช็คว่าได้ Point จากการจ่ายเงินด้วย (4800 // 25 = 192, แต่จ่ายไป 200 // 25 = 8 points)
        self.assertEqual(passenger.point, 8)

    def test_create_account_insufficient_funds(self):
        # Case: เงินไม่พอจ่ายค่าธรรมเนียม (Platinum fee = 500)
        with self.assertRaises(HTTPException):
            self.airline.create_account("Bob", "bob@email.com", "222222", 100.0, "Platinum")

    def test_create_account_invalid_tier(self):
        # Case: ใส่ชื่อคลาส (Tier) ผิด
        with self.assertRaises(HTTPException):
            self.airline.create_account("Charlie", "char@email.com", "333333", 1000.0, "Diamond")

    # ==========================================
    # 3. Test Booking Workflow
    # ==========================================
    def test_booking_and_payment_success(self):
        passenger = self.airline.create_account("Dave", "dave@email.com", "123456", 50000.0, "Guest")
        
        # จองที่นั่ง Economy 2 ที่
        booking = self.airline.booking(passenger.passenger_id, "TG123", self.depart_time, "Economy", 2)
        
        self.assertEqual(booking.booking_status, BookingStatus.PENDING)
        self.assertEqual(booking.seat_amount, 2)
        
        # จ่ายเงิน
        self.airline.pay_book(passenger.passenger_id, booking.pnr, "PayByCard", "123456")
        
        self.assertEqual(booking.booking_status, BookingStatus.CONFIRMED)
        self.assertEqual(booking.payment_status, PaymentStatus.PAID)
        
        # โควต้าที่นั่งบนเครื่องต้องลดลงไป 2
        f_instance = self.airline.find_flight_instance("TG123", datetime.strptime(self.depart_time, '%d-%m-%Y %H:%M'))
        self.assertEqual(f_instance.economy_booking_quota, 8) # จาก 10 เหลือ 8

    def test_booking_invalid_seat_amount(self):
        passenger = self.airline.create_account("Eve", "eve@email.com", "123456", 50000.0, "Guest")
        
        # Case: สั่งจองด้วยจำนวนติดลบหรือ 0
        with self.assertRaises(HTTPException):
            self.airline.booking(passenger.passenger_id, "TG123", self.depart_time, "Economy", -1)
            
        # Case: สั่งจองเกินโควต้าที่มี (มี 10 สั่ง 15)
        with self.assertRaises(HTTPException):
            self.airline.booking(passenger.passenger_id, "TG123", self.depart_time, "Economy", 15)

    def test_payment_wrong_pin_or_not_enough_money(self):
        passenger = self.airline.create_account("Frank", "frank@email.com", "123456", 500.0, "Guest")
        booking = self.airline.booking(passenger.passenger_id, "TG123", self.depart_time, "Economy", 1) # ราคาตั๋ว 10000 + 300
        
        # Case: พินผิด
        with self.assertRaises(HTTPException):
            self.airline.pay_book(passenger.passenger_id, booking.pnr, "PayByCard", "999999")
            
        # Case: เงินในบัตรไม่พอ (มี 500 แต่ตั๋วหมื่นกว่า)
        with self.assertRaises(HTTPException):
            self.airline.pay_book(passenger.passenger_id, booking.pnr, "PayByCard", "123456")

    # ==========================================
    # 4. Test Check-in and Seat Selection
    # ==========================================
    def test_check_in_and_choose_seat(self):
        # Setup: จองและจ่ายเงิน
        passenger = self.airline.create_account("Grace", "grace@email.com", "123456", 20000.0, "Guest")
        booking = self.airline.booking(passenger.passenger_id, "TG123", self.depart_time, "Economy", 1)
        self.airline.pay_book(passenger.passenger_id, booking.pnr, "PayByCard", "123456")
        
        # เตรียมเปิด Check-in ของเที่ยวบิน
        f_instance = booking.flight_instance
        f_instance.open_check_in()
        
        # ทำการ Check-in
        available_seats = self.airline.check_in_passenger(passenger.passenger_id, booking.pnr)
        self.assertTrue(len(available_seats) > 0)
        
        # เลือกที่นั่ง
        tickets = self.airline.choose_seat(passenger.passenger_id, booking.pnr, "E01")
        self.assertEqual(len(tickets), 1)
        self.assertEqual(tickets[0].seat.seat.seat_no, "E01")
        self.assertEqual(booking.booking_status, BookingStatus.COMPLETED)

    def test_choose_seat_duplicate_or_invalid(self):
        # Setup
        passenger = self.airline.create_account("Hank", "hank@email.com", "123456", 50000.0, "Guest")
        booking = self.airline.booking(passenger.passenger_id, "TG123", self.depart_time, "Economy", 2)
        self.airline.pay_book(passenger.passenger_id, booking.pnr, "PayByCard", "123456")
        booking.flight_instance.open_check_in()
        self.airline.check_in_passenger(passenger.passenger_id, booking.pnr)
        
        # Case: เลือกที่นั่งซ้ำกันเอง
        with self.assertRaises(HTTPException):
            self.airline.choose_seat(passenger.passenger_id, booking.pnr, "E01, E01")
            
        # Case: ใส่ฟอร์แมตผิด (ใส่ String มั่ว)
        with self.assertRaises(HTTPException):
            self.airline.choose_seat(passenger.passenger_id, booking.pnr, "I_WANT_WINDOW_SEAT")
            
        # Case: จำนวนที่นั่งที่เลือก ไม่ตรงกับที่จองไว้ (จอง 2 เลือก 1)
        with self.assertRaises(HTTPException):
            self.airline.choose_seat(passenger.passenger_id, booking.pnr, "E01")

    # ==========================================
    # 5. Test In-Flight Services (Food & Luggage)
    # ==========================================
    def test_buy_food_and_load_luggage(self):
        # Setup: เดินทางจนถึงสเตปเลือกที่นั่งเสร็จสมบูรณ์
        passenger = self.airline.create_account("Ivy", "ivy@email.com", "123456", 50000.0, "Silver") # Silver ได้น้ำหนัก +5kg
        booking = self.airline.booking(passenger.passenger_id, "TG123", self.depart_time, "Economy", 1)
        self.airline.pay_book(passenger.passenger_id, booking.pnr, "PayByCard", "123456")
        booking.flight_instance.open_check_in()
        self.airline.check_in_passenger(passenger.passenger_id, booking.pnr)
        self.airline.choose_seat(passenger.passenger_id, booking.pnr, "E05")
        
        food_on_flight = booking.flight_instance.food_list[0].name
        
        # Case: สั่งอาหารสำเร็จ
        response = self.airline.buy_food(passenger.passenger_id, booking.pnr, food_on_flight, 2, "PayByCard", "123456")
        self.assertEqual(response, "Order Food Success")
        
        # Case: โหลดกระเป๋าน้ำหนักเกิน (Economy=15 + Silver=5 = ลิมิต 20)
        passenger.set_weight(30.0) # น้ำหนักเกินมา 10 โล
        luggage_res = self.airline.load_luggage(booking.pnr)
        
        # ตรวจสอบว่ามีการคิดเงินเพิ่ม และมีบันทึกใน Transaction
        self.assertIn("Extra Fee", luggage_res["message"])
        
        # [แก้ตรงนี้] เปลี่ยนจาก 25.0 เป็น 20.0 ตาม Logic ที่ถูกต้องของคุณ
        self.assertEqual(luggage_res["weight_limit"], 20.0)

    # ==========================================
    # 6. Test Refund and Blacklist
    # ==========================================
    def test_refund_workflow(self):
        passenger = self.airline.create_account("Jack", "jack@email.com", "123456", 20000.0, "Guest")
        booking = self.airline.booking(passenger.passenger_id, "TG123", self.depart_time, "Economy", 1)
        self.airline.pay_book(passenger.passenger_id, booking.pnr, "PayByCard", "123456")
        
        old_balance = passenger.card.money
        
        # ขอคืนเงิน (เวลาเหลือเกิน 24 ชม. สามารถคืนได้)
        self.airline.request_refund(booking.pnr, passenger.passenger_id)
        
        # ตรวจสอบสถานะและยอดเงิน
        self.assertEqual(booking.booking_status, BookingStatus.CANCELED)
        self.assertEqual(booking.payment_status, PaymentStatus.REFUNDED)
        self.assertTrue(passenger.card.money > old_balance) # เงินต้องเพิ่มขึ้น
        self.assertEqual(passenger.refunded_total, 1)

    def test_refund_blacklist_limit(self):
        passenger = self.airline.create_account("Ken", "ken@email.com", "123456", 90000.0, "Guest")
        
        # ทำการจองและ Refund รัวๆ 3 ครั้ง
        for i in range(3):
            booking = self.airline.booking(passenger.passenger_id, "TG123", self.depart_time, "Economy", 1)
            self.airline.pay_book(passenger.passenger_id, booking.pnr, "PayByCard", "123456")
            self.airline.request_refund(booking.pnr, passenger.passenger_id)
            
        # ตรวจสอบว่าถูกแบนหรือยัง
        self.assertTrue(passenger.is_blacklisted)
        
        # ถ้าพยายามจะจองครั้งที่ 4 ต้อง Error
        with self.assertRaises(HTTPException):
            self.airline.booking(passenger.passenger_id, "TG123", self.depart_time, "Economy", 1)


if __name__ == '__main__':
    # รันโค้ดทดสอบทั้งหมด
    unittest.main(verbosity=2)