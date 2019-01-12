from django.shortcuts import render, redirect
from django.http import HttpResponse

from .tasks import *
from index.scripts.baseline import get_base_url


def endpoint_search(request):

    # Get subnet to use for search task.
    if request.method == 'POST' and 'endpoint_search' in request.POST:
        subnet = request.POST['endpoint_search']

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
        task = ENDPOINT_SEARCH.delay(base_urls, username, password, subnet)

        # Return task id back to client for ajax use.
        return HttpResponse(json.dumps({'task_id': task.id}), content_type='application/json')        

    # Get base url to use
    environment = request.session.get('environment')
    base_urls = get_base_url(environment)
    url_dict = base_urls['ACI']
    location_list = list(url_dict.keys())


    content = {'environment': environment, 'locations': location_list}
    return render(request, 'aci_deployment/aci_endpoint_search.html', content)


def external_epg_deployment(request):
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
        return HttpResponse(json.dumps({'task_id': task.id, 'rule_list': rule_list, 'location': location}),
                            content_type='application/json')

    environment = request.session.get('environment')
    content = {'environment': environment}
    return render(request, 'aci_deployment/aci_external_epg_deployment.html', content)


def external_epg_deployment_push(request):
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
        return HttpResponse(json.dumps({'task_id': task.id, 'rule_list': rule_list, 'location': location}),
                            content_type='application/json')

    environment = request.session.get('environment')
    content = {'environment': environment}
    return render(request, 'aci_deployment/aci_contract_deployment.html', content)


def contract_deployment_push(request):
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
