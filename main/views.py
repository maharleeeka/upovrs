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
import datetime, math
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle

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
    url = '/main/requestform'

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
            r = Request.objects.get(pk=self.object.pk)
            r.requested_by = request.user
            r.save()
            print (r.requested_by)
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
		rid = Request.objects.filter(requested_by=user)
		if rid.count() > 0:
			request_id = Request.objects.get(pk=rid)
			print(request_id)
			context['request'] = Request.objects.get(pk=request_id.pk)
			context['date_list'] = RequestedDate.objects.filter(request_id=request_id)
			context['equipment_list'] = RentedEquipment.objects.filter(request_id=request_id)
			context['office_status'] = OfficeStatus.objects.get(request_id=request_id)
			context['user'] = user
			print(context['date_list'])
			return context
		else:
			return reverse_lazy("requestform")

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

def todatetime(time):
	return datetime.datetime.today().replace(hour=time.hour, minute=time.minute, second=time.second, microsecond=time.microsecond, tzinfo=time.tzinfo)

def timestodelta(starttime, endtime):
	return todatetime(endtime) - todatetime(starttime)

class SubmitForm(FormView):
	template_name = 'success.html'
	form_class = forms.RequestStatus

	def get_success_url(self):
		return reverse_lazy("sucess")

	def get_context_data(self, **kwargs):
		total = 0
		context = super(SubmitForm, self).get_context_data(**kwargs)
		pk = self.request.GET.get("request_id")
		r = Request.objects.get(pk=pk)

		#get dates
		dates = RequestedDate.objects.filter(request_id=r)
		for date in dates:
			timedif = timestodelta(date.time_from, date.time_to)
			print(timedif)

			#get equipments
			equipments = RentedEquipment.objects.filter(request_id=r)
			for equipment in equipments:
				e = equipment.equipment_id
				price = e.price
				unit = equipment.unit

				hours, remainder = divmod(timedif.seconds, 3600)
				minutes, seconds = divmod(remainder, 60)
				minutes = hours*60 + minutes
				print("minutes: ",  minutes)

				hours = math.ceil(minutes/60)
				print("hours: ", hours)
				print("name: ", e.name)
				print("price: ", e.price)

				total = unit * price * hours + total
				print("total: ", total)

		#get venue
		venue = Venue.objects.get(pk=r.venue_id.pk)
		if venue.unit == "hour":
			total = total + (venue.price_general*hours)
		elif venue.unit == "package":
			print("package hours: ", venue.hours)
			total = total + venue.price_general

		print("total: ", total)

		#saving to Office Status
		o = OfficeStatus(request_id=r, osa_status='P', ada_status='P', cashier_status='P', cdmo_status='P')
		o.save()

		context['pk'] = pk
		context['equipment_list'] = equipments
		context['request'] = r
		context['total'] = total
		context['hours'] = hours

		#generate pdf
		# path_wkthmltopdf = r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe'
		# config = pdfkit.configuration(wkhtmltopdf=path_wkthmltopdf)
		# pdfkit.from_url('submitForm', 'star.pdf', configuration=config)
		# template = 'success.html'
		# #context = Context 
		# html = template.render(context)
		# pdfkit.from_string(html, 'out.pdf')
		# pdf = open("out.pdf")
		# response = HttpResponse(pdf.read(), content_type='application/pdf')  # Generates the response as pdf response.
		# response['Content-Disposition'] = 'attachment; filename=output.pdf'
		# pdf.close()
		# pdfkit.from_string(context, 'out.pdf')

		return context

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