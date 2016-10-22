from django.http import HttpResponse
from django.shortcuts import render
from django.views.generic import TemplateView, CreateView
from django.views import View
from main.models import Venue, Equipment, Request
from main import forms
from django.core.urlresolvers import reverse_lazy
from django.views.generic.edit import ModelFormMixin


def index(request):
    return HttpResponse("request")

def guidelines(request):
	template = 'main/guidelines.html'
	return render(request,template)

def login(request):
	template = 'main/login.html'
	return render(request,template)

def success(request):
	template = 'main/success.html'
	return render(request,template)

class home(TemplateView):
	template_name = "index.html"


class RequestView(CreateView):
	template_name = 'main/request_form.html'
	model = Request
	form_class = forms.RequestForm
	
	def form_valid(self, form):
 		self.object = form.save()
 		return super(ModelFormMixin, self).form_valid(form)

	def get_success_url(self):
		return reverse_lazy('success')

	def get_context_data(self, **kwargs):
		context = super(RequestView, self).get_context_data(**kwargs)
		context['venue_list'] = Venue.objects.all()
		context['equipment_list'] = Equipment.objects.all()
		return context