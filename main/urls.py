from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^requestform/$', views.RequestView.as_view(), name='requestform'),
    url(r'^guidelines/$', views.guidelines, name='guidelines'),
    url(r'^success/$', views.success, name='success'),
    url(r'^login/$', views.login, name='login'),
]