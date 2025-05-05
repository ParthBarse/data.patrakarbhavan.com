from flask import Flask, jsonify, request
import datetime
from datetime import datetime, timedelta
import pytz
import requests
from pymongo import MongoClient


app = Flask(__name__)
client_monogo = MongoClient(
    'mongodb+srv://patrakarbhavan:patrakarbhavan123@patrakarbhavan.xpncdbt.mongodb.net/?retryWrites=true&w=majority')
app.config['MONGO_URI'] = 'mongodb+srv://patrakarbhavan:patrakarbhavan123@patrakarbhavan.xpncdbt.mongodb.net/?retryWrites=true&w=majority'

app.config['SECRET_KEY'] = 'a6d217d048fdcd227661b755'
db = client_monogo['patrakar_bhavan_db']

db3 = client_monogo["hall_booking_conf"]
bookings_conf_collection = db3["bookings"]


def get_booked_slots_conf(date):
    """Fetch booked slots for a specific date."""
    bookings = bookings_conf_collection.find(
        {"date": date}, {"_id": 0, "start_time": 1, "end_time": 1})
    return [(entry["start_time"], entry["end_time"]) for entry in bookings]

@app.route("/")
def index():
    return "Hello World!"


USER_HALL_HOURS = {
    "press-conf": ("1130", "1530"),
    "program": ("1000", "2100"),
}
USER_TIME_INTERVAL = 30

@app.route("/booked")
def booked():
    date = request.args.get("date")
    bookings = get_booked_slots_conf(date)
    return {"bookings":bookings}

def user_generate_available_slots_conf(date, duration, event_type):
    """Generate available slots based on date, duration, and type."""
    if event_type == "Press Conference":
        event_type = "press-conf"
    elif event_type == "Program":
        event_type = "program"
    if event_type not in USER_HALL_HOURS:
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
            ist.localize(datetime.combine(
                slot_date_obj, datetime.strptime(start, "%H:%M").time())),
            ist.localize(datetime.combine(
                slot_date_obj, datetime.strptime(end, "%H:%M").time()))
        )
        for start, end in booked_slots_raw
    ]

    available_slots = []
    open_time_str, close_time_str = USER_HALL_HOURS[event_type]

    # Convert string times to hours and minutes
    open_hour = int(open_time_str[:2])
    open_minute = int(open_time_str[2:]) if len(open_time_str) > 2 else 0

    close_hour = int(close_time_str[:2])
    close_minute = int(close_time_str[2:]) if len(close_time_str) > 2 else 0

    start_of_day = ist.localize(datetime.combine(
        slot_date_obj, datetime.min.time()))
    min_start_time = start_of_day + \
        timedelta(hours=open_hour, minutes=open_minute)
    max_end_time = start_of_day + \
        timedelta(hours=close_hour, minutes=close_minute)

    # If selected date is today (in IST)
    if slot_date_obj == now.date():
        one_hour_later = now + timedelta(hours=1)
        remainder = one_hour_later.minute % USER_TIME_INTERVAL
        if remainder != 0:
            one_hour_later += timedelta(minutes=(USER_TIME_INTERVAL - remainder))
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


@app.route("/user_available_slots_conf", methods=["GET"])
def user_available_slots_conf():
    """API to get available slots for a given date, duration, and type."""
    try:
        # Check if all required parameters exist
        if "date" not in request.args:
            return jsonify({"error": "Missing required parameter: date"}), 400
        if "duration" not in request.args:
            return jsonify({"error": "Missing required parameter: duration"}), 400
        if "type" not in request.args:
            return jsonify({"error": "Missing required parameter: type"}), 400

        date = request.args.get("date")  # Expected format: YYYY-MM-DD
        
        # Safely convert duration to integer with proper error handling
        try:
            duration = int(request.args.get("duration"))  # Duration in minutes
        except ValueError:
            return jsonify({"error": "Duration must be a valid integer"}), 400
            
        event_type = request.args.get("type")  # Event type: press-conf or program

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
        if event_type not in USER_HALL_HOURS:
            return jsonify({"error": "Invalid event type"}), 400

        slots = user_generate_available_slots_conf(date, duration, event_type)
        return jsonify({"available_slots": slots})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8081, debug=True)
