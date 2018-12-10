import json
from django.shortcuts import render
from django.http import HttpResponse
from celery.result import AsyncResult


# Function to get task state and results to be used by ajax.
def get_task_info(request):
    task_id = request.GET.get('task_id', None)
    if task_id is not None:
        task = AsyncResult(task_id)
        data = {
            'state': task.state,
            'result': task.result,
        }
        print(type(data))
        return HttpResponse(json.dumps(data), content_type='application/json')
    else:
        return HttpResponse('No job id given.')

def login(request):
    return render(request, 'index/login.html')

def index(request):
    return render(request, 'index/home.html')
