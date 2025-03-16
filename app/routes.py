from flask import session
from flask.sessions import SecureCookieSessionInterface
import yagmail
from datetime import datetime, timedelta
from flask import Blueprint, render_template, jsonify, request, redirect, url_for, current_app
from app.models import PricingOption, Date, AvailableTimeSlot, User, db
import os
import re
import json

main = Blueprint('main', __name__)


@main.route('/')
def index():
    return render_template('index.html')


@main.route('/pricing')
def pricing():
    return render_template('pricing.html')


# @main.route('/payment')
# def payment():
#     user: User = get_user_by_session()
#     if not user:
#         return jsonify({"error": "Please enter your email first."}), 400


#     # Check if the user has a held timeslot

#     if user.held_timeslot:
#         # User has a held timeslot, render the payment page
#         return render_template('payment.html')
#     else:
#         # User does not have a held timeslot, redirect them
#         # Replace 'calendar' with the appropriate page route
#         return redirect(url_for('main.pricing'))


@main.route('/portfolio')
def portfolio():
    # photos_path = os.path.join(current_app.static_folder, 'images/photos')

    # # Grab all subfolders within the photos directory
    # subfolders = [f for f in os.listdir(photos_path) if os.path.isdir(os.path.join(photos_path, f))]

    # # Initialize a dictionary to store image files per subfolder
    # gallery_data = {}

    # for subfolder in subfolders:
    #     # Path to the current subfolder
    #     folder_path = os.path.join(current_app.static_folder, f'images/photos/{subfolder}')

    #     # List all files in the current subfolder and filter out the metadata.json file
    #     image_files = [f for f in os.listdir(folder_path)
    #                    if os.path.isfile(os.path.join(folder_path, f)) and f != 'metadata.json']

    #     # Load the metadata file if it exists
    #     metadata_path = os.path.join(folder_path, 'metadata.json')
    #     aspect_ratio = 1.0  # Default aspect ratio

    #     if os.path.exists(metadata_path):
    #         with open(metadata_path, 'r') as metadata_file:
    #             metadata = json.load(metadata_file)
    #             aspect_ratio = metadata.get('aspect_ratio', 1.0)  # Use default 1.0 if not specified

    #     # Add the subfolder, its images, and aspect ratio to the dictionary
    #     gallery_data[subfolder] = {
    #         'images': image_files,
    #         'aspect_ratio': aspect_ratio
    #     }

    # Render the template and pass the gallery_data
    return render_template('portfolio.html')  # , gallery_data=gallery_data)


@main.route('/portfolio/images')
def images():
    # Define the path to the portfolio folder
    portfolio_folder = os.path.join(
        current_app.static_folder, 'images', 'portfolio')

    # List all image files in the portfolio folder
    image_files = [f for f in os.listdir(portfolio_folder) if os.path.isfile(
        os.path.join(portfolio_folder, f))]

    # Create a list of URLs for the images in the portfolio folder
    image_list = [
        url_for('static', filename=f'images/portfolio/{image}')
        for image in image_files
    ]

    # Return the list of image URLs as a JSON array
    return jsonify(image_list)


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


# @main.route('/api/update_timeslot_status', methods=['PUT'])
# def update_timeslot_status():
#     # Parse the request data
#     data = request.get_json()

#     # Validate the request data
#     if not data or 'pricing_id' not in data or 'status' not in data or 'timeslot_id' not in data:
#         return jsonify({"error": "Invalid request data"}), 400

#     timeslot_id = data.get('timeslot_id')
#     new_status = data.get('status')
#     pricing_id = data.get('pricing_id')
#     email = data.get('email')
#     email = email[:255]  # sanitize

#     # Store email in session for future requests
#     session.clear()               # Clears previous session data
#     session['email'] = email      # Tie the new session to their email
#     session.modified = True       # Ensure session is saved

#     # Find or create the user in the DB
#     user = User.query.filter_by(email=email).first()
#     if not user:
#         user = User(email=email)
#         db.session.add(user)
#         db.session.commit()

#     if new_status != 'held':
#         return jsonify({"error": "Invalid status value"}), 400

#     user: User = get_user_by_session()
#     if not user:
#         return jsonify({"error": "Please enter your email first."}), 400

#     # Clear any timeslots currently held by the user
#     clear_timeslots_held_by_user(user)

#     # Retrieve the timeslot by ID
#     timeslot: AvailableTimeSlot = AvailableTimeSlot.query.get(timeslot_id)
#     if not timeslot:
#         return jsonify({"error": "Timeslot not found"}), 404

