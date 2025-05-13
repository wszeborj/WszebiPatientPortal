"""
https://docs.celeryq.dev/en/stable/django/first-steps-with-django.html
"""
import os

from celery import Celery
from celery.schedules import crontab
from django.conf import settings

# this code copied from manage.py
# set the default Django settings module for the 'celery' app.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")

# you can change the name here
app = Celery("core")

# read config from Django settings, the CELERY namespace would make celery
# config keys has `CELERY` prefix
app.config_from_object("django.conf:settings", namespace="CELERY")

# discover and load tasks.py from from all registered Django apps
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)

app.conf.beat_schedule = {
    "add-every-30-seconds": {
        "task": "appointments.services.email_utils.send_upcoming_appointment_reminders",
        "schedule": crontab(hour="1", minute="0"),
    },
}
app.conf.timezone = "CET"
