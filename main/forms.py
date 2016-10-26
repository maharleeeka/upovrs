from django import forms
from django.forms import ModelForm
from main.models import Request, RentedEquipment


class RequestForm(forms.ModelForm):
	"""def __init__(self, instance=None, *args, **kwargs):
		_fields = ('equipment_id', 'unit',)
		_initial = model_to_dict(instance.request, _fields) if instance is not None else {}
		super(RequestForm, self).__init__(initial=_initial, instance=instance, *args, **kwargs)
		self.fields.update(fields_for_model(RentedEquipment, _fields))"""
	
	class Meta:
		model = Request
		fields = ['name', 'organization', 'purpose', 'participants', 'speakers', 'venue_id', 'status']
		#exclude = ('request',)

	"""def save(self, *args, **kwargs):
		r = self.instance.request_id
		r.venue_id = self.cleaned_data['venue_id']
		r.unit = self.cleaned_data['unit']
		r.save()
		profile = super(RequestForm, self).save(*args, **kwargs)
		return profile"""

class RentedEqForm(forms.ModelForm):
	class Meta:
		model = RentedEquipment
		exclude = ('request',)


