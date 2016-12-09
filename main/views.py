from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.views.generic import TemplateView, CreateView, FormView, UpdateView, DeleteView
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
from django.contrib.auth.models import Group, User
import datetime, math
from django.utils.timezone import utc
from django.core.serializers.json import DjangoJSONEncoder
# from reportlab.pdfgen import canvas
# from reportlab.lib.pagesizes import letter
# from reportlab.lib.units import inch
# from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from django.core.serializers.json import DjangoJSONEncoder
import datetime, math, json
from django.urls import reverse

def group_check(user):
    return user.groups.filter(name__in=['ADA Staff',
                                        'CDMO Staff' 
                                        'Cashier Staff'
                                        'OSA Staff'])

class LoginView(FormView):
    success_url = '/main'
    success_office = '/main'
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
    url = '/main/'

    def get(self, request, *args, **kwargs):
        auth_logout(request)
        return super(LogoutView, self).get(request, *args, **kwargs)

class SuccessView(LoginRequiredMixin, TemplateView):
    template_name = "success.html"

class GuidelineView(TemplateView):
    template_name = "guidelines.html"

class MainView(TemplateView):
    template_name = "index.html"
    #get if the user logged in has pending requests

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
        	if 'pk' not in self.kwargs:
	            self.object = form.save()
	            self.object.requested_by = request.user
	            self.object.save()            
	        else:
        		pk = self.kwargs['pk']
	        	self.object = Request.objects.get(pk=pk)
	        	name = form.cleaned_data['name']
	        	organization = form.cleaned_data['organization']
	        	purpose = form.cleaned_data['purpose']
	        	participants = form.cleaned_data['participants']
	        	speakers = form.cleaned_data['speakers']
	        	venue = form.cleaned_data['venue_id']
	        	self.object.name = name
	        	self.object.organization = organization
	        	self.object.purpose = purpose
	        	self.object.participants = participants
	        	self.object.speakers = speakers
	        	self.object.venue_id = venue
	        	self.object.save()
	        	print ("name: ", name)
	        	print (self.object)

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

class EventLists(FormView):
	template_name = 'index.html'
	form_class = forms.RequestForm

	def get_context_data(self, **kwargs):
		context = super(EventLists, self).get_context_data(**kwargs)
		context['events'] = RequestedDate.objects.all().order_by('date_needed')[0:5]
		request_list = Request.objects.all()
		dates = RequestedDate.objects.all() 

		print (dates)
		context['dates'] = dates

		return context

class DatesView(FormView):
	template_name = 'request_form.html'
	form_class = forms.RequestDates

	def post(self, request, *args, **kwargs):
		form = self.get_form()
		if 'd' not in self.kwargs:
			print("here")
			if form.is_valid():
				print ('valid')
				date = form.cleaned_data['date_needed']
				st = form.cleaned_data['time_from']
				et = form.cleaned_data['time_to']
				self.object = form.save()
				
				return self.form_valid(form)
			else:
				return self.form_invalid(form)
		return self.form_valid(form)

	def get_success_url(self):
		return reverse_lazy("requestform", kwargs={'pk':self.object.request_id.pk})

	def get_context_data(self, **kwargs):
		context = super(DatesView, self).get_context_data(**kwargs)
		context['venue_list'] = Venue.objects.all()
		context['equipment_list'] = Equipment.objects.all()
		pk = 0
		d = 0
		if 'pk' in self.kwargs:
			pk = self.kwargs['pk']
			request_list = Request.objects.all()
			context['request'] = Request.objects.get(pk=pk)
			request_id = Request.objects.get(pk=pk)
			context['rented_equipments'] = RentedEquipment.objects.filter(request_id=request_id)
			context['requested_dates'] = RequestedDate.objects.filter(request_id=request_id)
			context['pk'] = pk

		return context

class RemoveDate(TemplateView):
	template_name = 'request_form.html'

	def get_success_url(self):
		pk = self.request.GET.get("pk")
		self.object = Request.objects.get(pk=pk)
		return reverse_lazy('requestform')

	def get_context_data(self, **kwargs):
		context = super(RemoveDate, self).get_context_data(**kwargs)
		context['venue_list'] = Venue.objects.all()
		context['equipment_list'] = Equipment.objects.all()

		q = self.request.GET.get("q")
		date = RequestedDate.objects.get(pk=q)

		context['request'] = date.request_id
		context['rented_equipments'] = RentedEquipment.objects.filter(request_id=date.request_id)
		context['requested_dates'] = RequestedDate.objects.filter(request_id=date.request_id)
		context['pk'] = date.request_id.pk
		print(q)
		date.delete()
		return context

