import json, requests, re, ipaddress
from datetime import datetime
from operator import itemgetter
from netaddr import IPNetwork, IPAddress

# Ignore SSL Errors
requests.packages.urllib3.disable_warnings()

from f5_deployment.scripts.baseline import bigip_login

def f5_generic_search(base_url, auth_token, search_options):
    headers = {'content-type': 'application/json', 'X-F5-Auth-Token': auth_token}
    get_url = base_url + '{0}'.format(search_options)

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


def get_vs_stats(base_url, selfLink, auth_token):
    headers = {'content-type': 'application/json', 'X-F5-Auth-Token': auth_token}
    get_url = base_url + '/{0}/stats'.format(selfLink)
    try:
        get_response = requests.get(get_url, headers=headers, timeout=5, verify=False)
        payload_response = json.loads(get_response.text)
        if get_response.status_code == 200:
            return payload_response

    except requests.exceptions.RequestException as error:
        #  Return Errors
        return error


def get_node_stats(base_url, nodeLink, auth_token):
    headers = {'content-type': 'application/json', 'X-F5-Auth-Token': auth_token}
    get_url = base_url + '/{0}/stats'.format(nodeLink)
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


def get_pool_stats(base_url, poolLink, auth_token):
    headers = {'content-type': 'application/json', 'X-F5-Auth-Token': auth_token}
    get_url = base_url + '/{0}/stats'.format(poolLink)
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


def get_pool_by_reference(base_url, poolLink, auth_token):
    headers = {'content-type': 'application/json', 'X-F5-Auth-Token': auth_token}
    get_url = base_url +'/{0}?expandSubcollections=true'.format(poolLink)

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


def get_all_vs(base_url, auth_token, search_options):
        # Build auth token header
        headers = {'content-type': 'application/json', 'X-F5-Auth-Token': auth_token}

        get_url = base_url + '/mgmt/tm/ltm/virtual/?expandSubcollections=true&$select={}'.format(search_options)
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


