from django.shortcuts import render, redirect
from django.http import HttpResponse

from .tasks import *
from index.scripts.baseline import get_base_url


def vs_deployment(request):
    content = {}
    return render(request, 'f5_deployment/vs_deployment.html', content)