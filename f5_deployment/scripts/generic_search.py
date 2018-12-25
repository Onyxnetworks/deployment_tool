import json, requests, re

# Ignore SSL Errors
requests.packages.urllib3.disable_warnings()

from f5_deployment.scripts.baseline import bigip_login

def get_vs_stats(base_url, selfLink, auth_token):
    headers = {'content-type': 'application/json', 'X-F5-Auth-Token': auth_token}
    get_url = base_url + '/{0}/stats?$select=status.availabilityState,status.enabledState,status.statusReason'.format(selfLink)
    try:
        get_response = requests.get(get_url, headers=headers, timeout=5, verify=False)
        payload_response = json.loads(get_response.text)
        if get_response.status_code == 200:
            return payload_response

    except requests.exceptions.RequestException as error:
        #  Return Errors
        return error


def get_pool_stats(base_url, poolLink, auth_token):
    headers = {'content-type': 'application/json', 'X-F5-Auth-Token': auth_token}
    get_url = base_url + '/{0}/stats?$select=status.availabilityState,status.statusReason'.format(poolLink)
    try:
        get_response = requests.get(get_url, headers=headers, timeout=5, verify=False)
        payload_response = json.loads(get_response.text)
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


def get_all_vs(base_url, auth_token):
        # Build auth token header
        headers = {'content-type': 'application/json', 'X-F5-Auth-Token': auth_token}

        get_url = base_url + '/mgmt/tm/ltm/virtual/?$select=name,selfLink,pool,destination'
        try:
            get_response = requests.get(get_url, headers=headers, timeout=5, verify=False)
            payload_response = json.loads(get_response.text)

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
        location = base_url.split('.')[0][8:]
        auth_token = bigip_login(base_url, username, password)
        # Get all Virtual Servers
        all_vs = get_all_vs(base_url, auth_token)
        for vs in all_vs['items']:
            vs_name = vs['name']
            vs_ip = re.split(':|/',vs['destination'])[-2]
            vs_port = re.split(':|/', vs['destination'])[-1]
            selfLink_ver = vs['selfLink'].split('/localhost/')[1]
            selfLink = selfLink_ver.split('?ver=')[0]
            vs_stats = get_vs_stats(base_url, selfLink, auth_token)
            vs_state_dict = vs_stats['entries'].values()
            for vs_values in vs_state_dict:
                vs_state = vs_values['nestedStats']['entries']['status.availabilityState']['description']
                vs_admin_state = vs_values['nestedStats']['entries']['status.enabledState']['description']
                vs_state_reason = vs_values['nestedStats']['entries']['status.statusReason']['description']
                vs_state_reason = vs_state_reason.replace("'", "")

            try:
                vs['poolReference']
                poolLink_ver = vs['poolReference']['link'].split('/localhost/')[1]
                poolLink = poolLink_ver.split('?ver=')[0]
                pool_name = vs['pool'].split('/')[-1]
                pool_stats = get_pool_stats(base_url, poolLink, auth_token)
                pool_state_dict = pool_stats['entries'].values()
                for pool_values in pool_state_dict:
                    pool_state = pool_values['nestedStats']['entries']['status.availabilityState']['description']
                    pool_state_reason = pool_values['nestedStats']['entries']['status.statusReason']['description']
                    pool_state_reason = pool_state_reason.replace("'", "")
                    results.append({'location': location, 'vs_name': vs_name, 'vs_state': vs_state, 'vs_admin_state': vs_admin_state, 'vs_state_reason': vs_state_reason, 'vs_ip': vs_ip, 'vs_port': vs_port, 'vs_pool': {'pool_name': pool_name, 'pool_state': pool_state, 'pool_state_reason': pool_state_reason}})




            except:
                results.append({'location': location, 'vs_name': vs_name, 'vs_state': vs_state, 'vs_admin_state': vs_admin_state, 'vs_state_reason': vs_state_reason, 'vs_ip': vs_ip, 'vs_port': vs_port, 'vs_pool': {'pool_name': 'none', 'pool_state': 'unknown', 'pool_state_reason': 'unknown'}})

        return results

