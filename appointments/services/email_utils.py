from django.conf import settings
from django.core.mail import send_mail


def send_appointment_created_email(appointment):
    send_mail(
        subject="Appointment booked",
        message=f"You have successfully booked an appointment on {appointment.date} at {appointment.time} for {appointment.doctor}.",
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[appointment.user.user.email],
    )


def send_note_added_email(appointment):
    send_mail(
        subject="New note added to your appointment",
        message=f"A note has been added to your appointment on {appointment.date} at {appointment.time} for {appointment.doctor}.",
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[appointment.user.user.email],
    )


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
