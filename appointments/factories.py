from datetime import datetime

import factory
from django.utils import timezone
from factory.django import DjangoModelFactory
from faker import Faker

from users.factories import DoctorFactory, PatientFactory

from .models import Appointment

fake = Faker()


class AppointmentFactory(DjangoModelFactory):
    class Meta:
        model = Appointment

    doctor = factory.SubFactory(DoctorFactory)
    user = factory.SubFactory(PatientFactory)
    date = factory.LazyFunction(lambda: timezone.now().date())
    time = factory.LazyFunction(
        lambda: datetime.time(hour=fake.random_int(min=8, max=16), minute=0)
    )
    notes = factory.Faker("paragraph", nb_sentences=2)
    created_at = factory.LazyFunction(timezone.now)
    modified_at = factory.LazyFunction(timezone.now)
    is_confirmed = factory.Faker("pybool")
