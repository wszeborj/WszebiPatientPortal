from unittest.mock import patch

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


class TestAssignUserToAdminGroup(TestCase):
    def setUp(self):
        self.user = UserFactory(role=User.Role.ADMIN)

    def test_staff_group_assigned(self):
        assign_user_to_permission_group(self.user)
        group = Group.objects.get(name="admin_group")
        self.assertIn(group, self.user.groups.all())


class TestAssignGroupForUnsupportedRole(TestCase):
    def setUp(self):
        self.user = UserFactory(role=User.Role.PATIENT, assign_group=False)
        self.user.role = "UNKNOWN"
        self.user.save()

    def test_invalid_role_raises_exception(self):
        with self.assertRaises(Exception) as context:
            assign_user_to_permission_group(self.user)

        self.assertIn(
            "Provided User with role UNKNOWN can not be assigned to any group",
            str(context.exception),
        )


class TestAssignUserMissingGroup(TestCase):
    def setUp(self):
        self.user = UserFactory(role=User.Role.PATIENT, assign_group=False)
        Group.objects.filter(name="patient_group").delete()

    @patch("users.services.perm_assign.Group.objects.get")
    def test_group_does_not_exist_raises_exception(self, mock_get):
        mock_get.side_effect = Group.DoesNotExist

        with self.assertRaises(Exception) as context:
            assign_user_to_permission_group(self.user)
        self.assertIn("Group 'patient_group' not found", str(context.exception))
