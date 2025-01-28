import json
import requests
from datetime import date, datetime, timedelta

from constants import Office, Services


def get_available_dates(
    start_date: date,
    end_date: date,
    office: Office,
    service: Services = Services.REISEPASS,
) -> dict:
    url = "https://www48.muenchen.de/buergeransicht/api/backend/available-days"
    response = requests.request(
        "GET",
        url,
        params={
            "startDate": start_date.strftime("%Y-%m-%d"),
            "endDate": end_date.strftime("%Y-%m-%d"),
            "officeId": office.office_id,
            "serviceId": service.value,
            "serviceCount": "1",
        },
    )

    return response.json()


def get_appointments_for_date(
    appointment_date: date, office: Office, service: Services = Services.REISEPASS
) -> dict:
    url = "https://www48.muenchen.de/buergeransicht/api/backend/available-appointments"
    response = requests.request(
        "GET",
        url,
        params={
            "date": appointment_date.strftime("%Y-%m-%d"),
            "officeId": office.office_id,
            "serviceId": service.value,
            "serviceCount": "1",
        },
    )

    return response.json()


if __name__ == "__main__":
    start_date = datetime.now().date()
    end_date = start_date + timedelta(weeks=26)

    result = {}
    for service in Services:
        print(f"Gather information for service {service}...")
        result[service.name] = {}

        for office in Office:
            if service == Services.NOTFALL_HILFE_AUFENTHALTSTITEL_BESCHAEFTIGTE_ANGEHOERIGE and office != Office.AUSLAENDERBEHOERDE:
                continue
            print(f"Gather information for office {office}...")
            result[service.name][office.name] = {}
            response = get_available_dates(start_date, end_date, office, service)

            for day in response.get("availableDays", []):
                print(f"Gather information for day {day}...")
                appointment_date = datetime.strptime(day, "%Y-%m-%d").date()
                appointments = get_appointments_for_date(appointment_date, office, service)
                result[service.name][office.name][day] = appointments
            print()
        print()

    with open("appointments.json", "w") as file:
        json.dump(result, file, indent=4)
