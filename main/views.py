from django.http import HttpResponse
from django.shortcuts import render
from django.views.generic import TemplateView, CreateView, FormView
from main.models import Venue, Equipment, Request, RentedEquipment
from main.forms import RequestForm
from main import forms, views
from django.core.urlresolvers import reverse_lazy
from django.views.generic.edit import ModelFormMixin
from django.core.paginator import Paginator, InvalidPage, EmptyPage, PageNotAnInteger


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

# class RequestListView(TemplateView):
# 	login_url = "login.html"
# 	template_name = "osa.html"


# 	def get_context_data(self, **kwargs):
# 		context = super(RequestListView, self).get_context_data(**kwargs)
# 		context['request_list'] = Request.objects.all()
# 		paginator = Paginator(context['request_list'],20)
		
# 		page = request.GET.get('page')
# 		try:
# 			requests = paginator.page(page)
# 		except PageNotAnInteger:
# 			requests = paginator.page(1)
# 		except EmptyPage:
# 			requests = paginator.page(paginator.num_pages)
# 		return context


def listing(request):
	request_list = Request.objects.all()
	paginator = Paginator(request_list,10)
	page = request.GET.get('page')

	try:
		requests = paginator.page(page)
	except PageNotAnInteger:
		requests = paginator.page(1)
	except EmptyPage:
		requests = paginator.page(paginator.num_pages)

	return render(request, 'osa.html', {'requests': requests})


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
	    	
	    	RentedEquipmentView.getPK(self.object)
	    	return self.form_valid(form)
	    else:
	        return self.form_invalid(form)
		
	def form_valid(self, form):
		return super(RequestView, self).form_valid(form)

	def get_success_url(self):
		return reverse_lazy('success')

	def get_context_data(self, **kwargs):
		context = super(RequestView, self).get_context_data(**kwargs)
		context['venue_list'] = Venue.objects.all()
		context['equipment_list'] = Equipment.objects.all()
		
		return context

class RentedEquipmentView(FormView):
	template_name = 'request_form.html'
	form_class = forms.RentedEqForm
	pk = None

	def getPK(object):
		RentedEquipmentView.pk = object
		print(RentedEquipmentView.pk)
		re = RentedEquipment(request_id=object) 
		re.save()
		return super(RequestView)

	def post(self, request, *args, **kwargs):
		print('here')
		form = RentedEquipment.get_form
		for equipment in forms.cleaned_data.get('equipment_id'):
			equipment = RentedEqForm({'equipment_id':equipment_id})
			unit = form.cleaned_data.get('unit'+equipment)
			r = RentedEquipment(request_id=pk, equipment_id=equipment, unit=unit)
			r.save()
		
	def form_valid(self, form):
		return super(RentedEquipmentView, self).form_valid(form)

	def get_success_url(self):
		return reverse_lazy('success')

	def get_context_data(self, **kwargs):
		context = super(RentedEquipmentView, self).get_context_data(**kwargs)
		return context

	def get_form(self, form_class=None):
		if form_class is None: 
			form_class = RentedEquipmentView.get_form_class()
		return form_class(**RentedEquipmentView.get_form_kwargs())

	def get_form_class(self):
		return self.form_class