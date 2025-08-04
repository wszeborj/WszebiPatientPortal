from django.core.management.base import BaseCommand

from users.services.permissions_in_groups import create_permission_groups


class Command(BaseCommand):
    def handle(self, *args, **options):
        create_permission_groups()
        self.stdout.write("Successfully created groups with permissions")
