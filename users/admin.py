from django.contrib import admin

from .models import Doctor, Patient, Specialization, User

# Register your models here.

admin.site.register(User)
admin.site.register(Patient)
admin.site.register(Specialization)
admin.site.register(Doctor)