def virtual_server_dashboard(url_list, request_type, search_string, username, password):
    results = []
    for base_url in url_list:
        # Authenticate against bigip
        location = base_url.split('.')[0][8:]
        bigip_login_response = bigip_login(base_url, username, password)
        auth_token = bigip_login_response['token']['token']
        # Get all Virtual Servers
        search_options = 'name,selfLink,pool,destination,partition'
        all_vs = get_all_vs(base_url, auth_token, search_options)


        for vs in all_vs['items']:
            vs_name = vs['name']
            vs_ip = re.split(':|/', vs['destination'])[-2]
            # Search based on VS Name
            if request_type == 'Virtual Server Name':
                if search_string.upper() not in vs_name.upper():
                    continue

            elif request_type == 'Pool':
                try:
                    if search_string.upper() not in vs['pool'].upper():
                        continue
                except:
                        continue

            elif request_type == 'Virtual Server IP':
                search_string = ipaddress.IPv4Network(search_string)
                vs_ip_search = ipaddress.IPv4Address(vs_ip)
                if vs_ip_search not in search_string:
                    continue

            vs_name = vs['name']
            vs_port = re.split(':|/', vs['destination'])[-1]
            selfLink_ver = vs['selfLink'].split('/localhost/')[1]
            selfLink = selfLink_ver.split('?ver=')[0]
            vs_selfLink = base_url + '/' + selfLink
            vs_partition = vs['partition']
            vs_stats = get_vs_stats(base_url, selfLink, auth_token)
            vs_state_dict = vs_stats['entries'].values()
            for vs_values in vs_state_dict:

                vs_state = vs_values['nestedStats']['entries']['status.availabilityState']['description']
                vs_admin_state = vs_values['nestedStats']['entries']['status.enabledState']['description']
                vs_state_reason = vs_values['nestedStats']['entries']['status.statusReason']['description']
                vs_bits_in = vs_values['nestedStats']['entries']['clientside.bitsIn']['value']
                vs_bits_out = vs_values['nestedStats']['entries']['clientside.bitsOut']['value']
                vs_packets_in = vs_values['nestedStats']['entries']['clientside.pktsIn']['value']
                vs_packets_out = vs_values['nestedStats']['entries']['clientside.pktsOut']['value']
                vs_conn_current = vs_values['nestedStats']['entries']['clientside.curConns']['value']
                vs_conn_max = vs_values['nestedStats']['entries']['clientside.maxConns']['value']
                vs_conn_total = vs_values['nestedStats']['entries']['clientside.totConns']['value']
                vs_state_reason = vs_state_reason.replace("'", "")
            try:
                vs['poolReference']
                poolLink_ver = vs['poolReference']['link'].split('/localhost/')[1]
                poolLink = poolLink_ver.split('?ver=')[0]
                pool_name = vs['pool'].split('/')[-1]
                pool_stats = get_pool_stats(base_url, poolLink, auth_token)
                pool_state_dict = pool_stats['entries'].values()
                # Get node details
                node_details = []
                try:
                    pool_reference = get_pool_by_reference(base_url, poolLink, auth_token)
                    pool_reference['membersReference']['items']
                    pool_available_members = len(pool_reference['membersReference']['items'])
                    for nodes in pool_reference['membersReference']['items']:
                        node_name = re.split(':', nodes['name'])[-2]
                        node_port = re.split(':', nodes['name'])[-1]
                        node_address = nodes['address']
                        nodeLink_ver = nodes['selfLink'].split('/localhost/')[1]
                        nodeLink = nodeLink_ver.split('?ver=')[0]
                        node_stats = get_node_stats(base_url, nodeLink, auth_token)
                        node_selfLink_ver = node_stats['selfLink'].split('/localhost/')[1]
                        node_selfLink = base_url + '/' + node_selfLink_ver.split('stats?ver=')[0]
                        node_stats_dict = node_stats['entries'].values()
                        for node_values in node_stats_dict:
                            node_admin_state = node_values['nestedStats']['entries']['status.enabledState']['description']
                            node_state = node_values['nestedStats']['entries']['status.availabilityState']['description']
                            node_state_reason = node_values['nestedStats']['entries']['status.statusReason']['description']
                            node_state_reason = node_state_reason.replace("'", "")
                            node_bits_in = node_values['nestedStats']['entries']['serverside.bitsIn']['value']
                            node_bits_out = node_values['nestedStats']['entries']['serverside.bitsOut']['value']
                            node_packets_in = node_values['nestedStats']['entries']['serverside.pktsIn']['value']
                            node_packets_out = node_values['nestedStats']['entries']['serverside.pktsOut']['value']
                            node_conn_current = node_values['nestedStats']['entries']['serverside.curConns']['value']
                            node_conn_max = node_values['nestedStats']['entries']['serverside.maxConns']['value']
                            node_conn_total = node_values['nestedStats']['entries']['serverside.totConns']['value']
                            node_requests_total = node_values['nestedStats']['entries']['totRequests']['value']
                            node_requests_depth = node_values['nestedStats']['entries']['connq.depth']['value']
                            node_requests_max_age = node_values['nestedStats']['entries']['connq.ageMax']['value']
                            node_details.append({'node_selfLink': node_selfLink,
                                                 'node_name': node_name, 'node_port': node_port,
                                                 'node_address': node_address, 'node_state': node_state,
                                                 'node_state_reason': node_state_reason,
                                                 'node_admin_state': node_admin_state, 'node_stats':
                                                     {'node_bits_in': node_bits_in, 'node_bits_out': node_bits_out,
                                                      'node_packets_in': node_packets_in,
                                                      'node_packets_out': node_packets_out,
                                                      'node_conn_current': node_conn_current,
                                                      'node_conn_max': node_conn_max, 'node_conn_total': node_conn_total,
                                                      'node_requests_total': node_requests_total,
                                                      'node_requests_depth': node_requests_depth,
                                                      'node_requests_max_age': node_requests_max_age}})
                except:
                    node_details = []
                for pool_values in pool_state_dict:
                    pool_state = pool_values['nestedStats']['entries']['status.availabilityState']['description']
                    pool_admin_state = pool_values['nestedStats']['entries']['status.enabledState']['description']
                    pool_state_reason = pool_values['nestedStats']['entries']['status.statusReason']['description']
                    pool_state_reason = pool_state_reason.replace("'", "")
                    pool_active_members = pool_values['nestedStats']['entries']['activeMemberCnt']['value']
                    #pool_available_members = pool_values['nestedStats']['entries']['memberCnt']['value']
                    pool_bits_in = pool_values['nestedStats']['entries']['serverside.bitsIn']['value']
                    pool_bits_out = pool_values['nestedStats']['entries']['serverside.bitsOut']['value']
                    pool_packets_in = pool_values['nestedStats']['entries']['serverside.pktsIn']['value']
                    pool_packets_out = pool_values['nestedStats']['entries']['serverside.pktsOut']['value']
                    pool_conn_current = pool_values['nestedStats']['entries']['serverside.curConns']['value']
                    pool_conn_max = pool_values['nestedStats']['entries']['serverside.maxConns']['value']
                    pool_conn_total = pool_values['nestedStats']['entries']['serverside.totConns']['value']
                    pool_requests_total = pool_values['nestedStats']['entries']['totRequests']['value']
                    pool_requests_depth = pool_values['nestedStats']['entries']['connqAll.depth']['value']
                    pool_requests_max_age = pool_values['nestedStats']['entries']['connqAll.ageMax']['value']
                    results.append({'location': location, 'vs_selfLink': vs_selfLink,
                                    'vs_partition': vs_partition,
                                    'vs_name': vs_name, 'vs_state': vs_state,
                                    'vs_admin_state': vs_admin_state, 'vs_state_reason': vs_state_reason,
                                    'vs_ip': vs_ip, 'vs_port': vs_port, 'vs_stats': {'vs_bits_in': vs_bits_in,
                                                                                     'vs_bits_out': vs_bits_out,
                                                                                     'vs_packets_in': vs_packets_in,
                                                                                     'vs_packets_out': vs_packets_out,
                                                                                     'vs_conn_current': vs_conn_current,
                                                                                     'vs_conn_max': vs_conn_max,
                                                                                     'vs_conn_total': vs_conn_total},
                                    'vs_pool': {'pool_name': pool_name, 'pool_state': pool_state,
                                                'pool_admin_state': pool_admin_state,
                                                'pool_state_reason': pool_state_reason,
                                                'pool_active_members': pool_active_members,
                                                'pool_available_members': pool_available_members,
                                                'pool_stats': {'pool_bits_in': pool_bits_in,
                                                               'pool_bits_out': pool_bits_out,
                                                               'pool_packets_in': pool_packets_in,
                                                               'pool_packets_out': pool_packets_out,
                                                               'pool_conn_current': pool_conn_current,
                                                               'pool_conn_max': pool_conn_max,
                                                               'pool_conn_total': pool_conn_total,
                                                               'pool_requests_total': pool_requests_total,
                                                               'pool_requests_depth': pool_requests_depth,
                                                               'pool_requests_max_age': pool_requests_max_age,
                                                               }
                                                },
                                    'vs_nodes': node_details
                                    })
            except:
                results.append({'location': location, 'vs_selfLink': vs_selfLink,
                                'vs_partition': vs_partition, 'vs_name': vs_name, 'vs_state': vs_state,
                                'vs_admin_state': vs_admin_state, 'vs_state_reason': vs_state_reason,
                                'vs_ip': vs_ip, 'vs_port': vs_port, 'vs_stats': {'vs_bits_in': vs_bits_in,
                                                                                 'vs_bits_out': vs_bits_out,
                                                                                 'vs_packets_in': vs_packets_in,
                                                                                 'vs_packets_out': vs_packets_out,
                                                                                 'vs_conn_current': vs_conn_current,
                                                                                 'vs_conn_max': vs_conn_max,
                                                                                 'vs_conn_total': vs_conn_total},
                                'vs_pool': {'pool_name': 'none', 'pool_state': 'unknown',
                                            'pool_state_reason': 'unknown'}})

    results = sorted(results, key=itemgetter('vs_name'), reverse=True)
    return results


