from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import (
    LoginView,
    LogoutView
)
from django.http import HttpResponse
from django.shortcuts import render
from django.urls import reverse
from django.views import View
from django.views.generic import (
    CreateView,
    TemplateView
)
from django.views.generic.edit import ModelFormMixin

from main import (
    forms,
    views
)
from main.models import (
    Equipment,
    Request,
    Venue
)


class SuccessView(LoginRequiredMixin, TemplateView):
	template_name = "success.html"
	login_url = "/"

class GuidelineView(LoginRequiredMixin, TemplateView):
	template_name = "guidelines.html"
	login_url = "/"

class MainView(LoginRequiredMixin, TemplateView):
	template_name = "index.html"
	login_url = "/"

class RateView(LoginRequiredMixin, TemplateView):
	template_name = "rates.html"
	login_url = "/"

class UserLoginView(LoginView):
	template_name = "login.html"

	def get_success_url(self):
		return reverse('index')


class RequestView(LoginRequiredMixin, CreateView):
	template_name = 'request_form.html'
	model = Request
	form_class = forms.RequestForm
	login_url = "/"
	
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
