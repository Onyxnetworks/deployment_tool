from django.shortcuts import render, redirect
from django.http import HttpResponse

from .tasks import *
from index.scripts.baseline import get_base_url


def vs_deployment(request):
    # Present file upload to screen and give options to user
    if request.method == 'POST' and 'file' in request.FILES:
        file = request.FILES['file']
        location = request.POST['location']

        environment = request.session.get('environment')
        if environment == 'Production':
            username = request.session.get('prod_username')
            password = request.session.get('prod_password')


        elif environment == 'Pre-Production':
            # Need to put in an error as PPE search wont work!
            username = request.session.get('ppe_username')
            password = request.session.get('ppe_password')

        elif environment == 'Lab':
            username = request.session.get('lab_username')
            password = request.session.get('lab_password')

        # Get base url to use
        base_urls = get_base_url(environment)
        url_dict = base_urls['F5']

        # Open workbook and build jason data structure.
        vs_dict = vs_deployment_excel_open_workbook(file)

        # Validate Request names and format
        task = vs_deployment_validation.delay(vs_dict, location, url_dict, username, password)

        # Return task id.
        return HttpResponse(json.dumps({'task_id': task.id, 'location': location}),
                            content_type='application/json')

    # Get base url to use
    environment = request.session.get('environment')
    base_urls = get_base_url(environment)
    url_dict = base_urls['F5']
    location_list = list(url_dict.keys())


    content = {'environment': environment, 'locations': location_list}
    return render(request, 'f5_deployment/f5_vs_deployment.html', content)


def vs_deployment_push(request):
    # Deploy LTM Virtual Server configuration
    if request.method == 'POST':
        response_json = request.body
        data = json.loads(response_json)
        location = data['location']
        vs_dict = data['vs_dict']


        environment = request.session.get('environment')
        if environment == 'Production':
            username = request.session.get('prod_username')
            password = request.session.get('prod_password')


        elif environment == 'Pre-Production':
            # Need to put in an error as PPE search wont work!
            username = request.session.get('ppe_username')
            password = request.session.get('ppe_password')

        elif environment == 'Lab':
            username = request.session.get('lab_username')
            password = request.session.get('lab_password')

        # Get base url to use
        base_urls = get_base_url(environment)
        url_dict = base_urls['F5']

        # Deploy APIC configuration
        task = virtual_server_deployment.delay(vs_dict, location, url_dict, username, password)

        # Return task id back to client for ajax use.
        return HttpResponse(json.dumps({'task_id': task.id}), content_type='application/json')

    return redirect('/vs_deployment/')


def generic_search(request):
    print(request.POST)
    # Get data to use for search task.
    if request.method == 'POST' and 'f5_search' in request.POST:
        search_string = request.POST['f5_search']
        request_type = request.POST['request_type']

        environment = request.session.get('environment')
        if environment == 'Production':
            username = request.session.get('prod_username')
            password = request.session.get('prod_password')

        if environment == 'Pre-Production':
            # Need to put in an error as PPE search wont work!
            username = request.session.get('ppe_username')
            password = request.session.get('ppe_password')

        if environment == 'Lab':
            username = request.session.get('lab_username')
            password = request.session.get('lab_password')

        # Get base url to use
        base_urls = get_base_url(environment)

        task = f5_generic_search.delay(base_urls, request_type, search_string, username, password)

        # Return task id back to client for ajax use.
        return HttpResponse(json.dumps({'task_id': task.id}), content_type='application/json')


    environment = request.session.get('environment')
    content = {'environment': environment}
    return render(request, 'f5_deployment/f5_generic_search.html', content)

def f5_disable_enable_push(request):
    # Get data to use Enable Disable task
    if request.method == 'POST':
        response_json = request.body
        data = json.loads(response_json)

        action = data['action']
        f5_selected_items = data['f5_selected_items']
        search_string = data['cached_search_string']
        request_type = data['cached_request_type']

        environment = request.session.get('environment')
        if environment == 'Production':
            username = request.session.get('prod_username')
            password = request.session.get('prod_password')

        if environment == 'Pre-Production':
            # Need to put in an error as PPE search wont work!
            username = request.session.get('ppe_username')
            password = request.session.get('ppe_password')

        if environment == 'Lab':
            username = request.session.get('lab_username')
            password = request.session.get('lab_password')

        # Get base url to use
        base_urls = get_base_url(environment)

        task = f5_disable_enable.delay(base_urls, action, f5_selected_items, request_type, search_string, username, password)

        # Return task id back to client for ajax use.
        return HttpResponse(json.dumps({'task_id': task.id}), content_type='application/json')
