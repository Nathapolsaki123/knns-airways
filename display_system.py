from datetime import datetime, timedelta

# เปลี่ยน 'main' เป็นชื่อไฟล์โค้ดหลักของคุณ
from _10Airline_system import (
    Airline, Airplane, Flight, FlightInstance, FlightFood,
    Card, Passenger, Guest, Member, Silver, Gold, Platinum,
    Booking, BookingStatus, PaymentStatus, FlightStatus,
    Seat, Economy, Business, FlightSeat, Ticket,
    Transaction, SubTransaction, Payment, PayByCard, PayByPoint
)

def simulate_absolutely_everything() -> Airline:
    print("="*60)
    print("🚀 [1] INITIALIZING AIRLINE & AIRPLANE")
    print("="*60)
    airline = Airline("KNNS Global Airways")
    
    # สร้างเครื่องบินที่มีที่นั่งทั้ง Economy และ Business
    airplane = Airplane(model_number="Airbus A380", registration_no="HS-MAX", eco=10, bus=4)
    airline.add_airplane(airplane)
    print(f"✔️ สร้าง Airplane: {airplane.model_number} สำเร็จ (Eco: {airplane.economy_seat_amount}, Bus: {airplane.business_seat_amount})")

    print("\n" + "="*60)
    print("🍔 [2] ADDING FLIGHT FOOD")
    print("="*60)
    airline.create_flightfood("Premium Steak", 350.0)
    airline.create_flightfood("Pad Thai", 150.0)
    airline.create_flightfood("Champagne", 500.0)
    print(f"✔️ เพิ่มเมนูอาหารเข้าระบบแล้ว {len(airline._Airline__flight_food_list)} รายการ")

    print("\n" + "="*60)
    print("🛫 [3] SCHEDULING FLIGHT & FLIGHT INSTANCE")
    print("="*60)
    airline.create_flight("KN999", "Bangkok (BKK)", "Tokyo (HND)")
    
    depart_time = (datetime.now() + timedelta(days=5)).strftime('%d-%m-%Y %H:%M')
    arrive_time = (datetime.now() + timedelta(days=5, hours=6)).strftime('%d-%m-%Y %H:%M')
    airline.create_flight_instance("KN999", "HS-MAX", depart_time, arrive_time)
    
    # ใช้งานการแก้ไขเวลา (edit_time)
    new_arrive = (datetime.now() + timedelta(days=5, hours=5)).strftime('%d-%m-%Y %H:%M')
    airline.update_flight("KN999", depart_time, depart_time, new_arrive)
    print("✔️ สร้าง Flight และ FlightInstance สำเร็จ พร้อมสุ่มเมนูอาหารขึ้นเครื่องเรียบร้อย")

    print("\n" + "="*60)
    print("👥 [4] REGISTERING ALL PASSENGER TIERS (GUEST, SILVER, GOLD, PLATINUM)")
    print("="*60)
    # รันครบทุก Tier เพื่อโชว์ Polymorphism
    p_guest = airline.create_account("Nath Guest", "guest@mail.com", "111111", 500000.0, "Guest")
    p_silver = airline.create_account("Nath Silver", "silv@mail.com", "222222", 500000.0, "Silver") # หัก 200
    p_gold = airline.create_account("Nath Gold", "gold@mail.com", "333333", 500000.0, "Gold") # หัก 300
    p_plat = airline.create_account("Nath Plat", "plat@mail.com", "444444", 500000.0, "Platinum") # หัก 500
    print("✔️ สมัครสมาชิกครบทุกระดับชั้น พร้อมหักค่าธรรมเนียมและคำนวณ Point อัตโนมัติ")

    print("\n" + "="*60)
    print("🎫 [5] BOOKING & PAYMENT PROCESS")
    print("="*60)
    # 5.1 Guest จองและจ่ายผ่านบัตร (PayByCard)
    book_guest = airline.booking(p_guest.passenger_id, "KN999", depart_time, "Economy", 1)
    airline.pay_book(p_guest.passenger_id, book_guest.pnr, "PayByCard", "111111")
    
    # 5.2 Platinum จองและจ่ายผ่านบัตร (จะได้พ้อยท์เยอะมาก เอาไปเทส PayByPoint)
    book_plat = airline.booking(p_plat.passenger_id, "KN999", depart_time, "Business", 1)
    airline.pay_book(p_plat.passenger_id, book_plat.pnr, "PayByCard", "444444")
    
    # 5.3 Silver ทำการจอง แต่เปลี่ยนใจ กดยกเลิกก่อนจ่ายเงิน! (Cancel Booking)
    book_silver = airline.booking(p_silver.passenger_id, "KN999", depart_time, "Economy", 1)
    airline.cancel_booking(p_silver.passenger_id, book_silver.pnr)
    
    # 5.4 Gold ทำการจองและจ่ายเงิน แต่ไปขอคืนเงินทีหลัง! (Refund)
    book_gold = airline.booking(p_gold.passenger_id, "KN999", depart_time, "Economy", 1)
    airline.pay_book(p_gold.passenger_id, book_gold.pnr, "PayByCard", "333333")
    airline.request_refund(book_gold.pnr, p_gold.passenger_id)
    
    print("✔️ ทดสอบระบบจอง, ยกเลิก (Cancel), และขอคืนเงิน (Refund) สำเร็จ")

    print("\n" + "="*60)
    print("✅ [6] CHECK-IN AND SEAT SELECTION")
    print("="*60)
    f_instance = book_guest.flight_instance
    f_instance.open_check_in() # เปลี่ยน FlightStatus เป็น CHECKINOPEN
    
    # Guest เช็คอินและเลือกที่นั่ง
    airline.check_in_passenger(p_guest.passenger_id, book_guest.pnr)
    airline.choose_seat(p_guest.passenger_id, book_guest.pnr, "E01")
    
    # Platinum เช็คอินและเลือกที่นั่ง
    airline.check_in_passenger(p_plat.passenger_id, book_plat.pnr)
    airline.choose_seat(p_plat.passenger_id, book_plat.pnr, "B01")
    
    print("✔️ เปลี่ยนสถานะไฟลท์ เปิดเช็คอิน และออกตั๋ว (Ticket) สำเร็จ")

    print("\n" + "="*60)
    print("🛍️ [7] IN-FLIGHT SERVICES (FOOD & LUGGAGE)")
    print("="*60)
    food_on_flight = f_instance.food_list[0].name
    
    # Guest ซื้ออาหาร จ่ายด้วยบัตร (PayByCard)
    airline.buy_food(p_guest.passenger_id, book_guest.pnr, food_on_flight, 1, "PayByCard", "111111")
    
    # Platinum ซื้ออาหาร **จ่ายด้วยพ้อยท์ (PayByPoint)**
    airline.buy_food(p_plat.passenger_id, book_plat.pnr, food_on_flight, 1, "PayByPoint", None)
    
    # โหลดกระเป๋าของ Guest (น้ำหนักเกิน Limit ของ Eco แน่นอน)
    p_guest.set_weight(25.0) 
    airline.load_luggage(book_guest.pnr)
    print("✔️ สั่งอาหารด้วย Card / Point และโหลดสัมภาระสำเร็จ (คำนวณส่วนลดตาม Tier)")
    
    return airline


