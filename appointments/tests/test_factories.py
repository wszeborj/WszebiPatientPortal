from datetime import datetime, time, timedelta

from django.test import TestCase, tag
from django.utils import timezone
from icecream import ic

from schedules.factories import ScheduleDayFactory

from ..factories import AppointmentFactory, _generate_slots_for_schedule_day
from ..models import Appointment


class TestAppointmentFactory(TestCase):
    def test_create_single_object(self):
        appointment = AppointmentFactory.create()

        self.assertIsInstance(appointment, Appointment)
        self.assertEqual(Appointment.objects.count(), 1)

        self.assertIsNotNone(appointment.doctor)
        self.assertIsNotNone(appointment.user)
        self.assertIsNotNone(appointment.date)
        self.assertIsNotNone(appointment.time)
        self.assertIsNotNone(appointment.created_at)
        self.assertIsNotNone(appointment.modified_at)
        self.assertFalse(appointment.is_canceled)
        self.assertNotEqual(appointment.notes, "")

    def test_create_multiple_objects(self):
        AppointmentFactory.create_batch(10)
        self.assertEqual(Appointment.objects.count(), 10)

    @tag("x")
    def test_generate_slots_for_schedule_day(self):
        schedule_day = ScheduleDayFactory(
            start_time=time(8, 0), end_time=time(12, 0), interval=timedelta(minutes=30)
        )
        datetime.combine(timezone.now().date(), schedule_day.start_time)
        slots = _generate_slots_for_schedule_day(schedule_day)

        ic(slots)

        self.assertEqual(len(slots), 8)
        self.assertEqual(slots[0], time(hour=8, minute=0))
        self.assertEqual(slots[-1], time(hour=11, minute=30))
