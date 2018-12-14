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

    content = {}
    return render(request, 'f5_deployment/vs_deployment.html', content)


def vs_deployment_push(request):
    # Deploy LTM Virtual Server configuration
    if request.method == 'POST':
        response_json = request.body
        data = json.loads(response_json)
        location = data['location']
        vs_dict = data['vs_dict'][1]

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