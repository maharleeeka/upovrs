from django import forms
from django.forms import ModelForm
from main.models import Request


class RequestForm(forms.ModelForm):
	class Meta:
		model = Request
		fields = '__all__'