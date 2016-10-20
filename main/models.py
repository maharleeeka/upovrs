from django.db import models

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
	remarks = models.CharField(max_length=500, blank=True)
	venue_id = models.ForeignKey(Venue, models.DO_NOTHING, db_column='venue_id', blank=True, null=True)
	date_needed = models.DateField(blank=True, null=True)
	time_from = models.TimeField(blank=True, null=True)
	time_to = models.TimeField(blank=True, null=True)
	
	

	def __str__(self):
		return str(self.name)

class RentedEquipment(models.Model):
	request_id = models.ForeignKey(Request, models.DO_NOTHING, db_column='request_id')
	equipment_id = models.ForeignKey(Equipment, models.DO_NOTHING, db_column='equipment_id')
	unit = models.DecimalField(max_digits = 4, decimal_places=0, null=True)

	def __str__(self):
		return str(self.pk)