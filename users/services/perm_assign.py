from django.contrib.auth.models import Group

from users.models import User

# from users.services.permissions_in_groups import add_permissions_to_group


def assign_user_to_permission_group(user: User):
    role_to_group = {
        User.Role.PATIENT: "patient_group",
        User.Role.DOCTOR: "doctor_group",
        User.Role.ADMIN: "admin_group",
    }

    group_name = role_to_group.get(user.role)
    if group_name:
        try:
            group = Group.objects.get(name=group_name)
            user.groups.add(group)
        except Group.DoesNotExist:
            raise Exception(
                f"Group '{group_name}' not found. Did you run `create_or_update_group_with_permissions`?"
            )
    else:
        raise Exception(
            f"Provided User with role {user.role} can not be assigned to any group"
        )

    # group_name = role_to_group.get(user.role)
    # if group_name:
    #     group, created = Group.objects.get_or_create(name=group_name)
    #     user.groups.add(group)
    #
    #     if created:
    #         add_permissions_to_group(group, user.role)
