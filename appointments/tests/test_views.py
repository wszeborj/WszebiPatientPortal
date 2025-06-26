from datetime import time, timedelta

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from appointments.factories import AppointmentFactory
from appointments.forms import AppointmentNoteForm
from appointments.models import Appointment
from schedules.factories import ScheduleDayFactory
from users.factories import DoctorFactory, PatientFactory


class UserAppointmentsViewTest(TestCase):
    def setUp(self):
        self.doctor = DoctorFactory()
        self.patient = PatientFactory()
        self.client.force_login(self.patient.user)

        today = timezone.now().date()

        AppointmentFactory.create(
            doctor=self.doctor,
            user=self.patient,
            date=today + timedelta(days=1),
            time=time(10, 0),
        )

        AppointmentFactory.create(
            doctor=self.doctor,
            user=self.patient,
            date=today - timedelta(days=1),
            time=time(9, 0),
        )

    def test_user_appointments_view_shows_upcoming_and_past(self):
        url = reverse("appointments:user-appointments")
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertIn("upcoming_appointment", response.context)
        self.assertIn("past_appointment", response.context)
        self.assertEqual(response.context["upcoming_appointment"].count(), 1)
        self.assertEqual(response.context["past_appointment"].count(), 1)


class DoctorAppointmentsViewTest(TestCase):
    def setUp(self):
        self.doctor = DoctorFactory()
        self.patient = PatientFactory()
        self.client.force_login(self.doctor.user)

        today = timezone.now().date()

        AppointmentFactory.create(
            doctor=self.doctor,
            user=self.patient,
            date=today + timedelta(days=1),
            time=time(10, 0),
        )

        AppointmentFactory.create(
            doctor=self.doctor,
            user=self.patient,
            date=today - timedelta(days=1),
            time=time(9, 0),
        )

    def test_doctor_appointments_view_shows_upcoming_and_past(self):
        url = reverse("appointments:doctor-appointments")
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertIn("upcoming_appointment", response.context)
        self.assertIn("past_appointment", response.context)
        self.assertEqual(response.context["upcoming_appointment"].count(), 1)
        self.assertEqual(response.context["past_appointment"].count(), 1)


class AppointmentCreateViewTest(TestCase):
    def setUp(self):
        self.doctor = DoctorFactory()
        self.patient = PatientFactory()
        self.client.force_login(self.patient.user)

        self.work_date = timezone.now().date() + timedelta(days=1)
        ScheduleDayFactory.create(
            doctor=self.doctor,
            work_date=self.work_date,
            start_time=time(9, 0),
            end_time=time(12, 0),
            interval=timedelta(minutes=20),
        )

    def test_get_appointment_create_form(self):
        url = reverse("appointments:appointment-create")
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "appointments/appointment_form.html")

    def test_post_valid_appointment_creates_object(self):
        url = reverse("appointments:appointment-create")
        data = {
            "doctor": self.doctor.pk,
            "date": timezone.now().date() + timedelta(days=1),
            "time": time(10, 0),
        }
        response = self.client.post(url, data)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(Appointment.objects.count(), 1)


class AppointmentConfirmationViewTest(TestCase):
    def setUp(self):
        self.doctor = DoctorFactory()
        self.patient = PatientFactory()
        self.client.force_login(self.patient.user)

        self.work_date = timezone.now().date() + timedelta(days=1)
        ScheduleDayFactory.create(
            doctor=self.doctor,
            work_date=self.work_date,
            start_time=time(9, 0),
            end_time=time(12, 0),
            interval=timedelta(minutes=20),
        )

        self.appointment = AppointmentFactory.create(
            user=self.patient, is_confirmed=False, date=self.work_date, time=time(10, 0)
        )

    def test_confirm_appointment(self):
        url = reverse(
            "appointments:appointment-confirm", kwargs={"pk": self.appointment.pk}
        )
        response = self.client.post(url)

        self.appointment.refresh_from_db()
        self.assertTrue(self.appointment.is_confirmed)
        self.assertRedirects(response, reverse("appointments:appointments-list"))


class AppointmentDeleteViewTest(TestCase):
    def setUp(self):
        self.doctor = DoctorFactory()
        self.patient = PatientFactory()
        self.appointment = AppointmentFactory.create(
            doctor=self.doctor, user=self.patient
        )
        self.client.force_login(self.patient.user)

    def test_delete_appointment_redirects_correctly(self):
        url = reverse("appointments:appointment-delete", args=[self.appointment.pk])
        response = self.client.post(url)
        self.assertRedirects(response, reverse("appointments:user-appointments"))
        self.assertFalse(Appointment.objects.filter(pk=self.appointment.pk).exists())


class AppointmentNoteViewTest(TestCase):
    def setUp(self):
        self.doctor = DoctorFactory()
        self.patient = PatientFactory()
        self.appointment = AppointmentFactory(doctor=self.doctor, user=self.patient)
        self.client.force_login(self.doctor.user)

    def test_note_detail_view_as_doctor(self):
        url = reverse("appointments:appointment-note", args=[self.appointment.pk])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "appointments/appointment_note_detail.html")
        self.assertEqual(response.context["appointment"], self.appointment)

    def test_note_detail_view_as_patient(self):
        self.client.force_login(self.patient.user)
        url = reverse("appointments:appointment-note", args=[self.appointment.pk])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.appointment.doctor)


class AppointmentNoteUpdateViewTest(TestCase):
    def setUp(self):
        self.doctor = DoctorFactory()
        self.patient = PatientFactory()
        self.appointment = AppointmentFactory(doctor=self.doctor, user=self.patient)
        self.client.force_login(self.doctor.user)

    def test_get_update_note_form(self):
        url = reverse(
            "appointments:appointment-note-update", args=[self.appointment.pk]
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.context["form"], AppointmentNoteForm)

    def test_post_update_note_form(self):
        url = reverse(
            "appointments:appointment-note-update", args=[self.appointment.pk]
        )
        data = {"notes": "Updated patient note."}
        response = self.client.post(url, data)
        self.assertRedirects(response, reverse("appointments:doctor-appointments"))
        self.appointment.refresh_from_db()
        self.assertEqual(self.appointment.notes, "Updated patient note.")
