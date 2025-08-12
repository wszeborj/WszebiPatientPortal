from datetime import date, time, timedelta
from unittest.mock import patch

from django.contrib.messages import get_messages
from django.test import TestCase
from django.urls import reverse

from schedules.factories import ScheduleDayFactory
from schedules.forms import ScheduleDayForm
from schedules.models import ScheduleDay
from users.factories import DoctorFactory, UserFactory
from users.models import User


class TestScheduleCalendarView(TestCase):
    def test_schedule_for_staff_user(self):
        user = UserFactory(role=User.Role.ADMIN, is_staff=True)

        ScheduleDayFactory.create_batch(3)

        self.client.force_login(user)
        response = self.client.get(reverse("schedules:schedule-calendar"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "calendar")
        self.assertEqual(len(response.context["schedule_days"]), 3)

    def test_schedule_for_non_doctor_non_staff_user(self):
        patient = UserFactory(role=User.Role.PATIENT)
        ScheduleDayFactory.create_batch(2)

        self.client.force_login(patient)
        response = self.client.get(reverse("schedules:schedule-calendar"))

        self.assertEqual(response.status_code, 403)


class ScheduleDayViewTests(TestCase):
    def setUp(self):
        self.doctor = DoctorFactory()
        self.client.force_login(self.doctor.user)

    def test_calendar_view_returns_200(self):
        url = reverse("schedules:schedule-calendar")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "schedules/schedule_calendar.html")

    def test_schedule_day_create_view_get(self):
        url = reverse("schedules:schedule-day-create")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.context["form"], ScheduleDayForm)

    def test_schedule_day_create_post_valid(self):
        url = reverse("schedules:schedule-day-create")
        data = {
            "work_date": date.today(),
            "start_time": time(8, 0),
            "end_time": time(10, 0),
            "interval": 20,
            "action": "save_exit",
        }
        response = self.client.post(url, data, follow=True)
        self.assertRedirects(response, reverse("schedules:schedule-calendar"))
        self.assertTrue(ScheduleDay.objects.filter(doctor=self.doctor).exists())
        messages = list(get_messages(response.wsgi_request))
        self.assertIn("Schedule saved!.", [m.message for m in messages])

    def test_post_with_action_save_redirects_and_sets_success_message(self):
        url = reverse("schedules:schedule-day-create")
        data = {
            "work_date": date.today(),
            "start_time": time(8, 0),
            "end_time": time(10, 0),
            "interval": 20,
            "action": "save",
        }

        response = self.client.post(url, data, follow=True)
        self.assertRedirects(response, url)

        messages = list(get_messages(response.wsgi_request))
        self.assertIn(
            "Schedule saved! You can add another day.", [m.message for m in messages]
        )
        self.assertTrue(ScheduleDay.objects.filter(doctor=self.doctor).exists())

    @patch("schedules.views.logger")
    def test_schedule_day_create_post_invalid(self, mock_logger):
        url = reverse("schedules:schedule-day-create")
        data = {
            "work_date": date.today(),
            "start_time": time(10, 0),
            "end_time": time(9, 0),  # error in time
            "interval": 20,
            "action": "save_exit",
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 200)
        form = response.context["form"]
        self.assertFalse(form.is_valid())
        self.assertIn("End time is before start time.", form.non_field_errors())

        mock_logger.error.assert_called()
        log_message = mock_logger.error.call_args[0][0]
        self.assertIn("End time is before start time", log_message)

    def test_schedule_day_create_post_invalid_interval_mismatch(self):
        url = reverse("schedules:schedule-day-create")
        data = {
            "work_date": date.today(),
            "start_time": time(8, 0),
            "end_time": time(9, 0),
            "interval": 45,  # not dividing evenly into 60
            "action": "save_exit",
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 200)
        form = response.context["form"]
        self.assertTrue(form.errors)
        self.assertIn("Suggested end time", form.non_field_errors()[0])

    def test_schedule_day_create_post_overlap(self):
        ScheduleDayFactory(
            doctor=self.doctor,
            work_date=date.today(),
            start_time=time(8, 0),
            end_time=time(10, 0),
        )

        url = reverse("schedules:schedule-day-create")
        data = {
            "work_date": date.today(),
            "start_time": time(9, 0),  # overlaps with above
            "end_time": time(11, 0),
            "interval": 15,
            "action": "save_exit",
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 200)
        form = response.context["form"]
        self.assertIn("overlaps with an existing one", form.non_field_errors()[0])

    def test_schedule_day_create_missing_field(self):
        url = reverse("schedules:schedule-day-create")
        data = {
            "work_date": date.today(),
            "start_time": time(8, 0),
            "end_time": time(10, 0),
            # no interval!
            "action": "save_exit",
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 200)
        form = response.context["form"]
        self.assertIn(
            "The field 'interval' must be filled out.", form.non_field_errors()
        )

    def test_schedule_day_create_prefills_from_last_schedule(self):
        ScheduleDayFactory(
            doctor=self.doctor,
            work_date=date(2025, 5, 27),
            start_time=time(9, 0),
            end_time=time(12, 0),
            interval=timedelta(minutes=20),
        )

        url = reverse("schedules:schedule-day-create")
        response = self.client.get(url)
        form = response.context["form"]
        self.assertEqual(form.fields["start_time"].initial, time(9, 0))
        self.assertEqual(form.fields["end_time"].initial, time(12, 0))
        self.assertEqual(form.fields["interval"].initial, 20)
        self.assertEqual(form.fields["work_date"].initial, date(2025, 5, 27))

    def test_schedule_day_update_view(self):
        schedule = ScheduleDayFactory(doctor=self.doctor)
        url = reverse("schedules:schedule-day-update", args=[schedule.pk])
        data = {
            "work_date": schedule.work_date,
            "start_time": time(10, 0),
            "end_time": time(12, 0),
            "interval": 20,
        }
        response = self.client.post(url, data, follow=True)
        self.assertRedirects(response, reverse("schedules:schedule-calendar"))
        schedule.refresh_from_db()
        self.assertEqual(schedule.start_time, time(10, 0))

    def test_schedule_day_delete_view(self):
        schedule = ScheduleDayFactory(doctor=self.doctor)
        url = reverse("schedules:schedule-day-delete", args=[schedule.pk])
        response = self.client.post(url, follow=True)
        self.assertRedirects(response, reverse("schedules:schedule-calendar"))
        self.assertFalse(ScheduleDay.objects.filter(pk=schedule.pk).exists())