class RemoveEquipments(TemplateView):
	template_name = 'request_form.html'

	def get_success_url(self):
		pk = self.request.GET.get("pk")
		self.object = Request.objects.get(pk=pk)
		return reverse_lazy('requestform')

	def get_context_data(self, **kwargs):
		context = super(RemoveEquipments, self).get_context_data(**kwargs)
		context['venue_list'] = Venue.objects.all()
		context['equipment_list'] = Equipment.objects.all()

		q = self.request.GET.get("q")
		eq = RentedEquipment.objects.get(pk=q)

		context['request'] = eq.request_id
		context['rented_equipments'] = RentedEquipment.objects.filter(request_id=eq.request_id)
		context['requested_dates'] = RequestedDate.objects.filter(request_id=eq.request_id)
		context['pk'] = eq.request_id.pk
		print(q)
		eq.delete()
		return context	


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
				group = Group.objects.get(name="OSA Staff")
				if group in user.groups.all():
					office_status.osa_remarks = form.cleaned_data['osa_remarks']
					office_status.osa_status = form.cleaned_data['osa_status']

					if office_status.osa_status == "R":
						request_id.status = False
						request_id.save()

				group = Group.objects.get(name="CDMO Staff")
				if group in user.groups.all():
					office_status.cdmo_remarks = form.cleaned_data['cdmo_remarks']
					office_status.cdmo_status = form.cleaned_data['cdmo_status']

					if office_status.cdmo_status == "R":
						request_id.status = False
						request_id.save()

				group = Group.objects.get(name="ADA Staff")
				if group in user.groups.all():
					office_status.ada_remarks = form.cleaned_data['ada_remarks']
					office_status.ada_status = form.cleaned_data['ada_status']

					if office_status.ada_status == "R":
						request_id.status = False
						request_id.save()

				group = Group.objects.get(name="Cashier Staff")
				if group in user.groups.all():
					office_status.cashier_remarks = form.cleaned_data['cashier_remarks']
					office_status.cashier_status = form.cleaned_data['cashier_status']

				office_status.save()
			return requestlisting(request)
		else:
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

	def get_context_data(self, **kwargs):

		context = super(RequesterView, self).get_context_data(**kwargs)
		user = 	self.request.user
		q = self.request.GET.get("q")
		print(q)
		request_id = Request.objects.get(pk=q)
		print(request_id)
		context['request'] = Request.objects.get(pk=request_id.pk)
		context['date_list'] = RequestedDate.objects.filter(request_id=request_id)
		context['equipment_list'] = RentedEquipment.objects.filter(request_id=request_id)
		context['office_status'] = OfficeStatus.objects.get(request_id=request_id)
		context['user'] = user
		print(context['date_list'])
		return context

def todatetime(time):
	return datetime.datetime.today().replace(hour=time.hour, minute=time.minute, second=time.second, microsecond=time.microsecond, tzinfo=time.tzinfo)

def timestodelta(starttime, endtime):
	return todatetime(endtime) - todatetime(starttime)

