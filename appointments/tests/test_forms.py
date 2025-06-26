from datetime import date, time, timedelta

from django.test import TestCase

from appointments.forms import AppointmentForm
from appointments.models import Appointment
from schedules.models import ScheduleDay
from users.factories import DoctorFactory, PatientFactory


class AppointmentFormTests(TestCase):
    def setUp(self):
        self.doctor = DoctorFactory()
        self.patient = PatientFactory()
        self.work_date = date(2025, 6, 1)
        self.start_time = time(10, 0)
        self.end_time = time(12, 0)
        self.interval = timedelta(minutes=20)

        self.schedule = ScheduleDay.objects.create(
            doctor=self.doctor,
            work_date=self.work_date,
            start_time=self.start_time,
            end_time=self.end_time,
            interval=self.interval,
        )

    def get_valid_kwargs(self, **overrides):
        kwargs = {
            "doctor": self.doctor,
            "date": self.work_date,
            "time": time(10, 20),
        }
        kwargs.update(overrides)
        return kwargs

    def test_form_is_valid_with_correct_data(self):
        form = AppointmentForm(data=self.get_valid_kwargs())
        self.assertTrue(form.is_valid())

    def test_appointment_form_saves_when_slot_is_available(self):
        form = AppointmentForm(data=self.get_valid_kwargs())
        self.assertTrue(form.is_valid())
        form.instance.user = self.patient
        instance = form.save()
        self.assertEqual(instance.doctor, self.doctor)
        self.assertEqual(instance.user, self.patient)
        self.assertEqual(instance.date, date(2025, 6, 1))
        self.assertEqual(instance.time, time(10, 20))

    def test_form_invalid_when_doctor_not_available_at_given_time(self):
        form = AppointmentForm(data=self.get_valid_kwargs(time=time(8, 0)))
        form.instance.user = self.patient
        self.assertFalse(form.is_valid())
        self.assertIn("The doctor is not available", str(form.errors["__all__"]))

    def test_form_invalid_when_appointment_overlaps(self):
        Appointment.objects.create(
            doctor=self.doctor,
            user=self.patient,
            date=self.work_date,
            time=time(10, 20),
        )
        form = AppointmentForm(data=self.get_valid_kwargs())
        form.instance.user = self.patient
        self.assertFalse(form.is_valid())
        self.assertIn("overlaps with an existing one", str(form.errors["__all__"]))

    def test_appointment_form_fails_if_missing_doctor_date_time_user(self):
        form = AppointmentForm(data={})
        form.instance.user = self.patient
        self.assertFalse(form.is_valid())
        self.assertIn("Missing data", str(form.errors["__all__"]))

    def test_form_valid_for_other_available_time_slot(self):
        Appointment.objects.create(
            doctor=self.doctor,
            user=self.patient,
            date=self.work_date,
            time=time(10, 20),
        )
        form = AppointmentForm(data=self.get_valid_kwargs(time=time(10, 40)))
        form.instance.user = self.patient
        self.assertTrue(form.is_valid())

    def test_form_excludes_instance_from_overlap_check(self):
        appointment = Appointment.objects.create(
            doctor=self.doctor,
            user=self.patient,
            date=self.work_date,
            time=time(10, 20),
        )
        form = AppointmentForm(data=self.get_valid_kwargs(), instance=appointment)
        form.instance.user = self.patient
        self.assertTrue(form.is_valid())
