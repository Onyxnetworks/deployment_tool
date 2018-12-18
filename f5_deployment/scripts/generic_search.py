import json, requests

# Ignore SSL Errors
requests.packages.urllib3.disable_warnings()

from f5_deployment.scripts.baseline import bigip_login


def get_virtual_server(url_list, username, password):
    results = []
    for base_url in url_list:
        # Authenticate against bigip
        auth_token = bigip_login(base_url, username, password)
        # Build auth token header
        headers = {'content-type': 'application/json', 'X-F5-Auth-Token': auth_token}

        get_url = base_url + '/mgmt/tm/ltm/virtual/'
        try:
            get_response = requests.get(get_url, headers=headers, timeout=5, verify=False)
            payload_response = json.loads(get_response.text)
            
            if get_response.status_code == 200:
                for vs_items in payload_response['items']:
                    vs_name = vs_items['name']
                    results.append({'vs_name': vs_name})
                

        except requests.exceptions.HTTPError as errh:
            error_code = "Http Error:" + str(errh)
            return error_code
        except requests.exceptions.ConnectionError as errc:
            error_code = "Error Connecting:" + str(errc)
            return error_code
        except requests.exceptions.Timeout as errt:
            error_code = "Timeout Error:" + str(errt)
            return error_code
        except requests.exceptions.RequestException as err:
            error_code = "Error:" + str(err)
            return error_code
    return results
