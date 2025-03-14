from datetime import datetime, timedelta

from django.core.management.base import BaseCommand
from icecream import ic

from schedules.models import ScheduleDay
from users.models import Doctor

from ...models import Appointment


class Command(BaseCommand):
    def handle(self, *args, **options):
        self.check_schedule_day_appointments2()

    def check_schedule_day_appointments2(self):
        # week_param = self.request.GET.get("week")
        week_param = None
        if week_param:
            start_of_week = datetime.strptime(week_param, "%Y-%m-%d")
        else:
            today = datetime.today()
            start_of_week = today - timedelta(days=today.weekday())

        # previous_week = (start_of_week - timedelta(days=7)).strftime("%Y-%m-%d")
        # next_week = (start_of_week + timedelta(days=7)).strftime("%Y-%m-%d")
        end_of_week = start_of_week + timedelta(days=6)

        all_doctors = Doctor.objects.all()

        doctor_week_schedule = {}
        for doctor in all_doctors:
            schedule_days = ScheduleDay.objects.filter(
                doctor=doctor, work_date__range=[start_of_week, end_of_week]
            )
            doctor_schedule_day = {}
            for schedule_day in schedule_days:
                available_slots = []
                current_time = datetime.combine(
                    schedule_day.work_date, schedule_day.start_time
                )
                ic(current_time)
                end_time = datetime.combine(
                    schedule_day.work_date, schedule_day.end_time
                )
                while current_time < end_time:
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
                    available_slots.append(slot)
                    current_time += schedule_day.interval

                doctor_schedule_day[schedule_day.work_date] = available_slots

            for day_num in range(7):
                date_time = start_of_week + timedelta(days=day_num)
                date = date_time.date()

                if date not in doctor_schedule_day.keys():
                    doctor_schedule_day[date] = []
            doctor_week_schedule[doctor] = doctor_schedule_day
