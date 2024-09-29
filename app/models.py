from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime

db: SQLAlchemy = SQLAlchemy()
migrate = Migrate()

class PricingOption(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(255))
    hold_price = db.Column(db.Float)
    price = db.Column(db.Float, nullable=False)

    def __repr__(self):
        return f'<PricingOption {self.name}: ${self.price}>'

class Date(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False, unique=True)  # Ensure uniqueness for each date

    def __repr__(self):
        return f'<Date {self.date}>'

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ip = db.Column(db.String(30), nullable=True)
    held_timeslot = db.Column(db.Integer, db.ForeignKey('available_time_slot.id'), nullable=True)
    hold_until = db.Column(db.DateTime, nullable=True)  # Optional expiration for held timeslots
    held_price = db.Column(db.Integer, db.ForeignKey('pricing_option.id'), nullable=True)
    held_message = db.Column(db.String(255), nullable=True)

    held_timeslot_rel = db.relationship('AvailableTimeSlot', backref=db.backref('users', lazy=True))
    held_price_rel = db.relationship('PricingOption', backref=db.backref('users', lazy=True))

    def __init__(self, ip):
        self.ip = ip



class AvailableTimeSlot(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date_id = db.Column(db.Integer, db.ForeignKey('date.id'), nullable=False)  # Foreign key to Date table
    timeslot = db.Column(db.String(10), nullable=False)  # morning, afternoon, evening
    status = db.Column(db.String(20), nullable=False, default='available')  # available, held, etc.

    date = db.relationship('Date', backref=db.backref('timeslots', lazy=True))

    def to_dict(self):
        return self.id
