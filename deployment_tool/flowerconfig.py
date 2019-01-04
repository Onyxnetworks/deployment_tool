from flower.utils.template import humanize

def format_task(task):
    task.args = tuple(task.args)

    print(type(task.args))
    print(task.args)
    print(task.kwargs)
    #task.args = humanize(task.args)
    #ask.kwargs.pop('password')
    #task.result = humanize(task.result, length=20)
    return task

basic_auth = ['home:mote74']
port = '8443'