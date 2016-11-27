from django import forms
from django.forms import ModelForm
from django.forms.models import inlineformset_factory
from main.models import Request, RentedEquipment, RequestedDate, OfficeStatus

class RequestForm(forms.ModelForm):
	class Meta:
		model = Request
		fields = ['name', 'organization', 'purpose', 'participants', 'speakers', 'venue_id', 'status']
	
class RentedEqForm(forms.ModelForm):
	class Meta:
		model = RentedEquipment
		fields = ['request_id', 'equipment_id', 'unit']

class RequestDates(forms.ModelForm):
	class Meta:
		model = RequestedDate
		fields = ['request_id', 'date_needed', 'time_from', 'time_to']

class RequestStatus(forms.ModelForm):
	class Meta:
		model = OfficeStatus
		fields = ['request_id', 'osa_status', 'cdmo_status', 'cashier_status', 'ada_status']

class RemarksForm(forms.ModelForm):
	class Meta:
		model = OfficeStatus
		fields = ['request_id', 'osa_remarks', 'cdmo_remarks', 'cashier_remarks', 'ada_remarks']

