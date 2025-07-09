from datetime import date, datetime
from datetime import time as time_obj
from datetime import timedelta

from django.test import TestCase

from appointments.factories import AppointmentFactory
from appointments.services.doctor_schedule import DoctorScheduleService
from schedules.factories import ScheduleDayFactory
from users.factories import DoctorFactory


class DoctorScheduleServiceTests(TestCase):
    def setUp(self):
        self.start_of_week = date.today()
        self.end_of_week = self.start_of_week + timedelta(days=6)
        self.doctor = DoctorFactory()
        self.schedule_day = ScheduleDayFactory(
            doctor=self.doctor,
            work_date=self.start_of_week,
            start_time=time_obj(9, 0),
            end_time=time_obj(10, 0),
            interval=timedelta(minutes=30),
        )
        self.appointment = AppointmentFactory(
            doctor=self.doctor,
            date=self.start_of_week,
            time=time_obj(9, 0),
        )

    def test_get_slot_status_returns_correct_flags(self):
        appointment_lookup = {(self.doctor.id, self.start_of_week, time_obj(9, 0))}
        current_time = datetime.combine(self.start_of_week, time_obj(9, 0))
        slot = DoctorScheduleService.get_slot_status(
            current_time, self.schedule_day, appointment_lookup
        )
        self.assertTrue(slot["is_taken"])
        self.assertIn("is_past", slot)
        self.assertEqual(slot["time"], "09:00")

    def test_get_doctor_schedule_day_generates_slots(self):
        appointments = {(self.doctor.id, self.start_of_week, time_obj(9, 0))}
        result = DoctorScheduleService.get_doctor_schedule_day(
            [self.schedule_day], appointments
        )
        self.assertIn(self.start_of_week, result)
        self.assertEqual(len(result[self.start_of_week]), 2)
        self.assertTrue(result[self.start_of_week][0]["is_taken"])

    def test_fulfill_week_schedule_by_days_fills_all_days(self):
        partial_schedule = {
            self.start_of_week: [{"time": "09:00", "is_taken": False, "is_past": False}]
        }
        full_schedule = DoctorScheduleService.fulfill_week_schedule_by_days(
            partial_schedule, self.start_of_week
        )
        self.assertEqual(len(full_schedule), 7)
        self.assertIn(self.start_of_week + timedelta(days=6), full_schedule)

    def test_get_doctor_schedule_week_returns_expected_structure(self):
        schedule = DoctorScheduleService.get_doctor_schedule_week(
            self.start_of_week, self.end_of_week, [self.doctor]
        )
        self.assertIn(self.doctor, schedule)
        self.assertEqual(len(schedule[self.doctor]), 7)
        self.assertIn(self.start_of_week, schedule[self.doctor])
