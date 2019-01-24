from django.conf.urls import url, include

from . import views

urlpatterns = [
    url(r'^endpoint_search/$', views.endpoint_search, name='endpoint_search'),
    url(r'^ipg_search/$', views.ipg_search, name='ipg_search'),
    url(r'^external_epg_deployment/$', views.external_epg_deployment, name='external_epg_deployment'),
    url(r'^external_epg_deployment_push/$', views.external_epg_deployment_push, name='external_epg_deployment_push'),
    url(r'^contract_deployment/$', views.contract_deployment, name='contract_deployment'),
    url(r'^contract_deployment_push/$', views.contract_deployment_push, name='contract_deployment_push'),

]
