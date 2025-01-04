from django.contrib import admin

from .models import Appointment, ScheduleDay

admin.site.register(Appointment)
admin.site.register(ScheduleDay)
