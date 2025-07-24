from datetime import datetime, timedelta
from typing import List

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.utils import timezone
from faker import Faker

from appointments.factories import AppointmentFactory
from core.env import env
from schedules.factories import ScheduleDayFactory
from schedules.models import ScheduleDay
from users.factories import DoctorFactory, PatientFactory
from users.models import Doctor, User

from .create_permission_groups import create_permission_groups

fake = Faker()

SPECIALIZATIONS_BY_DEPARTMENT = {
    "Cardiology Department": ["Cardiology", "Pediatric Cardiology", "Cardiac Surgery"],
    "Surgery Department": [
        "Surgery",
        "Pediatric Surgery",
        "Thoracic Surgery",
        "Vascular Surgery",
        "Oncological Surgery",
        "Plastic Surgery",
        "Maxillofacial Surgery",
        "Neurosurgery",
        "Orthopedics and Traumatology",
        "Urology",
        "Pediatric Urology",
    ],
    "Neurology Department": ["Neurology", "Pediatric Neurology"],
    "Oncology Department": [
        "Oncology",
        "Gynecologic Oncology",
        "Pediatric Oncology and Hematology",
        "Hematology",
    ],
    "Internal Medicine Department": [
        "Internal Medicine",
        "Endocrinology",
        "Diabetology",
        "Nephrology",
        "Infectious Diseases",
        "Hypertensiology",
        "Rheumatology",
    ],
    "Pediatrics Department": ["Pediatrics", "Neonatology"],
    "Radiology Department": ["Radiology", "Nuclear Medicine"],
    "Mental Health Department": [
        "Psychiatry",
        "Sexology",
        "Clinical Psychology",
        "Clinical Pharmacology",
    ],
    "Women's Health Department": ["Obstetrics and Gynecology"],
    "Dentistry Department": ["Dentistry"],
    "Emergency Department": ["Emergency Medicine"],
    "Immunology Department": ["Clinical Immunology"],
    "Genetics Department": ["Clinical Genetics"],
    "Pathology Department": ["Pathomorphology"],
    "Rehabilitation Department": ["Physiotherapy", "Medical Rehabilitation"],
    "General Department": [
        "Dermatology",
        "Gastroenterology",
        "Allergology",
        "Anesthesiology",
        "Angiology",
        "Audiology",
        "Balneology",
        "Epidemiology",
        "Laboratory Diagnostics",
        "Phthisiology",
        "Laryngology",
        "Occupational Medicine",
        "Family Medicine",
        "Forensic Medicine",
        "Sports Medicine",
        "Medical Microbiology",
        "Ophthalmology",
        "Otorhinolaryngology",
        "Clinical Toxicology",
        "Clinical Transfusiology",
        "Clinical Transplantology",
    ],
}


class Command(BaseCommand):
    help = (
        "Generuje losowe wizyty dla 20 lekarzy i 1000 pacjentów na najbliższy miesiąc."
    )

    def handle(self, *args, **options):
        self.stdout.write("Creating superuser...")
        self.create_super_user()

        self.stdout.write("Creating permission groups...")
        create_permission_groups()

        self.stdout.write("Creating doctors...")
        doctors = [DoctorFactory(confirmed=True) for _ in range(20)]

        self.stdout.write("Creating patients...")
        patients = [PatientFactory() for _ in range(100)]

        self.stdout.write("Creating schedule days and appointments...")
        schedule_days, appointments = generate_appointments_for_month(doctors, patients)

        self.stdout.write(
            self.style.SUCCESS(
                f"Created {len(schedule_days)} schedule days, {len(appointments)} appointments."
            )
        )

    def create_super_user(self):
        User = get_user_model()
        if not User.objects.filter(username=env("SUPERUSER_NAME")).exists():
            user = User.objects.create_superuser(
                username=env("SUPERUSER_NAME"),
                email=env("SUPERUSER_MAIL"),
                password=env("SUPERUSER_PASSWORD"),
                # phone="123456789",
                # birth_date=datetime.fromisoformat("1990-12-04"),
            )
            self.stdout.write(
                self.style.SUCCESS(f'Superuser "{user} created successfully.')
            )
        else:
            self.stdout.write(self.style.SUCCESS("Superuser already exist."))


def generate_slots_for_schedule_day(schedule_day: ScheduleDay):
    slots = []
    current_time = datetime.combine(schedule_day.work_date, schedule_day.start_time)
    end_time = datetime.combine(schedule_day.work_date, schedule_day.end_time)

    while current_time < end_time:
        slots.append(current_time.time())
        current_time += schedule_day.interval

    return slots


def fill_schedule_day(
    schedule_day: ScheduleDay, patients: List[User], fill_percent: float = 0.7
):
    slots = generate_slots_for_schedule_day(schedule_day)
    slots_to_fill = int(len(slots) * fill_percent)
    selected_slots = fake.random_elements(
        elements=slots, length=slots_to_fill, unique=True
    )

    appointments = []
    for slot in selected_slots:
        patient = fake.random_element(patients)
        appointment = AppointmentFactory(
            doctor=schedule_day.doctor,
            user=patient.user.patient_profile,
            date=schedule_day.work_date,
            time=slot,
        )
        appointments.append(appointment)
    return appointments


def generate_appointments_for_month(
    doctors: List[Doctor], patients: List[User], fill_percent: float = 0.7
):
    start_date = timezone.now().date()
    schedule_days = []
    all_appointments = []

    for doctor in doctors:
        for day_offset in range(30):
            work_date = start_date + timedelta(days=day_offset)

            schedule_day = ScheduleDayFactory(
                doctor=doctor,
                work_date=work_date,
                start_time=timezone.datetime.strptime("08:00", "%H:%M").time(),
                end_time=timezone.datetime.strptime("16:00", "%H:%M").time(),
                interval=timedelta(minutes=15),
            )
            schedule_days.append(schedule_day)

            appointments = fill_schedule_day(schedule_day, patients, fill_percent)
            all_appointments.extend(appointments)

    return schedule_days, all_appointments
