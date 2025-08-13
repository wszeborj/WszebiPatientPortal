import logging

from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType

from appointments.models import Appointment
from schedules.models import ScheduleDay
from users.models import Specialization, User

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


ROLE_GROUP_PERMISSIONS = {
    User.Role.PATIENT: [
        "add_appointment",
        "view_appointment",
        "delete_appointment",
    ],
    User.Role.DOCTOR: [
        "add_scheduleday",
        "change_scheduleday",
        "delete_scheduleday",
        "view_scheduleday",
        "add_specialization",
        "view_scheduleday",
        "view_appointment",
        "change_appointment",
        "delete_appointment",
    ],
    User.Role.ADMIN: [
        "add_user",
        "change_user",
        "delete_user",
        "view_user",
        "add_doctor",
        "change_doctor",
        "delete_doctor",
        "view_doctor",
        "add_patient",
        "change_patient",
        "delete_patient",
        "view_patient",
        "add_scheduleday",
        "change_scheduleday",
        "delete_scheduleday",
        "view_scheduleday",
        "add_specialization",
        "change_specialization",
        "delete_specialization",
        "view_specialization",
        "add_appointment",
        "change_appointment",
        "delete_appointment",
        "view_appointment",
    ],
}

MODEL_CLASSES = [
    Appointment,
    ScheduleDay,
    Specialization,
    User,
]


def get_permission_objects(permission_codenames: str) -> list[Permission]:
    permissions = []
    for model in MODEL_CLASSES:
        content_type = ContentType.objects.get_for_model(model)
        perms = Permission.objects.filter(
            content_type=content_type, codename__in=permission_codenames
        )
        permissions.extend(perms)
    return permissions


def create_or_update_group_with_permissions(role: str) -> Group:
    permission_codenames = ROLE_GROUP_PERMISSIONS.get(role, [])
    group_name = f"{role.lower()}_group"

    group, created = Group.objects.get_or_create(name=group_name)

    permissions = get_permission_objects(permission_codenames)
    group.permissions.set(permissions)
    return group


def create_permission_groups():
    existing_group_names = set(Group.objects.values_list("name", flat=True))
    expected_group_names = {f"{role.lower()}_group" for role in ROLE_GROUP_PERMISSIONS}

    if expected_group_names.issubset(existing_group_names):
        logger.info("Groups already exist. Skipping creation.")
        return

    for role in ROLE_GROUP_PERMISSIONS:
        create_or_update_group_with_permissions(role)
