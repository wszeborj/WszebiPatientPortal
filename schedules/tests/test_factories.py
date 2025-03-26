import datetime

from django.test import TestCase

from ..factories import ScheduleDayFactory
from ..models import ScheduleDay


class TestScheduleDayFactory(TestCase):
    def test_schedule_day_factory_creates_instance(self):
        schedule = ScheduleDayFactory()

        assert isinstance(schedule, ScheduleDay)
        assert schedule.doctor is not None
        assert schedule.work_date is not None
        assert schedule.start_time is not None
        assert schedule.end_time is not None
        assert schedule.interval is not None
        assert schedule.created_at is not None
        assert schedule.modified_at is not None

        assert schedule.start_time == datetime.time(8, 0)
        assert schedule.end_time == datetime.time(16, 0)
        assert schedule.interval == datetime.timedelta(minutes=15)

    def test_create_batch_of_schedule_day_instances(self):
        batch_size = 3
        schedules = ScheduleDayFactory.create_batch(batch_size)

        assert len(schedules) == batch_size

        for schedule in schedules:
            assert isinstance(schedule, ScheduleDay)
        doctors = [schedule.doctor for schedule in schedules]
        assert len(set(doctors)) == batch_size
