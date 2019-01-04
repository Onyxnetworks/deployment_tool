Overview
------
This is a Network tool to automate F5/ACI tasks. it is presented via a webpage hosted on Django/Apache and uses celery for the task scheduling.

Requirements
------
1. This has been deployed using Python 3.6 with the follwing set during configuration **_--enable-shared --enable-loadable-sqlite-extensions_**
2. **rabbitmq** is used with celery which will require **erlang** to be installed. A guide for this can be found [here](https://www.rabbitmq.com/install-rpm.html "Installing RabbitMQ on CentOS")
3. A full list of python requirements can be found in [requirements.txt](../requirements.txt)
4. It is reccomended that this is run in a python virtual envrionemrnt. 
5. Apache(httpd) is required with the mod_wsgi module loaded. A guide for this can be found [here](link to guide)

Example Files
------
within `deployment_tool/deployment_tool` create a file called `secrets.py`
```python
# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'SECRET KEY PUT HERE'
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
