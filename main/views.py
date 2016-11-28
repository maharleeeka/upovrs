from django.http import HttpResponse
from django.shortcuts import render
from django.views.generic import TemplateView, CreateView, FormView, UpdateView
from main.models import Venue, Equipment, Request, RentedEquipment, RequestedDate, OfficeStatus
from main.forms import RequestForm, RemarksForm
from main import forms, views
from django.db.models import Q
from django.core.urlresolvers import reverse_lazy
from django.views.generic.edit import ModelFormMixin
from django.core.paginator import Paginator, InvalidPage, EmptyPage, PageNotAnInteger
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.decorators import permission_required
from django.utils.http import is_safe_url
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import REDIRECT_FIELD_NAME, login as auth_login, logout as auth_logout
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.debug import sensitive_post_parameters
from django.views.generic import FormView, RedirectView
from django.contrib.auth.models import Group

def group_check(user):
    return user.groups.filter(name__in=['ADA Staff',
                                        'CDMO Staff' 
                                        'Cashier Staff'
                                        'OSA Staff'])

class LoginView(FormView):
    success_url = '/main/requestform'
    success_office = '/main/requestlist'
    form_class = AuthenticationForm
    template_name = "login.html"
    redirect_field_name = '/templates/request_form'
    redirect_field_name_office = '/templates/osa'

    @method_decorator(sensitive_post_parameters('password'))
    @method_decorator(csrf_protect)
    @method_decorator(never_cache)
    def dispatch(self, request, *args, **kwargs):
        # Sets a test cookie to make sure the user has cookies enabled
        request.session.set_test_cookie()

        return super(LoginView, self).dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        #print(form.get_user())
        #print(form.get_user().groups.values_list('name', flat = True))
        auth_login(self.request, form.get_user())
        # If the test cookie worked, go ahead and
        # delete it since its no longer needed
        if self.request.session.test_cookie_worked():
            self.request.session.delete_test_cookie()

        return super(LoginView, self).form_valid(form)

    def get_success_url(self):

        if self.request.user.groups.filter(name="Approvers").exists():
            redirect_to = self.request.POST.get(self.redirect_field_name_office)
            if not is_safe_url(url=redirect_to, host=self.request.get_host()):
                redirect_to = self.success_office
            return redirect_to

        elif self.request.user.groups.filter(name="Requesters").exists():
            redirect_to = self.request.POST.get(self.redirect_field_name)
            if not is_safe_url(url=redirect_to, host=self.request.get_host()):
                redirect_to = self.success_url
            return redirect_to


class LogoutView(RedirectView):
    url = '/templates/login/'

    def get(self, request, *args, **kwargs):
        auth_logout(request)
        return super(LogoutView, self).get(request, *args, **kwargs)

class SuccessView(TemplateView):
    template_name = "success.html"

class GuidelineView(TemplateView):
    template_name = "guidelines.html"

class MainView(TemplateView):
    template_name = "index.html"

class RateView(TemplateView):
    template_name = "rates.html"

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

class RequestView(LoginRequiredMixin, FormView):
    login_url = 'login'
    # redirect_field_name = 'request_form'
    template_name = 'request_form.html'
    success_url = '/main/requestform'
    form_class = forms.RequestForm

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            self.object = form.save()
            o = OfficeStatus(request_id=self.object, osa_status='P', ada_status='P', cashier_status='P', cdmo_status='P')
            o.save()
            return self.form_valid(form)
        else:
            return self.form_invalid(form)
		
    def form_valid(self, form):
        return super(RequestView, self).form_valid(form)

    def get_success_url(self):
        return reverse_lazy("requestform", kwargs={'pk':self.object.pk})
        
    def get_context_data(self, **kwargs):
        context = super(RequestView, self).get_context_data(**kwargs)
        context['venue_list'] = Venue.objects.all()
        context['equipment_list'] = Equipment.objects.all()
        pk = 0
        if 'pk' in self.kwargs:
        	pk = self.kwargs['pk']
        	context['request'] = Request.objects.get(pk=pk)
        	request_id = Request.objects.get(pk=pk)
        	context['rented_equipments'] = RentedEquipment.objects.filter(request_id=request_id)
        	context['requested_dates'] = RequestedDate.objects.filter(request_id=request_id)
       	context['pk'] = pk

        return context

class RentedEquipmentsView(LoginRequiredMixin, FormView):
	template_name = 'request_form.html'
	form_class = forms.RentedEqForm

	def post(self, request, *args, **kwargs):
		form = self.get_form()
		if form.is_valid():
			print ('valid')
			print (form)
			self.object = form.save()
			return self.form_valid(form)
		else:
			return self.form_invalid(form)

	def get_success_url(self):
		return reverse_lazy("requestform", kwargs={'pk':self.object.request_id.pk})

	def get_context_data(self, **kwargs):
		context = super(RentedEquipmentsView, self).get_context_data(**kwargs)
		context['venue_list'] = Venue.objects.all()
		context['equipment_list'] = Equipment.objects.all()
		pk = 0
		if 'pk' in self.kwargs:
			pk = self.kwargs['pk']
			context['request'] = Request.objects.get(pk=pk)
			request_id = Request.objects.get(pk=pk)
			context['rented_equipments'] = RentedEquipment.objects.filter(request_id=request_id)
			context['requested_dates'] = RequestedDate.objects.filter(request_id=request_id)
		context['pk'] = pk
		return context

