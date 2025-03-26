from django.contrib.auth import get_user_model
from django.test import TestCase

from ..factories import (
    DoctorFactory,
    PatientFactory,
    SpecializationFactory,
    UserFactory,
)

User = get_user_model()


class TestUserFactory(TestCase):
    def test_create_user(self):
        user = UserFactory.create()
        assert isinstance(user, User)
        assert user.pk is not None
        assert user.username is not None
        assert user.email is not None
        assert user.phone_number is not None
        assert user.pesel is not None
        assert len(user.pesel) == 11
        assert len(user.phone_number) == 9
        assert user.role in [User.Role.PATIENT, User.Role.DOCTOR, User.Role.ADMIN]

    def test_create_admin_user(self):
        admin = UserFactory(role=User.Role.ADMIN)
        assert admin.role == User.Role.ADMIN
        assert admin.is_staff is True
        assert admin.is_superuser is False

    def test_create_patient_user(self):
        patient_user = UserFactory(role=User.Role.PATIENT)
        assert patient_user.role == User.Role.PATIENT
        assert patient_user.is_staff is False
        assert patient_user.is_superuser is False

    def test_create_doctor_user(self):
        doctor_user = UserFactory(role=User.Role.DOCTOR)
        assert doctor_user.role == User.Role.DOCTOR
        assert doctor_user.is_staff is False
        assert doctor_user.is_superuser is False

    def test_password_generation(self):
        user = UserFactory()
        assert user.check_password("password123") is True

    def test_unique_username(self):
        user1 = UserFactory(username="testuser")
        assert user1.username == "testuser"

        user2 = UserFactory(username="testuser")
        assert user1.pk == user2.pk

    def test_pesel_format(self):
        user = UserFactory(pesel="12345678901")
        assert user.pesel == "12345678901"
        assert len(user.pesel) == 11
        assert user.pesel.isdigit()

    def test_phone_number_format(self):
        user = UserFactory(phone_number="123456789")
        assert user.phone_number == "123456789"
        assert len(user.phone_number) == 9
        assert user.phone_number.isdigit()


class TestPatientFactory(TestCase):
    def test_create_patient(self):
        patient = PatientFactory()
        assert patient.pk is not None
        assert patient.user is not None
        assert patient.user.role == User.Role.PATIENT
        assert hasattr(patient, "created_at")
        assert hasattr(patient, "modified_at")

    def test_create_multiple_patients(self):
        patients = PatientFactory.create_batch(5)
        assert len(patients) == 5
        for patient in patients:
            assert patient.pk is not None
            assert patient.user.role == User.Role.PATIENT


class TestSpecializationFactory(TestCase):
    def test_create_specialization(self):
        spec = SpecializationFactory()
        assert spec.pk is not None
        assert spec.name is not None
        assert spec.description is not None

    def test_unique_name(self):
        spec1 = SpecializationFactory(name="Cardiology")
        assert spec1.name == "Cardiology"

        spec2 = SpecializationFactory(name="Cardiology")
        assert spec1.pk == spec2.pk


class TestDoctorFactory(TestCase):
    def test_create_doctor(self):
        doctor = DoctorFactory()
        assert doctor.pk is not None
        assert doctor.user is not None
        assert doctor.user.role == User.Role.DOCTOR
        assert doctor.title is not None
        assert doctor.description is not None
        assert hasattr(doctor, "created_at")
        assert hasattr(doctor, "modified_at")

    def test_specialization_assignment(self):
        doctor = DoctorFactory()
        assert doctor.specialization.count() > 0
        assert doctor.specialization.count() <= 3

    def test_specific_specializations(self):
        cardiology = SpecializationFactory(name="Cardiology")
        neurology = SpecializationFactory(name="Neurology")

        doctor = DoctorFactory(specialization=(cardiology, neurology))
        assert doctor.specialization.count() == 2
        assert "Cardiology" in [s.name for s in doctor.specialization.all()]
        assert "Neurology" in [s.name for s in doctor.specialization.all()]
