from django import forms
from django.forms import ModelForm
from main.models import Request, RentedEquipment


class RequestForm(forms.ModelForm):
	class Meta:
		model = Request
		fields = ['name', 'organization', 'purpose', 'participants', 'speakers', 'venue_id', 'date_needed', 'time_from', 'time_to', 'status']

class RentedEqForm(forms.ModelForm):
	class Meta:
		model = RentedEquipment
		exclude = ('request',)