class SubmitForm(TemplateView):
	template_name = 'success.html'
	form_class = forms.RequestStatus

	def get_context_data(self, *args, **kwargs):
		tothours = 0
		total = 0
		bond = 0
		context = super(SubmitForm, self).get_context_data(**kwargs)
		pk = self.request.GET.get("request_id")
		r = Request.objects.get(pk=pk) # request object
		print (r);
		print (r.requested_by) 
		upk = r.requested_by # requester (user)
		print(upk)
		user = User.objects.get(pk=r.requested_by.pk) # user object
		print("user: ", user);

		# geting all the dates involved in a request
		dates = RequestedDate.objects.filter(request_id=r)
		if dates.count() > 0:
			venue = Venue.objects.get(pk=r.venue_id.pk) # the venue object
			for date in dates:
				timedif = timestodelta(date.time_from, date.time_to)
				print(timedif) # the time difference between from time_from to time_to

				hours, remainder = divmod(timedif.seconds, 3600)
				minutes, seconds = divmod(remainder, 60)
				minutes = hours*60 + minutes
				print("minutes: ",  minutes) # the total number of minutes
				hours = math.ceil(minutes/60) # minutes to hours
				print("hours: ", hours)

				# getting all equipments
				equipments = RentedEquipment.objects.filter(request_id=r)
				for equipment in equipments:
					e = equipment.equipment_id # e is the equipment object
					price = e.price # the price of the equipment

					# if AVR 1 or AS Conference Hall
					if venue.pk == 21 or venue.pk == 22 or venue.pk == 17 or venue.pk == 18:
						price = 150

					unit = equipment.unit # the number of equipments being rented

					print("pk: ", venue.pk)
					print("name: ", e.name) 
					print("price: ", price)

					# total += ((the number of equipments rented * the price of the equipment) * the total number of hours)
					total = unit * price * hours + total 
					print("total: ", total)

				tothours = tothours + hours # counts the total number of hours of all requested dates

			#get venue
			p = 0	
			if venue.unit == "hour":
				# checks what group the user belongs in and add the venue price to the current total times the number of hours
				if user.groups.filter(name="Outsiders").count():
					total = total + (venue.price_general*tothours)
					p = venue.price_general
				elif user.groups.filter(name="Alumni").count():
					total = total + (venue.price_alumni*tothours)
					p = venue.price_alumni
				else: 
					total = total + (venue.price_student*tothours)
					p = venue.price_student

			elif venue.unit == "package":
				# checks what group the user belongs in and add the venue price to the current total
				if user.groups.filter(name="Outsiders").count():
					total = total + venue.price_general * dates.count()
					p = venue.price_general
				elif user.groups.filter(name="Alumni").count():
					total = total + venue.price_alumni * dates.count()
					p = venue.price_alumni
				else: 
					total = total + venue.price_student * dates.count()
					p = venue.price_student

			if venue.pk == 21 or venue.pk == 22 or (venue.pk <= 44 and venue.pk >= 39):
				if total >= 12000:
					bond = 5000.00 
				if user.groups.filter(name="UPC Orgs").count():
					bond = 0
			print("bond: ", bond)
			print("total: ", total)


			if OfficeStatus.objects.filter(request_id=r).exists():
				print("request is already in officestatus model")
			else:
				# saving to Office Status
				o = OfficeStatus(request_id=r, osa_status='P', ada_status='P', cashier_status='P', cdmo_status='P')
				o.save()

			context['pk'] = pk
			context['equipment_list'] = equipments
			context['request'] = r
			context['total'] = total
			context['hours'] = hours
			context['date'] = date
			context['dates'] = dates
			context['tothours'] = tothours
			context['price'] = p
			context['bond'] = bond

			print("tothours: ", tothours)

			return context
		else:
			return super(SubmitForm, self).get_context_data(**kwargs)

def MyRequests(request):
	request_list = Request.objects.filter(requested_by = request.user)
	paginator = Paginator(request_list,10)
	page = request.GET.get('page')

	try:
		requests = paginator.page(page)
	except PageNotAnInteger:
		requests = paginator.page(1)
	except EmptyPage:
		requests = paginator.page(paginator.num_pages)

	return render(request, 'my_requests.html', {'requests': requests})

