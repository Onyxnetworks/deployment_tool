from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.conf import settings
import logging
from .tasks import *
from index.scripts.baseline import get_base_url
from index.scripts.external_links import *

logging.basicConfig(filename='{0}aci_deployment.log'.format(settings.LOG_URL), format='%(asctime)s - aci - %(levelname)s - %(message)s', level=settings.LOG_LEVEL)

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
        logging.info('Action: EPG Deployment Validation | File Name: {0} | Location: {1}  | Environment: {2}  | Username: {3}'.format(file.name, location, environment, user))
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
        if file.name.endswith('yaml'):
            logging.info('File Name: {0}  |  Yaml File detected, running external_epg_open_yaml.'.format(file.name))
            rule_list = external_epg_open_yaml(file, location)

        else:
            logging.info('File Name: {0}  |  Excel File detected, running external_epg_open_yaml.'.format(file.name))
            rule_list = EXTERNAL_EPG_EXCEL_OPEN_WORKBOOK(file, location)

        # Validate Request names and format
        logging.info('File Name: {0}  |  Running External EPG Validation.'.format(file.name))
        task = EXTERNAL_EPG_VALIDATION.delay(rule_list, location, url_dict, username, password)
        logging.info('File Name: {0}  |  External EPG Validation sent to celery for processing..'.format(file.name))

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
        logging.info('Action: EPG Deployment Push | Location: {0}  | Environment: {1}  | Username: {2}'.format(location, environment, user))
        logging.info('Config Data: {0}'.format(rule_list))

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
        logging.info('Username: {0}  |  Running External EPG Push.'.format(user))
        task = EXTERNAL_EPG_DEPLOYMENT.delay(rule_list, location, url_dict, username, password)
        logging.info('Username: {0}  |   External EPG Push sent to celery for processing..'.format(user))

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
        logging.info('Action: Contract Deployment Validation | File Name: {0} | Location: {1}  | Environment: {2}  | Username: {3}'.format(file.name, location, environment, user))
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
        logging.info('File Name: {0}  |  Excel File detected, running contract_deployment_excel_open_workbook.'.format(file.name))
        rule_list = CONTRACT_DEPLOYMENT_EXCEL_OPEN_WORKBOOK(file, location)

        # Validate Request names and format
        logging.info('Username: {0}  |  Running Contract Validation.'.format(user))
        task = CONTRACT_DEPLOYMENT_VALIDATION.delay(rule_list, location, url_dict, username, password)
        logging.info('Username: {0}  |   Contract validation sent to celery for processing..'.format(user))

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
        logging.info('Action: Contract Deployment Push | Location: {0}  | Environment: {1}  | Username: {2}'.format(location, environment, user))
        logging.info('Config Data: {0}'.format(rule_list))
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
        logging.info('Username: {0}  |  Running Contract Push.'.format(user))
        task = CONTRACT_DEPLOYMENT.delay(rule_list, location, url_dict, username, password)
        logging.info('Username: {0}  |   Contract Push sent to celery for processing..'.format(user))
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
        logging.info('Action: Contract Deployment Validation | File Name: {0} | Location: {1}  | Environment: {2}  | Username: {3}'.format(file.name, location, environment, user))
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
        if file.name.endswith('yaml'):
            logging.info('File Name: {0}  |  Yaml File detected, running ipg_deployment_open_yaml.'.format(file.name))
            ipg_list = ipg_deployment_open_yaml(file, location)

        else:
            logging.info('File Name: {0}  |  Excel File detected, running ipg_deployment_excel_open_workbook.'.format(file.name))
            ipg_list = ipg_deployment_excel_open_workbook(file, location)

        # Validate Request names and format
        logging.info('Username: {0}  |  Running IPG Deployment validation.'.format(user))
        task = ipg_deployment_validation.delay(ipg_list, location, url_dict, username, password)
        logging.info('Username: {0}  |  IPG Deployment validation sent to celery for processing.'.format(user))

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


def ipg_deployment_push(request):
    user = request.session.get('user')
    role = request.session.get('role')
    # Deploy IPG configuration
    if request.method == 'POST':
        response_json = request.body
        data = json.loads(response_json)
        location = data['location']
        ipg_list = data['ipg_list']
        environment = request.session.get('environment')
        logging.info('Action: Contract Deployment Push | Location: {0}  | Environment: {1}  | Username: {2}'.format(location, environment, user))
        logging.info('Config Data: {0}'.format(ipg_list))
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
        logging.info('Username: {0}  |  Running IPG Deployment Push.'.format(user))
        task = ipg_deployment_post.delay(ipg_list, location, url_dict, username, password)
        logging.info('Username: {0}  |  IPG Deployment sent to celery for processing..'.format(user))
        # Return task id back to client for ajax use.
        return HttpResponse(json.dumps({'task_id': task.id}), content_type='application/json')

    return redirect('/ipg_deployment/')

