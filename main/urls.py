from django.conf.urls import url
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.models import Group

from . import views

urlpatterns = [
    url(r'^$', views.MainView.as_view(), name='index'),
    # url(r'^$', views.HomepageView.as_view(), name='index'),
    # url(r'^requestform/$', views.RequestView.as_view(), name='requestform'),
    url(r'^requestform/$', views.RequestView.as_view(), name='requestform'),
    # url(r'^requestform/(?P<pk>\d+)/$', views.RequestView.as_view(), name='requestform'),
    url(r'^submitEquipments/$', views.RentedEquipmentsView.as_view(), name='submitEquipments'),
    url(r'^submitDates/$', views.DatesView.as_view(), name='submitDates'),
    url(r'^requestform/(?P<pk>\d+)/$', 
        user_passes_test(lambda u: Group.objects.get(name='Requesters') in u.groups.all())
        (views.RequestView.as_view()),name="requestform"),
    url(r'^requestform/(?P<pk>\d+)/$', views.RequestView.as_view(), name='requestform'),
    url(r'^submitEquipments/$', views.RentedEquipmentsView.as_view(), name='submitEquipments'),
    url(r'^submitDates/$', views.DatesView.as_view(), name='submitDates'),
    # url(r'^requestform/(?P<pk>\d+)/$', 
    #     user_passes_test(lambda u: Group.objects.get(name='Requesters') in u.groups.all())
    #     (views.RequestView.as_view()),name="requestform"),
    url(r'^guidelines/$', views.GuidelineView.as_view(), name='guidelines'),
    url(r'^rates/$', views.RateView.as_view(), name='rate'),
    url(r'^success/$', views.SuccessView.as_view(), name='success'),
    url(r'^login/$', views.LoginView.as_view(), name='login'),
    url(r'^logout/$', views.LogoutView.as_view(), name='logout'),
    # url(r'^osa/requestlist$', views.RequestListView.as_view(), name='requestlist'),
    #url(r'^osa/requestlist$', views.listing, name='requestlist'),
    # url(r'^osa/requestlist$', 
    #     user_passes_test(lambda u: Group.objects.get(name='Approvers') in u.groups.all())
    #     (views.requestlisting),name="requestlist"),
    url(r'^viewrequestdetails/', views.requestViewing, name='viewrequestdetails'),
    url(r'^osaview/', views.listing, name='osaview'),
    url(r'^requestlist/$', 
        user_passes_test(lambda u: Group.objects.get(name='Approvers') in u.groups.all()) 
        (views.requestlisting), name="requeslist"),
    url(r'^submitForm/$', views.SubmitForm.as_view(), name='submitForm'),
    url(r'^submitDates/$', views.DatesView.as_view(), name='submitDates'),
    #url(r'^addRemarks/$', views.AddRemarksView.as_view(), name='addRemarks')

    url(r'^requester/$', views.RequesterView.as_view(), name='requester'),
    url(r'^cashier/$', views.CashierView.as_view(), name='cashier'),
    url(r'^invoice/$', views.invoiceViewing, name='invoice'),
]


