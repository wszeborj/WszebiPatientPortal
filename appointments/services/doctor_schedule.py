from datetime import date, datetime, timedelta
from typing import Dict, List

from django.db.models import QuerySet

from schedules.models import ScheduleDay
from users.models import Doctor

from ..models import Appointment


class DoctorScheduleService:
    @staticmethod
    def get_doctor_schedule_week(
        start_of_week: date, end_of_week: date, doctors: List[Doctor] = None
    ) -> Dict[Doctor, Dict[date, List[Dict[str, str | bool]]]]:
        if doctors is None:
            doctors = Doctor.objects.select_related("user").all()

        all_schedule_days = ScheduleDay.objects.filter(
            doctor__in=doctors, work_date__range=[start_of_week, end_of_week]
        ).select_related("doctor")

        all_appointments = Appointment.objects.filter(
            doctor__in=doctors, date__range=[start_of_week, end_of_week]
        ).values("doctor_id", "date", "time")

        appointment_lookup = set()
        for apt in all_appointments:
            appointment_lookup.add((apt["doctor_id"], apt["date"], apt["time"]))

        from collections import defaultdict

        doctor_schedules = defaultdict(list)

        for schedule_day in all_schedule_days:
            doctor_schedules[schedule_day.doctor].append(schedule_day)

        doctor_week_schedule = {}

        for doctor in doctors:
            schedule_days = doctor_schedules.get(doctor, [])

            doctor_schedule_day = DoctorScheduleService.get_doctor_schedule_day(
                schedule_days, appointment_lookup
            )
            doctor_schedule_day = DoctorScheduleService.fulfill_week_schedule_by_days(
                doctor_schedule_day, start_of_week
            )

            doctor_week_schedule[doctor] = doctor_schedule_day
        return doctor_week_schedule

    @staticmethod
    def get_doctor_schedule_day(
        schedule_days: QuerySet[ScheduleDay], appointment_lookup
    ) -> Dict[date, List[Dict[str, str | bool]]]:
        doctor_schedule_day = {}
        for schedule_day in schedule_days:
            available_slots = []
            current_time = datetime.combine(
                schedule_day.work_date, schedule_day.start_time
            )
            end_time = datetime.combine(schedule_day.work_date, schedule_day.end_time)
            while current_time < end_time:
                slot = DoctorScheduleService.get_slot_status(
                    current_time, schedule_day, appointment_lookup
                )

                available_slots.append(slot)
                current_time += schedule_day.interval

            doctor_schedule_day[schedule_day.work_date] = available_slots
        return doctor_schedule_day

    @staticmethod
    def get_slot_status(
        current_time: datetime, schedule_day: ScheduleDay, appointment_lookup
    ) -> Dict[str, str | bool]:
        is_past = current_time < datetime.now()

        appointment_key = (
            schedule_day.doctor.id,
            schedule_day.work_date,
            current_time.time(),
        )
        is_taken = appointment_key in appointment_lookup
        slot = {
            "time": current_time.strftime("%H:%M"),
            "is_taken": is_taken,
            "is_past": is_past,
        }
        return slot

    @staticmethod
    def fulfill_week_schedule_by_days(
        doctor_schedule_day: Dict[date, List[Dict[str, str | bool]]],
        start_of_week: date,
    ) -> Dict[date, List]:
        for day_num in range(7):
            date_time = start_of_week + timedelta(days=day_num)
            schedule_day = date_time
            if schedule_day not in doctor_schedule_day.keys():
                doctor_schedule_day[schedule_day] = []

        doctor_schedule_day = dict(sorted(doctor_schedule_day.items()))
        return doctor_schedule_day
