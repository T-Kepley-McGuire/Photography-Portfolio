from flask import session
from flask_cors import CORS, cross_origin
from flask.sessions import SecureCookieSessionInterface
import yagmail
from datetime import datetime, timedelta
from flask import Blueprint, render_template, jsonify, request, redirect, url_for, current_app
from app.models import PricingOption, Date, AvailableTimeSlot, User, db
import os
import re
import json
import calendar

main = Blueprint('main', __name__)

pricing_data = [
    {
        'id': 1,
        'name': "Minis",
        'description': "20 min session with minimum of 10 edited photos",
        'holdPrice': 50,
        'price': 125
    }, {
        'id': 2,
        'name': "Standard",
        'description': "40 min session with minimum of 20 edited photos",
        'holdPrice': 50,
        'price': 225
    }, {
        'id': 3,
        'name': "Extended",
        'description': "1 hour session with minimum of 30 edited photos",
        'holdPrice': 50,
        'price': 330
    }
]


@main.route('/')
def index():
    return render_template('index.html')


@main.route('/pricing')
def pricing():
    return render_template('pricing.html')


# @main.route('/portfolio')
# def portfolio():
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
    # return render_template('portfolio.html')  # , gallery_data=gallery_data)


@main.route('/portfolio/images')
@cross_origin()
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

@main.route('/homeAlt')
def homeAlt():
    return render_template('homeAlt.html')

# @main.route('/about')
# def about():
#     return render_template('about.html')

@main.route('/ping')
@cross_origin()
def ping():
    return jsonify("pong")

@main.route('/api/pricing')
@cross_origin()
def get_pricing():
    # pricing_options: list[PricingOption] = PricingOption.query.all()
    # pricing_data = [
    #     {
    #         'id': option.id,
    #         'name': option.name,
    #         'description': option.description,
    #         'holdPrice': 0 if option.hold_price is None else option.hold_price,
    #         'price': option.price
    #     } for option in pricing_options
    # ]
    return jsonify(pricing_data)


HOLD_DURATION = timedelta(minutes=30)


