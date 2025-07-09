from datetime import timedelta

from django.test import TestCase
from django.utils.timezone import now

from schedules.factories import ScheduleDayFactory
from schedules.models import ScheduleDay
from schedules.services.schedule_clearing import delete_older_schedules


class DeleteOlderSchedulesTest(TestCase):
    def setUp(self):
        today = now().date()
        self.old_schedule = ScheduleDayFactory(work_date=today - timedelta(days=31))
        self.recent_schedule = ScheduleDayFactory(work_date=today - timedelta(days=29))

    def test_delete_old_schedules_only(self):
        self.assertEqual(ScheduleDay.objects.count(), 2)

        delete_older_schedules()

        schedules = ScheduleDay.objects.all()
        self.assertEqual(schedules.count(), 1)
        self.assertEqual(schedules.first().id, self.recent_schedule.id)