def certificate_checker(url_list, request_type, search_string, username, password):
    results = []
    # Get the current Date & Time
    current_datetime = datetime.now().date()

    for base_url in url_list:
        # Authenticate against bigip
        location = base_url.split('.')[0][8:]
        bigip_login_response = bigip_login(base_url, username, password)
        auth_token = bigip_login_response['token']['token']
        # Get all Virtual Certificates
        search_options = '/mgmt/tm/sys/crypto/cert?expandSubcollections=true'
        get_cert_response = f5_generic_search(base_url, auth_token, search_options)

        # Get all Virtual Servers
        search_options = 'name,destination,profilesReference'
        get_all_vs_response = get_all_vs(base_url, auth_token, search_options)

        for cert in get_cert_response['items']:
            vs_list = []
            cert_name = re.split('.crt|/', cert['fullPath'])[-2]

            if request_type == 'Certificate Name':
                if search_string.upper() not in cert_name.upper():
                    continue

            cert_expiration = cert['apiRawValues']['expiration']

            # Convert Expiration date into datetime format
            datetime_object = datetime.strptime(cert_expiration, '%b %d %H:%M:%S %Y %Z')

            # Get difference in dates bny dats.
            datetime_result = datetime_object.date() - current_datetime
            datetime_result = datetime_result.days

            if datetime_object.date() < current_datetime:
                cert_status = 'danger'
                cert_status_message = 'Certificate has expired.'

            elif datetime_result <= 90:
                cert_status = 'warning'
                cert_status_message = 'Less than 90 Days until expiry.'

            else:
                cert_status = 'success'
                cert_status_message = 'Certificate has over 90 days until expiry.'

            try:
                # Check for common name
                common_name = cert['commonName']
            except:
                common_name = ''
            try:
                san = cert['subjectAlternativeName'].split()
            except:
                san = ''

            for vs in get_all_vs_response['items']:
                for profiles in vs['profilesReference']['items']:
                    if 'context' in profiles:
                        if profiles['context'] == 'clientside':
                            vs_cert_name = profiles['name']
                            if cert_name == vs_cert_name:
                                # Cert used by VIP
                                vs_name = vs['name']

                                vs_port = re.split(':|/', vs['destination'])[-1]
                                vs_destination = re.split(':|/', vs['destination'])[-2]
                                vs_list.append(vs_name)

            if request_type == 'Virtual Server Name':
                # Convert VS List into upper case
                vs_name_upper = [element.upper() for element in vs_list]
                search_string = search_string.upper()
                if not [s for s in vs_name_upper if search_string in s.upper()]:
                    continue

            results.append({'location': location, 'cert_name': cert_name, 'cert_expiration': cert_expiration,
                            'cert_status': cert_status, 'cert_status_message': cert_status_message,
                            'remaining_days': datetime_result, 'common_name': common_name,
                            'san': san, 'vs_list': vs_list })

    results = sorted(results, key=itemgetter('remaining_days'), reverse=False)
    return results




