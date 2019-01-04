Overview
------
This is a Network tool to automate F5/ACI tasks. it is presented via a webpage hosted on Django/Apache and uses celery for the task scheduling.

Requirements
------
1. This has been deployed using Python 3.6 with the follwing set during configuration **_--enable-shared --enable-loadable-sqlite-extensions_**
2. **rabbitmq** is used with celery which will require **erlang** to be installed. A guide for this can be found [here](https://www.rabbitmq.com/install-rpm.html "Installing RabbitMQ on CentOS")
3. A full list of python requirements can be found in [requirements.txt](../requirements.txt)
4. It is reccomended that this is run in a python virtual envrionemrnt. A guide for this can be found [here](https://www.google.com)
5. Apache(httpd) is required with the mod_wsgi module loaded. A guide for this can be found [here](https://www.google.com)

Example Files
------
within `deployment_tool/deployment_tool` create a file called `secrets.py`
```python
# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'SECRET KEY PUT HERE'

# Flower Config
flower_basic_auth = ['USERNAME:PASSWORD']
```
This is a file that is not stored om GIT and is used to keep your sensitive information.

within `/deployment_tool/index/scripts` create a file called `baseline.py`
```python
def get_base_url(environment):
    if environment == 'Production':
        base_urls = {'ACI': {'UKDC1': 'https://ukdc1-aci-url/api', 'UKDC2': 'https://ukdc2-aci-url'}, 'F5': {'UKDC1': {'FUNCTION1': 'https://ukdc1-function1-f5-url', 'FUNCTION2':'https://ukdc1-function2-f5-url'}, 'UKDC2': {'FUNCTION1': 'https://ukdc2-function1-f5-url', 'FUNCTION2':'https://ukdc2-function2-f5-url'}}}
        return base_urls

    if environment == 'Pre-Production':
        base_urls = {'ACI': {'UKDC1': 'https://ukdc1-aci-url/api', 'UKDC2': 'https://ukdc2-aci-url'}, 'F5': {'UKDC1': {'FUNCTION': 'https://ukdc1-function-f5-url'}, 'UKDC2': {'FUNCTION': 'https://ukdc2-function-f5-url'}}}
        return base_urls


    if environment == 'Lab':
        base_urls = {'ACI': {'LAB': 'https://lab-aci-url/api/'}, 'F5': {'LAB': {'LAB': 'https://lab-f5-url'}}}
        return base_urls
```
This file defines the URL's for all of the tasks our site can run. For ACI its straight forward its a key,value pair with the DC loation and URL. for F5 its a bit more complex as the different F5's at each DC serve a different function which is refernece as part of our deployment tasks.

Daemonization of Celery and flower
------
As already stated Celery is used to queue tasks and provide results, Flower is used to provide an environment to monitor the status of Celery. The base config for both of these are included in this repo, however for best results we want both processes to run as a daemon and to startup on boot. To do this follow the below steps.

#### Create init files
**Celery**
create the following file: `/etc/systemd/system/celery.service`
```Shell Session
[Unit]
Description=Celery Service
After=network.target

[Service]
Type=forking
User=USERNAME
Group=USERGROUP

# directory with tasks.py
WorkingDirectory=PATH_TO_REPO_LOCATION

# !!! using the below systemd is REQUIRED in this case!
# (you will still get a warning "PID file /var/run/celery/single.pid not readable (yet?) after start." from systemd but service will in fact be starting, stopping and restarting properly. I haven't found a way to get rid of this warning.)
PIDFile=/var/run/celery/single.pid

# !!! using --pidfile option here and below is REQUIRED in this case!
# !!! also: don't use "%n" in pidfile or logfile paths - you will get these files named after the systemd service instead of after the worker (?)
ExecStart=PATH_TO_VENV/bin/celery multi start single-worker -A deployment_tool --pidfile=/var/run/celery/single.pid --logfile=/var/log/celery/single.log "-c 4 -Q celery -l INFO"

ExecStop=PATH_TO_VENV/bin/celery multi stopwait single-worker --pidfile=/var/run/celery/single.pid --logfile=/var/log/celery/single.log

ExecReload=/PATH_TO_VENV/bin/celery multi restart single-worker --pidfile=/var/run/celery/single.pid --logfile=/var/log/celery/single.log

# Creates /var/run/celery, if it doesn't exist
RuntimeDirectory=celery

[Install]
WantedBy=multi-user.target
```

**Flower**
create the following file: `/etc/systemd/system/flower.service`
```Shell Session
[Unit]
Description=Flower Celery Service

[Service]
User=USERNAME
Group=USERGROUP
WorkingDirectory=/var/www/html/deployment_tool
ExecStart=PATH_TO_VENV/bin/flower --conf=PATH_TO_REPO_LOCATION/deployment_tool/flowerconfig.py -A deployment_tool
Restart=on-failure
Type=simple

[Install]
WantedBy=multi-user.target
```

There are some attributes you will need to change:
`USERNAME` `USERGROUP` `PATH_TO_REPO_LOCATION` `PATH_TO_VENV`

After these files have been created run `sudo systemctl daemon-reload`. This will register our new services. 

They can now be started/stopped/restarted using:
```Shell Session
systemctl start celery
systemctl stop celery
systemctl restart celery

systemctl start flower
systemctl stop flower
systemctl restart flower
```

To make the service start on boot run the following:

`sudo systemctl enable celery`

`sudo systemctl enable flower`
