from email.mime.application import MIMEApplication
import pytz
from datetime import datetime, timedelta
import razorpay
from flask import request, jsonify
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from flask import Flask
from flask import request, session, make_response
from pymongo import MongoClient
from flask import Flask, request, jsonify, send_file, render_template
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user
from flask_bcrypt import Bcrypt
from flask_cors import CORS
import datetime
from datetime import datetime
from email.mime.text import MIMEText
import smtplib
import uuid
import re
import os
import requests
import subprocess
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
import requests
import json
import base64
from fpdf import FPDF
from num2words import num2words

# ----------------------------------------------------------------------------------


app = Flask(__name__)
CORS(app)

client_monogo = MongoClient(
    'mongodb+srv://patrakarbhavan:patrakarbhavan123@patrakarbhavan.xpncdbt.mongodb.net/?retryWrites=true&w=majority')
app.config['MONGO_URI'] = 'mongodb+srv://patrakarbhavan:patrakarbhavan123@patrakarbhavan.xpncdbt.mongodb.net/?retryWrites=true&w=majority'

app.config['SECRET_KEY'] = 'a6d217d048fdcd227661b755'
db = client_monogo['patrakar_bhavan_db']

pch_bookings_db = client_monogo['hall_booking_conf']
pch_bookings_collection = pch_bookings_db['bookings']
logs_collection = pch_bookings_db["logs"]
host = ""


@app.route('/')
def hello_world():
    return 'Hello World!'


@app.route('/home')
def home():
    return 'Home Page - BnB Developers'


def create_logs(msg):
    ist = pytz.timezone('Asia/Kolkata')  # Set timezone to IST
    current_time = datetime.now(ist).strftime(
        "%d/%m/%Y - %H:%M")  # Get current IST time

    logs_collection.insert_one({
        "msg": msg,
        "timestamp": current_time
    })

