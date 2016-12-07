from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

# class Profile(models.Model):
#     user = models.OneToOneField(User, on_delete=models.CASCADE)
#     organization = models.CharField(max_length=200, blank=True)

#     def __str__(self):  # __unicode__ for Python 2
#         return self.user.username

# @receiver(post_save, sender=User)
# def create_or_update_user_profile(sender, instance, created, **kwargs):
#     if created:
#         Profile.objects.create(user=instance)
#     	instance.profile.save()

# Create your models here.
class Equipment(models.Model):
	#equipment_id = models.AutoField()
	name = models.CharField(max_length=200, blank=True)
	price = models.DecimalField(max_digits=10, decimal_places=2, blank=True)
	unit = models.CharField(max_length=200, blank=True)

	def __str__(self):
		return str(self.name)


class Office(models.Model):
	#offices_id = models.AutoField()
	name = models.CharField(max_length=200)
	name_abbv = models.CharField(max_length=20)

	def __str__(self):
		return str(self.name)


class Venue(models.Model):
	#venue_id = models.AutoField()
	name = models.CharField(max_length=200)
	unit = models.CharField(max_length=200)
	price_general = models.DecimalField(max_digits=10, decimal_places=2)
	price_student = models.DecimalField(max_digits=10, decimal_places=2)
	price_alumni = models.DecimalField(max_digits=10, decimal_places=2)
	hours = models.DecimalField(max_digits=5, decimal_places=0, blank=True, null=True)
	description = models.CharField(max_length=500, blank=True)

	def __str__(self):
		return str(self.name)


class Request(models.Model):
	date_filed = models.DateField(auto_now=True, blank=True)
	name = models.CharField(max_length=200, blank=True)
	organization = models.CharField(max_length=200, blank=True)
	purpose = models.CharField(max_length=500, blank=True)
	participants = models.CharField(max_length=200, blank=True)
	speakers = models.CharField(max_length=200, blank=True)
	status = models.BooleanField(blank=True)
	venue_id = models.ForeignKey(Venue, models.DO_NOTHING, db_column='venue_id', blank=True, null=True)
	requested_by = models.ForeignKey(User, blank=True, null=True)
	
	
	def __str__(self):
		return str(self.name)

class RentedEquipment(models.Model):
	request_id = models.ForeignKey(Request, models.DO_NOTHING, db_column='request_id', null=True, blank=True)
	equipment_id = models.ForeignKey(Equipment, models.DO_NOTHING, db_column='equipment_id', null=True, blank=True)
	unit = models.DecimalField(max_digits = 4, decimal_places=0, null=True)

	def __str__(self):
		return str(self.pk)

class RequestedDate(models.Model):
	request_id = models.ForeignKey(Request, models.DO_NOTHING, db_column='request_id')
	date_needed = models.DateField(blank=True, null=True)
	time_from = models.TimeField(blank=True, null=True)
	time_to = models.TimeField(blank=True, null=True)

	def __str__(self):
		return str(self.pk)

class OfficeStatus(models.Model):
    OFFICE_STATUS = (
        ('R','Rejected'),
        ('A','Approved'),
        ('P','Pending'),
        ('AC', 'Active'),
    )
    request_id = models.ForeignKey(
        Request, models.DO_NOTHING, db_column='request_id')
    osa_status = models.CharField(max_length=8, choices=OFFICE_STATUS)
    osa_remarks = models.CharField(max_length=500, blank=True)
    cdmo_status = models.CharField(max_length=8, choices=OFFICE_STATUS)
    cdmo_remarks = models.CharField(max_length=500, blank=True)
    cashier_status = models.CharField(max_length=8, choices=OFFICE_STATUS)
    cashier_remarks = models.CharField(max_length=500, blank=True)
    ada_status = models.CharField(max_length=8, choices=OFFICE_STATUS)
    ada_remarks = models.CharField(max_length=500, blank=True)

    def __str__(self):
        return str(self.pk)