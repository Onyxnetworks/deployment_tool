from django.conf.urls import url, include
from . import views

urlpatterns = [
    url(r'^index/', views.index, name='Index'),
    url(r'login/', views.login, name='Login'),
    url(r'^get_task_info/', views.get_task_info, name='get_task_info'),
]