def display_comprehensive_report(airline: Airline):
    print("\n\n" + "#"*80)
    print(f" 📊 COMPREHENSIVE SYSTEM REPORT: {airline.airline_name} ")
    print("#"*80)

    # ========================================================
    print("\n[✈️ 1. FLEET & SEAT CLASSES ]")
    for plane in airline._Airline__airplane_list:
        print(f"  Airplane: {plane.model_number} [{plane.registration_no}]")
        eco_seat = next((s for s in plane.seat_layout_list if isinstance(s, Economy)), None)
        bus_seat = next((s for s in plane.seat_layout_list if isinstance(s, Business)), None)
        
        print(f"   > Class {type(eco_seat).__name__} | Price: {eco_seat.SEAT_PRICE} | Luggage Limit: {eco_seat.luggage_limit}kg")
        print(f"   > Class {type(bus_seat).__name__} | Price: {bus_seat.SEAT_PRICE} | Luggage Limit: {bus_seat.luggage_limit}kg")

    # ========================================================
    print("\n[🛫 2. FLIGHT INSTANCES & ENUMS ]")
    for flight in airline._Airline__flight_list:
        print(f"  Blueprint: Flight {flight.flight_no} ({flight.origin} -> {flight.destination})")
        for inst in flight.flight_instance_list:
            print(f"   > Instance Status: {inst.status.name} (Enum Value: {inst.status.value})")
            print(f"   > Time: {inst.departure_time} to {inst.arrival_time} (Duration: {inst.calculate_flight_time()})")
            print(f"   > Menu Available: {[food.name for food in inst.food_list]}")
            print(f"   > Quota Left: Economy={inst.economy_booking_quota}, Business={inst.business_booking_quota}")
            print(f"   > Total Accumulated Income: {inst.total_income:,.2f} THB")

    # ========================================================
    print("\n[👥 3. PASSENGERS, CARDS & MEMBERSHIP TIERS ]")
    for p in airline._Airline__passenger_list:
        print(f"  👤 Passenger: {p.name} (ID: {p.passenger_id}) | Tier Class: {type(p).__name__}")
        print(f"     > Card: PIN {p.card.pin} | Balance: {p.card.money:,.2f} THB")
        
        if isinstance(p, Member):
            print(f"     > Accumulated Points: {p.point} pts")
            print(f"     > Perks: {p.DISCOUNT*100}% Discount | +{p.EXTRA_WEIGHT}kg Luggage")

        for book in p.booking_list:
            print(f"     ---------------------------------------------")
            print(f"     🎟️ Booking PNR: {book.pnr} | Fare: {book.fare:,.2f} THB")
            print(f"     > Status: {book.booking_status.name} | Payment: {book.payment_status.name}")
            
            # เจาะลึก Transactions & SubTransactions
            if book.transaction:
                print(f"     > Main Transaction: {book.transaction.amount:,.2f} THB (Method: {book.transaction.payment_type})")
                for sub in book.transaction.sub_transaction_list:
                    print(f"       - SubTransaction: {sub.name} | {sub.amount:,.2f} THB | Method: {type(Payment.get_payment_type(sub.payment_type)).__name__}")
            
            # เจาะลึก Ticket & FlightSeat & FlightFood
            for tk in book._Booking__ticket_list:
                print(f"     > Issued Ticket:")
                print(f"       {tk}")  # เรียกใช้ __str__ ของ Ticket
                if tk.seat.food_list:
                    print(f"       * Ordered Food on Seat: {[f.name for f in tk.seat.food_list]}")

    # ========================================================
    print("\n[📑 4. OFFICIAL GENERATED REPORTS ]")
    print("  --- 4.1 Income Report ---")
    income_reports = airline.create_income_report("KN999")
    for r in income_reports:
        print(f"   {r}")
        
    print("\n  --- 4.2 Seat Occupancy Report ---")
    seat_reports = airline.create_flight_seat_report("KN999")
    for r in seat_reports:
        print(f"   {r}")

    print("\n" + "#"*80)


if __name__ == "__main__":
    # 1. รันเหตุการณ์เพื่อดึงทุก Class มาใช้งานจริง
    my_airline = simulate_absolutely_everything()
    
    # 2. ปริ้นท์เพื่อเจาะลึกเข้าไปดูทุกซอกทุกมุมของ Object (ใช้ type().__name__ เพื่อพิสูจน์)
    display_comprehensive_report(my_airline)