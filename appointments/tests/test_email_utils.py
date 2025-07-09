from unittest.mock import patch

from django.test import TestCase
from django.utils.timezone import now, timedelta

from appointments.factories import AppointmentFactory


class EmailUtilsTestCase(TestCase):
    def setUp(self):
        self.appointment = AppointmentFactory(
            is_confirmed=True, date=now().date() + timedelta(days=1)
        )

    @patch("appointments.services.email_utils.send_mail")
    def test_send_appointment_created_email(self, mock_send_mail):
        from appointments.services.email_utils import send_appointment_created_email

        send_appointment_created_email(self.appointment)
        mock_send_mail.assert_called_once()
        self.assertIn("Appointment booked", mock_send_mail.call_args[1]["subject"])

    @patch("appointments.services.email_utils.send_mail")
    def test_send_appointment_confirmed_email(self, mock_send_mail):
        from appointments.services.email_utils import send_appointment_confirmed_email

        send_appointment_confirmed_email(self.appointment)
        mock_send_mail.assert_called_once()
        self.assertIn("Appointment confirmed", mock_send_mail.call_args[1]["subject"])

    @patch("appointments.services.email_utils.send_mail")
    def test_send_note_added_email(self, mock_send_mail):
        from appointments.services.email_utils import send_note_added_email

        send_note_added_email(self.appointment)
        mock_send_mail.assert_called_once()
        self.assertIn("note added", mock_send_mail.call_args[1]["subject"])

    @patch("appointments.services.email_utils.send_mail")
    def test_send_appointment_deleted_email(self, mock_send_mail):
        from appointments.services.email_utils import send_appointment_deleted_email

        send_appointment_deleted_email(self.appointment)
        mock_send_mail.assert_called_once()
        self.assertIn("cancelled", mock_send_mail.call_args[1]["subject"])

    @patch("appointments.services.email_utils.send_mail")
    def test_send_appointment_reminder_email(self, mock_send_mail):
        from appointments.services.email_utils import send_appointment_reminder_email

        send_appointment_reminder_email(self.appointment)
        mock_send_mail.assert_called_once()
        self.assertIn("reminder", mock_send_mail.call_args[1]["subject"])

    @patch("appointments.services.email_utils.send_appointment_reminder_email")
    def test_send_upcoming_appointment_reminders(self, mock_reminder_func):
        from appointments.services.email_utils import (
            send_upcoming_appointment_reminders,
        )

        send_upcoming_appointment_reminders()
        mock_reminder_func.assert_called_once_with(self.appointment)
