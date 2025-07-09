from datetime import timedelta

from django.utils.timezone import now

from ..models import ScheduleDay


def delete_older_schedules():
    """
    Configured as periodic task, is done everyday at 1 am in the night
    """
    date_back = now().date() - timedelta(days=30)
    old_schedules = ScheduleDay.objects.filter(work_date__lt=date_back)
    old_schedules.delete()
