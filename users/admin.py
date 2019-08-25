from django.contrib import admin

# Register your models here.
from users.models import Patient, Doctor, Guardian, TreatShip, GuardianShip, Appointment

admin.site.register(Patient)
admin.site.register(Doctor)
admin.site.register(Guardian)
admin.site.register(TreatShip)
admin.site.register(GuardianShip)
admin.site.register(Appointment)