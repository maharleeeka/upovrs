from django.conf.urls import url
from django.contrib.auth import views as auth_views

from . import views

urlpatterns = [
    url(r'^$', views.UserLoginView.as_view(), name='login'),
    url(r'^logout/$', auth_views.LogoutView.as_view(), name='logout'),
    url(r'^index/$', views.MainView.as_view(), name='index'),
    url(r'^requestform/$', views.RequestView.as_view(), name='requestform'),
    url(r'^guidelines/$', views.GuidelineView.as_view(), name='guidelines'),
    url(r'^rates/$', views.RateView.as_view(), name='rate'),
    url(r'^success/$', views.SuccessView.as_view(), name='success'),
]
