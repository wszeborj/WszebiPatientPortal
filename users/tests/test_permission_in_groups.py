from unittest.mock import patch

from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.test import TestCase

from appointments.models import Appointment
from users.models import User
from users.services.permissions_in_groups import (
    ROLE_GROUP_PERMISSIONS,
    create_or_update_group_with_permissions,
    create_permission_groups,
    get_permission_objects,
)


class GetPermissionObjectsTests(TestCase):
    def test_get_permission_objects_returns_expected_permission(self):
        content_type = ContentType.objects.get_for_model(Appointment)
        perm, created = Permission.objects.get_or_create(
            codename="view_appointment",
            name="Can view appointment",
            content_type=content_type,
        )
        result = get_permission_objects(["view_appointment"])
        self.assertIn(perm, result)


class CreateOrUpdateGroupWithPermissionsTests(TestCase):
    def test_assign_group_to_role(self):
        group = create_or_update_group_with_permissions(User.Role.PATIENT)

        self.assertIsInstance(group, Group)
        self.assertEqual(group.name, "patient_group")
        self.assertTrue(group.permissions.exists())

    def test_uses_custom_group_name(self):
        group = create_or_update_group_with_permissions(
            User.Role.PATIENT, group_name="custom_group"
        )

        self.assertEqual(group.name, "custom_group")


class CreatePermissionGroupsTests(TestCase):
    @patch("users.services.perm_assign.create_or_update_group_with_permissions")
    @patch("users.services.perm_assign.logger")
    def test_skips_creation_if_groups_exist(self, mock_logger, mock_create_fn):
        # Given: wszystkie grupy istnieją
        for role in ROLE_GROUP_PERMISSIONS:
            Group.objects.create(name=f"{role.lower()}_group")

        # When
        create_permission_groups()

        # Then
        mock_create_fn.assert_not_called()
        mock_logger.info.assert_called_once_with(
            "Groups already exist. Skipping creation."
        )

    @patch("users.services.perm_assign.create_or_update_group_with_permissions")
    def test_creates_groups_if_not_all_exist(self, mock_create_fn):
        # Given: brak jakiejkolwiek grupy
        Group.objects.all().delete()

        # When
        create_permission_groups()

        # Then
        calls = [call_args[0][0] for call_args in mock_create_fn.call_args_list]
        expected_roles = set(ROLE_GROUP_PERMISSIONS.keys())
        self.assertEqual(set(calls), expected_roles)