def send_email_with_invoice(to_email, invoice_path, booking_data):
    """Sends an HTML email with the invoice attached"""
    sender_email = "no-reply@patrakarbhavan.com"
    sender_password = "no-reply@patrakarbhavan"
    subject = "Booking Confirmation - Patrakar Bhavan"
    html_template = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Booking Confirmation - Patrakar Bhavan</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            margin: 0;
            padding: 0;
        }
        .container {
            max-width: 600px;
            margin: 0 auto;
            padding: 20px;
        }
        .header {
            text-align: center;
            padding: 20px 0;
            background-color: #f9f9f9;
        }
        .logo {
            max-width: 100%;
            height: auto;
        }
        .content {
            padding: 20px 0;
        }
        .booking-details {
            background-color: #f5f5f5;
            padding: 15px;
            border-radius: 5px;
            margin: 20px 0;
        }
        .detail-row {
            margin-bottom: 10px;
        }
        .detail-label {
            font-weight: bold;
            display: inline-block;
            width: 150px;
        }
        .button {
            display: inline-block;
            background-color: #1a73e8;
            color: white;
            padding: 12px 20px;
            text-decoration: none;
            border-radius: 4px;
            font-weight: bold;
            margin-top: 15px;
            text-color: white;
        }
        .footer {
            text-align: center;
            margin-top: 30px;
            padding-top: 20px;
            border-top: 1px solid #eee;
            font-size: 12px;
            color: #777;
        }
        .important-note {
            background-color: #fff8e1;
            padding: 15px;
            border-left: 4px solid #ffc107;
            margin: 20px 0;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <img src="https://files.patrakarbhavan.com/email-banner.jpg" alt="Patrakar Bhavan" class="logo">
            <h2>Booking Confirmation</h2>
        </div>
        
        <div class="content">
            <p>Dear <strong>{{name}}</strong>,</p>
            
            <p>Your booking for B. V. Rao Press Conference Hall has been confirmed. Thank you for choosing Patrakar Bhavan for your event.</p>
            
            <div class="booking-details">
                <div class="detail-row">
                    <span class="detail-label">Event Date:</span> {{date}}
                </div>
                <div class="detail-row">
                    <span class="detail-label">Time Slot:</span> {{start_time}} - {{end_time}}
                </div>
                <div class="detail-row">
                    <span class="detail-label">Event Type:</span> {{subCatType}}
                </div>
                <div class="detail-row">
                    <span class="detail-label">Duration:</span> {{duration}} minutes
                </div>
                <div class="detail-row">
                    <span class="detail-label">Amount:</span> ₹{{amount_rupees}} (Invoice #{{invoice_no}})
                </div>
            </div>
            
            <div class="important-note">
                <p><strong>Important information:</strong></p>
                <ul>
                    <li>Please arrive at least 30 minutes before your scheduled start time.</li>
                    <li>Kindly bring the attached invoice and a valid government ID matching the booking details.</li>
                    <li>Any changes to your booking must be made at least 24 hours in advance.</li>
                </ul>
            </div>
            
            <p>We've attached your invoice to this email for your records. If you need to view any details regarding your booking, please click the button below or contact our help desk.</p>
            
            <div style="text-align: center;">
                <a href="https://bookings.patrakarbhavan.com/booking-status?orderId={{order_id}}" class="button">View Booking Details</a>
            </div>
        </div>
        
        <div class="footer">
            <p>Patrakar Bhavan | Pune Union of Working Journalist</p>
            <p>Pune Patrakar Pratishthan, Near Ganjave Chauk, Navi Peth, Pune- 411 030</p>
            <p>Phone: +91 98 34 881 247 | Email: puwj2013@gmail.com</p>
            <p>&copy; 2025 Patrakar Bhavan. All rights reserved.</p>
        </div>
    </div>
</body>
</html>
"""  # Insert the HTML template here

    # Replace placeholders with actual booking data
    html_content = html_template.replace("{{name}}", booking_data["name"])
    html_content = html_content.replace(
        "{{order_id}}", booking_data["order_id"])
    html_content = html_content.replace("{{date}}", booking_data["date"])
    html_content = html_content.replace(
        "{{start_time}}", booking_data["start_time"])
    html_content = html_content.replace(
        "{{end_time}}", booking_data["end_time"])
    html_content = html_content.replace(
        "{{subCatType}}", booking_data["subCatType"])
    html_content = html_content.replace(
        "{{duration}}", booking_data["duration"])
    html_content = html_content.replace(
        "{{invoice_no}}", str(booking_data["invoice_no"]))
    html_content = html_content.replace(
        "{{amount_rupees}}", str(int(booking_data["amount"])/100))

    msg = MIMEMultipart()
    msg["From"] = sender_email
    msg["To"] = to_email
    msg["Subject"] = subject

    # Attach HTML content
    msg.attach(MIMEText(html_content, "html"))

    # Attach the invoice PDF
    with open(invoice_path, "rb") as attachment:
        part = MIMEApplication(
            attachment.read(), Name=os.path.basename(invoice_path))
        part["Content-Disposition"] = f'attachment; filename="{os.path.basename(invoice_path)}"'
        msg.attach(part)

    # Send the email
    with smtplib.SMTP("mail.patrakarbhavan.com", 587) as server:
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, to_email, msg.as_string())


def send_email_without_invoice(to_email, booking_data):
    """Sends an HTML email with the invoice attached"""
    sender_email = "no-reply@patrakarbhavan.com"
    sender_password = "no-reply@patrakarbhavan"
    subject = "Booking Confirmation - Patrakar Bhavan"
    html_template = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Booking Confirmation - Patrakar Bhavan</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            margin: 0;
            padding: 0;
        }
        .container {
            max-width: 600px;
            margin: 0 auto;
            padding: 20px;
        }
        .header {
            text-align: center;
            padding: 20px 0;
            background-color: #f9f9f9;
        }
        .logo {
            max-width: 100%;
            height: auto;
        }
        .content {
            padding: 20px 0;
        }
        .booking-details {
            background-color: #f5f5f5;
            padding: 15px;
            border-radius: 5px;
            margin: 20px 0;
        }
        .detail-row {
            margin-bottom: 10px;
        }
        .detail-label {
            font-weight: bold;
            display: inline-block;
            width: 150px;
        }
        .button {
            display: inline-block;
            background-color: #1a73e8;
            color: white;
            padding: 12px 20px;
            text-decoration: none;
            border-radius: 4px;
            font-weight: bold;
            margin-top: 15px;
            text-color: white;
        }
        .footer {
            text-align: center;
            margin-top: 30px;
            padding-top: 20px;
            border-top: 1px solid #eee;
            font-size: 12px;
            color: #777;
        }
        .important-note {
            background-color: #fff8e1;
            padding: 15px;
            border-left: 4px solid #ffc107;
            margin: 20px 0;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <img src="https://files.patrakarbhavan.com/email-banner.jpg" alt="Patrakar Bhavan" class="logo">
            <h2>Booking Confirmation</h2>
        </div>
        
        <div class="content">
            <p>Dear <strong>{{name}}</strong>,</p>
            
            <p>Your booking for B. V. Rao Press Conference Hall has been confirmed. Thank you for choosing Patrakar Bhavan for your event.</p>
            
            <div class="booking-details">
                <div class="detail-row">
                    <span class="detail-label">Event Date:</span> {{date}}
                </div>
                <div class="detail-row">
                    <span class="detail-label">Time Slot:</span> {{start_time}} - {{end_time}}
                </div>
                <div class="detail-row">
                    <span class="detail-label">Event Type:</span> {{subCatType}}
                </div>
                <div class="detail-row">
                    <span class="detail-label">Duration:</span> {{duration}} minutes
                </div>
                <div class="detail-row">
                    <span class="detail-label">Amount:</span> ₹{{amount_rupees}}
                </div>
            </div>
            
            <div class="important-note">
                <p><strong>Important information:</strong></p>
                <ul>
                    <li>Please arrive at least 30 minutes before your scheduled start time.</li>
                    <li>Kindly bring the attached invoice and a valid government ID matching the booking details.</li>
                    <li>Any changes to your booking must be made at least 24 hours in advance.</li>
                </ul>
            </div>
            
            <p>We've attached your invoice to this email for your records. If you need to view any details regarding your booking, please click the button below or contact our help desk.</p>
        </div>
        
        <div class="footer">
            <p>Patrakar Bhavan | Pune Union of Working Journalist</p>
            <p>Pune Patrakar Pratishthan, Near Ganjave Chauk, Navi Peth, Pune- 411 030</p>
            <p>Phone: +91 98 34 881 247 | Email: puwj2013@gmail.com</p>
            <p>&copy; 2025 Patrakar Bhavan. All rights reserved.</p>
        </div>
    </div>
</body>
</html>
"""  # Insert the HTML template here

    # Replace placeholders with actual booking data
    html_content = html_template.replace("{{name}}", booking_data["name"])
    html_content = html_content.replace("{{date}}", booking_data["date"])
    html_content = html_content.replace(
        "{{start_time}}", booking_data["start_time"])
    html_content = html_content.replace(
        "{{end_time}}", booking_data["end_time"])
    html_content = html_content.replace(
        "{{subCatType}}", booking_data["subCatType"])
    html_content = html_content.replace(
        "{{duration}}", booking_data["duration"])
    html_content = html_content.replace(
        "{{amount_rupees}}", str(int(booking_data["amount"])/100))

    msg = MIMEMultipart()
    msg["From"] = sender_email
    msg["To"] = to_email
    msg["Subject"] = subject

    # Attach HTML content
    msg.attach(MIMEText(html_content, "html"))

    # Send the email
    with smtplib.SMTP("mail.patrakarbhavan.com", 587) as server:
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, to_email, msg.as_string())

# ------------------------------------------------------------------------------------------------------------

# ^
SECRET_KEY = "your_secret_key"
# ^


def create_jwt_token(uid):
    payload = {
        "uid": uid
    }
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")

# ^


@app.route('/registerAdmin', methods=['POST'])
def register_admin():
    try:
        data = request.get_json()

        username = data.get('username')
        password = data.get('password')

        # Check if username and password are provided
        if not username or not password:
            return jsonify({"error": "Username and password are required.", "success": False}), 400

        # Access the database
        admin_db = db["patrakar_bhavan_admin_db"]
        admins_collection = admin_db["admins"]

        # Check if username already exists
        existing_admin = admins_collection.find_one({"username": username})
        if existing_admin:
            return jsonify({"error": "Username already exists.", "success": False}), 400

        # Hash the password
        hashed_password = generate_password_hash(password)

        # Generate a unique UID
        uid = uuid.uuid4().hex

        # Store the admin in the database
        new_admin = {
            "uid": uid,
            "username": username,
            "password": hashed_password
        }
        admins_collection.insert_one(new_admin)

        return jsonify({"message": "Admin registered successfully.", "success": True, "uid": uid}), 201

    except Exception as e:
        return jsonify({"error": str(e), "success": False}), 500

# ^


@app.route('/loginAdmin', methods=['POST'])
def login_admin():
    try:
        data = request.get_json()

        username = data.get('username')
        password = data.get('password')

        if not username or not password:
            return jsonify({"error": "Username and password are required.", "success": False}), 400

        # Access the database
        admin_db = db["patrakar_bhavan_admin_db"]
        admins_collection = admin_db["admins"]

        # Find the admin by username
        admin = admins_collection.find_one({"username": username}, {"_id": 0})

        if not admin or not check_password_hash(admin.get("password", ""), password):
            return jsonify({"error": "Invalid username or password.", "success": False}), 401

        # Generate JWT token
        token = create_jwt_token(admin['uid'])

        return jsonify({
            "message": "Login successful.",
            "success": True,
            "uid": admin['uid'],
            "name": admin['username'],
            "token": token
        }), 200

    except Exception as e:
        return jsonify({"error": str(e), "success": False}), 500


# ^
db_member = client_monogo['patrakar_bhavan_db']
members_collection = db_member['members_db']
special_day_collection = db_member['special_day_collection']

# ^


@app.route('/addMember', methods=['POST'])
def add_member():
    try:
        data = request.json

        # Generate unique mid
        data["mid"] = uuid.uuid4().hex

        data['username'] = data['email']
        data['password'] = generate_password_hash(data['phone'])

        # Insert into MongoDB
        members_collection.insert_one(data)

        return jsonify({"message": "Member added successfully", "mid": data["mid"]}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ^


@app.route('/addSpecialDay', methods=['POST'])
def add_special_day():
    try:
        data = request.json

        # Generate unique mid
        data["spid"] = uuid.uuid4().hex

        if not data["date"]:
            return jsonify({"message": "Error : Date not selected"}), 400

        all_data = special_day_collection.find_one({"date": data["date"]})

        if all_data:
            return jsonify({"message": "Error : Date already added"}), 400

        # Insert into MongoDB
        special_day_collection.insert_one(data)

        return jsonify({"message": "Special Day added successfully", "spid": data["spid"]}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ^


@app.route('/filterSpecialDays', methods=['POST'])
def filter_special_days():
    try:
        filter_params = request.json  # Get filter parameters from request payload
        filter_query = build_filter_query_special_days(
            filter_params)  # Build dynamic filter query

        special_days = special_day_collection.find(
            filter_query, {"_id": 0})  # Fetch filtered special days
        special_day_list = list(special_days)  # Convert cursor to list

        return jsonify({"specialDays": special_day_list[::-1]}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ^


def build_filter_query_special_days(params):
    filter_query = {}

    for key, value in params.items():
        if value:
            # Handle date exact match
            if key == 'date':
                filter_query[key] = value

            # Use regex for partial matching (case insensitive) for other fields
            else:
                filter_query[key] = re.compile(
                    f".*{re.escape(value)}.*", re.IGNORECASE)

    return filter_query

# ^


@app.route('/deleteSpecialDay', methods=['DELETE'])
def delete_special_day():
    try:
        # Use .get() to retrieve query parameters
        spid = request.args.get("spid")
        if not spid:
            return jsonify({"error": "Missing SPID"}), 400

        result = special_day_collection.delete_one({"spid": spid})

        if result.deleted_count == 0:
            return jsonify({"error": "Special Day not found"}), 404

        return jsonify({"message": "Special Day deleted successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
# ^


@app.route('/deleteInquiry', methods=['DELETE'])
def delete_inq():
    try:
        inq_collection = db['inquiry_db']
        # Use .get() to retrieve query parameters
        inqid = request.args.get("inqid")
        if not inqid:
            return jsonify({"error": "Missing inqid"}), 400

        result = inq_collection.delete_one({"inqid": inqid})

        if result.deleted_count == 0:
            return jsonify({"error": "Inquiry not found"}), 404

        return jsonify({"message": "Inquiry deleted successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
# ^


@app.route('/updateMember', methods=['PUT'])
def update_member():
    try:
        data = request.json
        mid = data.get("mid")
        if not mid:
            return jsonify({"error": "Missing member ID"}), 400

        update_data = {k: v for k, v in data.items() if k != "mid"}

        if "phone" in update_data:
            update_data['password'] = generate_password_hash(
                update_data['phone'])

        result = members_collection.update_one(
            {"mid": mid}, {"$set": update_data})

        if result.matched_count == 0:
            return jsonify({"error": "Member not found"}), 404

        return jsonify({"message": "Member updated successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ^


@app.route('/deleteMember', methods=['DELETE'])
def delete_member():
    try:
        # Use .get() to retrieve query parameters
        mid = request.args.get("mid")
        if not mid:
            return jsonify({"error": "Missing member ID"}), 400

        result = members_collection.delete_one({"mid": mid})

        if result.deleted_count == 0:
            return jsonify({"error": "Member not found"}), 404

        return jsonify({"message": "Member deleted successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ^


@app.route('/filterMembers', methods=['POST'])
def filter_members():
    try:
        filter_params = request.json  # Get filter parameters from request payload
        filter_query = build_filter_query_member(
            filter_params)  # Build dynamic filter query

        members = members_collection.find(
            filter_query, {"_id": 0})  # Fetch filtered members
        member_list = list(members)  # Convert cursor to list

        return jsonify({"members": member_list}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ^


def build_filter_query_member(params):
    filter_query = {}

    for key, value in params.items():
        if value:
            # Handle experience-range filter
            if key == 'experience-range':
                min_experience, max_experience = map(int, value.split(','))
                filter_query['journalism_details.experience'] = {
                    "$gte": min_experience, "$lte": max_experience}

            # Handle gender and other exact match fields
            elif key in ['gender', 'blood_group']:  # Add any other exact match fields here
                filter_query[key] = value

            # Use regex for partial matching (case insensitive) for other fields
            else:
                filter_query[key] = re.compile(
                    f".*{re.escape(value)}.*", re.IGNORECASE)

    return filter_query
# ^


@app.route('/submitInquiry', methods=['POST'])
def submitInquiry():
    try:
        data = request.json  # Get JSON data from request
        if not data:
            return jsonify({"error": "No data provided"}), 400

        # Insert data into MongoDB
        new_inquiry = {
            "name": data.get("name"),
            "phone": data.get("phone"),
            "gender": data.get("gender"),
            "email": data.get("email"),
            "organization": data.get("organization"),
            "experience": data.get("experience"),
            "designation": data.get("designation"),
            "inqid": str(uuid.uuid4())
        }
        members_collection = db['inquiry_db']
        result = members_collection.insert_one(new_inquiry)

        return jsonify({"message": "Inquiry sent successfully", "id": str(result.inserted_id)}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500
# ^


@app.route('/getAllInquiries', methods=['GET'])
def get_all_inquiries():
    members_collection = db['inquiry_db']
    # Exclude MongoDB's _id field
    members = list(members_collection.find({}, {"_id": 0}))
    return jsonify(members[::-1])

# @app.route('/getAllLogs', methods=['GET'])
# def get_all_logs():
#     # Exclude MongoDB's _id field
#     logs = list(logs_collection.find({}, {"_id": 0}))
#     return jsonify({"logs":logs[::-1], "c1":""})
# ^


@app.route('/getAllLogs', methods=['GET'])
def get_all_logs():
    db = client_monogo["patrakar_bhavan_db"]
    db1 = client_monogo["hall_booking_conf"]
    logs_collection = db1["logs"]
    members_db = db["members_db"]
    inquiry_db = db["inquiry_db"]
    bookings = db1["bookings"]
    canceledPaymentsPCH = db1["canceledPaymentsPCH"]
    # Get logs and exclude MongoDB's _id field
    logs = list(logs_collection.find({}, {"_id": 0}))

    # Get counts from collections
    total_members = members_db.count_documents({})
    total_inquiries = inquiry_db.count_documents({})
    all_bookings = bookings.count_documents({})
    canceled_bookings = canceledPaymentsPCH.count_documents({})

    # Get today's date in yyyy-MM-dd format
    today_date = datetime.today().strftime('%Y-%m-%d')
    todays_booking = bookings.count_documents({"date": today_date})

    return jsonify({
        "logs": logs[::-1],
        "total_members": total_members,
        "total_inquiries": total_inquiries,
        "all_bookings": all_bookings,
        "todays_booking": todays_booking,
        "canceled_bookings": canceled_bookings
    })
# ^


@app.route('/filterAllInquiries', methods=['POST'])
def filter_all_inquiries():
    try:
        # Get filter parameters from request payload (JSON)
        filter_params = request.json

        # Build the filter query using the helper function
        filter_query = build_filter_query_inq(filter_params)

        # Access the MongoDB collection for inquiries
        members_collection = db['inquiry_db']
        # Find inquiries based on the filter query
        members = members_collection.find(
            filter_query, {"_id": 0})  # Exclude MongoDB's _id field

        # Convert the cursor to a list of dictionaries for easier serialization
        member_list = list(members)

        return jsonify({"inquiries": member_list[::-1]})

    except Exception as e:
        return jsonify({"error": str(e)}), 500  # Internal Server Error

# ^


def build_filter_query_inq(params):
    filter_query = {}

    for key, value in params.items():
        if value:
            # For 'experience-range', parse min_experience and max_experience and add to the filter query
            if key == 'experience-range':
                min_experience, max_experience = value.split(',')
                filter_query['experience'] = {"$gte": int(
                    min_experience), "$lte": int(max_experience)}

            # For other parameters, use regex for partial matching
            else:
                filter_query[key] = re.compile(
                    f".*{re.escape(value)}.*", re.IGNORECASE)

    return filter_query


# ^
pch_bookings_db = client_monogo['hall_booking_conf']
pch_bookings_collection = pch_bookings_db['bookings']

# ^


@app.route('/filterPCHBookings', methods=['POST'])
def filter_pch_bookings():
    try:
        # Get filter parameters from request payload (JSON)
        filter_params = request.json

        # Build the filter query using the helper function
        filter_query = build_pch_filter_query(filter_params)

        # Find bookings based on the filter query
        bookings = pch_bookings_collection.find(
            filter_query, {"_id": 0})  # Exclude MongoDB's _id field

        # Convert the cursor to a list of dictionaries for easier serialization
        bookings_list = list(bookings)

        return jsonify({"pch_bookings": bookings_list[::-1]}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500  # Internal Server Error

# ^


def build_pch_filter_query(params):
    filter_query = {}

    for key, value in params.items():
        if value:
            # For date and exact match fields
            if key in ["date", "start_time", "end_time", "status", "serviceName"]:
                filter_query[key] = value

            # For numeric values like amount
            elif key == "amount":
                filter_query[key] = int(value)

            # For contact numbers (exact match)
            elif key in ["contact", "phnNo"]:
                filter_query[key] = re.compile(
                    f"^{re.escape(value)}$", re.IGNORECASE)

            # Use regex for partial matching (case insensitive) for other text fields
            else:
                filter_query[key] = re.compile(
                    f".*{re.escape(value)}.*", re.IGNORECASE)

    return filter_query


# ^
pch_cancel_db = client_monogo['hall_booking_conf']
canceled_bookings_collection = pch_cancel_db['canceledPaymentsPCH']
# ^


@app.route('/filterCancelBookings', methods=['POST'])
def filter_cancel_bookings():
    try:
        # Get filter parameters from request payload (JSON)
        filter_params = request.json

        # Build the filter query using the helper function
        filter_query = build_pch_filter_query(filter_params)

        # Find canceled bookings based on the filter query
        canceled_bookings = canceled_bookings_collection.find(
            filter_query, {"_id": 0}  # Exclude MongoDB's _id field
        )

        # Convert the cursor to a list of dictionaries for easier serialization
        canceled_bookings_list = list(canceled_bookings)

        return jsonify({"canceled_bookings": canceled_bookings_list[::-1]}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500  # Internal Server Error


# ^
# Define hall timings
HALL_OPEN = 11  # 11:00 AM
HALL_CLOSE = 16  # 4:00 PM
TIME_INTERVAL = 30  # Minimum slot size in minutes


# ----------------------------------------------------------------------------------

# ^
db3 = client_monogo["hall_booking_conf"]
bookings_conf_collection = db3["bookings"]

# ^
HALL_HOURS = {
    "press-conf": (11, 16),  # 11 AM - 4 PM
    "program": (10, 21),  # 10 AM - 9 PM
}
TIME_INTERVAL = 30  # Interval in minutes
# ^


def get_booked_slots_conf(date):
    """Fetch booked slots for a specific date."""
    bookings = bookings_conf_collection.find(
        {"date": date}, {"_id": 0, "start_time": 1, "end_time": 1})
    return [(entry["start_time"], entry["end_time"]) for entry in bookings]

# ^


# def generate_available_slots_conf(date, duration, event_type):
#     """Generate available slots based on date, duration, and type."""
#     if event_type == "Press Conference":
#         event_type = "press-conf"
#     elif event_type == "Program":
#         event_type = "program"
#     if event_type not in HALL_HOURS:
#         raise ValueError("Invalid event type")

#     # Set IST timezone
#     ist = pytz.timezone("Asia/Kolkata")
#     now_utc = datetime.utcnow().replace(tzinfo=pytz.utc)
#     now = now_utc.astimezone(ist)

#     # Parse the slot date as a date object
#     slot_date_obj = datetime.strptime(date, "%Y-%m-%d").date()

#     # Booked slots → datetime objects (IST-aware)
#     booked_slots_raw = get_booked_slots_conf(date)
#     booked_slots = [
#         (
#             ist.localize(datetime.combine(slot_date_obj, datetime.strptime(start, "%H:%M").time())),
#             ist.localize(datetime.combine(slot_date_obj, datetime.strptime(end, "%H:%M").time()))
#         )
#         for start, end in booked_slots_raw
#     ]

#     available_slots = []
#     open_hour, close_hour = HALL_HOURS[event_type]

#     start_of_day = ist.localize(datetime.combine(slot_date_obj, datetime.min.time()))
#     min_start_time = start_of_day + timedelta(hours=open_hour)
#     max_end_time = start_of_day + timedelta(hours=close_hour)

#     # If selected date is today (in IST)
#     if slot_date_obj == now.date():
#         one_hour_later = now + timedelta(hours=1)
#         remainder = one_hour_later.minute % TIME_INTERVAL
#         if remainder != 0:
#             one_hour_later += timedelta(minutes=(TIME_INTERVAL - remainder))
#         one_hour_later = one_hour_later.replace(second=0, microsecond=0)

#         if one_hour_later > min_start_time:
#             min_start_time = one_hour_later

#     current_time = min_start_time

#     while current_time + timedelta(minutes=duration) <= max_end_time:
#         slot_start = current_time
#         slot_end = current_time + timedelta(minutes=duration)

#         # Check for overlap
#         overlap = any(
#             slot_start < booked_end and slot_end > booked_start
#             for booked_start, booked_end in booked_slots
#         )

#         if not overlap:
#             available_slots.append({
#                 "start": slot_start.strftime("%H:%M"),
#                 "end": slot_end.strftime("%H:%M")
#             })

#         # Always move to next TIME_INTERVAL, even if slot overlaps
#         current_time += timedelta(minutes=TIME_INTERVAL)

#     return available_slots

def generate_available_slots_conf(date, duration, event_type):
    """Generate available slots based on date, duration, and type."""
    if event_type == "Press Conference":
        event_type = "press-conf"
    elif event_type == "Program":
        event_type = "program"
    if event_type not in HALL_HOURS:
        raise ValueError("Invalid event type")

    # Set IST timezone
    ist = pytz.timezone("Asia/Kolkata")
    now_utc = datetime.utcnow().replace(tzinfo=pytz.utc)
    now = now_utc.astimezone(ist)

    # Parse the slot date as a date object
    slot_date_obj = datetime.strptime(date, "%Y-%m-%d").date()

    # Booked slots → datetime objects (IST-aware)
    booked_slots_raw = get_booked_slots_conf(date)
    booked_slots = [
        (
            ist.localize(datetime.combine(slot_date_obj, datetime.strptime(start, "%H:%M").time())),
            ist.localize(datetime.combine(slot_date_obj, datetime.strptime(end, "%H:%M").time()))
        )
        for start, end in booked_slots_raw
    ]

    available_slots = []
    open_hour, close_hour = HALL_HOURS[event_type]

    start_of_day = ist.localize(datetime.combine(slot_date_obj, datetime.min.time()))
    min_start_time = start_of_day + timedelta(hours=open_hour)
    max_end_time = start_of_day + timedelta(hours=close_hour)

    # If selected date is today (in IST)
    if slot_date_obj == now.date():
        one_hour_later = now + timedelta(hours=1)
        remainder = one_hour_later.minute % TIME_INTERVAL
        if remainder != 0:
            one_hour_later += timedelta(minutes=(TIME_INTERVAL - remainder))
        one_hour_later = one_hour_later.replace(second=0, microsecond=0)

        if one_hour_later > min_start_time:
            min_start_time = one_hour_later

    current_time = min_start_time

    # Use a fixed slot interval of 30 minutes instead of using TIME_INTERVAL
    slot_interval = 30  # minutes
    
    while current_time + timedelta(minutes=duration) <= max_end_time:
        slot_start = current_time
        slot_end = current_time + timedelta(minutes=duration)

        # Check for overlap
        overlap = any(
            slot_start < booked_end and slot_end > booked_start
            for booked_start, booked_end in booked_slots
        )

        if not overlap:
            available_slots.append({
                "start": slot_start.strftime("%H:%M"),
                "end": slot_end.strftime("%H:%M")
            })

        # Increment by slot_interval (30 min) instead of TIME_INTERVAL
        current_time += timedelta(minutes=slot_interval)

    return available_slots


@app.route("/available_slots_conf", methods=["GET"])
def available_slots_conf():
    """API to get available slots for a given date, duration, and type."""
    try:
        date = request.args.get("date")  # Expected format: YYYY-MM-DD
        duration = int(request.args.get("duration"))  # Duration in minutes
        # Event type: press-conf or program
        event_type = request.args.get("type")

        # Validate date format
        try:
            datetime.strptime(date, "%Y-%m-%d")
        except ValueError:
            return jsonify({"error": "Invalid date format, use YYYY-MM-DD"}), 400

        if duration < 30 or duration > 600:
            return jsonify({"error": "Duration must be between 30 and 600 minutes"}), 400

        if event_type == "Press Conference":
            event_type = "press-conf"
        elif event_type == "Program":
            event_type = "program"
        if event_type not in HALL_HOURS:
            return jsonify({"error": "Invalid event type"}), 400

        slots = generate_available_slots_conf(date, duration, event_type)
        return jsonify({"available_slots": slots})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/book_slot_conf", methods=["POST"])
def book_slot_conf():
    """API to book a slot for a specific date."""
    try:
        data = request.json
        date = data.get("date")  # YYYY-MM-DD
        start_time = data.get("start_time")  # e.g., "11:00"
        end_time = data.get("end_time")  # e.g., "12:00"
        event_type = data.get("type")  # "press-conf" or "program"
        name = data.get("name")
        ins_name = data.get("insName")
        email = data.get("email")
        phn_no = data.get("phnNo")
        amount = data.get("amount")

        # Validate required fields
        if not all([date, start_time, end_time, event_type, name, email, phn_no, amount]):
            return jsonify({"error": "Missing required fields"}), 400

        # Validate date format
        try:
            datetime.strptime(date, "%Y-%m-%d")
        except ValueError:
            return jsonify({"error": "Invalid date format, use YYYY-MM-DD"}), 400

        # Validate time format
        try:
            start_time_obj = datetime.strptime(start_time, "%H:%M")
            end_time_obj = datetime.strptime(end_time, "%H:%M")
        except ValueError:
            return jsonify({"error": "Invalid time format, use HH:MM"}), 400

        if event_type == "Press Conference":
            event_type = "press-conf"
        elif event_type == "Program":
            event_type = "program"
        # Validate event type
        if event_type not in HALL_HOURS:
            return jsonify({"error": "Invalid event type"}), 400

        hall_open, hall_close = HALL_HOURS[event_type]

        # Ensure booking is within allowed hours
        if start_time_obj < datetime.strptime(f"{hall_open}:00", "%H:%M") or end_time_obj > datetime.strptime(f"{hall_close}:00", "%H:%M"):
            return jsonify({"error": "Time slot out of allowed range"}), 400

        # Validate duration (minimum 30 mins)
        if (end_time_obj - start_time_obj).total_seconds() / 60 < 30:
            return jsonify({"error": "Minimum booking duration is 30 minutes"}), 400

        # Check if slot is available
        booked_slots = get_booked_slots_conf(date)
        for booked_start, booked_end in booked_slots:
            if not (end_time <= booked_start or start_time >= booked_end):
                return jsonify({"error": "Slot already booked"}), 400

        # Format amount (convert to cents if applicable)
        data["amount"] = str(int(amount) * 100)

        # Additional booking details
        data["status"] = "booked"
        data["payment_id"] = uuid.uuid4().hex
        data["bookedBy"] = "Admin"
        data["subCatType"] = data["type"]
        data["slot"] = ""
        data["serviceId"] = "press-conference"
        data["serviceName"] = "PUWJ | B. V. Rao Press Conference Hall"
        if data["type"] == "press-conf":
            data["subCatType"] = "Press Conference"
        else:
            data["subCatType"] = "Program"

        ist = pytz.timezone("Asia/Kolkata")
        now_ist = datetime.now(ist)

        # Format: dd-mm-yyyy, hh:mm AM/PM
        formatted_time = now_ist.strftime("%d-%m-%Y, %I:%M %p")
        
        data["timestamp"] = formatted_time

        # Store booking
        bookings_conf_collection.insert_one(data)

        send_email_without_invoice(to_email=data["email"], booking_data=data)
        send_email_without_invoice(to_email="puwj2013@gmail.com", booking_data=data)
        
        msg = f"Booked Slot {data['start_time']} - {data['end_time']} on {data['date']} by {data['a_name']}"
        create_logs(msg)

        return jsonify({"message": "Slot booked successfully", "date": date, "start_time": start_time, "end_time": end_time})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/getBookingDetails", methods=["GET"])
def getBookingDetails():
    """API to get available slots for a given date, duration, and type."""
    try:
        # Expected format: YYYY-MM-DD
        payment_id = request.args.get("payment_id")
        booking_data = pch_bookings_collection.find_one(
            {"payment_id": payment_id}, {"_id": 0})
        return jsonify({"booking": booking_data})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/getCanceledBookingDetails", methods=["GET"])
def getCanceledBookingDetails():
    """API to get available slots for a given date, duration, and type."""
    try:
        # Expected format: YYYY-MM-DD
        payment_id = request.args.get("payment_id")
        booking_data = canceled_bookings_collection.find_one(
            {"payment_id": payment_id}, {"_id": 0})
        return jsonify({"booking": booking_data})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


def is_slot_available(date, start_time, end_time, payment_id=None):
    """Check if a time slot is available on a given date, ignoring the current booking."""
    booked_slots = bookings_conf_collection.find(
        # Ignore the current booking
        {"date": date, "payment_id": {"$ne": payment_id}},
        {"_id": 0, "start_time": 1, "end_time": 1}
    )

    for booked in booked_slots:
        booked_start = booked["start_time"]
        booked_end = booked["end_time"]

        if not (end_time <= booked_start or start_time >= booked_end):
            return False  # Overlapping slot found

    return True


@app.route("/modify_booking_conf", methods=["POST"])
def modify_booking_conf():
    """Modify an existing booking, verifying slot availability if time fields are changed."""
    try:
        data = request.json
        payment_id = data.get("payment_id")

        if not payment_id:
            return jsonify({"error": "Missing payment_id"}), 400

        existing_booking = bookings_conf_collection.find_one(
            {"payment_id": payment_id})

        if not existing_booking:
            return jsonify({"error": "Booking not found"}), 404

        update_data = {}

        # Check if date, start_time, or end_time is modified
        date_changed = data.get(
            "date") and data["date"] != existing_booking["date"]
        start_time_changed = data.get(
            "start_time") and data["start_time"] != existing_booking["start_time"]
        end_time_changed = data.get(
            "end_time") and data["end_time"] != existing_booking["end_time"]

        if date_changed or start_time_changed or end_time_changed:
            new_date = data.get("date", existing_booking["date"])
            new_start_time = data.get(
                "start_time", existing_booking["start_time"])
            new_end_time = data.get("end_time", existing_booking["end_time"])

            # Validate date format
            try:
                datetime.strptime(new_date, "%Y-%m-%d")
            except ValueError:
                return jsonify({"error": "Invalid date format, use YYYY-MM-DD"}), 400

            # Validate time format
            try:
                new_start_time_obj = datetime.strptime(new_start_time, "%H:%M")
                new_end_time_obj = datetime.strptime(new_end_time, "%H:%M")
            except ValueError:
                return jsonify({"error": "Invalid time format, use HH:MM"}), 400

            event_type = data["subCatType"]
            if event_type == "Press Conference":
                event_type = "press-conf"
            elif event_type == "Program":
                event_type = "program"
            if event_type not in HALL_HOURS:
                return jsonify({"error": "Invalid event type"}), 400

            hall_open, hall_close = HALL_HOURS[event_type]

            # Ensure new booking is within allowed hours
            if new_start_time_obj < datetime.strptime(f"{hall_open}:00", "%H:%M") or new_end_time_obj > datetime.strptime(f"{hall_close}:00", "%H:%M"):
                return jsonify({"error": "Time slot out of allowed range"}), 400

            # Check if new slot is available
            if not is_slot_available(new_date, new_start_time, new_end_time, payment_id):
                return jsonify({"error": "Selected slot is not available"}), 400

            # If available, update time-related fields
            update_data["date"] = new_date
            update_data["start_time"] = new_start_time
            update_data["end_time"] = new_end_time

        # Update other fields directly if provided
        updatable_fields = [
            "name", "email", "contact", "phnNo", "amount", "insName", "subCatType",
            "bookedBy", "gstNo", "govId", "subject", "address", "pinCode", "remark"
        ]
        for field in updatable_fields:
            if field in data and data[field] != existing_booking.get(field):
                update_data[field] = data[field]

        if not update_data:
            return jsonify({"message": "No changes detected"}), 200

        bookings_conf_collection.update_one(
            {"payment_id": payment_id}, {"$set": update_data}
        )

        msg = f"Booking of {data['name']} is modified by {data['a_name']}"
        create_logs(msg)

        return jsonify({"message": "Booking updated successfully"})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/reschedulePCHBooking", methods=["POST"])
def reschedule_booking():
    """API to reschedule a booking if the slot is still available."""
    try:
        # 1. Extract query parameters
        payment_id = request.args.get("payment_id")
        date = request.args.get("date")  # YYYY-MM-DD
        start_time = request.args.get("start_time")  # HH:MM
        end_time = request.args.get("end_time")      # HH:MM
        a_name = request.args.get("a_name")

        if not all([payment_id, date, start_time, end_time]):
            return jsonify({"error": "Missing required parameters"}), 400

        # 2. Validate date format
        try:
            datetime.strptime(date, "%Y-%m-%d")
        except ValueError:
            return jsonify({"error": "Invalid date format"}), 400

        # 3. Validate time format
        try:
            start_dt = datetime.strptime(start_time, "%H:%M")
            end_dt = datetime.strptime(end_time, "%H:%M")
        except ValueError:
            return jsonify({"error": "Invalid time format"}), 400

        if end_dt <= start_dt:
            return jsonify({"error": "End time must be after start time"}), 400

        # 4. Find booking by payment_id
        booking = bookings_conf_collection.find_one({"payment_id": payment_id})
        if not booking:
            return jsonify({"error": "Booking not found"}), 404

        duration = int((end_dt - start_dt).total_seconds() / 60)
        # e.g. "press-conf" or "program"
        event_type = booking.get("subCatType")

        # 5. Check if the requested slot is available
        all_available = generate_available_slots_conf(
            date, duration, event_type)

        is_valid = any(slot["start"] == start_time and slot["end"]
                       == end_time for slot in all_available)
        if not is_valid:
            return jsonify({"error": "Selected slot is no longer available"}), 409

        # 6. Update booking in the database
        bookings_conf_collection.update_one(
            {"payment_id": payment_id},
            {"$set": {
                "date": date,
                "start_time": start_time,
                "end_time": end_time
            }}
        )

        msg = f"Booking of {booking['name']} is Rescheduled to {date} : {start_time} - {end_time} by {a_name}"
        create_logs(msg)

        return jsonify({"message": "Booking successfully rescheduled"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# -------------------------------------------------------------------------------------------


# Razorpay credentials
# RAZORPAY_KEY_ID = 'rzp_test_7DsJGQPeYoXK0N'
# RAZORPAY_KEY_SECRET = 'cmwhT5lOuC2zINSqg66xhwCR'

RAZORPAY_KEY_ID = 'rzp_live_1pRyN7ScXA82sH'
RAZORPAY_KEY_SECRET = 'HL5XNchqR0grnKwu89IdEF9a'

# RAZORPAY_KEY_ID = 'rzp_live_K3QhOj3mTW1MqD'
# RAZORPAY_KEY_SECRET = 'Ox4T869elURtieZlrVRy1TTN'

client = razorpay.Client(auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET))


@app.route("/create_order", methods=["POST"])
def create_order():
    data = request.json
    amount = int(data.get("amount", 1)) * 100  # Convert INR to paise
    date = data.get("date", "")
    duration = data.get("duration", "")
    start_time = data.get("start_time", "")
    end_time = data.get("end_time", "")
    serviceId = data.get("serviceId", ""),
    serviceName = data.get("serviceName", ""),
    name = data.get("name", ""),
    email = data.get("email", ""),
    phnNo = data.get("phnNo", ""),
    insName = data.get("insName", "")
    subCatType = data.get("type", "")
    subject = data.get("subject", "")
    govId = data.get("govId", "")
    gstNo = data.get("gstNo", "")

    gst = data.get("gst", "")
    platformFee = data.get("platformFee", "")
    baseAmount = data.get("baseAmount", "")

    address = data.get("address", "")
    pinCode = data.get("pinCode", "")

    if amount <= 0:
        return jsonify({"error": "Invalid amount"}), 400

    order_data = {
        "amount": amount,
        "currency": "INR",
        "receipt": "order_rcptid_11",
        "notes": [
            {"date": date,
             "start_time": start_time,
             "end_time": end_time,
             "duration": duration,
             "serviceId": serviceId,
             "serviceName": serviceName,
             "name": name,
             "email": email,
             "phnNo": phnNo,
             "insName": insName,
             "subCatType": subCatType,
             "govId": govId,
             "subject": subject,
             "gstNo": gstNo,
             "gst": gst,
             "platformFee": platformFee,
             "baseAmount": baseAmount,
             "address": address,
             "pinCode": pinCode
             }]
    }

    order = client.order.create(data=order_data)

    return jsonify({
        "order_id": order["id"],
        "amount": order["amount"],
        "key_id": RAZORPAY_KEY_ID
    })


@app.route("/verify_payment", methods=["POST"])
def verify_payment():
    data = request.json
    try:
        client.utility.verify_payment_signature({
            "razorpay_order_id": data["razorpay_order_id"],
            "razorpay_payment_id": data["razorpay_payment_id"],
            "razorpay_signature": data["razorpay_signature"]
        })
        return jsonify({"success": True})
    except razorpay.errors.SignatureVerificationError:
        return jsonify({"success": False}), 400


@app.route("/get_payment_details/<order_id>", methods=["GET"])
def get_payment_details(order_id):
    try:
        # Fetch payments for the given order ID
        payments = client.order.payments(order_id)

        return jsonify(payments)
    except razorpay.errors.BadRequestError as e:
        return jsonify({"error": "Invalid order ID", "message": str(e)}), 400
    except Exception as e:
        return jsonify({"error": "Something went wrong", "message": str(e)}), 500


invoice_counter_collection = db3["invoice_counters"]
bookings_conf_collection = db3["bookings"]


class PDF(FPDF):
    def header(self):
        """ Set background image """
        self.image("template2.jpeg", x=0, y=0, w=210, h=297)  # A4 size
        self.set_font("Arial", size=12)


def get_next_invoice_number():
    """ Fetch and increment the last invoice number from invoice_counters collection. """
    counter_doc = invoice_counter_collection.find_one_and_update(
        {"_id": "invoice_number"},
        {"$inc": {"last_invoice": 1}},
        upsert=True,
        return_document=True
    )

    if counter_doc and "last_invoice" in counter_doc:
        return counter_doc["last_invoice"]

    return 1000  # Default starting invoice number if collection was empty


@app.route("/checkStatus/<order_id>")
def checkStatus(order_id):
    try:
        payments = client.order.payments(order_id)
        payment_items = payments.get('items', [])
        if not payment_items:
            return jsonify({"status": False, "msg": "No payments found for this order."})

        if payment_items[-1].get('status') == 'captured':
            notes = payment_items[-1]['notes'][0]
            json_str = json.dumps(notes, ensure_ascii=False)
            safe_dict = json.loads(json_str)
            final_payment = payment_items[-1]

            try:
                date = safe_dict.get("date", "")
                start_time = safe_dict.get("start_time", "")
                end_time = safe_dict.get("end_time", "")
                name = safe_dict.get('name', " ")[0]
                insName = safe_dict.get("insName", "")
                email = safe_dict.get("email", " ")[0]
                phnNo = safe_dict.get("phnNo", " ")[0]
                amount = final_payment['amount']
                contact = final_payment['contact']
                method = final_payment['method']
                payment_id = final_payment["id"]
                serviceId = safe_dict.get("serviceId", " ")[0]
                serviceName = safe_dict.get("serviceName", " ")[0]
                subCatType = safe_dict.get("subCatType", " ")
                duration = safe_dict.get("duration", "")
                govId = safe_dict.get("govId", " ")
                gstNo = safe_dict.get("gstNo", " ")
                subject = safe_dict.get("subject", " ")
                gst = safe_dict.get("gst", "")
                platformFee = safe_dict.get("platformFee", "")
                baseAmount = safe_dict.get("baseAmount", "")
                address = safe_dict.get("address", [" "]),
                address = list(address)[0]
                pinCode = safe_dict.get("pinCode", "")

                # data_bk1 = bookings_conf_collection.find_one({"invoice_no":int(invoice_no-1), "_id":-1})
                data_bk2 = bookings_conf_collection.find_one(
                    {"payment_id": payment_id})

                if data_bk2:
                    return jsonify({
                        "status": True,
                        "msg": "Already Payment successful! Slot booked successfully, and Invoice generated.",
                    })

                invoice_no = get_next_invoice_number()
                invoice_no = str("OR-"+str(invoice_no))

                invoice_link, invoice_path = generate_invoice({
                    "date": date,
                    "start_time": start_time,
                    "end_time": end_time,
                    "duration": duration,
                    "status": "booked",
                    "name": name,
                    "email": email,
                    "contact": contact,
                    "serviceId": serviceId,
                    "serviceName": serviceName,
                    "phnNo": phnNo,
                    "amount": amount,
                    "method": method,
                    "payment_id": payment_id,
                    "order_id": order_id,
                    "insName": insName,
                    "subCatType": subCatType,
                    "gstNo": gstNo,
                    "govId": govId,
                    "subject": subject,
                    "gst": gst,
                    "platformFee": platformFee,
                    "baseAmount": baseAmount,
                    "invoice_no": invoice_no,
                    "address": address,
                    "pinCode": pinCode
                })


                ist = pytz.timezone("Asia/Kolkata")
                now_ist = datetime.now(ist)

                # Format: dd-mm-yyyy, hh:mm AM/PM
                formatted_time = now_ist.strftime("%d-%m-%Y, %I:%M %p")

                bookings_conf_collection.insert_one({
                    "date": date,
                    "start_time": start_time,
                    "end_time": end_time,
                    "duration": duration,
                    "status": "booked",
                    "name": name,
                    "email": email,
                    "contact": contact,
                    "serviceId": serviceId,
                    "serviceName": serviceName,
                    "phnNo": phnNo,
                    "amount": amount,
                    "method": method,
                    "payment_id": payment_id,
                    "order_id": order_id,
                    "insName": insName,
                    "subCatType": subCatType,
                    "bookedBy": "Online",
                    "gstNo": gstNo,
                    "govId": govId,
                    "subject": subject,
                    "gst": gst,
                    "platformFee": platformFee,
                    "baseAmount": baseAmount,
                    "invoice_no": invoice_no,
                    "invoice_link": invoice_link,
                    "address": address,
                    "pinCode": pinCode,
                    "timestamp" : formatted_time
                })

                send_email_with_invoice(email, invoice_path, {
                    "date": date,
                    "start_time": start_time,
                    "end_time": end_time,
                    "duration": duration,
                    "status": "booked",
                    "name": name,
                    "email": email,
                    "contact": contact,
                    "serviceId": serviceId,
                    "serviceName": serviceName,
                    "phnNo": phnNo,
                    "amount": amount,
                    "method": method,
                    "payment_id": payment_id,
                    "order_id": order_id,
                    "insName": insName,
                    "subCatType": subCatType,
                    "gstNo": gstNo,
                    "govId": govId,
                    "subject": subject,
                    "gst": gst,
                    "platformFee": platformFee,
                    "baseAmount": baseAmount,
                    "invoice_no": invoice_no,
                    "address": address,
                    "pinCode": pinCode
                })

                send_email_with_invoice("puwj2013@gmail.com", invoice_path, {
                    "date": date,
                    "start_time": start_time,
                    "end_time": end_time,
                    "duration": duration,
                    "status": "booked",
                    "name": name,
                    "email": "puwj2013@gmail.com",
                    "contact": contact,
                    "serviceId": serviceId,
                    "serviceName": serviceName,
                    "phnNo": phnNo,
                    "amount": amount,
                    "method": method,
                    "payment_id": payment_id,
                    "order_id": order_id,
                    "insName": insName,
                    "subCatType": subCatType,
                    "gstNo": gstNo,
                    "govId": govId,
                    "subject": subject,
                    "gst": gst,
                    "platformFee": platformFee,
                    "baseAmount": baseAmount,
                    "invoice_no": invoice_no,
                    "address": address,
                    "pinCode": pinCode
                })


                return jsonify({
                    "status": True,
                    "msg": "Payment successful! Slot booked successfully, and Invoice generated.",
                    "invoice_no": invoice_no,
                    "invoice_link": invoice_link
                })

            except Exception as e:
                return jsonify({"error": str(e), "payment_items": payment_items, "safe_dict": safe_dict}), 500

        else:
            return jsonify({"status": False, "msg": "Payment failed or not captured."})

    except Exception as e:
        return jsonify({"status": False, "msg": f"Something went wrong: {str(e)}"})


def generate_invoice(receipt_data):
    """ Generates and saves an invoice as a PDF and returns the invoice link & file path """
    pdf = PDF()
    pdf.add_page()
    pdf.set_font("Arial", size=10)

    # Convert values
    receipt_data["words"] = num2words(
        receipt_data["amount"]/100, lang='en_IN').capitalize()
    receipt_data["tcswords"] = num2words(
        receipt_data["gst"], lang='en_IN').capitalize()
    receipt_data['base'] = float(receipt_data['baseAmount'])

    # Invoice details
    pdf.set_xy(101, 27)
    pdf.cell(0, 10, f"{receipt_data['invoice_no']}", ln=True)
    from datetime import datetime

    # Get current date in desired format (e.g., 04-04-2025)
    current_date = datetime.now().strftime("%d-%m-%Y")

    pdf.set_xy(141, 27)
    pdf.cell(0, 10, f"{current_date}", ln=True)

    # Customer details
    pdf.set_xy(14, 60)
    pdf.set_font("Arial", style="B", size=10)
    pdf.cell(0, 10, f"Name: {receipt_data['name']}", ln=True)

    pdf.set_xy(101, 93)
    pdf.set_font("Arial", size=10)
    pdf.cell(
        0, 10, f"Booking Date: {receipt_data['date']}, Time: {receipt_data['start_time']} - {receipt_data['end_time']}", ln=True)

    pdf.set_xy(14, 80)
    pdf.cell(0, 10, f"Phone: {receipt_data['phnNo']}", ln=True)

    pdf.set_xy(14, 69)
    pdf.multi_cell(
        80, 4, f"Address:{receipt_data['address']}, Pincode-{receipt_data['pinCode']}")

    pdf.set_xy(14, 90)
    pdf.cell(0, 10, f"Email: {receipt_data['email']}", ln=True)

    # Amount details
    pdf.set_xy(170, 163)
    pdf.set_font("Arial", style="B", size=10)
    pdf.cell(0, 10, f"{receipt_data['amount']/100}", ln=True)

    pdf.set_xy(14, 172)
    pdf.set_font("Arial", style="B", size=10)
    pdf.cell(0, 10, f"{receipt_data['words']}", ln=True)

    # Tax & GST breakdown
    pdf.set_xy(60, 190)
    pdf.set_font("Arial", size=10)
    pdf.cell(0, 10, f"{receipt_data['base']}", ln=True)
    pdf.set_xy(90, 190)
    pdf.cell(0, 10, f"9", ln=True)
    pdf.set_xy(105, 190)
    pdf.cell(0, 10, f"{receipt_data['gst']/2}", ln=True)
    pdf.set_xy(125, 190)
    pdf.cell(0, 10, f"9", ln=True)
    pdf.set_xy(140, 190)
    pdf.cell(0, 10, f"{receipt_data['gst']/2}", ln=True)
    pdf.set_xy(175, 190)
    pdf.cell(0, 10, f"{receipt_data['gst']}", ln=True)

    pdf.set_xy(60, 200)
    pdf.cell(0, 10, f"{receipt_data['base']}", ln=True)
    pdf.set_xy(105, 200)
    pdf.cell(0, 10, f"{receipt_data['gst']/2}", ln=True)
    pdf.set_xy(140, 200)
    pdf.cell(0, 10, f"{receipt_data['gst']/2}", ln=True)
    pdf.set_xy(175, 200)
    pdf.cell(0, 10, f"{receipt_data['gst']}", ln=True)

    pdf.set_xy(14, 213)
    pdf.cell(0, 10, f"{receipt_data['tcswords']}", ln=True)

    # Conditional formatting based on subCatType
    if receipt_data['subCatType'] == 'Program':
        pdf.set_xy(30, 144)
        pdf.cell(0, 10, f"Platform Fee", ln=True)
        pdf.set_xy(70, 136)
        pdf.cell(0, 10, f"Output CGST@9%", ln=True)
        pdf.set_xy(136, 120)
        pdf.cell(0, 10, f"18", ln=True)
        pdf.set_xy(148, 128)
        pdf.cell(0, 10, f"9%", ln=True)
        pdf.set_xy(148, 136)
        pdf.cell(0, 10, f"9%", ln=True)
        pdf.set_xy(70, 128)
        pdf.cell(0, 10, f"Output SGST@9%", ln=True)
        pdf.set_xy(30, 120)
        pdf.cell(0, 10, f"{receipt_data['serviceName']}", ln=True)
        pdf.set_xy(170, 120)
        pdf.cell(0, 10, f"{receipt_data['baseAmount']}", ln=True)
        pdf.set_xy(170, 136)
        pdf.cell(0, 10, f"{receipt_data['gst']/2}", ln=True)
        pdf.set_xy(170, 128)
        pdf.cell(0, 10, f"{receipt_data['gst']/2}", ln=True)
        pdf.set_xy(170, 144)
        pdf.cell(0, 10, f"{receipt_data['platformFee']}", ln=True)
    else:
        pdf.set_xy(30, 152)
        pdf.cell(0, 10, f"Platform Fee", ln=True)
        pdf.set_xy(70, 144)
        pdf.cell(0, 10, f"Output CGST@9%", ln=True)
        pdf.set_xy(136, 120)
        pdf.cell(0, 10, f"18", ln=True)
        pdf.set_xy(148, 136)
        pdf.cell(0, 10, f"9%", ln=True)
        pdf.set_xy(148, 144)
        pdf.cell(0, 10, f"9%", ln=True)
        pdf.set_xy(70, 136)
        pdf.cell(0, 10, f"Output SGST@9%", ln=True)
        pdf.set_xy(30, 120)
        pdf.cell(0, 10, f"{receipt_data['serviceName']}", ln=True)
        pdf.set_xy(30, 128)
        pdf.cell(0, 10, f"News Distribution", ln=True)
        pdf.set_xy(136, 128)
        pdf.cell(0, 10, f"18", ln=True)
        pdf.set_xy(170, 120)
        pdf.cell(
            0, 10, f"{float(receipt_data['baseAmount']) - 254.24}", ln=True)
        pdf.set_xy(170, 144)
        pdf.cell(0, 10, f"{receipt_data['gst']/2}", ln=True)
        pdf.set_xy(170, 136)
        pdf.cell(0, 10, f"{receipt_data['gst']/2}", ln=True)
        pdf.set_xy(170, 152)
        pdf.cell(0, 10, f"{receipt_data['platformFee']}", ln=True)
        pdf.set_xy(170, 128)
        pdf.cell(0, 10, f"254.24", ln=True)

    # Save PDF
    # Generate PDF in memory
    current_date = datetime.now().strftime('%Y-%m-%d')
    pdf_filename = f"invoice_{receipt_data['invoice_no']}.pdf"
    pdf_path = f"/tmp/{pdf_filename}"  # Temporary storage for uploading
    pdf.output(pdf_path)

    # Upload PDF to external server
    with open(pdf_path, "rb") as pdf_file:
        files = {"file": (pdf_filename, pdf_file, "application/pdf")}
        response = requests.post(
            "https://api2.patrakarbhavan.com/upload", files=files)

    invoice_link = ""

    # Check if the upload was successful
    if response.status_code == 200:
        # Assuming the API returns the file URL
        invoice_link = response.json().get("file_url")
    else:
        print("Error uploading file")

    # invoice_link = f"https://files.patrakarbhavan.com/receipts/{current_date}/invoice_{receipt_data['invoice_no']}.pdf"
    pdf_file_path = invoice_link.replace(
        "https://files.patrakarbhavan.com", "/home/rzeaiuym/files.patrakarbhavan.com")
    return invoice_link, pdf_path


canceled_collection = pch_bookings_db["canceledPaymentsPCH"]


@app.route("/cancelPCHBooking", methods=["POST"])
def cancel_pch_booking():
    try:
        data = request.json
        payment_id = data.get("payment_id")
        reason = data.get("reason")
        remark = data.get("remark")

        if not payment_id or not reason:
            return jsonify({"success": False, "message": "Missing required fields."}), 400

        # Find the booking
        booking = pch_bookings_collection.find_one({"payment_id": payment_id})
        if not booking:
            return jsonify({"success": False, "message": "Booking not found."}), 404

        # Remove from current collection
        pch_bookings_collection.delete_one({"payment_id": payment_id})

        # Update status and move to canceledPaymentsPCH
        canceled_booking = {
            **booking,
            "status": "canceled",
            "cancelReason": reason,
            "cancelRemark": remark,
        }

        canceled_collection.insert_one(canceled_booking)

        msg = f"Booking of Payment Id {data['payment_id']} is deleted by {data['a_name']}"
        create_logs(msg)

        return jsonify({"success": True, "message": "Booking canceled successfully."})

    except Exception as e:
        print("Error canceling booking:", str(e))
        return jsonify({"success": False, "message": "Internal server error."}), 500

# -------------------------------------------------------------------------------------------

# Database reference
db_chroma = client_monogo["hall_booking_chroma"]
bookings_chroma_collection = db_chroma["bookings"]

CHROMA_HOURS = (9, 20)  # 10 AM - 8 PM
TIME_INTERVAL = 60  # Interval in minutes


def get_booked_slots_chroma(date):
    """Fetch booked Chroma Studio slots for a specific date."""
    bookings = bookings_chroma_collection.find(
        {"date": date}, {"_id": 0, "start_time": 1, "end_time": 1})
    return [(entry["start_time"], entry["end_time"]) for entry in bookings]

from datetime import datetime, timedelta
import pytz

def generate_available_slots_chroma(date, duration):
    """Generate available Chroma Studio slots for a date and duration."""
    ist = pytz.timezone("Asia/Kolkata")
    now = datetime.utcnow().replace(tzinfo=pytz.utc).astimezone(ist)
    slot_date_obj = datetime.strptime(date, "%Y-%m-%d").date()

    # Get existing bookings
    booked_slots_raw = get_booked_slots_chroma(date)
    booked_slots = [
        (
            ist.localize(datetime.combine(slot_date_obj, datetime.strptime(start, "%H:%M").time())),
            ist.localize(datetime.combine(slot_date_obj, datetime.strptime(end, "%H:%M").time()))
        )
        for start, end in booked_slots_raw
    ]

    available_slots = []
    open_hour, close_hour = CHROMA_HOURS

    start_of_day = ist.localize(datetime.combine(slot_date_obj, datetime.min.time()))
    min_start_time = start_of_day + timedelta(hours=open_hour)
    max_end_time = start_of_day + timedelta(hours=close_hour)

    if slot_date_obj == now.date():
        one_hour_later = now + timedelta(hours=1)
        remainder = one_hour_later.minute % TIME_INTERVAL
        if remainder != 0:
            one_hour_later += timedelta(minutes=(TIME_INTERVAL - remainder))
        one_hour_later = one_hour_later.replace(second=0, microsecond=0)

        if one_hour_later > min_start_time:
            min_start_time = one_hour_later

    current_time = min_start_time

    while current_time + timedelta(minutes=duration) <= max_end_time:
        slot_start = current_time
        slot_end = current_time + timedelta(minutes=duration)

        # Check overlap
        overlap = any(
            slot_start < booked_end and slot_end > booked_start
            for booked_start, booked_end in booked_slots
        )

        if not overlap:
            available_slots.append({
                "start": slot_start.strftime("%H:%M"),
                "end": slot_end.strftime("%H:%M")
            })

        current_time += timedelta(minutes=TIME_INTERVAL)

    return available_slots


@app.route("/available_slots_chroma", methods=["GET"])
def available_slots_chroma():
    """API to get available Chroma Studio slots for a given date and duration."""
    try:
        date_str = request.args.get("date")  # Expected: YYYY-MM-DD
        duration = int(request.args.get("duration"))

        try:
            datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError:
            return jsonify({"error": "Invalid date format, use YYYY-MM-DD"}), 400

        if duration < 30 or duration > 660:
            return jsonify({"error": "Duration must be between 30 and 660 minutes"}), 400

        slots = generate_available_slots_chroma(date_str, duration)
        return jsonify({"available_slots": slots})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

def generate_invoice_chroma(receipt_data):
    """ Generates and saves an invoice as a PDF and returns the invoice link & file path """
    pdf = PDF()
    pdf.add_page()
    pdf.set_font("Arial", size=10)

    # Convert values
    receipt_data["words"] = num2words(receipt_data["amount"]/100, lang='en_IN').capitalize()
    receipt_data["tcswords"] = num2words(receipt_data["gst"], lang='en_IN').capitalize()
    receipt_data['base'] = float(receipt_data['baseAmount'])

    # Invoice details
    pdf.set_xy(101, 27)
    pdf.cell(0, 10, f"{receipt_data['invoice_no']}", ln=True)
    from datetime import datetime

    # Get current date in desired format (e.g., 04-04-2025)
    current_date = datetime.now().strftime("%d-%m-%Y")

    pdf.set_xy(141, 27)
    pdf.cell(0, 10, f"{current_date}", ln=True)


    # Customer details
    pdf.set_xy(14, 60)
    pdf.set_font("Arial", style="B", size=10)
    pdf.cell(0, 10, f"Name: {receipt_data['name']}", ln=True)

    pdf.set_xy(101, 93)
    pdf.set_font("Arial", size=10)
    pdf.cell(0, 10, f"Time: {receipt_data['start_time']} - {receipt_data['end_time']}", ln=True)

    pdf.set_xy(14, 83)
    pdf.cell(0, 10, f"Phone: {receipt_data['phnNo']}", ln=True)

    pdf.set_xy(14, 69)
    pdf.multi_cell(80,4, f"Address: {receipt_data['address']} Pincode- {receipt_data['pinCode']}")

    pdf.set_xy(14, 90)
    pdf.cell(0, 10, f"Email: {receipt_data['email']}", ln=True)

    # Amount details
    pdf.set_xy(170, 163)
    pdf.set_font("Arial", style="B", size=10)
    pdf.cell(0, 10, f"{receipt_data['amount']/100}", ln=True)

    pdf.set_xy(14, 172)
    pdf.set_font("Arial", style="B", size=10)
    pdf.cell(0, 10, f"{receipt_data['words']}", ln=True)

    # Tax & GST breakdown
    pdf.set_xy(60, 190)
    pdf.set_font("Arial", size=10)
    pdf.cell(0, 10, f"{receipt_data['base']}", ln=True)
    pdf.set_xy(90, 190)
    pdf.cell(0, 10, f"9", ln=True)
    pdf.set_xy(105, 190)
    pdf.cell(0, 10, f"{receipt_data['gst']/2}", ln=True)
    pdf.set_xy(125, 190)
    pdf.cell(0, 10, f"9", ln=True)
    pdf.set_xy(140, 190)
    pdf.cell(0, 10, f"{receipt_data['gst']/2}", ln=True)
    pdf.set_xy(175, 190)
    pdf.cell(0, 10, f"{receipt_data['gst']}", ln=True)

    pdf.set_xy(60, 200)
    pdf.cell(0, 10, f"{receipt_data['base']}", ln=True)
    pdf.set_xy(105, 200)
    pdf.cell(0, 10, f"{receipt_data['gst']/2}", ln=True)
    pdf.set_xy(140, 200)
    pdf.cell(0, 10, f"{receipt_data['gst']/2}", ln=True)
    pdf.set_xy(175, 200)
    pdf.cell(0, 10, f"{receipt_data['gst']}", ln=True)

    pdf.set_xy(14, 213)
    pdf.cell(0, 10, f"{receipt_data['tcswords']}", ln=True)

    pdf.set_xy(136, 120)
    pdf.cell(0, 10, f"18", ln=True)
    pdf.set_xy(30, 120)
    pdf.cell(0, 10, f"{receipt_data['serviceName']}", ln=True)
    pdf.set_xy(170, 120)
    pdf.cell(0, 10, f"{receipt_data['baseAmount']}", ln=True)
    pdf.set_xy(170, 136)
    pdf.cell(0, 10, f"{receipt_data['gst']/2}", ln=True)
    pdf.set_xy(170, 128)
    pdf.cell(0, 10, f"{receipt_data['gst']/2}", ln=True)
    pdf.set_xy(70, 136)
    pdf.cell(0, 10, f"Output CGST@9%", ln=True)
    pdf.set_xy(70, 128)
    pdf.cell(0, 10, f"Output SGST@9%", ln=True)
    pdf.set_xy(148, 128)
    pdf.cell(0, 10, f"9%", ln=True)
    pdf.set_xy(148, 136)
    pdf.cell(0, 10, f"9%", ln=True)
    # Conditional formatting based on subCatType



    # Save PDF
    # Generate PDF in memory
    current_date = datetime.now().strftime('%Y-%m-%d')
    pdf_filename = f"invoice_{receipt_data['invoice_no']}.pdf"
    pdf_path = f"/tmp/{pdf_filename}"  # Temporary storage for uploading
    pdf.output(pdf_path)

    # Upload PDF to external server
    with open(pdf_path, "rb") as pdf_file:
        files = {"file": (pdf_filename, pdf_file, "application/pdf")}
        response = requests.post("https://api2.patrakarbhavan.com/upload", files=files)

    invoice_link = ""
    
    # Check if the upload was successful
    if response.status_code == 200:
        invoice_link = response.json().get("file_url")  # Assuming the API returns the file URL
    else:
        print("Error uploading file")

    # invoice_link = f"https://files.patrakarbhavan.com/receipts/{current_date}/invoice_{receipt_data['invoice_no']}.pdf"
    pdf_file_path = invoice_link.replace("https://files.patrakarbhavan.com","/home/rzeaiuym/files.patrakarbhavan.com")
    return invoice_link, pdf_path

@app.route("/checkStatusChroma/<order_id>")
def checkStatusChroma(order_id):
    try:
        payments = client.order.payments(order_id)
        payment_items = payments.get('items', [])
        if not payment_items:
            return jsonify({"status": False, "msg": "No payments found for this order."})

        if payment_items[-1].get('status') == 'captured':
            notes = payment_items[-1]['notes'][0]
            final_payment = payment_items[-1]

            try:
                date = notes.get("date", "")
                start_time = notes.get("start_time", "")
                end_time = notes.get("end_time", "")
                name = notes.get('name', " ")[0]
                insName = notes.get("insName", "")
                email = notes.get("email", " ")[0]
                phnNo = notes.get("phnNo", " ")[0]
                amount = final_payment['amount']
                contact = final_payment['contact']
                method = final_payment['method']
                payment_id = final_payment["id"]
                serviceId = notes.get("serviceId", " ")[0]
                serviceName = notes.get("serviceName", " ")[0]
                subCatType = notes.get("subCatType", " ")
                duration = notes.get("duration", "")
                govId = notes.get("govId", " ")
                gstNo = notes.get("gstNo", " ")
                subject = notes.get("subject", " ")
                gst = notes.get("gst", "")
                platformFee = notes.get("platformFee", "")
                baseAmount = notes.get("baseAmount", "")
                address = notes.get("address", [" "]),
                address = list(address)[0]
                pinCode = notes.get("pinCode", "")

                # data_bk1 = bookings_conf_collection.find_one({"invoice_no":int(invoice_no-1), "_id":-1})
                data_bk2 = bookings_chroma_collection.find_one(
                    {"payment_id": payment_id})

                if data_bk2:
                    return jsonify({
                        "status": True,
                        "msg": "Already Payment successful! Slot booked successfully, and Invoice generated.",
                    })

                invoice_no = get_next_invoice_number()
                invoice_no = str("OR-"+str(invoice_no))

                invoice_link, invoice_path = generate_invoice_chroma({
                    "date": date,
                    "start_time": start_time,
                    "end_time": end_time,
                    "duration": duration,
                    "status": "booked",
                    "name": name,
                    "email": email,
                    "contact": contact,
                    "serviceId": serviceId,
                    "serviceName": serviceName,
                    "phnNo": phnNo,
                    "amount": amount,
                    "method": method,
                    "payment_id": payment_id,
                    "order_id": order_id,
                    "insName": insName,
                    "subCatType": subCatType,
                    "gstNo": gstNo,
                    "govId": govId,
                    "subject": subject,
                    "gst": gst,
                    "platformFee": platformFee,
                    "baseAmount": baseAmount,
                    "invoice_no": invoice_no,
                    "address": address,
                    "pinCode": pinCode
                })

                ist = pytz.timezone("Asia/Kolkata")
                now_ist = datetime.now(ist)

                # Format: dd-mm-yyyy, hh:mm AM/PM
                formatted_time = now_ist.strftime("%d-%m-%Y, %I:%M %p")

                bookings_chroma_collection.insert_one({
                    "date": date,
                    "start_time": start_time,
                    "end_time": end_time,
                    "duration": duration,
                    "status": "booked",
                    "name": name,
                    "email": email,
                    "contact": contact,
                    "serviceId": serviceId,
                    "serviceName": serviceName,
                    "phnNo": phnNo,
                    "amount": amount,
                    "method": method,
                    "payment_id": payment_id,
                    "order_id": order_id,
                    "insName": insName,
                    "subCatType": subCatType,
                    "bookedBy": "Online",
                    "gstNo": gstNo,
                    "govId": govId,
                    "subject": subject,
                    "gst": gst,
                    "platformFee": platformFee,
                    "baseAmount": baseAmount,
                    "invoice_no": invoice_no,
                    "invoice_link": invoice_link,
                    "address": address,
                    "pinCode": pinCode,
                    "timestamp": formatted_time
                })

                send_email_with_invoice(email, invoice_path, {
                    "date": date,
                    "start_time": start_time,
                    "end_time": end_time,
                    "duration": duration,
                    "status": "booked",
                    "name": name,
                    "email": email,
                    "contact": contact,
                    "serviceId": serviceId,
                    "serviceName": serviceName,
                    "phnNo": phnNo,
                    "amount": amount,
                    "method": method,
                    "payment_id": payment_id,
                    "order_id": order_id,
                    "insName": insName,
                    "subCatType": subCatType,
                    "gstNo": gstNo,
                    "govId": govId,
                    "subject": subject,
                    "gst": gst,
                    "platformFee": platformFee,
                    "baseAmount": baseAmount,
                    "invoice_no": invoice_no,
                    "address": address,
                    "pinCode": pinCode
                })

                return jsonify({
                    "status": True,
                    "msg": "Payment successful! Slot booked successfully, and Invoice generated.",
                    "invoice_no": invoice_no,
                    "invoice_link": invoice_link
                })

            except Exception as e:
                return jsonify({"error": str(e)}), 500

        else:
            return jsonify({"status": False, "msg": "Payment failed or not captured."})

    except Exception as e:
        return jsonify({"status": False, "msg": f"Something went wrong: {str(e)} {payments}", "payment_items":payment_items})


db3 = client_monogo["Announcement"]
announcement_collection = db3["announcement_db"]

@app.route('/addAnnouncements', methods=['POST'])
def add_announcement():
    """Handles announcement submission, uploads file to external service if provided, and stores metadata."""
    title = request.form.get("title")
    link = request.form.get("link")
    file = request.files.get("file")

    if not title:
        return jsonify({"error": "Title is required"}), 400

    file_url = None

    # Upload file to external API if file is provided
    if file and file.filename:
        try:
            upload_response = requests.post(
                "https://api2.patrakarbhavan.com/uploadDoc",
                files={"file": (file.filename, file.stream, file.mimetype)}
            )

            if upload_response.status_code != 200:
                return jsonify({"error": "File upload failed", "details": upload_response.text}), 500

            file_url = upload_response.json().get("file_url")

        except Exception as e:
            return jsonify({"error": "Upload failed", "exception": str(e)}), 500

    announcement = {
        "title": title,
        "link": link,
        "file_url": file_url,
        "aid": uuid.uuid4().hex
    }

    announcement_collection.insert_one(announcement)

    return jsonify({
        "message": "Announcement added successfully",
        "file_url":file_url
    }), 200

@app.route('/getAnnouncements', methods=['GET'])
def get_announcements():
    announcements = list(announcement_collection.find({}, {"_id": 0}))
    return jsonify(announcements), 200

@app.route('/deleteAnnouncement/<aid>', methods=["DELETE"])
def delete_announcement(aid):
    try:
        result = announcement_collection.delete_one({"aid": aid})
        if result.deleted_count == 1:
            return jsonify({"success": True, "message": "Announcement deleted successfully."}), 200
        else:
            return jsonify({"success": False, "error": "Announcement not found."}), 404
    except Exception as e:
        print(f"Error deleting announcement with aid={aid}: {e}")
        return jsonify({"success": False, "error": "Server error occurred."}), 500



#-----------------------------------------------------------------------------------------


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8081)
