import re
from django.shortcuts import render, redirect
from django.conf import settings

EXEMPT_URL = settings.LOGIN_URL.lstrip('/')

# Class to redirect user to login unless they have a valid APIC Cookie


class LoginRequiredMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        return response

    def process_view(self, request, view_func, view_args, view_kwargs):

        path = request.path_info.lstrip('/')
        # if not request.session.has_key('APIC_COOKIE'):
        #    if not path in EXEMPT_URL:
        #        print('Test')
        #        print(request.session.has_key('APIC_COOKIE'))
        #        return redirect(settings.LOGIN_URL)


        if request.session.has_key('APIC_COOKIE') and path in EXEMPT_URL:
            return redirect(settings.LOGIN_REDIRECT_URL)

        elif request.session.has_key('APIC_COOKIE') or path in EXEMPT_URL:
            return None

        else:
            return redirect(settings.LOGIN_URL)
