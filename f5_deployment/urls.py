from django.conf.urls import url, include

from . import views

urlpatterns = [
    url(r'^vs_deployment/$', views.vs_deployment, name='vs_deployment'),
    url(r'^vs_deployment_push/$', views.vs_deployment_push, name='vs_deployment_push'),
]
