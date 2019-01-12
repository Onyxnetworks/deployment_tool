from django.conf.urls import url, include

from . import views

urlpatterns = [
    url(r'^vs_deployment/$', views.vs_deployment, name='vs_deployment'),
    url(r'^vs_deployment_push/$', views.vs_deployment_push, name='vs_deployment_push'),
    url(r'^generic_search/$', views.generic_search, name='generic_search'),
    url(r'^f5_disable_enable_push/$', views.f5_disable_enable_push, name='f5_disable_enable_push'),
]
