from datetime import date, datetime, timedelta
from typing import Dict, List

from django.db.models import QuerySet

from schedules.models import ScheduleDay
from users.models import Doctor

from ..models import Appointment


class DoctorScheduleService:
    @staticmethod
    def get_doctor_schedule_week(
        start_of_week: date, end_of_week: date
    ) -> Dict[Doctor, Dict[date, List[Dict[str, str | bool]]]]:
        all_doctors = Doctor.objects.all()

        doctor_week_schedule = {}
        for doctor in all_doctors:
            schedule_days = ScheduleDay.objects.filter(
                doctor=doctor, work_date__range=[start_of_week, end_of_week]
            )

            doctor_schedule_day = DoctorScheduleService.get_doctor_schedule_day(
                schedule_days
            )
            doctor_schedule_day = DoctorScheduleService.fulfill_week_schedule_by_days(
                doctor_schedule_day, start_of_week
            )

            doctor_week_schedule[doctor] = doctor_schedule_day
        return doctor_week_schedule

    @staticmethod
    def get_doctor_schedule_day(
        schedule_days: QuerySet[ScheduleDay],
    ) -> Dict[date, List[Dict[str, str | bool]]]:
        doctor_schedule_day = {}
        for schedule_day in schedule_days:
            available_slots = []
            current_time = datetime.combine(
                schedule_day.work_date, schedule_day.start_time
            )
            end_time = datetime.combine(schedule_day.work_date, schedule_day.end_time)
            while current_time < end_time:
                slot = DoctorScheduleService.get_slot_status(current_time, schedule_day)

                available_slots.append(slot)
                current_time += schedule_day.interval

            doctor_schedule_day[schedule_day.work_date] = available_slots
        return doctor_schedule_day

    @staticmethod
    def fulfill_week_schedule_by_days(
        doctor_schedule_day: Dict[date, List[Dict[str, str | bool]]],
        start_of_week: date,
    ) -> Dict[date, List]:
        for day_num in range(7):
            date_time = start_of_week + timedelta(days=day_num)
            schedule_day = date_time.date()
            if schedule_day not in doctor_schedule_day.keys():
                doctor_schedule_day[schedule_day] = []

        doctor_schedule_day = dict(sorted(doctor_schedule_day.items()))
        return doctor_schedule_day

    @staticmethod
    def get_slot_status(
        current_time: datetime, schedule_day: ScheduleDay
    ) -> Dict[str, str | bool]:
        is_past = current_time < datetime.now()
        is_taken = Appointment.objects.filter(
            doctor=schedule_day.doctor,
            date=schedule_day.work_date,
            time=current_time.time(),
        ).exists()
        slot = {
            "time": current_time.strftime("%H:%M"),
            "is_taken": is_taken,
            "is_past": is_past,
        }
        return slot
