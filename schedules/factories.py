import datetime

import factory
from django.utils import timezone
from factory.django import DjangoModelFactory

from users.factories import DoctorFactory

from .models import ScheduleDay


class ScheduleDayFactory(DjangoModelFactory):
    class Meta:
        model = ScheduleDay

    doctor = factory.SubFactory(DoctorFactory)
    work_date = factory.LazyFunction(lambda: timezone.now().date())
    start_time = factory.LazyFunction(lambda: datetime.time(8, 0))
    end_time = factory.LazyFunction(lambda: datetime.time(16, 0))
    interval = factory.LazyFunction(lambda: datetime.timedelta(minutes=15))
    created_at = factory.LazyFunction(timezone.now)
    modified_at = factory.LazyFunction(timezone.now)
