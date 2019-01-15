import json
from django.shortcuts import render, redirect
from django.http import HttpResponse
from celery.result import AsyncResult

from f5_deployment.scripts.baseline import bigip_login
from index.scripts.baseline import get_base_url
from index.scripts.external_links import *
# Function to get task state and results to be used by ajax.
def get_task_info(request):
    task_id = request.GET.get('task_id', None)
    if task_id is not None:
        task = AsyncResult(task_id)
        data = {
            'state': task.state,
            'result': task.result,
        }

        return HttpResponse(json.dumps(data), content_type='application/json')

    else:
        return HttpResponse('No job id given.')


def f5_operator_login(request):
    content = {}
    if request.method == 'POST':
        if 'username' and 'password' in request.POST:
            username = request.POST['username']
            password = request.POST['password']
            environment = request.POST['environment']
            request.session['user'] = username

            request.session['environment'] = environment
            if environment == 'Production':
                request.session['prod_username'] = username
                request.session['prod_password'] = password

            elif environment == 'Pre-Production':
                request.session['ppe_username'] = username
                request.session['ppe_password'] = password

            elif environment == 'Lab':
                request.session['lab_username'] = username
                request.session['lab_password'] = password

            # Get base url to use for authentication and scripts and try to login to UKDC1 APIC
            base_urls = get_base_url(environment)

            # Attempt to authenticate user
            # Get a value from the dictionary to use for login URL.
            base_url = next(iter(base_urls['F5'].values()))
            base_url = next(iter(base_url.values()))
            login_response = bigip_login(base_url, username, password)

            try:
                auth_token = login_response['token']['token']
            except:
                auth_token = False
            if auth_token:
                request.session['APIC_COOKIE'] = auth_token
                request.session['role'] = 'F5_Operator'
                return redirect(index)
            else:
                content = {'error': True, 'message': 'Unable to authenticate, please check credentials.'}
                redirect(request.path_info)

    return render(request, 'index/login.html', content)

def admin_login(request):
    content = {}
    if request.method == 'POST':
        if 'username' and 'password' in request.POST:
            username = request.POST['username']
            password = request.POST['password']
            environment = request.POST['environment']
            request.session['user'] = username

            request.session['environment'] = environment
            if environment == 'Production':
                request.session['prod_username'] = username
                request.session['prod_password'] = password

            elif environment == 'Pre-Production':
                request.session['ppe_username'] = username
                request.session['ppe_password'] = password

            elif environment == 'Lab':
                request.session['lab_username'] = username
                request.session['lab_password'] = password

            # Get base url to use for authentication and scripts and try to login to UKDC1 APIC
            base_urls = get_base_url(environment)

            # Attempt to authenticate user
            # Get a value from the dictionary to use for login URL.
            base_url = next(iter(base_urls['F5'].values()))
            base_url = next(iter(base_url.values()))
            login_response = bigip_login(base_url, username, password)

            try:
                auth_token = login_response['token']['token']
            except:
                auth_token = False
            if auth_token:
                request.session['APIC_COOKIE'] = auth_token
                request.session['role'] = 'Administrator'
                return redirect(index)
            else:
                content = {'error': True, 'message': 'Unable to authenticate, please check credentials.'}
                redirect(request.path_info)

    return render(request, 'index/login.html', content)


def index(request):

    role = request.session.get('role')
    user = request.session.get('user')
    environment = request.session.get('environment')
    content = {'environment': environment, 'url_list': url_list, 'role': role, 'user': user}
    return render(request, 'index/home.html', content)


def admin_logout(request):
    # Delete session data containing user details
    request.session.flush()
    return redirect(admin_login)
