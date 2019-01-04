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
