import json
import requests
from datetime import date, datetime, timedelta
from enum import Enum


class Office(Enum):
    """Bürgerbüros in Munich"""

    ORLEANSPLATZ = "BÜRGERBÜRO ORLEANSPLATZ", 102522
    LEONRODSTRASSE = "BÜRGERBÜRO LEONRODSTRASSE", 102523
    RIESENFELDSTRASSE = "BÜRGERBÜRO RIESENFELDSTRASSE", 102524
    FORSTENRIEDER = "BÜRGERBÜRO FORSTENRIEDER ALLEE", 102526
    RUPPERTSTRASSE = "BÜRGERBÜRO RUPPERTSTRASSE", 10489
    PASING = "BÜRGERBÜRO PASING", 54261


class Services(Enum):
    REISEPASS = 1063453
    BEGLAUBIGUNG_VON_BIS_ZU_5_DOKUMENTEN = 1063426
    BEGLAUBIGUNG_VON_UNTERSCHRIFTEN = 1063428
    PERSONALAUSWEIS = 1063441
    WOHNSITZ_ANMELDEN_ODER_UMMELDEN = 1063475
    VERLUST_ODER_DIEBSTAHL_PERSONALAUSWEIS = 1076889
    VORLAEUFIGER_REISEPASS = 1080582
    HAUSHALTSBESCHEINIGUNG = 1080843
    PERSONENDATEN_IM_MELDEREGISTER_AENDERN = 10224136
    EINSCHALTEN_ELD_FUNKTION_ODER_AENDERUNG_DER_PIN = 10225119
    BEGLAUBIGUNG_VON_BIS_ZU_20_DOKUMENTEN = 10225119
    AUSWEISDOKUMENTE_FAMILIE = 10225205
    ADRESSAENDERUNG_PERSONALAUSWEIS_REISEPASS_EAT = 10242339
    ELD_KARTE_EU_EWR = 10306925


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
            "officeId": office.value[1],
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
            "officeId": office.value[1],
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
