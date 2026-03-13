# ---------------------------
# Put this test harness at the bottom of your file
# ---------------------------

from fastapi import HTTPException
from datetime import datetime, timedelta
from _10Airline_system import*

def sprint(title: str):
    print("\n" + "="*10 + f" {title} " + "="*10)

if __name__ == "__main__":
    sprint("SETUP AIRLINE & CORE RESOURCES")
    try:
        airline = Airline("TestAir")
        # Add some flight food catalog
        airline.create_flightfood("Chicken Rice", 50.0)
        airline.create_flightfood("Pad Thai", 60.0)
        airline.create_flightfood("Coffee", 30.0)

        # Create an airplane and add to airline
        plane = Airplane("A320", "REG001", eco=12, bus=4)
        airline.add_airplane(plane)

        # Create flight and flight instance (departure in 2 days)
        airline.create_flight("TA123", "BKK", "HKT")
        depart_dt = (datetime.now() + timedelta(days=2)).strftime('%d-%m-%Y %H:%M')
        arrive_dt = (datetime.now() + timedelta(days=2, hours=3)).strftime('%d-%m-%Y %H:%M')
        airline.create_flight_instance("TA123", "REG001", depart_dt, arrive_dt)

        # Create a second flight instance departing in 6 hours (for non-refundable test)
        airline.create_flight("TA456", "BKK", "DMK")
        depart_soon = (datetime.now() + timedelta(hours=6)).strftime('%d-%m-%Y %H:%M')
        arrive_soon = (datetime.now() + timedelta(hours=8)).strftime('%d-%m-%Y %H:%M')
        airline.create_flight_instance("TA456", "REG001", depart_soon, arrive_soon)
        print("Setup done.")
    except HTTPException as e:
        print("Setup error:", e.detail)

    # ---------------------------
    # Create accounts (Guest, Silver, Gold, Platinum)
    # ---------------------------
    sprint("CREATE ACCOUNTS")
    try:
        guest = airline.create_account("Guest One", "guest@example.com", "111111", 100.0, "Guest")
        silver = airline.create_account("Silver One", "silver@example.com", "222222", 500.0, "Silver")
        gold = airline.create_account("Gold One", "gold@example.com", "333333", 2000.0, "Gold")
        platinum = airline.create_account("Platinum One", "plat@example.com", "444444", 1000.0, "Platinum")
        print("Passengers created:", guest.passenger_id, silver.passenger_id, gold.passenger_id, platinum.passenger_id)
    except HTTPException as e:
        print("Create account error:", e.detail)

    # Add extra points to gold for PayByPoint test
    try:
        if isinstance(gold, Member):
            gold.change_point(20000)  # give many points for testing PayByPoint
            print("Gold points set to:", gold.point)
    except HTTPException as e:
        print("Setting points error:", e.detail)

    # ---------------------------
    # BOOKING FLOW: create bookings for each passenger
    # ---------------------------
    sprint("BOOKING / PAY / CHECK-IN / CHOOSE SEAT")
    bookings = {}
    try:
        # get departure datetime objects for find_flight_instance
        dt_main = datetime.strptime(depart_dt, '%d-%m-%Y %H:%M')
        dt_soon = datetime.strptime(depart_soon, '%d-%m-%Y %H:%M')

        # Book for guest (pay by card)
        b_guest = airline.booking(guest.passenger_id, "TA123", depart_dt, "Economy", 1)
        bookings['guest'] = b_guest
        # Book for silver (pay by card)
        b_silver = airline.booking(silver.passenger_id, "TA123", depart_dt, "Business", 1)
        bookings['silver'] = b_silver
        # Book for gold (we'll pay by points)
        b_gold = airline.booking(gold.passenger_id, "TA123", depart_dt, "Economy", 1)
        bookings['gold'] = b_gold
        # Book for platinum on the soon flight (to test non-refundable)
        b_plat_soon = airline.booking(platinum.passenger_id, "TA456", depart_soon, "Economy", 1)
        bookings['plat_soon'] = b_plat_soon

        print("Bookings created PNRs:", {k: v.pnr for k, v in bookings.items()})
    except HTTPException as e:
        print("Booking error:", e.detail)

    # Pay bookings
    sprint("PAY BOOKING")
    try:
        # Guest pay by card
        airline.pay_book(guest.passenger_id, bookings['guest'].pnr, "PayByCard", "111111")
        print("Guest paid. Transaction:", bookings['guest'].transaction.get_all_subtransaction())

        # Silver pay by card
        airline.pay_book(silver.passenger_id, bookings['silver'].pnr, "PayByCard", "222222")
        print("Silver paid. Transaction:", bookings['silver'].transaction.get_all_subtransaction())

        # Gold pay by points
        # Ensure gold has enough points (we set above)
        airline.pay_book(gold.passenger_id, bookings['gold'].pnr, "PayByPoint")
        print("Gold paid by points. Transaction:", bookings['gold'].transaction.get_all_subtransaction())

        # Platinum pay by card for soon flight
        airline.pay_book(platinum.passenger_id, bookings['plat_soon'].pnr, "PayByCard", "444444")
        print("Platinum (soon flight) paid.")
    except HTTPException as e:
        print("Pay error:", e.detail)

    # Open check-in for TA123 and check-in passengers
    sprint("OPEN CHECK-IN & CHECK-IN")
    try:
        fl_inst = bookings['guest'].flight_instance
        fl_inst.open_check_in()
        # Check-in guest
        avail_guest = airline.check_in_passenger(guest.passenger_id, bookings['guest'].pnr)
        print("Guest available seats count:", len(avail_guest))
        # Check-in silver
        avail_silver = airline.check_in_passenger(silver.passenger_id, bookings['silver'].pnr)
        print("Silver available seats count:", len(avail_silver))
        # Check-in gold
        avail_gold = airline.check_in_passenger(gold.passenger_id, bookings['gold'].pnr)
        print("Gold available seats count:", len(avail_gold))
    except HTTPException as e:
        print("Check-in error:", e.detail)

    # Choose seats (valid cases)
    sprint("CHOOSE SEAT")
    try:
        # pick first available economy seat for guest and gold
        avail = fl_inst.get_available_seat("Economy")
        seat1 = avail[0].seat_no
        airline.choose_seat(guest.passenger_id, bookings['guest'].pnr, seat1)
        print(f"Guest chose seat {seat1}")

        # for gold choose next seat
        avail = fl_inst.get_available_seat("Economy")
        seat2 = avail[0].seat_no
        airline.choose_seat(gold.passenger_id, bookings['gold'].pnr, seat2)
        print(f"Gold chose seat {seat2}")

        # for silver (business)
        avail_bus = fl_inst.get_available_seat("Business")
        seatb = avail_bus[0].seat_no
        airline.choose_seat(silver.passenger_id, bookings['silver'].pnr, seatb)
        print(f"Silver chose seat {seatb}")
    except HTTPException as e:
        print("Choose seat error:", e.detail)

    # ---------------------------
    # BUY FOOD (should work for COMPLETED bookings)
    # ---------------------------
    sprint("BUY FOOD")
    try:
        # Guest orders Chicken Rice x2 by card
        result = airline.buy_food(guest.passenger_id, bookings['guest'].pnr, "Chicken Rice", 2, "PayByCard", "111111")
        print("Guest buy food result:", result)
        # Silver orders Coffee x1 by card
        result = airline.buy_food(silver.passenger_id, bookings['silver'].pnr, "Coffee", 1, "PayByCard", "222222")
        print("Silver buy food result:", result)
    except HTTPException as e:
        print("Buy food error:", e.detail)

    # ---------------------------
    # LUGGAGE: within limit and extra fee path
    # ---------------------------
    sprint("LUGGAGE")
    try:
        # Guest within limit
        guest.set_weight(10.0)
        res = airline.load_luggage(bookings['guest'].pnr)
        print("Guest luggage load:", res)

        # Now push guest overweight to provoke extra-fee
        guest.set_weight(40.0)  # heavy -> should charge extra
        res = airline.load_luggage(bookings['guest'].pnr)
        print("Guest overweight load result:", res)
    except HTTPException as e:
        print("Luggage error:", e.detail)

    # ---------------------------
    # REFUND: refundable case and non-refundable case
    # ---------------------------
    sprint("REFUND")
    try:
        # Refund gold booking (flight >24h) -> should succeed
        print("Requesting refund for gold PNR:", bookings['gold'].pnr)
        msg = airline.request_refund(bookings['gold'].pnr, gold.passenger_id)
        print("Refund result:", msg)
    except HTTPException as e:
        print("Refund error (gold):", e.detail)

    try:
        # Try refund platinum soon flight (<24h) -> should fail
        print("Requesting refund for plat soon PNR:", bookings['plat_soon'].pnr)
        msg = airline.request_refund(bookings['plat_soon'].pnr, platinum.passenger_id)
        print("Refund result (shouldn't happen):", msg)
    except HTTPException as e:
        print("Refund error (plat soon expected):", e.detail)

    # ---------------------------
    # REPORTS
    # ---------------------------
    sprint("REPORTS")
    try:
        seat_report = airline.create_flight_seat_report("TA123")
        print("Seat report:\n", "\n".join(seat_report))

        income_report = airline.create_income_report("TA123")
        print("Income report:\n", "\n".join(income_report))
    except HTTPException as e:
        print("Report error:", e.detail)

    # ---------------------------
    # UTILITIES & EDGE CASES
    # ---------------------------
    sprint("UTILITIES & EDGE CASES")
    try:
        # parse_seats with invalid/duplicate inputs
        avail_for_parse = fl_inst.get_available_seat("Economy")
        chosen, invalid, duplicates, objs = Airline.parse_seats("E01, E02, XX, E01", avail_for_parse)
        print("parse_seats -> chosen:", chosen, "invalid:", invalid, "duplicates:", duplicates)
    except HTTPException as e:
        print("Parse seats error:", e.detail)

    try:
        # get_data_by_pnr works
        p, b = airline.get_data_by_pnr(bookings['guest'].pnr)
        print("get_data_by_pnr:", p.name, b.pnr)
    except HTTPException as e:
        print("get_data_by_pnr error:", e.detail)

    try:
        # get_weight_limit
        wlim = airline.get_weight_limit(bookings['guest'].pnr)
        print("Weight limit for guest:", wlim)
    except HTTPException as e:
        print("get_weight_limit error:", e.detail)

    try:
        # get_account for a non-existing tier -> should raise
        try:
            airline.get_account("Diamond")
        except HTTPException as ex:
            print("get_account(Diamond) expected error:", ex.detail)
    except Exception as e:
        print("Unexpected get_account flow error:", str(e))

    sprint("ALL TESTS DONE")