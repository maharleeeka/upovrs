from django.http import HttpResponse
from django.shortcuts import render
from django.views.generic import TemplateView, CreateView, FormView
from main.models import Venue, Equipment, Request, RentedEquipment
from main.forms import RequestForm, RentedEqForm
from main import forms, views
from django.core.urlresolvers import reverse_lazy
from django.views.generic.edit import ModelFormMixin


def login(request):
	template = 'login.html'
	return render(request,template)

class SuccessView(TemplateView):
	template_name = "success.html"

class GuidelineView(TemplateView):
	template_name = "guidelines.html"

class MainView(TemplateView):
	template_name = "index.html"

class RateView(TemplateView):
	template_name = "rates.html"

class LoginView(TemplateView):
	template_name = "login.html"

	def form_valid(self, form):
 		self.object = form.save()
 		return super(ModelFormMixin, self).form_valid(form)

class RequestView(FormView):
	template_name = 'request_form.html'
	form_class = forms.RequestForm

	def post(self, request, *args, **kwargs):
	    form = self.get_form()
	    if form.is_valid():
	    	self.object = form.save()
	    	"""reqForm = RequestForm(request.POST, instance=Request())
	    	renEqForm = RentedEqForm(request.POST, instance=RentedEquipment())
	    	if reqForm.is_valid():
	    		new = reqForm.save()
	    		for cf in reqForm:
	    			new_req = cf.save(commit=False)
	    			new_req.request_id = new_req
	    			new_req.save()"""
	    	return self.form_valid(form)
	    else:
	        return self.form_invalid(form)
		
	def form_valid(self, form):
		
		#renEq = RentedEquipment(request_id=self.object,equipment_id='',unit='')
		#renEq.save()
		return super(RequestView, self).form_valid(form)

	def get_success_url(self):
		return reverse_lazy('success')

	def get_context_data(self, **kwargs):
		context = super(RequestView, self).get_context_data(**kwargs)
		context['venue_list'] = Venue.objects.all()
		context['equipment_list'] = Equipment.objects.all()
		return context



