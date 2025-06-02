from datetime import date, time, timedelta

from django.test import TestCase

from schedules.forms import ScheduleDayForm
from schedules.models import ScheduleDay
from users.factories import DoctorFactory


class ScheduleDayFormTests(TestCase):
    def setUp(self):
        self.doctor = DoctorFactory()

    def get_valid_data(self, **overrides):
        data = {
            "work_date": date.today(),
            "start_time": time(8, 0),
            "end_time": time(10, 0),
            "interval": 20,
        }
        data.update(overrides)
        return data

    def test_valid_form(self):
        form = ScheduleDayForm(data=self.get_valid_data(), doctor=self.doctor)
        self.assertTrue(form.is_valid())

    def test_invalid_time_order(self):
        form = ScheduleDayForm(
            data={
                "work_date": date.today(),
                "start_time": time(10, 0),
                "end_time": time(9, 0),
                "interval": 20,
            },
            user=self.doctor.user,
        )
        self.assertFalse(form.is_valid())
        self.assertIn("End time is before start time.", form.non_field_errors())

    def test_invalid_interval_not_multiple_of_5(self):
        data = self.get_valid_data(interval=17)
        form = ScheduleDayForm(data=data, doctor=self.doctor)
        self.assertFalse(form.is_valid())
        self.assertIn("interval", form.errors)

    def test_invalid_interval_too_small(self):
        data = self.get_valid_data(interval=4)
        form = ScheduleDayForm(data=data, doctor=self.doctor)
        self.assertFalse(form.is_valid())
        self.assertIn("interval", form.errors)

    def test_invalid_interval_too_large(self):
        data = self.get_valid_data(interval=61)
        form = ScheduleDayForm(data=data, doctor=self.doctor)
        self.assertFalse(form.is_valid())
        self.assertIn("interval", form.errors)

    def test_interval_longer_than_time_range(self):
        data = self.get_valid_data(
            start_time=time(9, 0), end_time=time(9, 10), interval=15
        )
        form = ScheduleDayForm(data=data, doctor=self.doctor)
        self.assertFalse(form.is_valid())
        self.assertIn("__all__", form.errors)
        self.assertIn("interval is longer", form.errors["__all__"][0])

    def test_interval_does_not_fit_evenly_in_range(self):
        data = self.get_valid_data(
            start_time=time(8, 0), end_time=time(8, 45), interval=20
        )
        form = ScheduleDayForm(data=data, doctor=self.doctor)
        self.assertFalse(form.is_valid())
        self.assertIn("Suggested end time", str(form.errors["__all__"]))

    def test_missing_interval(self):
        form = ScheduleDayForm(
            data={
                "work_date": date.today(),
                "start_time": time(8, 0),
                "end_time": time(10, 0),
                # missing interval
            },
            user=self.doctor.user,
        )
        self.assertFalse(form.is_valid())
        self.assertIn(
            "The field 'interval' must be filled out.", form.non_field_errors()
        )

    def test_schedule_overlap(self):
        ScheduleDay.objects.create(
            doctor=self.doctor,
            work_date=date.today(),
            start_time=time(9, 0),
            end_time=time(11, 0),
            interval=timedelta(minutes=15),
        )

        data = self.get_valid_data(start_time=time(10, 0), end_time=time(12, 0))
        form = ScheduleDayForm(data=data, doctor=self.doctor)
        self.assertFalse(form.is_valid())
        self.assertIn("overlaps", form.errors["__all__"][0])

    def test_defaults_set_from_last_schedule(self):
        ScheduleDay.objects.create(
            doctor=self.doctor,
            work_date=date(2025, 5, 10),
            start_time=time(7, 30),
            end_time=time(13, 45),
            interval=timedelta(minutes=20),
        )
        form = ScheduleDayForm(doctor=self.doctor)
        self.assertEqual(form.fields["start_time"].initial, time(7, 30))
        self.assertEqual(form.fields["end_time"].initial, time(13, 45))
        self.assertEqual(form.fields["interval"].initial, 20)
        self.assertEqual(form.fields["work_date"].initial, date(2025, 5, 10))
