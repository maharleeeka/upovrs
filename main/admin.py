from django.contrib import admin
from main.models import *
from django.contrib.auth.models import User

# Register your models here.
admin.site.register(Equipment)
admin.site.register(Office)
admin.site.register(Venue)
admin.site.register(Request)
admin.site.register(RentedEquipment)
admin.site.register(RequestedDate)
# admin.site.register(User)