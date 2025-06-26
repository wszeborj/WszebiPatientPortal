from datetime import timedelta

from django.core import mail
from django.test import TestCase, override_settings
from django.utils.timezone import now

from appointments.factories import AppointmentFactory
from appointments.services.email_utils import send_upcoming_appointment_reminders


@override_settings(CELERY_TASK_ALWAYS_EAGER=True)
class SendAppointmentReminderTaskTest(TestCase):
    def setUp(self):
        self.appointment = AppointmentFactory.create(
            date=now().date() + timedelta(days=1),
            is_confirmed=True,
        )

    def test_send_upcoming_appointment_reminders_sends_email(self):
        self.assertEqual(len(mail.outbox), 0)

        send_upcoming_appointment_reminders()

        self.assertEqual(len(mail.outbox), 1)
        self.assertIn("Upcoming appointment reminder", mail.outbox[0].subject)
        self.assertIn(str(self.appointment.date), mail.outbox[0].body)
