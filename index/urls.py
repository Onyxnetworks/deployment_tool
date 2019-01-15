from django.conf.urls import url, include
from . import views

urlpatterns = [
    url(r'^index/', views.index, name='index'),
    url(r'^login/', views.admin_login, name='admin_login'),
    url(r'^operator_login/', views.f5_operator_login, name='f5_operator_login'),
    url(r'^$', views.admin_login, name='admin_login'),
    url(r'^get_task_info/', views.get_task_info, name='get_task_info'),
    url(r'^logout/', views.admin_logout, name='admin_logout'),
]

