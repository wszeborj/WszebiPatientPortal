from django.contrib.auth.models import Group
from django.test import TestCase

from users.factories import UserFactory
from users.models import User
from users.services.perm_assign import assign_user_to_permission_group


class TestAssignUserToPatientGroup(TestCase):
    def setUp(self):
        self.user = UserFactory(role=User.Role.PATIENT)

    def test_patient_group_assigned(self):
        assign_user_to_permission_group(self.user)
        group = Group.objects.get(name="patient_group")
        self.assertIn(group, self.user.groups.all())


class TestAssignUserToDoctorGroup(TestCase):
    def setUp(self):
        self.user = UserFactory(role=User.Role.DOCTOR)

    def test_doctor_group_assigned(self):
        assign_user_to_permission_group(self.user)
        group = Group.objects.get(name="doctor_group")
        self.assertIn(group, self.user.groups.all())


class TestAssignUserToStaffGroup(TestCase):
    def setUp(self):
        self.user = UserFactory(role=User.Role.ADMIN)

    def test_staff_group_assigned(self):
        assign_user_to_permission_group(self.user)
        group = Group.objects.get(name="staff_group")
        self.assertIn(group, self.user.groups.all())
