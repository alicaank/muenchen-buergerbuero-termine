#!/usr/bin/env python3
"""
generate_ics_per_category.py

Reads JSON data, then for each top-level category (e.g. "REISEPASS"),
generates a separate ICS calendar file, containing all appointments
in that category.
"""

import json
import re
from datetime import datetime, timedelta
from icalendar import Calendar, Event
from pathlib import Path

# ------------
# CONFIG
# ------------
JSON_FILE = "appointments.json"  # Input JSON with the structure shown in the example
OUTPUT_DIR_NAME = "ics"  # Output directory for ICS files

def clean_filename(name):
    """
    Convert category name into a filename-friendly string, e.g. removing spaces, slashes, etc.
    """
    return re.sub(r'[^A-Za-z0-9_\-]+', '_', name)

def load_appointments(json_file):
    """Load the appointment data from the JSON file."""
    with open(json_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data

def generate_ics_for_category(category_name, category_data):
    """
    Create an ICS Calendar object for a single category.
    category_data is the dict of { location -> { date -> {...} } }
    """
    cal = Calendar()
    cal.add('prodid', f'-//Appointments Buergerbuero Muenchen//{category_name}//')
    cal.add('version', '2.0')

    # Iterate over locations in this category
    for location_name, dates_dict in category_data.items():
        for date_str, info in dates_dict.items():
            # If there's an errorCode, skip
            if "errorCode" in info:
                continue

            # appointmentTimestamps is the list of start times (epoch)
            timestamps = info.get("appointmentTimestamps", [])
            for start_ts in timestamps:
                start_dt = datetime.fromtimestamp(start_ts)
                end_dt = start_dt + timedelta(minutes=15)  # Each appointment is 15 min

                event = Event()
                event.add('summary', f"{category_name} - {location_name}")
                event.add('dtstart', start_dt)
                event.add('dtend', end_dt)
                event.add('dtstamp', datetime.utcnow())
                event.add('location', location_name)
                event.add('description', f"Category: {category_name}\nLocation: {location_name}")
                # Unique identifier for the event
                event['uid'] = f"{start_ts}-{location_name.replace(' ', '_')}@example.com"

                cal.add_component(event)

    return cal

def main():
    data = load_appointments(JSON_FILE)

    # For each top-level category (key), generate one ICS file
    # Create output directory if it doesn't exist
    output_dir = Path(OUTPUT_DIR_NAME)
    output_dir.mkdir(exist_ok=True)

    for category_name, category_data in data.items():
        cal = generate_ics_for_category(category_name, category_data)

        # Make a safe filename from the category name
        safe_cat = clean_filename(category_name)
        output_file = output_dir / f"{safe_cat}.ics"

        with open(output_file, 'wb') as f:
            f.write(cal.to_ical())

        print(f"Created ICS for category '{category_name}' -> {output_file}")

if __name__ == "__main__":
    main()