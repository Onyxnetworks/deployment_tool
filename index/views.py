import json
from django.shortcuts import render, redirect
from django.http import HttpResponse
from celery.result import AsyncResult

from aci_deployment.scripts.baseline import APIC_LOGIN

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


def login(request):
    if request.method == 'POST':
        response_json = request.body
        data = json.loads(response_json)
        if 'username' and 'password' in data:
            username = data['username']
            password = data['password']
            environment = data['environment']

            print(username + password + environment)

            if environment == 'Production':
                request.session['prod_username'] = username
                request.session['prod_password'] = password


            elif environment == 'Pre-Production':
                request.session['ppe_username'] = username
                request.session['ppe_password'] = password

            elif environment == 'Lab':
                request.session['lab_username'] = username
                request.session['lab_password'] = password

            apic_cookie = APIC_LOGIN(base_url, username, password)

            if apic_cookie:
                request.session['APIC_COOKIE'] = apic_cookie
                return HttpResponse(json.dumps({'message': 'redirect', 'redirect-url': '/aci/endpoint_search/'}),
                                    content_type='application/json')

            else:
                message = 'Unable to authenticate, please check credentials.'
                return HttpResponse(json.dumps({'message': message}),
                                    content_type='application/json')


    return render(request, 'index/login.html')


def index(request):
    print('test')
    return render(request, 'index/home.html')


def logout(request):
    # Delete session data containing user details
    request.session.flush()
    return redirect(login)
