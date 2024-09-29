from app import create_app
from app.models import db, PricingOption, Date, AvailableTimeSlot
from datetime import datetime, timedelta

# Create the app context for the mock data script
app = create_app()
app.app_context().push()

# Drop all existing tables and recreate them
db.drop_all()
db.create_all()

# Sample mock data for pricing options
pricing_options = [
    PricingOption(name="Basic Package", description="1-hour photo shoot, 20 edited photos", hold_price=10.00, price=100.00),
    PricingOption(name="Standard Package", description="2-hour photo shoot, 30 edited photos", hold_price=20.00, price=180.00),
    PricingOption(name="Premium Package", description="4-hour photo shoot, 45 edited photos", hold_price=30.00, price=320.00),
]

# Sample mock data for dates and available time slots
today = datetime.today()

# Create dates (Date table)
dates = [
    Date(date=today),
    Date(date=today + timedelta(days=1)),
    Date(date=today + timedelta(days=2)),
    Date(date=today + timedelta(days=3))
]

# Create available time slots (AvailableTimeSlot table)
available_time_slots = [
    # Day 1
    AvailableTimeSlot(date_id=1, timeslot="morning", status="available"),
    AvailableTimeSlot(date_id=1, timeslot="evening", status="available"),

    # Day 2
    AvailableTimeSlot(date_id=2, timeslot="morning", status="available"),
    AvailableTimeSlot(date_id=2, timeslot="afternoon", status="available"),

    # Day 3
    AvailableTimeSlot(date_id=3, timeslot="afternoon", status="available"),
    AvailableTimeSlot(date_id=3, timeslot="evening", status="available"),

    # Day 4
    AvailableTimeSlot(date_id=4, timeslot="morning", status="available"),
    AvailableTimeSlot(date_id=4, timeslot="afternoon", status="available"),
    AvailableTimeSlot(date_id=4, timeslot="evening", status="available"),
]

# Insert mock data into the database
db.session.add_all(pricing_options)
db.session.add_all(dates)
db.session.add_all(available_time_slots)
db.session.commit()

print("Mock data inserted successfully.")