def chargeslip(request):
	logo1 = 'main/static/images/UP_logo.png'
	logo2 = 'main/static/images/UPC_logo.png'

	response = HttpResponse(content_type='application/pdf')
	response['Content-Disposition'] = 'attachment; filename="chargeslip.pdf"'

	print('pk')
	pk = request.GET.get("q")
	print(pk)
	#request itsekf
	r = Request.objects.get(pk=pk)
	user = User.objects.get(pk=r.requested_by.pk)

	#getting the user type of the user
	if user.groups.filter(name="UPC Orgs").exists():
		user_type = "UPC Orgs"
		venue_price = Decimal(Venue.objects.filter(request=r)[0].price_student)
		venue_unit = Venue.objects.filter(request=r)[0].unit
	elif user.groups.filter(name="Outsiders"):
		user_type = "Outsiders"
		venue_price = Decimal(Venue.objects.filter(request=r)[0].price_general)
		venue_unit = Venue.objects.filter(request=r)[0].unit
	elif user.groups.filter(name="Outsiders"):
		user_type = "Alumni"
		venue_price = Decimal(Venue.objects.filter(request=r)[0].price_alumni)
		venue_unit = Venue.objects.filter(request=r)[0].unit

	venue = Venue.objects.get(pk=r.venue_id.pk)
	if venue.unit == "hour":
		porh = '(Hourly Rate)'
	elif venue.unit == "package":
		porh = '(Package Rate)'
	#Draw things on the PDF. Here's where the PDF generation happens.
	#See the ReportLab documentation for the full list of functionality.
	#Create the PDF object, using the response object as its "file."
	p = canvas.Canvas(response)
	p.setLineWidth(.3)
	p.setFont('Helvetica', 12)
	p.drawImage(logo1, 270, 750, 0.5*inch, 0.5*inch, mask='auto')
	p.drawImage(logo2, 310, 750, 0.55*inch, 0.55*inch, mask='auto')
	p.drawString(230,730,'University of the Philippines')
	p.drawString(220,710,'Gorordo Avenue, Lahug, Cebu City')
	p.drawString(1*inch/2,690,'OR Number:')
	p.line(140,690,250,690)
	p.drawString(1*inch/2,670,'Name:')
	p.drawString(300,670,'Organization:')
	p.drawString(80,670, r.name)
	p.drawString(380, 670, r.organization)
	p.drawString(1*inch/2,650, 'Venue: ')
	venue_name = Venue.objects.filter(request=r)[0].name
	p.drawString(80, 650, venue_name)
	p.drawString(300, 650, porh)
	p.setFont('Helvetica-Bold', 12)
	p.drawString(1*inch/2, 610, 'Date/s')
	p.drawString(200, 610, 'Hours')
	p.drawString(300, 610, 'Rate')
	p.drawString(400, 610, 'Sub-total')
	p.setFont('Helvetica', 12)
	y = 590

	# calculating the expenses and printing it on canvas
	venue_total = 0
	user = User.objects.get(pk=r.requested_by.pk)

	#get dates
	dates = RequestedDate.objects.filter(request_id=r)
	total_hours = 0
	if dates.count() > 0:

		for date in dates:
			timedif = timestodelta(date.time_from, date.time_to)
			hours, remainder = divmod(timedif.seconds, 3600)
			print(timedif)
			p.drawString(1*inch/2, y, str(date.date_needed))
			p.drawString(200, y, str(hours))
			p.drawString(300, y, str(venue_price))
			total_hours = total_hours + hours
			

			#get venue
			venue = Venue.objects.get(pk=r.venue_id.pk)
			if venue.unit == "hour":
				if user.groups.filter(name="Outsiders").count():
					venue_total = venue_total + (venue_price*hours)
				elif user.groups.filter(name="Alumni").count():
					venue_total = venue_total + (venue_price*hours)
				else: 
					venue_total = venue_total + (venue_price*hours)
				p.drawString(400, y, str(venue_price*hours))
			elif venue.unit == "package":
				print("package hours: ", venue.hours)
				if user.groups.filter(name="Outsiders").count():
					venue_total = venue_total + venue_price
				elif user.groups.filter(name="Alumni").count():
					venue_total = venue_total + venue_price
				else: 
					venue_total = venue_total + venue_price
				p.drawString(400, y, str(venue_price))

			y = y - 20

	print("total: ", venue_total)
	p.drawString(300, y, 'Sub-total: ')
	p.drawString(400, y, str(venue_total))
	y = y - 30

	#for equipments
	p.setFont('Helvetica-Bold', 12)
	p.drawString(1*inch/2, y, 'Equipments Rented')
	y = y - 20
	p.drawString(1*inch/2, y, 'Equipment Name')
	p.drawString(150, y, 'Hours')
	p.drawString(250, y, 'Rate')
	p.drawString(350, y, 'Unit')
	p.drawString(450, y, 'Sub-total')
	p.setFont('Helvetica', 12)

	equipments = RentedEquipment.objects.filter(request_id=r)
	total = 0
	equipment_total = 0
	
	for equipment in equipments:
		e = equipment.equipment_id
		price = e.price
		unit = equipment. unit
		total = unit * price * total_hours
		equipment_total = equipment_total + total
		y = y - 20
		p.drawString(1*inch/2, y, e.name)
		p.drawString(160, y, str(total_hours))
		p.drawString(250, y, str(price))
		p.drawString(360, y, str(unit))
		p.drawString(450, y, str(total))

	y = y - 20
	p.drawString(350, y, 'Sub-total: ')
	p.drawString(450, y, str(equipment_total))
	y = y - 30
	bond = 0 
	print(user_type)
	if venue.pk == 21 or venue.pk == 22 or (venue.pk <= 44 and venue.pk >= 39):
		if venue_total >= 12000:
			if user_type is not "UPC Orgs":
				bond = 5000.00

	p.setFont('Helvetica-Bold', 12)
	p.drawString(1*inch/2, y, 'Bond: ')
	p.setFont('Helvetica', 12)
	p.drawString(350, y, 'Sub-total: ')
	p.drawString(450, y, str(bond))

	y = y - 30
	p.setFont('Helvetica-Bold', 12)
	p.drawString(350, y, 'TOTAL: ')
	overall = equipment_total + venue_total
	p.drawString(450, y, str(overall))
	p.setFont('Helvetica', 10)
	p.drawString(1*inch/2, y-40, "***In case a package has been chosen by the requster, number of hours won't matter.")

	p.showPage()
	p.save()
	
	return response

