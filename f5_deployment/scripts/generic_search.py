import json, requests

# Ignore SSL Errors
requests.packages.urllib3.disable_warnings()

from f5_deployment.scripts.baseline import bigip_login


def virtual_server_name_search(url_list, search_string, username, password):
    results =[]
    for base_url in url_list:
        # Authenticate against bigip
        auth_token = bigip_login(base_url, username, password)

        # Build auth token header
        headers = {'content-type': 'application/json', 'X-F5-Auth-Token': auth_token}

        get_url = base_url + '/mgmt/tm/ltm/virtual/{0}'.format(search_string)

        try:
            get_response = requests.get(get_url, headers=headers, timeout=5, verify=False)
            payload_response = json.loads(get_response.text)

            if get_response.status_code == 200:
                results.append(payload_response)
                return results


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
