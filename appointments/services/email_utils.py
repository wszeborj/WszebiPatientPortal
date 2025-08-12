import logging
from datetime import timedelta

from django.conf import settings
from django.core.mail import send_mail
from django.utils.timezone import now

from core.celery import app

from ..models import Appointment

logger = logging.getLogger(__name__)


@app.task
def send_appointment_created_email(appointment):
    send_mail(
        subject="Appointment booked",
        message=f"You have successfully booked an appointment on {appointment.date} at {appointment.time} for {appointment.doctor}."
        f"You need to confirm it",
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[appointment.user.user.email],
    )


@app.task
def send_appointment_confirmed_email(appointment):
    send_mail(
        subject="Appointment confirmed",
        message=f"You have successfully confirmed an appointment on {appointment.date} at {appointment.time} for {appointment.doctor}.",
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[appointment.user.user.email],
    )


@app.task
def send_note_added_email(appointment):
    send_mail(
        subject="New note added to your appointment",
        message=f"A note has been added to your appointment on {appointment.date} at {appointment.time} for {appointment.doctor}.",
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[appointment.user.user.email],
    )


@app.task
def send_appointment_deleted_email(appointment):
    send_mail(
        subject="Appointment cancelled",
        message=f"Your appointment on {appointment.date} at {appointment.time} for {appointment.doctor} has been cancelled.",
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[appointment.user.user.email],
    )


def send_appointment_reminder_email(appointment):
    send_mail(
        subject="Upcoming appointment reminder",
        message=f"Reminder: You have an appointment on {appointment.date} at {appointment.time} for {appointment.doctor}.",
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[appointment.user.user.email],
    )


@app.task
def send_upcoming_appointment_reminders():
    """
    Configured as periodic task, is done everyday at 1 am in the night
    """
    tomorrow = now().date() + timedelta(days=1)
    appointments = Appointment.objects.filter(
        date=tomorrow, is_confirmed=True
    ).select_related("user__user", "doctor__user")
    # print(f"Found {appointments.count()} appointments for {tomorrow}")

    for appointment in appointments:
        try:
            send_appointment_reminder_email(appointment)
            # print(f"Sent reminder for appointment id ={appointment.id}")
        except Exception as e:
            logger.error(
                f"Error during sending of reminder for appointment id ={appointment.id}: {e}"
            )
