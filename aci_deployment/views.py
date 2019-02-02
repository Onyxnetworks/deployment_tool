from django.shortcuts import render, redirect
from django.http import HttpResponse

from .tasks import *
from index.scripts.baseline import get_base_url
from index.scripts.external_links import *


def endpoint_search(request):
    user = request.session.get('user')
    role = request.session.get('role')
    # Get subnet to use for search task.
    if request.method == 'POST' and 'endpoint_search' in request.POST:
        search_string = request.POST['endpoint_search']
        filter_default = True
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

        # Submit task to celery to process
        task = ENDPOINT_SEARCH.delay(base_urls, filter_default, username, password, search_string)

        # Return task id back to client for ajax use.
        return HttpResponse(json.dumps({'task_id': task.id}), content_type='application/json')        

    # Get base url to use
    environment = request.session.get('environment')
    base_urls = get_base_url(environment)
    url_dict = base_urls['ACI']
    location_list = list(url_dict.keys())

    content = {'environment': environment, 'locations': location_list, 'url_list': url_list, 'role': role, 'user': user}
    return render(request, 'aci_deployment/aci_endpoint_search.html', content)


def ipg_search(request):
    user = request.session.get('user')
    role = request.session.get('role')
    # Get subnet to use for search task.
    if request.method == 'POST' and 'ipg_search' in request.POST:

        search_string = request.POST['ipg_search']
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

        # Submit task to celery to process
        task = aci_ipg_search.delay(base_urls, username, password, search_string)

        # Return task id back to client for ajax use.
        return HttpResponse(json.dumps({'task_id': task.id}), content_type='application/json')

    # Get base url to use
    environment = request.session.get('environment')
    base_urls = get_base_url(environment)
    url_dict = base_urls['ACI']
    location_list = list(url_dict.keys())

    content = {'environment': environment, 'locations': location_list, 'url_list': url_list, 'role': role, 'user': user}
    return render(request, 'aci_deployment/aci_ipg_search.html', content)


def external_epg_deployment(request):
    user = request.session.get('user')
    role = request.session.get('role')
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
        url_dict = base_urls['ACI']

        # Open workbook and build jason data structure.
        rule_list = EXTERNAL_EPG_EXCEL_OPEN_WORKBOOK(file, location)

        # Validate Request names and format
        task = EXTERNAL_EPG_VALIDATION.delay(rule_list, location, url_dict, username, password)

        # Return task id.
        return HttpResponse(json.dumps({'task_id': task.id, 'rule_list': rule_list, 'location': location,
                                        'role': role, 'user': user}),
                            content_type='application/json')

    # Get base url to use
    environment = request.session.get('environment')
    base_urls = get_base_url(environment)
    url_dict = base_urls['ACI']
    location_list = list(url_dict.keys())

    content = {'environment': environment, 'locations': location_list, 'url_list': url_list, 'role': role, 'user': user}
    return render(request, 'aci_deployment/aci_external_epg_deployment.html', content)


def external_epg_deployment_push(request):
    user = request.session.get('user')
    role = request.session.get('role')
    # Deploy External EPG configuration
    if request.method == 'POST':
        response_json = request.body
        data = json.loads(response_json)
        location = data['location']
        rule_list = data['rule_list']

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
        url_dict = base_urls['ACI']

        # Deploy APIC configuration
        task = EXTERNAL_EPG_DEPLOYMENT.delay(rule_list, location, url_dict, username, password)

        # Return task id back to client for ajax use.
        return HttpResponse(json.dumps({'task_id': task.id}), content_type='application/json')

    return redirect('/external_epg_deployment/')


def contract_deployment(request):
    user = request.session.get('user')
    role = request.session.get('role')
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
        url_dict = base_urls['ACI']

        # Open workbook and build jason data structure.
        rule_list = CONTRACT_DEPLOYMENT_EXCEL_OPEN_WORKBOOK(file, location)

        # Validate Request names and format
        task = CONTRACT_DEPLOYMENT_VALIDATION.delay(rule_list, location, url_dict, username, password)

        # Return task id.
        return HttpResponse(json.dumps({'task_id': task.id, 'rule_list': rule_list, 'location': location,
                                        'role': role, 'user': user}),
                            content_type='application/json')

    # Get base url to use
    environment = request.session.get('environment')
    base_urls = get_base_url(environment)
    url_dict = base_urls['ACI']
    location_list = list(url_dict.keys())

    content = {'environment': environment, 'locations': location_list, 'url_list': url_list, 'role': role, 'user': user}
    return render(request, 'aci_deployment/aci_contract_deployment.html', content)


def contract_deployment_push(request):
    user = request.session.get('user')
    role = request.session.get('role')
    # Deploy External EPG configuration
    if request.method == 'POST':
        response_json = request.body
        data = json.loads(response_json)
        location = data['location']
        rule_list = data['rule_list']

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
        url_dict = base_urls['ACI']

        # Deploy APIC configuration
        task = CONTRACT_DEPLOYMENT.delay(rule_list, location, url_dict, username, password)

        # Return task id back to client for ajax use.
        return HttpResponse(json.dumps({'task_id': task.id}), content_type='application/json')

    return redirect('/contract_deployment/')


def ipg_deployment(request):
    user = request.session.get('user')
    role = request.session.get('role')
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
        url_dict = base_urls['ACI']

        # Open workbook and build jason data structure.
        ipg_list = ipg_deployment_excel_open_workbook(file, location)
        # Validate Request names and format
        task = ipg_deployment_validation.delay(ipg_list, location, url_dict, username, password)

        # Return task id.
        return HttpResponse(json.dumps({'task_id': task.id, 'ipg_list': ipg_list, 'location': location,
                                        'role': role, 'user': user}),
                            content_type='application/json')

    # Get base url to use
    environment = request.session.get('environment')
    base_urls = get_base_url(environment)
    url_dict = base_urls['ACI']
    location_list = list(url_dict.keys())

    content = {'environment': environment, 'locations': location_list, 'url_list': url_list, 'role': role, 'user': user}
    return render(request, 'aci_deployment/aci_ipg_deployment.html', content)
