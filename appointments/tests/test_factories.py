from django.test import TestCase

from ..factories import AppointmentFactory
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