#     # Check if the timeslot is available
#     if timeslot.status != 'available':
#         return jsonify({"error": "Timeslot is not available"}), 400

#     pricing: PricingOption = PricingOption.query.get(pricing_id)
#     if not pricing:
#         return jsonify({"error": "Pricing option not found"}), 404

#     # Update the timeslot to be held by the user
#     timeslot.status = 'held'
#     user.held_timeslot = timeslot_id
#     user.hold_until = datetime.now() + HOLD_DURATION
#     user.held_price = pricing_id
#     user.email = email

#     try:
#         # Commit the changes to the database
#         db.session.commit()

#         emailUser = os.getenv('EMAIL_ADDRESS')
#         emailPass = os.getenv('EMAIL_PASSWORD')

#         yag = yagmail.SMTP(user=emailUser, password=emailPass)

#         def sendEmail(recipientEmail, subject, attachments=None):
#             try:
#                 # Send the email
#                 yag.send(
#                     to=recipientEmail,
#                     subject=subject,
#                     contents=render_template('confirmation.html', user=user, timeslot=str(timeslot)),
#                     attachments=attachments  # Optional list or string path to file
#                 )
#                 print(f"Email sent successfully to {recipientEmail}!")
#             except Exception as e:
#                 print(f"Failed to send email: {e}")

#         # Example usage
#         sendEmail(
#             recipientEmail=email,
#             subject='Booking Confirmation',
#         )


#         return jsonify({"message": "Timeslot held successfully"}), 200


