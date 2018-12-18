import json, requests

# Ignore SSL Errors
requests.packages.urllib3.disable_warnings()

from f5_deployment.scripts.baseline import bigip_login

def get_vs_stats(base_url, selfLink, auth_token):
    headers = {'content-type': 'application/json', 'X-F5-Auth-Token': auth_token}
    get_url = base_url +  '/{0}/stats?$select=status.availabilityState,status.enabledState,status.statusReason'.format(selfLink)
    try:
        get_response = requests.get(get_url, headers=headers, timeout=5, verify=False)
        payload_response = json.loads(get_response.text)
        print(payload_response)
        if get_response.status_code == 200:
            return payload_response

    except requests.exceptions.RequestException as error:
        #  Return Errors
        return error


def get_pool_stats(base_url, pool_name, auth_token):
    headers = {'content-type': 'application/json', 'X-F5-Auth-Token': auth_token}
    get_url = base_url +  '/mgmt/tm/ltm/pool/{0}/stats?$select=status.availabilityState,'.format(pool_name)

    try:
        get_response = requests.get(get_url, headers=headers, timeout=5, verify=False)
        payload_response = json.loads(get_response.text)

        if get_response.status_code == 200:
            return payload_response

    except requests.exceptions.RequestException as error:
        #  Return Errors
        return error


def get_all_vs(base_url, auth_token):
        # Build auth token header
        headers = {'content-type': 'application/json', 'X-F5-Auth-Token': auth_token}

        get_url = base_url + '/mgmt/tm/ltm/virtual/?$select=name,selfLink,'
        try:
            get_response = requests.get(get_url, headers=headers, timeout=5, verify=False)
            payload_response = json.loads(get_response.text)
            print(payload_response)
            if get_response.status_code == 200:
                return payload_response


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


def virtual_server_dashboard(url_list, username, password):
    results = []
    for base_url in url_list:
        # Authenticate against bigip
        auth_token = bigip_login(base_url, username, password)

        # Get all Virtual Servers
        all_vs = get_all_vs(base_url, auth_token)
        for vs in all_vs['items']:
            vs_name = vs['name']
            selfLink_ver = vs['selfLink'].split('/localhost/')[1]
            selfLink = selfLink_ver.split('?ver=')[0]
            vs_stats = get_vs_stats(base_url, selfLink, auth_token)
            vs_state_dict = vs_stats['entries'].values()
            for vs_values in vs_state_dict:
                vs_state = vs_values['nestedStats']['entries']['status.availabilityState']['description']
                results.append({'vs_name': vs_name, 'vs_state': vs_state})
            #try:
            #    pool_name = vs['pool'].split('/')[-1]
            #    pool_stats = get_pool_stats(base_url, pool_name, auth_token)
            #    pool_state_dict = pool_stats['entries'].values()
            #    for pool_values in pool_state_dict:
            #        pool_state = pool_values['nestedStats']['entries']['status.availabilityState']['description']

            #        


            #except:
            #    results.append({'vs_name': vs_name, 'vs_state': vs_state, 'vs_pool': {'pool_name': 'none', 'pool_state': 'unknown'}})

    return results

