from datetime import datetime, timedelta
from flask import Blueprint, render_template, jsonify, request, redirect, url_for, current_app
from app.models import PricingOption, Date, AvailableTimeSlot, User, db
import os
import json

main = Blueprint('main', __name__)


@main.route('/')
def index():
    return render_template('index.html')


@main.route('/pricing')
def pricing():
    return render_template('pricing.html')


@main.route('/payment')
def payment():
    user: User = get_or_create_user(request.remote_addr)

    # Check if the user has a held timeslot

    if user.held_timeslot:
        # User has a held timeslot, render the payment page
        return render_template('payment.html')
    else:
        # User does not have a held timeslot, redirect them
        # Replace 'calendar' with the appropriate page route
        return redirect(url_for('main.pricing'))


@main.route('/portfolio')
def portfolio():
    # folder_path = os.path.join(
    #     current_app.static_folder, 'images/photos/creme_de_la_creme')

    # # List all files in the folder
    # image_files = [f for f in os.listdir(
    #     folder_path) if os.path.isfile(os.path.join(folder_path, f))]

    # # Render the template, passing the list of image files
    # return render_template('portfolio.html', image_files=image_files)

    # return render_template('portfolio.html')
    photos_path = os.path.join(current_app.static_folder, 'images/photos')

    # Grab all subfolders within the photos directory
    subfolders = [f for f in os.listdir(photos_path) if os.path.isdir(os.path.join(photos_path, f))]

    # Initialize a dictionary to store image files per subfolder
    gallery_data = {}

    for subfolder in subfolders:
        # Path to the current subfolder
        folder_path = os.path.join(current_app.static_folder, f'images/photos/{subfolder}')

        # List all files in the current subfolder and filter out the metadata.json file
        image_files = [f for f in os.listdir(folder_path) 
                       if os.path.isfile(os.path.join(folder_path, f)) and f != 'metadata.json']

        # Load the metadata file if it exists
        metadata_path = os.path.join(folder_path, 'metadata.json')
        aspect_ratio = 1.0  # Default aspect ratio

        if os.path.exists(metadata_path):
            with open(metadata_path, 'r') as metadata_file:
                metadata = json.load(metadata_file)
                aspect_ratio = metadata.get('aspect_ratio', 1.0)  # Use default 1.0 if not specified

        # Add the subfolder, its images, and aspect ratio to the dictionary
        gallery_data[subfolder] = {
            'images': image_files,
            'aspect_ratio': aspect_ratio
        }

    # Render the template and pass the gallery_data
    return render_template('portfolio.html', gallery_data=gallery_data)



@main.route('/about')
def about():
    return render_template('about.html')

# Route for getting pricing data via API


@main.route('/api/pricing')
def get_pricing():
    pricing_options: list[PricingOption] = PricingOption.query.all()
    pricing_data = [
        {
            'id': option.id,
            'name': option.name,
            'description': option.description,
            'holdPrice': 0 if option.hold_price is None else option.hold_price,
            'price': option.price
        } for option in pricing_options
    ]
    return jsonify(pricing_data)


HOLD_DURATION = timedelta(minutes=30)


@main.route('/api/update_timeslot_status', methods=['PUT'])
def update_timeslot_status():
    # Parse the request data
    data = request.get_json()

    # Validate the request data
    if not data or 'pricing_id' not in data or 'status' not in data or 'timeslot_id' not in data:
        return jsonify({"error": "Invalid request data"}), 400

    timeslot_id = data.get('timeslot_id')
    new_status = data.get('status')
    pricing_id = data.get('pricing_id')
    message: str = data.get('message')
    message = message[:255]

    if new_status != 'held':
        return jsonify({"error": "Invalid status value"}), 400

    # Retrieve the user based on the request IP
    user: User = get_or_create_user(ip=request.remote_addr)

    # Clear any timeslots currently held by the user
    clear_timeslots_held_by_user(user)

    # Retrieve the timeslot by ID
    timeslot: AvailableTimeSlot = AvailableTimeSlot.query.get(timeslot_id)
    if not timeslot:
        return jsonify({"error": "Timeslot not found"}), 404

    # Check if the timeslot is available
    if timeslot.status != 'available':
        return jsonify({"error": "Timeslot is not available"}), 400

    pricing: PricingOption = PricingOption.query.get(pricing_id)
    if not pricing:
        return jsonify({"error": "Pricing option not found"}), 404

    # Update the timeslot to be held by the user
    timeslot.status = 'held'
    user.held_timeslot = timeslot_id
    user.hold_until = datetime.now() + HOLD_DURATION
    user.held_price = pricing_id
    user.held_message = message

    try:
        # Commit the changes to the database
        db.session.commit()
        return jsonify({"message": "Timeslot held successfully"}), 200
    except Exception as e:
        # Rollback in case of any errors and return an error message
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@main.route('/api/available_dates')
def get_available_dates():
    user = get_or_create_user()

    available_timeslots = (
        db.session.query(AvailableTimeSlot)
        .join(Date, Date.id == AvailableTimeSlot.date_id)
        .filter(
            (AvailableTimeSlot.status == 'available')
            | (
                (AvailableTimeSlot.status == 'held') &
                (user.held_timeslot == AvailableTimeSlot.id)
            )
        )
        .all()
    )

    # Group timeslots by date
    date_timeslot_map = {}

    for timeslot in available_timeslots:
        if timeslot.date_id not in date_timeslot_map:
            date_timeslot_map[timeslot.date_id] = []
        date_timeslot_map[timeslot.date_id].append(timeslot)

    # Build response
    date_timeslot_list = [
        build_date_dict(date_id, timeslots)
        for date_id, timeslots in date_timeslot_map.items()
    ]

    update_expired_timeslots()

    return jsonify(date_timeslot_list)


def build_date_dict(date_id, timeslots):
    # Build the dictionary for the date and its valid timeslots
    date: Date = Date.query.get(date_id)
    date_dict = {
        "year": date.date.year,
        "month": date.date.month,
        "day": date.date.day,
        "time_slots": {}
    }

    # Populate the time_slots dictionary only with available or held timeslots
    for timeslot in timeslots:
        date_dict["time_slots"][timeslot.timeslot] = timeslot.to_dict()

    return date_dict

# Helper method to update timeslots that are held past their due date


def update_expired_timeslots():
    expired_users = db.session.query(User).filter(
        User.hold_until < datetime.now(),
        User.held_timeslot.isnot(None)
    ).all()

    for user in expired_users:
        clear_timeslots_held_by_user(user)

    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(f"An error occurred: {e}")


def clear_timeslots_held_by_user(user: User):
    if user.held_timeslot is None:
        return

    # Retrieve the held timeslot
    held_timeslot: AvailableTimeSlot = AvailableTimeSlot.query.get(
        user.held_timeslot)

    if held_timeslot:
        held_timeslot.status = 'available'

    # Clear the user's held timeslot
    user.held_timeslot = None
    user.hold_until = None
    user.held_price = None
    user.held_message = None

    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(f"An error occurred: {e}")


def get_or_create_user(ip=None) -> User:
    if not ip:
        ip = request.remote_addr
    user: User = db.session.query(User).filter(User.ip == ip).first()
    if not user:
        user = User(request.remote_addr)
        db.session.add(user)
        db.session.commit()

    return user


def pricing_option_to_dict(self):
    return {
        "id": self.id,
        "name": self.name,
        "description": self.description,
        "price": self.price
    }


PricingOption.to_dict = pricing_option_to_dict
# AvailableDate.to_dict = available_date_to_dict
