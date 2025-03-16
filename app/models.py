from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

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
        if not self.date:
            return 'Invalid Date'
        return self.date.strftime('%b. %d, %Y')  # Example: Dec. 10, 2020


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), nullable=False, unique=True)  # Email is required and unique
    held_timeslot = db.Column(db.Integer, db.ForeignKey('available_time_slot.id'), nullable=True)
    hold_until = db.Column(db.DateTime, nullable=True)
    held_price = db.Column(db.Integer, db.ForeignKey('pricing_option.id'), nullable=True)

    held_timeslot_rel = db.relationship('AvailableTimeSlot', backref=db.backref('users', lazy=True))
    held_price_rel = db.relationship('PricingOption', backref=db.backref('users', lazy=True))

    def __repr__(self):
        return f'<User {self.email}>'




class AvailableTimeSlot(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date_id = db.Column(db.Integer, db.ForeignKey('date.id'), nullable=False)  # Foreign key to Date table
    timeslot = db.Column(db.String(10), nullable=False)  # morning, afternoon, evening
    status = db.Column(db.String(20), nullable=False, default='available')  # available, held, etc.

    date = db.relationship('Date', backref=db.backref('timeslots', lazy=True))

    def to_dict(self):
        return self.id
    
    def __repr__(self):
        # Safely fetch the date if it's loaded, otherwise fetch from the db
        timeslot_date = Date.query.get(self.date_id).date

        return f'the {self.timeslot} of {timeslot_date}'

