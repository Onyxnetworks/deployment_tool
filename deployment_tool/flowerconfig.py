from flower.utils.template import humanize

def format_task(task):
    task.args = humanize(task.args, length=10)
    print(task.kwargs)
    #task.kwargs.pop('password')
    #task.result = humanize(task.result, length=20)
    return task