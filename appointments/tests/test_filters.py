from django.test import TestCase

from appointments.filters import DoctorFilter
from users.factories import DoctorFactory, SpecializationFactory, UserFactory
from users.models import Doctor


class DoctorFilterTests(TestCase):
    def setUp(self):
        self.cardio = SpecializationFactory(name="Cardiology")
        self.derma = SpecializationFactory(name="Dermatology")

        self.user1 = UserFactory(
            first_name="Anna", last_name="Nowak", email="a@example.com"
        )
        self.user2 = UserFactory(
            first_name="Jan", last_name="Kowalski", email="j@example.com"
        )

        self.doc1 = DoctorFactory(user=self.user1, title="Dr", confirmed=True)
        self.doc1.specialization.add(self.cardio)

        self.doc2 = DoctorFactory(user=self.user2, title="Prof", confirmed=True)
        self.doc2.specialization.add(self.derma)

    def test_filter_by_specialization(self):
        f = DoctorFilter(
            data={"specialization": [self.cardio.id]}, queryset=Doctor.objects.all()
        )
        self.assertIn(self.doc1, f.qs)
        self.assertNotIn(self.doc2, f.qs)

    def test_filter_by_doctor_name(self):
        f1 = DoctorFilter(data={"doctor_name": "Anna"}, queryset=Doctor.objects.all())
        f2 = DoctorFilter(data={"doctor_name": "Nowak"}, queryset=Doctor.objects.all())
        f3 = DoctorFilter(
            data={"doctor_name": "Anna Nowak"}, queryset=Doctor.objects.all()
        )

        self.assertIn(self.doc1, f1.qs)
        self.assertIn(self.doc1, f2.qs)
        self.assertIn(self.doc1, f3.qs)

        self.assertNotIn(self.doc2, f1.qs)

    def test_filter_by_title(self):
        f = DoctorFilter(data={"doctor_title": "Dr"}, queryset=Doctor.objects.all())
        self.assertIn(self.doc1, f.qs)
        self.assertNotIn(self.doc2, f.qs)

    def test_doctor_title_choices_function(self):
        from appointments.filters import get_doctor_title_choices

        choices = get_doctor_title_choices()
        self.assertIn(("Dr", "Dr"), choices)
        self.assertIn(("Prof", "Prof"), choices)
