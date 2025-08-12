from datetime import date, time, timedelta
from unittest.mock import patch

from django.test import RequestFactory, TestCase
from django.urls import reverse
from django.utils import timezone

from appointments.factories import AppointmentFactory
from appointments.forms import AppointmentForm, AppointmentNoteForm
from appointments.models import Appointment
from appointments.views import AppointmentListView
from schedules.factories import ScheduleDayFactory
from users.factories import DoctorFactory, PatientFactory, UserFactory
from users.models import User


class AppointmentListViewTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def test_get_week_param_with_valid_week(self):
        request = self.factory.get("/appointments/?week=2025-07-15")
        view = AppointmentListView()
        view.request = request

        start_of_week, end_of_week, previous_week, next_week = view.get_week_param()

        self.assertEqual(start_of_week, date(2025, 7, 15))
        self.assertEqual(end_of_week, date(2025, 7, 21))
        self.assertEqual(previous_week, "2025-07-08")
        self.assertEqual(next_week, "2025-07-22")

    def test_get_week_param_without_week(self):
        today = date.today()
        expected_start = today - timedelta(days=today.weekday())
        expected_end = expected_start + timedelta(days=6)
        expected_prev = (expected_start - timedelta(days=7)).strftime("%Y-%m-%d")
        expected_next = (expected_start + timedelta(days=7)).strftime("%Y-%m-%d")

        request = self.factory.get("/appointments/")
        view = AppointmentListView()
        view.request = request

        start_of_week, end_of_week, previous_week, next_week = view.get_week_param()

        self.assertEqual(start_of_week, expected_start)
        self.assertEqual(end_of_week, expected_end)
        self.assertEqual(previous_week, expected_prev)
        self.assertEqual(next_week, expected_next)


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
        self.url = reverse("appointments:appointment-create")

    def test_get_appointment_create_form(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "appointments/appointment_form.html")

    def test_post_valid_appointment_creates_object(self):
        data = {
            "doctor": self.doctor.pk,
            "date": timezone.now().date() + timedelta(days=1),
            "time": time(10, 0),
        }
        response = self.client.post(self.url, data)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(Appointment.objects.count(), 1)

    @patch("appointments.views.logger")
    def test_post_invalid_form_appointment_log_error(self, mock_logger):
        data = {}
        response = self.client.post(self.url, data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Appointment.objects.count(), 0)

        mock_logger.error.assert_called()

        form = AppointmentForm(data={})
        form.instance.user = self.patient
        self.assertFalse(form.is_valid())

        self.assertIn("Missing data", str(form.errors["__all__"]))


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

        self.url = reverse(
            "appointments:appointment-confirm", kwargs={"pk": self.appointment.pk}
        )

    def test_appointment_confirm_get(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "appointments/appointment_confirm.html")

    def test_appointment_confirm_post(self):
        response = self.client.post(self.url)

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

    def test_delete_appointment_as_patient_redirects_to_user_appointments(self):
        self.client.force_login(self.patient.user)
        url = reverse("appointments:appointment-delete", args=[self.appointment.pk])
        response = self.client.post(url)
        self.assertRedirects(response, reverse("appointments:user-appointments"))
        self.assertFalse(Appointment.objects.filter(pk=self.appointment.pk).exists())

    def test_delete_appointment_as_doctor_redirects_to_doctor_appointments(self):
        self.client.force_login(self.doctor.user)
        appointment = AppointmentFactory(doctor=self.doctor)

        response = self.client.post(
            reverse("appointments:appointment-delete", kwargs={"pk": appointment.pk}),
            follow=True,
        )

        self.assertRedirects(response, reverse("appointments:doctor-appointments"))

    def test_delete_appointment_as_admin_redirects_to_appointments_list(self):
        admin_user = UserFactory(role=User.Role.ADMIN)
        self.client.force_login(admin_user)
        appointment = AppointmentFactory()

        response = self.client.post(
            reverse("appointments:appointment-delete", kwargs={"pk": appointment.pk}),
            follow=True,
        )

        self.assertRedirects(response, reverse("appointments:appointments-list"))


class AppointmentNoteViewTest(TestCase):
    def setUp(self):
        self.doctor = DoctorFactory()
        self.patient = PatientFactory()
        self.appointment = AppointmentFactory(doctor=self.doctor, user=self.patient)

    def test_note_detail_view_as_doctor(self):
        self.client.force_login(self.doctor.user)
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

    # todo: think about different output
    def test_note_detail_view_as_user_without_profile(self):
        user = UserFactory(role=User.Role.ADMIN)
        self.client.force_login(user)
        response = self.client.get(
            reverse("appointments:appointment-note", args=[self.appointment.pk])
        )
        self.assertEqual(response.status_code, 404)


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
