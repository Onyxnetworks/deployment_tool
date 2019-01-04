from flower.utils.template import humanize

def format_task(task):
    print(task.args)
    #task.args = humanize(task.args, length=10)
    #ask.kwargs.pop('password')
    #task.result = humanize(task.result, length=20)
    return task