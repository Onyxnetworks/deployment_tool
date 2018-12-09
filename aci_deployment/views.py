from django.shortcuts import render, redirect, reverse
from django.http import HttpResponse
from django.core.files.storage import FileSystemStorage

import json
from .tasks import *


def endpoint_search(request):

    # Get subnet to use for search task.
    if request.method == 'POST' and 'endpoint_search' in request.POST:
        subnet = request.POST['endpoint_search']
        BASE_URL = 'https://sandboxapicdc.cisco.com/api/'
        APIC_USERNAME = 'admin'
        APIC_PASSWORD = 'ciscopsdt'

        # Submit task to celery to process
        task = SUBNET_SEARCH.delay(BASE_URL, APIC_USERNAME, APIC_PASSWORD, subnet)

        # Return task id back to client for ajax use.
        return HttpResponse(json.dumps({'task_id': task.id}), content_type='application/json')        

    content = {}
    return render(request, 'aci_deployment/aci_endpoint_search.html', content)


def external_epg_deployment(request):
    base_url = 'https://sandboxapicdc.cisco.com/api/'
    apic_username = 'admin'
    apic_password = 'ciscopsdt'
    # Present file upload to screen and give options to user
    if request.method == 'POST' and 'file' in request.FILES:
        file = request.FILES['file']
        location = request.POST['location']
        #fs = FileSystemStorage()
        #filename = fs.save(file.name, file)
        #uploaded_file_url = fs.url(filename)
        #fs.delete(filename)

        # Open workbook and build jason data structure.
        rule_list = EXTERNAL_EPG_EXCEL_OPEN_WORKBOOK(file, location)
        request.session['LOCATION'] = location
        request.session['RULE_LIST'] = rule_list
        # Validate Request names and format
        task = EXTERNAL_EPG_VALIDATION.delay(rule_list, location, apic_username, apic_password)
        print(request.session.get('RULE_LIST'))
        # Return file url.
        return HttpResponse(json.dumps({'task_id': task.id}), content_type='application/json')
    content = {}
    return render(request, 'aci_deployment/aci_external_epg_deployment.html', content)


def contract_deployment(request):
    APIC_USERNAME = 'admin'
    APIC_PASSWORD = 'ciscopsdt'
    VALIDATION_ERROR = False
    APIC_VALIDATION_ERROR = False
    # Present file upload to screen and give options to user
    if request.method == 'POST' and 'myfile' in request.FILES:
        myfile = request.FILES['myfile']
        if ' ' not in myfile.name:
            myfile = request.FILES['myfile']
            Location = request.POST['dc_select']
            request.session['LOCATION'] = Location
            request.session['WORKBOOK_NAME'] = myfile.name
            print(myfile)
            print(Location)
            # Try to open workbook and build Rule List dict.
            try:
                RULE_LIST = CONTRACT_DEPLOYMENT_EXCEL_OPEN_WORKBOOK(myfile, Location)

            except:

                del request.session['LOCATION']
                del request.session['WORKBOOK_NAME']
                content = {'upload_error': 'Unable to open Workbook, check tabs and location.', 'nbar': 'Contract_Deployment', 'errors': True}

                return render(request, 'aci_deployment/aci_contract_deployment.html', content)

            # Run Excel Validation to make sure policy conforms to naming standards.
            if RULE_LIST:
                VALIDATED_DATA = CONTRACT_DEPLOYMENT_EXCEL_FORMAT_VALIDATION(RULE_LIST)

                for output in VALIDATED_DATA:
                    if 'Errors' in output:
                        VALIDATION_ERROR = True


                # Tell user to fix errors and go back to upload page.
                if VALIDATION_ERROR:
                    del request.session['LOCATION']
                    del request.session['WORKBOOK_NAME']
                    content = {'data': VALIDATED_DATA, 'validation_error': 'Please Fix Errors before continuing', 'nbar': 'Contract_Deployment', 'errors': True}

                    return render(request, 'aci_deployment/aci_contract_deployment.html', content)

                # Login to apic to do further checks.
                elif not VALIDATION_ERROR:
                    APIC_VALIDATION = CONTRACT_DEPLOYMENT_APIC_VALIDATION(BASE_URL, APIC_USERNAME, APIC_PASSWORD, RULE_LIST, VALIDATED_DATA)

                    for output in APIC_VALIDATION:
                        if 'Errors' in output:
                            APIC_VALIDATION_ERROR = True

                    if APIC_VALIDATION_ERROR:
                        del request.session['LOCATION']
                        del request.session['WORKBOOK_NAME']
                        content = {'data': APIC_VALIDATION, 'validation_error': 'Please Fix Errors before continuing',
                                   'nbar': 'Contract_Deployment', 'start': True, 'errors': True}

                        return render(request, 'aci_deployment/aci_contract_deployment.html', content)


                    #Check to see if user wants to deploy data.
                    else:
                        request.session['CONFIG_DATA'] = RULE_LIST

                        content = {'data': VALIDATED_DATA, 'validation_error': 'Please Use Button on right to Deploy APIC Configuration', 'nbar': 'Contract_Deployment', 'WorkbookValid': True, 'WorkbookName': myfile.name, 'Location': Location, 'errors': False , 'deploy': True}
                        return render(request, 'aci_deployment/aci_contract_deployment.html', content)

        else:
            content = {'upload_error': 'File name must not contain spaces.',
                       'nbar': 'Contract_Deployment', 'errors': True}
            return render(request, 'aci_deployment/aci_contract_deployment.html', content)

    if 'CONFIG_DATA' in request.session:
        if request.session.get('WORKBOOK_NAME') in request.get_raw_uri():
            APIC_USERNAME = request.session.get('APIC_USERNAME')
            APIC_PASSWORD = request.session.get('APIC_PASSWORD')
            WorkbookName = request.session.get('WORKBOOK_NAME')
            Location = request.session.get('LOCATION')
            CONFIG_DATA = request.session.get('CONFIG_DATA')
            #Deploy Config
            DEPLOYMENT_VALIDATION = CONTRACT_DEPLOYMENT_APIC_CONFIGURATION(BASE_URL, APIC_USERNAME, APIC_PASSWORD, CONFIG_DATA)

            #Remove cookies with workbook data after push
            del request.session['CONFIG_DATA']
            del request.session['LOCATION']
            del request.session['WORKBOOK_NAME']


            content = {'data': DEPLOYMENT_VALIDATION, 'nbar': 'Contract_Deployment', 'WorkbookValid': True, 'WorkbookName': WorkbookName, 'Location': Location,  'errors': False, 'deploy': False}
            return render(request, 'aci_deployment/aci_contract_deployment.html', content)
        else:
            del request.session['CONFIG_DATA']
            del request.session['LOCATION']
            del request.session['WORKBOOK_NAME']

            content = {'nbar': 'Contract_Deployment', 'start': True}
            return render(request, 'aci_deployment/aci_contract_deployment.html', content)

    content = {'nbar': 'Contract_Deployment', 'start': True }
    return render(request, 'aci_deployment/aci_contract_deployment.html', content)
