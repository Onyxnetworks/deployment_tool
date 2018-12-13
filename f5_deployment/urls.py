from django.conf.urls import url, include

from . import views

urlpatterns = [
    url(r'^vs_deployment/$', views.vs_deployment, name='vs_deployment'),
]
