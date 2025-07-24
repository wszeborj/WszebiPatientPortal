from django.contrib.auth.models import Group

from users.models import User


def assign_user_to_permission_group(user):
    role_to_group = {
        User.Role.PATIENT: "patient_group",
        User.Role.DOCTOR: "doctor_group",
        User.Role.ADMIN: "staff_group",
    }

    group_name = role_to_group.get(user.role)
    if group_name:
        group, _ = Group.objects.get_or_create(name=group_name)
        user.groups.add(group)