@main.route('/api/update_timeslot_status', methods=['PUT'])
# @cross_origin()
def update_timeslot_status():
    # --- Parse the request data ---
    data = request.get_json()

    # --- Basic request validation ---
    required_fields = ['pricing_id',
                       'timeslot', 'dates', 'first_name', 'last_name', 'email']
    if not data or not all(field in data for field in required_fields):
        return jsonify({"error": "Missing required fields"}), 400

    # --- Extract and sanitize data ---
    # timeslot_id = data.get('timeslot_id')
    dates = data.get("dates")
    timeslot = data.get("timeslot")
    # new_status = data.get('status')
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
    # if new_status != 'held':
    #     return jsonify({"error": "Invalid status value"}), 400

    # --- Store session data ---
    session.clear()                    # Clears any previous session data
    session['email'] = email           # Associate session with user email
    session.modified = True

    # --- Find or create user ---
    # user = User.query.filter_by(email=email).first()
    # if not user:
    #     user = User(email=email, first_name=first_name, last_name=last_name)
    #     db.session.add(user)
    #     db.session.commit()
    # else:
    #     # Update first and last name if already exists
    #     user.first_name = first_name
    #     user.last_name = last_name
    #     db.session.commit()

    # --- Clear any existing held timeslots ---
    # clear_timeslots_held_by_user(user)

    # --- Retrieve the timeslot ---
    # timeslot = AvailableTimeSlot.query.get(timeslot_id)
    # if not timeslot:
    #     return jsonify({"error": "Timeslot not found"}), 404

    # --- Validate that the timeslot belongs to the correct day (future proofing) ---
    # if not is_timeslot_valid_for_day(timeslot, data.get('day_id')):
    #     return jsonify({"error": "Timeslot does not belong to the specified day"}), 400

    # --- Check if the timeslot is currently available ---
    # if timeslot.status != 'available':
    #     return jsonify({"error": "Timeslot is not available"}), 400

    # --- Retrieve and validate pricing option ---
    pricing = None
    for po in pricing_data:
        if po["id"] == pricing_id:
            pricing = po
    # pricing = pricing_data.[po if po["id"] == pricing_id for po in pricing_data][0] # PricingOption.query.get(pricing_id)
    if not pricing:
        return jsonify({"error": "Pricing option not found"}), 404

    # --- Update timeslot and user holding info ---
    # timeslot.status = 'held'
    # user.held_timeslot = timeslot_id
    # user.hold_until = datetime.now() + HOLD_DURATION
    # user.held_price = pricing_id
    try:
        # --- Commit changes to the database ---
        # db.session.commit()

        # --- Send confirmation email ---
        emailUser = os.getenv('EMAIL_ADDRESS')
        emailPass = os.getenv('EMAIL_PASSWORD')

        yag = yagmail.SMTP(user=emailUser, password=emailPass)
        dateString = dates[0] if len(dates) == 1 else f'{dates[0]} or {dates[1]}' if len(
            dates) == 2 else f'{dates[0]}, {dates[1]}, or {dates[2]}'
        pricingOptionString = f'Pricing Option: {pricing["name"]}\n{pricing["description"]}\nHolding Price: {pricing["holdPrice"]}\nPrice: {pricing["price"]}'
        def sendEmail(recipientEmail, subject, body=None, attachments=None):
            try:
                # Send the email with first and last name now in the template
                yag.send(
                    to=recipientEmail,
                    subject=subject,
                    contents=body if body is not None else
                    render_template(
                        'confirmation.html',
                        # user=user,
                        timeslot=f'{timeslot} of {dateString}',
                        first_name=first_name,
                        last_name=last_name,
                        current_year=datetime.now().strftime("%Y")
                    ),
                    attachments=attachments
                )
            except Exception as e:
                pass # print(f"Failed to send email: {e}")

        # Send the confirmation email
        sendEmail(
            recipientEmail=email,
            subject='Booking Confirmation'
        )
        sendEmail(
            recipientEmail="lizzymare00@gmail.com",
            subject=f'Photography Booking with {first_name} {last_name}',
            body=f'{first_name} {last_name} has booked an appointment with you for {timeslot} of {dateString}\nEmail: {email}\n{pricingOptionString}'
        )

        return jsonify({"message": "Timeslot held successfully"}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@main.route("/api/submit-booking", methods=["POST"])
# @cross_origin()
def submit_booking():
    data = request.get_json()

    # 1. Required fields present and not empty
    required_fields = ["name", "email", "phone", "packageId", "timeslots"]
    for field in required_fields:
        if field not in data or not data[field]:
            return jsonify({"error": f"Missing or empty field: {field}"}), 400

    # 2. Validate packageId
    matching_package = next((p for p in pricing_data if p['id'] == data["packageId"]), None)
    if not matching_package:
        return jsonify({"error": "Invalid packageId"}), 400

    # 3. Validate timeslots
    timeslots = data["timeslots"]
    if not isinstance(timeslots, list) or len(timeslots) == 0:
        return jsonify({"error": "timeslots must be a non-empty list"}), 400

    now = datetime.now()

    for ts in timeslots:
        # Ensure keys exist
        if not all(k in ts for k in ["date", "morning", "afternoon", "evening"]):
            return jsonify({"error": "Invalid timeslot structure"}), 400

        # Ensure at least one time period is selected
        if not (ts["morning"] or ts["afternoon"] or ts["evening"]):
            return jsonify({"error": "At least one of morning/afternoon/evening must be selected"}), 400

        date = ts["date"]
        if not all(k in date for k in ["year", "month", "day"]):
            return jsonify({"error": "Invalid date structure in timeslot"}), 400

        # Parse date and check it's in the future
        month_num = parse_month(date["month"])
        if not month_num:
            return jsonify({"error": f"Invalid month format: {date['month']}"}), 400

        try:
            slot_date = datetime(int(date["year"]), month_num, int(date["day"]))
        except ValueError:
            return jsonify({"error": f"Invalid calendar date: {date}"}), 400

        if slot_date <= now:
            return jsonify({"error": "Date must be in the future"}), 400

    # ✅ All checks passed
    print("Validated payload:")
    print(data)
    print("Selected package:")
    print(matching_package)

    # return jsonify({"status": "success", "message": "Booking validated", "selectedPackage": matching_package}), 200
    try:
    # --- Commit booking to database here, if needed ---
    # db.session.commit()

    # --- Prepare email sending ---
        emailUser = os.getenv('EMAIL_ADDRESS')
        emailPass = os.getenv('EMAIL_PASSWORD')
        yag = yagmail.SMTP(user=emailUser, password=emailPass)

        # --- Format timeslot and pricing information ---
        formattedTimeslots = formatTimeslots(data["timeslots"])  # <- helper function
        pricingOption = matching_package  # already found in earlier validation
        pricingString = (
            f"Pricing Option: {pricingOption['name']}\n"
            f"{pricingOption['description']}\n"
            f"Holding Price: ${pricingOption['holdPrice']}\n"
            f"Total Price: ${pricingOption['price']}"
        )

        # --- Send confirmation emails ---
        def sendEmail(recipientEmail, subject, body=None, attachments=None):
            try:
                yag.send(
                    to=recipientEmail,
                    subject=subject,
                    contents=body if body is not None else
                    render_template(
                        'confirmation-new.html',
                        first_name=data["name"].split()[0],  # crude first name extraction
                        last_name=' '.join(data["name"].split()[1:]) or '',  # crude last name fallback
                        timeslot=formattedTimeslots,
                        current_year=datetime.now().strftime("%Y")
                    ),
                    attachments=attachments
                )
            except Exception as e:
                pass  # You can log or print the exception here

        # Send to user
        sendEmail(
            recipientEmail=data["email"],
            subject="Booking Confirmation"
        )

        # Send to you (admin/staff)
        sendEmail(
            recipientEmail= os.getenv("PERSONAL_EMAIL_ADDRESS"),
            subject=f"Photography Booking with {data['name']}",
            body=(
                f"{data['name']} has booked an appointment.\n"
                f"Timeslot(s): {formattedTimeslots}\n"
                f"Email: {data['email']}\n"
                f"{pricingString}"
            )
        )

        return jsonify({"message": "Timeslot held successfully"}), 200

    except Exception as e:
        # Roll back any DB changes
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@main.route("/api/submit-external-booking", methods=["POST"])
@cross_origin()
def submit_external_booking():
    data = request.get_json()

    # 1. Required fields present and not empty
    required_fields = ["fullName", "email", "phone", "selectedSessions"]
    for field in required_fields:
        if field not in data or not data[field]:
            return jsonify({"error": f"Missing or empty field: {field}"}), 400

    # 2. Validate selectedSessions
    selected_sessions = data["selectedSessions"]
    if not isinstance(selected_sessions, list) or len(selected_sessions) == 0:
        return jsonify({"error": "selectedSessions must be a non-empty list"}), 400

    # Optional fields
    location = data.get("location", "")
    message = data.get("message", "")
    referral_source = data.get("referralSource", "")

    # ✅ All checks passed
    print("Validated payload:")
    print(data)

    try:
        # --- Prepare email sending ---
        emailUser = os.getenv('EMAIL_ADDRESS')
        emailPass = os.getenv('EMAIL_PASSWORD')
        yag = yagmail.SMTP(user=emailUser, password=emailPass)

        # Split name for template
        name_parts = data["fullName"].split()
        first_name = name_parts[0] if name_parts else ""
        last_name = ' '.join(name_parts[1:]) if len(name_parts) > 1 else ""

        # --- Format session information ---
        formatted_sessions = ", ".join(selected_sessions)

        # Generate placeholder appointment options for the template
        appointment_options = []

        # --- Send confirmation emails ---
        def send_email(recipient_email, subject, use_template=True, body=None):
            try:
                if use_template:
                    # Use the HTML template for client email
                    contents = render_template(
                        'confirmation-v3.html',
                        recipient_name=data["fullName"],
                        session_type=formatted_sessions,
                        appointment_options=appointment_options,
                        company_name="Lizzie McGuire Photography",
                        sender_name="Lizzie McGuire",
                        contact_email=emailUser,
                        contact_phone=os.getenv("PERSONAL_PHONE_NUMBER") | ""
                    )
                else:
                    # Use plain text for admin notification
                    contents = body

                yag.send(
                    to=recipient_email,
                    subject=subject,
                    contents=contents
                )
            except Exception as e:
                print(f"Email sending error: {str(e)}")

        # Send to user (HTML template)
        send_email(
            recipient_email=data["email"],
            subject="Booking Confirmation",
            use_template=True
        )

        # Send to admin (plain text)
        admin_email = os.getenv("PERSONAL_EMAIL_ADDRESS")
        admin_message = f"""
New booking received:

Full Name: {data['fullName']}
Email: {data['email']}
Phone: {data['phone']}
Selected Sessions: {formatted_sessions}
Location: {location}
Referral Source: {referral_source}
Message: 
{message}
        """
        
        send_email(
            recipient_email=admin_email,
            subject=f"New Booking Request from {data['fullName']}",
            use_template=False,
            body=admin_message
        )

        return jsonify({"message": "Booking submitted successfully"}), 200

    except Exception as e:
        # Log the error
        print(f"Error processing booking: {str(e)}")
        return jsonify({"error": str(e)}), 500



@main.route('/api/held_timeslot')
@cross_origin()
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
@cross_origin()
def get_available_dates():
    # user: User = get_user_by_session()
    # if not user:
    #     return jsonify({"error": "Please enter your email first."}), 400

    # update_expired_timeslots()

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


from datetime import datetime

def formatTimeslots(timeslots: list) -> str:
    """
    Convert a list of timeslot dictionaries into a human-readable string.
    Example output:
        April 23, 2025 (Morning)
        April 24, 2025 (Afternoon, Evening)
    """
    formatted = []

    for ts in timeslots:
        date_dict = ts.get("date", {})
        year = date_dict.get("year")
        month_str = date_dict.get("month")
        day = date_dict.get("day")

        # Convert JS-style short month name to full month name with datetime
        try:
            parsed_date = datetime.strptime(f"{month_str} {day} {year}", "%b %d %Y")
            formatted_date = parsed_date.strftime("%B %d, %Y")
        except ValueError:
            formatted_date = f"{month_str} {day}, {year}"  # fallback in case of error

        slots = []
        if ts.get("morning"): slots.append("Morning")
        if ts.get("afternoon"): slots.append("Afternoon")
        if ts.get("evening"): slots.append("Evening")

        if slots:
            formatted.append(f"{formatted_date} ({', '.join(slots)})")

    return formatted




def parse_month(month_str):
    try:
        return list(calendar.month_abbr).index(month_str[:3])
    except ValueError:
        return None


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