#     except Exception as e:
#         # Rollback in case of any errors and return an error message
#         db.session.rollback()
#         return jsonify({"error": str(e)}), 500
@main.route('/api/update_timeslot_status', methods=['PUT'])
def update_timeslot_status():
    # --- Parse the request data ---
    data = request.get_json()

    # --- Basic request validation ---
    required_fields = ['pricing_id', 'status',
                       'timeslot_id', 'first_name', 'last_name', 'email']
    if not data or not all(field in data for field in required_fields):
        return jsonify({"error": "Missing required fields"}), 400

    # --- Extract and sanitize data ---
    timeslot_id = data.get('timeslot_id')
    new_status = data.get('status')
    pricing_id = data.get('pricing_id')

    first_name = data.get('first_name', '').strip()[:255]
    last_name = data.get('last_name', '').strip()[:255]
    email = data.get('email', '').strip()[:255]

    # --- Validate user-provided data ---
    if not len(first_name) > 0:
        return jsonify({"error": "Invalid first name"}), 400

    if not len(last_name) > 0:
        return jsonify({"error": "Invalid last name"}), 400

    if not is_valid_email(email):
        return jsonify({"error": "Invalid email address"}), 400

    # --- Validate status value ---
    if new_status != 'held':
        return jsonify({"error": "Invalid status value"}), 400

    # --- Store session data ---
    session.clear()                    # Clears any previous session data
    session['email'] = email           # Associate session with user email
    session.modified = True

    # --- Find or create user ---
    user = User.query.filter_by(email=email).first()
    if not user:
        user = User(email=email, first_name=first_name, last_name=last_name)
        db.session.add(user)
        db.session.commit()
    else:
        # Update first and last name if already exists
        user.first_name = first_name
        user.last_name = last_name
        db.session.commit()

    # --- Clear any existing held timeslots ---
    clear_timeslots_held_by_user(user)

    # --- Retrieve the timeslot ---
    timeslot = AvailableTimeSlot.query.get(timeslot_id)
    if not timeslot:
        return jsonify({"error": "Timeslot not found"}), 404

    # --- Validate that the timeslot belongs to the correct day (future proofing) ---
    # if not is_timeslot_valid_for_day(timeslot, data.get('day_id')):
    #     return jsonify({"error": "Timeslot does not belong to the specified day"}), 400

    # --- Check if the timeslot is currently available ---
    if timeslot.status != 'available':
        return jsonify({"error": "Timeslot is not available"}), 400

    # --- Retrieve and validate pricing option ---
    pricing = PricingOption.query.get(pricing_id)
    if not pricing:
        return jsonify({"error": "Pricing option not found"}), 404

    # --- Update timeslot and user holding info ---
    timeslot.status = 'held'
    user.held_timeslot = timeslot_id
    user.hold_until = datetime.now() + HOLD_DURATION
    user.held_price = pricing_id

    try:
        # --- Commit changes to the database ---
        db.session.commit()

        # --- Send confirmation email ---
        emailUser = os.getenv('EMAIL_ADDRESS')
        emailPass = os.getenv('EMAIL_PASSWORD')

        yag = yagmail.SMTP(user=emailUser, password=emailPass)

        def sendEmail(recipientEmail, subject, attachments=None):
            try:
                # Send the email with first and last name now in the template
                yag.send(
                    to=recipientEmail,
                    subject=subject,
                    contents=f"{user.first_name} {user.last_name},\n\tThank you for booking with Lizzie McGuire Photography\nYour session is held for {str(timeslot)}\nIf you have any questions, feel free to reply to this email.\n\nThanks, \n\tLizzie McGuire",
                    # render_template(
                    #     'confirmation.html',
                    #     user=user,
                    #     timeslot=str(timeslot),
                    #     first_name=user.first_name,
                    #     last_name=user.last_name
                    # ),
                    attachments=attachments
                )
                print(f"Email sent successfully to {recipientEmail}!")
            except Exception as e:
                print(f"Failed to send email: {e}")

        # Send the confirmation email
        sendEmail(
            recipientEmail=email,
            subject='Booking Confirmation'
        )

        return jsonify({"message": "Timeslot held successfully"}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@main.route('/api/held_timeslot')
def held_timeslot():
    data = request.get_json()

    user: User = get_user_by_session()
    if not user:
        return jsonify({"error": "Please enter your email first."}), 400
    timeslot = get_timeslot_held_by_user(user)

    if timeslot is None:
        return jsonify({"message": "No timeslot held"}), 404

    return jsonify(build_date_dict(timeslots=timeslot)), 200


@main.route('/api/available_dates')
def get_available_dates():
    # user: User = get_user_by_session()
    # if not user:
    #     return jsonify({"error": "Please enter your email first."}), 400

    update_expired_timeslots()

    available_timeslots = (
        db.session.query(AvailableTimeSlot)
        .join(Date, Date.id == AvailableTimeSlot.date_id)
        .filter(
            (AvailableTimeSlot.status == 'available')
            # | (
            #     (AvailableTimeSlot.status == 'held') &
            #     (user.held_timeslot == AvailableTimeSlot.id)
            # )
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


def clear_timeslots_held_by_user(user):
    if user.held_timeslot:
        timeslot = AvailableTimeSlot.query.get(user.held_timeslot)
        if timeslot and timeslot.status == 'held':
            timeslot.status = 'available'
        user.held_timeslot = None
        user.hold_until = None
        user.held_price = None
        db.session.commit()

        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            print(f"An error occurred: {e}")


def get_user_by_session():
    email = session.get('email')
    if not email:
        return None  # No email tied to this session yet

    user = User.query.filter_by(email=email).first()
    return user


def pricing_option_to_dict(self):
    return {
        "id": self.id,
        "name": self.name,
        "description": self.description,
        "price": self.price
    }


def get_timeslot_held_by_user(user: User):
    """
    Returns the timeslot held by the given user, if any.
    """
    if not user or user.held_timeslot is None:
        return None  # User doesn't hold any timeslot

    held_timeslot = AvailableTimeSlot.query.get(user.held_timeslot)

    if not held_timeslot:
        return None  # Timeslot not found in the database

    return held_timeslot.to_dict()  # Assuming you want to return a dict, not the object

# def is_timeslot_valid_for_day(timeslot, day_id):
#     """
#     Checks if the timeslot belongs to the specified day.

#     Args:
#         timeslot (AvailableTimeSlot): The timeslot instance to check.
#         day_id (int): The day ID to validate against.

#     Returns:
#         bool: True if the timeslot belongs to the given day, False otherwise.
#     """
#     if not timeslot:
#         # No timeslot provided
#         return False

#     if not isinstance(day_id, int):
#         # Day ID must be an integer
#         return False

#     return timeslot.date_id == day_id


def is_valid_email(email):
    """
    Validates an email address format using regex.

    Args:
        email (str): The email address to validate.

    Returns:
        bool: True if the email format is valid, False otherwise.
    """
    if not email:
        return False

    # General pattern for most use cases (RFC 5322 compliant enough)
    email_regex = re.compile(
        r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)"
    )

    return bool(email_regex.match(email))


PricingOption.to_dict = pricing_option_to_dict
# AvailableDate.to_dict = available_date_to_dict
