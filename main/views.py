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

		context['events'] = RequestedDate.objects.filter(status=True)[0:5]

		all_dates = RequestedDate.objects.all().order_by('date_needed')
		context['all'] = RequestedDate.objects.all().order_by('date_needed')

		for date in all_dates:
			request_id = date.request_id
			r = OfficeStatus.objects.get(request_id=request_id)

			if r.osa_status == "A" and r.ada_status =="A" and r.cdmo_status== "A":
				date.status = True
				date.save()

		context['approved'] = RequestedDate.objects.filter(status=True)
		context['pending'] = RequestedDate.objects.exclude(status=True)

		request_list = Request.objects.all()
		dates = RequestedDate.objects.all() 
		pending = RequestedDate.objects.exclude(status=True)

		print (pending)

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
			context['events'] = RequestedDate.objects.all()[0:5]

			print("tothours: ", tothours)

			return context
		else:
			return super(SubmitForm, self).get_context_data(**kwargs)

def MyRequests(request):
	request_list = Request.objects.filter(requested_by=request.user)
	print(request.user)
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
	# path_wkthmltopdf = r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe'
	# config = pdfkit.configuration(wkhtmltopdf=path_wkthmltopdf)
	# pdfkit.from_url('main/templates/success.html', '2.pdf', configuration=config)
	# template = get_template("success.html")
	# #context = Context({"data": SubmitForm.get_context_data})  # data is the context data that is sent to the html file to render the output. 
	# html = template.render(context)  # Renders the template with the context data.
	# pdfkit.from_string(html, 'out.pdf')
	# pdf = open("out.pdf")
	# response = HttpResponse(pdf.read(), content_type='application/pdf')  # Generates the response as pdf response.
	# response['Content-Disposition'] = 'attachment; filename=output.pdf'
	# pdf.close()
	# #os.remove("out.pdf")  # remove the locally created pdf file.
	# return response  # returns the response.
	# Create the HttpResponse object with the appropriate PDF headers.
	#context = super(SubmitForm, self).get_context_data(**kwargs)	
	logo1 = 'main/static/images/UP_logo.png'
	logo2 = 'main/static/images/UPC_logo.png'

	response = HttpResponse(content_type='application/pdf')
	response['Content-Disposition'] = 'attachment; filename="chargeslip.pdf"'

	# Create the PDF object, using the response object as its "file."
	p = canvas.Canvas(response)

	# Draw things on the PDF. Here's where the PDF generation happens.
	# See the ReportLab documentation for the full list of functionality.
	#canvas = canvas.Canvas("form.pdf", pagesize=letter)
	p.setLineWidth(.3)
	p.setFont('Helvetica', 12)
	p.drawImage(logo1, 270, 750, 0.5*inch, 0.5*inch, mask='auto')
	p.drawImage(logo2, 310, 750, 0.55*inch, 0.55*inch, mask='auto')
	p.drawString(230,730,'University of the Philippines')
	p.drawString(220,710,'Gorordo Avenue, Lahug, Cebu City')
	p.drawString(1*inch,690,'OR Number:')
	p.line(140,690,250,690)
	p.drawString(1*inch,670,'Name:')
	p.drawString(300,670,'Organization:')
	p.drawString(1*inch,650,'James Reid')
	p.drawString(300,650,'ABS-CBN Station/Star Magic')

	# p.drawString(275,725,'AMOUNT OWED:')
	# p.drawString(500,725,"$1,000.00")
	# p.line(378,723,580,723)

	# p.drawString(30,703,'RECEIVED BY:')
	# p.line(120,700,580,700)
	# p.drawString(120,703,"JOHN DOE")

	# Close the PDF object cleanly, and we're done.
	p.showPage()
	p.save()
	return response
