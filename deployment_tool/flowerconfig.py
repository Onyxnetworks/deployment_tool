from flower.utils.template import humanize

def format_task(task):
    task.args = humanize(task.args, length=20)
    task.result = humanize(task.result, length=20)
    return task

basic_auth = ['home:mote74']
port = '8443'