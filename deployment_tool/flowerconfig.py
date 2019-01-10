from flower.utils.template import humanize
from deployment_tool.secrets import *

def format_task(task):
    task.args = humanize(task.args, length=20)
    task.result = humanize(task.result, length=20)
    return task

tasks_columns = ['name', 'state', 'args', 'result', 'received', 'started', 'runtime', 'worker']
basic_auth = flower_basic_auth
port = '8443'
