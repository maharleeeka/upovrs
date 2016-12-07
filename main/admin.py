from django.contrib import admin
from main.models import *
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin

# from .models import Profile

# Register your models here.
admin.site.register(Equipment)
admin.site.register(Office)
admin.site.register(Venue)
admin.site.register(Request)
admin.site.register(RentedEquipment)
admin.site.register(RequestedDate)
admin.site.register(OfficeStatus)

# class ProfileInline(admin.StackedInline):
#     model = Profile
#     can_delete = False
#     verbose_name_plural = 'Profile'
#     fk_name = 'user'

# class CustomUserAdmin(UserAdmin):
#     inlines = (ProfileInline, )
#     list_display = ('username', 'first_name', 'last_name', 'get_location')
#     list_select_related = ('profile', )

#     def get_location(self, instance):
#         return instance.profile.organization
#     get_location.short_description = 'Organization'

#     def get_inline_instances(self, request, obj=None):
#         if not obj:
#             return list()
#         return super(CustomUserAdmin, self).get_inline_instances(request, obj)


# admin.site.unregister(User)
# admin.site.register(User, CustomUserAdmin)