class DatesView(FormView):
	template_name = 'rates.html'
	form_class = forms.RequestDates

	def post(self, request, *args, **kwargs):
		form = self.get_form()
		if form.is_valid():
			print ('valid')
			print (form)
			self.object = form.save()
			return self.form_valid(form)
		else:
			return self.form_invalid(form)

	def get_success_url(self):
		return reverse_lazy("requestform", kwargs={'pk':self.object.request_id.pk})

	def get_context_data(self, **kwargs):
		context = super(DatesView, self).get_context_data(**kwargs)
		context['venue_list'] = Venue.objects.all()
		context['equipment_list'] = Equipment.objects.all()
		pk = 0
		if 'pk' in self.kwargs:
			pk = self.kwargs['pk']
			context['request'] = Request.objects.get(pk=pk)
			request_id = Request.objects.get(pk=pk)
			context['rented_equipments'] = RentedEquipment.objects.filter(request_id=request_id)
			context['requested_dates'] = RequestedDate.objects.filter(request_id=request_id)
		context['pk'] = pk
		return context

class SubmitForm(FormView):
	template_name = 'success.html'
	form_class = forms.RequestStatus

	def post(self, request, *args, **kwargs):
		form = self.get_form()
		if form.is_valid():
			print (form)
			self.object = form.save()
			return self.form_valid(form)
		else:
			return self.form_invalid(form)

	def get_success_url(self):
		return reverse_lazy("sucess")

def requestViewing(request):
	query = request.GET.get("q")
	aprroved = request.GET.get("a")
	user = request.user

	if query:
		queryset_list = Request.objects.get(pk=query)
		request_id = Request.objects.get(pk=query)
		date_list = RequestedDate.objects.filter(request_id=request_id)
		equipment_list = RentedEquipment.objects.filter(request_id=request_id)
		# office_status = OfficeStatus.objects.filter(request_id=request_id)[0:1]
		office_status = OfficeStatus.objects.get(request_id=request_id)

		if request.method == 'POST':
			form = RemarksForm(request.POST)
			if form.is_valid():
				office_status.osa_remarks = form.cleaned_data['osa_remarks']
				office_status.cdmo_remarks = form.cleaned_data['cdmo_remarks']
				office_status.cashier_remarks = form.cleaned_data['cashier_remarks']
				office_status.ada_remarks = form.cleaned_data['ada_remarks']

				group = Group.objects.get(name="OSA Staff")
				if group in user.groups.all():
					office_status.osa_status = form.cleaned_data['osa_status']
					print (form.cleaned_data['osa_status'])

				group = Group.objects.get(name="CDMO Staff")
				if group in user.groups.all():
					office_status.osa_status = form.cleaned_data['cdmo_status']

				group = Group.objects.get(name="ADA Staff")
				if group in user.groups.all():
					office_status.osa_status = form.cleaned_data['asa_status']

				group = Group.objects.get(name="Cashier Staff")
				if group in user.groups.all():
					office_status.osa_status = form.cleaned_data['cashier_status']

				office_status.save()
				print("here")

		return render(request, 'request_details.html', {'req': queryset_list, 'date_list': date_list, 'equipment_list': equipment_list, 'status': office_status})
	else:
		return render(request, 'request_details.html')

def requestlisting(request):
	request_list = OfficeStatus.objects.all()
	paginator = Paginator(request_list,10)
	page = request.GET.get('page')

	try:
		requests = paginator.page(page)
	except PageNotAnInteger:
		requests = paginator.page(1)
	except EmptyPage:
		requests = paginator.page(paginator.num_pages)

	return render(request, 'pending_requests.html', {'requests': requests})

class RequesterView(TemplateView):
	template_name = 'requester-view.html'

def invoiceViewing(request):
	queryset_requestlist = Request.objects.all()

	q = request.GET.get("quer")
	if q:
		queryset_requestlist = queryset_requestlist.filter(Q(pk__icontains=q))
		request_id = Request.objects.get(pk=q)
		equipment_list = RentedEquipment.objects.filter(request_id=request_id)

		paginator = Paginator(queryset_requestlist, 10)
		page = request.GET.get('page')

		try:
			requests = paginator.page(page)
		except PageNotAnInteger:
			requests = paginator.page(1)
		except EmptyPage:
			requests = paginator.page(paginator.num_pages)

		return render(request, 'payment_invoice.html', {'requests': requests, 'equipment_list': equipment_list})
	else:
		return render(request, 'payment_invoice.html')