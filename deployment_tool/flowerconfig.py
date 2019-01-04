from flower.utils.template import humanize

def format_task(task):
    task.args = humanize(task.args)
    print(type(task.args))
    print(task.args)
    print(task.kwargs)
    #ask.kwargs.pop('password')
    #task.result = humanize(task.result, length=20)
    return task