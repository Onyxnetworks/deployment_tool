from django.conf.urls import url, include
from . import views

urlpatterns = [
    url(r'^index/', views.index, name='index'),
    url(r'login/', views.login, name='login'),
    url(r'^get_task_info/', views.get_task_info, name='get_task_info'),
    url(r'^logout/', views.logout, name='logout'),
]

