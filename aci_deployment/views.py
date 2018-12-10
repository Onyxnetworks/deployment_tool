from django.shortcuts import render, redirect, reverse
from django.http import HttpResponse
from django.core.files.storage import FileSystemStorage

import json
from .tasks import *
from aci_deployment.scripts.secrets import *

def endpoint_search(request):

    # Get subnet to use for search task.
    if request.method == 'POST' and 'endpoint_search' in request.POST:
        subnet = request.POST['endpoint_search']
        # Submit task to celery to process
        task = ENDPOINT_SEARCH.delay(BASE_URL, APIC_USERNAME, APIC_PASSWORD, subnet)

        # Return task id back to client for ajax use.
        return HttpResponse(json.dumps({'task_id': task.id}), content_type='application/json')        

    content = {}
    return render(request, 'aci_deployment/aci_endpoint_search.html', content)


def external_epg_deployment(request):
    # Present file upload to screen and give options to user
    if request.method == 'POST' and 'file' in request.FILES:
        file = request.FILES['file']
        location = request.POST['location']

        # Open workbook and build jason data structure.
        rule_list = EXTERNAL_EPG_EXCEL_OPEN_WORKBOOK(file, location)

        # Validate Request names and format
        task = EXTERNAL_EPG_VALIDATION.delay(rule_list, location, apic_username, apic_password)

        # Return task id.
        return HttpResponse(json.dumps({'task_id': task.id, 'rule_list': rule_list, 'location': location}), content_type='application/json')

    content = {}
    return render(request, 'aci_deployment/aci_external_epg_deployment.html', content)


def external_epg_deployment_push(request):
    # Deploy External EPG configuration
    if request.method == 'POST':
        response_json = request.body
        #response_json = json.dumps(response_json)
        data = json.loads(response_json)
        location = data['location']
        rule_list = data['rule_list']

        # Deploy APIC configuration
        task = EXTERNAL_EPG_DEPLOYMENT.delay(location, apic_username, apic_password, rule_list)

        # Return task id back to client for ajax use.
        return HttpResponse(json.dumps({'task_id': task.id}), content_type='application/json')
    content = {}
    return render(request, 'aci_deployment/aci_external_epg_deployment.html', content)

def contract_deployment(request):
    # Present file upload to screen and give options to user
    if request.method == 'POST' and 'file' in request.FILES:
        file = request.FILES['file']
        location = request.POST['location']

        # Open workbook and build jason data structure.
        rule_list = CONTRACT_DEPLOYMENT_EXCEL_OPEN_WORKBOOK(file, location)

        # Validate Request names and format
        task = CONTRACT_DEPLOYMENT_APIC_VALIDATION.delay(rule_list, location, apic_username, apic_password)

        # Return task id.
        return HttpResponse(json.dumps({'task_id': task.id, 'rule_list': rule_list, 'location': location}), content_type='application/json')
    content = {}
    return render(request, 'aci_deployment/aci_contract_deployment.html', content)


def contract_deployment_push(request):
    # Deploy External EPG configuration
    #if request.method == 'POST':
        #response_json = request.body
        # response_json = json.dumps(response_json)
        #data = json.loads(response_json)
        #location = data['location']
        #rule_list = data['rule_list']
        #print(rule_list)

        # Deploy APIC configuration
        #task = EXTERNAL_EPG_DEPLOYMENT.delay(location, apic_username, apic_password, rule_list)

        # Return task id back to client for ajax use.
        #return HttpResponse(json.dumps({'task_id': task.id}), content_type='application/json')
    content = {}
    return render(request, 'aci_deployment/aci_external_epg_deployment.html', content)