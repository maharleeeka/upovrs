from django import forms
from django.forms import ModelForm
from django.forms.models import inlineformset_factory
from main.models import Request, RentedEquipment

class RequestForm(forms.ModelForm):
	class Meta:
		model = Request
		fields = ['name', 'organization', 'purpose', 'participants', 'speakers', 'venue_id', 'status']
	
class RentedEqForm(forms.ModelForm):
	class Meta:
		model = RentedEquipment
		fields = '__all__'