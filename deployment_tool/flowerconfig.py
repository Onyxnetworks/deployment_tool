from flower.utils.template import humanize

def format_task(task):
    args_list = task.args.split()
    args_no_pass = args_list.remove(args_list[-1])
    task.args = str(args_no_pass)
    task.args = humanize(task.args, length=10)
    print(type(task.args))
    print(task.args)
    #task.kwargs.pop('password')
    task.result = humanize(task.result, length=20)
    return task