from flower.utils.template import humanize

def format_task(task):
    # Change the task.args string to a tuple then a list.
    task.args = list(eval(task.args))
    # Remove password field from list (password is always last item in list).
    del task.args[-1]
    # Change it back to a tuple then a string.
    task.args = str(tuple(task.args))
    task.args = humanize(task.args)
    print(task.args)
    #task.kwargs.pop('password')
    task.result = humanize(task.result, length=20)
    return task

basic_auth = ['home:mote74']
port = '8443'