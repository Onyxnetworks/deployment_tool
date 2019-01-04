from flower.utils.template import humanize
from deployment_tool.secrets import *

def format_task(task):
    task.args = humanize(task.args, length=20)
    task.result = humanize(task.result, length=20)
    return task

basic_auth = flower_basic_auth
port = '8443'