from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand
from icecream import ic

from schedules.models import ScheduleDay
from users.models import Specialization, User

from ...models import Appointment


class Command(BaseCommand):
    def handle(self, *args, **options):
        create_permission_groups()
        self.stdout.write("Successfully created groups with permissions")

        # assign_group_to_user()
        # self.stdout.write("Successfully assigned groups to users")


def create_permission_groups():
    groups_permissions = {
        "patient_group": [
            "add_appointment",
            "change_appointment",
            "delete_appointment",
            "view_appointment",
        ],
        "doctor_group": [
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
        "staff_group": [
            "delete_specialization",
            "change_specialization",
        ],
    }
    groups_permissions["staff_group"].extend(groups_permissions.get("patient_group"))
    groups_permissions["staff_group"].extend(groups_permissions.get("doctor_group"))

    existing_groups = Group.objects.filter(
        name__in=groups_permissions.keys()
    ).values_list("name", flat=True)
    if set(groups_permissions.keys()).issubset(set(existing_groups)):
        print("Groups already exist. Skipping creation.")
        return

    perm_models = [Appointment, ScheduleDay, Specialization]

    for group_name, permission_codenames in groups_permissions.items():
        group, created = Group.objects.get_or_create(name=group_name)
        if created:
            print(f"Created group: {group_name}")
            for perm_model in perm_models:
                content_type = ContentType.objects.get_for_model(perm_model)
                all_permissions = Permission.objects.filter(content_type=content_type)
                for perm in all_permissions:
                    if perm.codename in permission_codenames:
                        group.permissions.add(perm)


def assign_group_to_user():
    role_to_group = {
        User.Role.PATIENT: "patient_group",
        User.Role.DOCTOR: "doctor_group",
        User.Role.ADMIN: "staff_group",
    }

    users = User.objects.all()
    for user in users:
        group_name = role_to_group.get(user.role)
        if group_name:
            group, _ = Group.objects.get_or_create(name=group_name)
            user.groups.add(group)

        ic(user)
        ic(user.get_all_permissions())
