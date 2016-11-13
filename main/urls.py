from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.MainView.as_view(), name='index'),
    # url(r'^$', views.HomepageView.as_view(), name='index'),
    url(r'^requestform/$', views.RequestView.as_view(), name='requestform'),
    url(r'^requestform/(?P<pk>\d+)/$', views.RequestView.as_view(), name='requestform'),
    url(r'^submitEquipments/$', views.RentedEquipmentsView.as_view(), name='submitEquipments'),
    url(r'^submitDates/$', views.DatesView.as_view(), name='submitDates'),
    url(r'^requestform/(?P<pk>\d+)/$', views.RequestView.as_view(), name='requestform'),
    url(r'^guidelines/$', views.GuidelineView.as_view(), name='guidelines'),
    url(r'^rates/$', views.RateView.as_view(), name='rate'),
    url(r'^success/$', views.SuccessView.as_view(), name='success'),
    url(r'^login/$', views.LoginView.as_view(), name='login'),
    url(r'^viewrequestdetails/', views.requestViewing, name='viewrequestdetails'),
    url(r'^osaview/', views.listing, name='osaview'),
    url(r'^requestlist/$', views.requestlisting, name='requestlist')
]

