import json, requests

# Ignore SSL Errors
requests.packages.urllib3.disable_warnings()

from f5_deployment.scripts.baseline import bigip_login


def virtual_server_name_search(url_list, search_string, username, password):
    for base_url in url_list:
        # Authenticate against bigip
        auth_token = bigip_login(base_url, username, password)

        # Build auth token header
        headers = {'content-type': 'application/json', 'X-F5-Auth-Token': auth_token}