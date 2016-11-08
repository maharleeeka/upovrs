from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.MainView.as_view(), name='index'),
    # url(r'^$', views.HomepageView.as_view(), name='index'),
    url(r'^requestform/$', views.RequestView.as_view(), name='requestform'),
    url(r'^guidelines/$', views.GuidelineView.as_view(), name='guidelines'),
    url(r'^rates/$', views.RateView.as_view(), name='rate'),
    url(r'^success/$', views.SuccessView.as_view(), name='success'),
    url(r'^osa/requestlist/$', views.listing, name='osa'),
    url(r'^login/$', views.login, name='login'),
    url(r'^requestform/&id=(?P<pk>\d+)/$', views.RequestView.as_view(), name='requestform'),
]
