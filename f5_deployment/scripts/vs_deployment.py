import requests, json

# Ignore SSL Errors
requests.packages.urllib3.disable_warnings()


def create_connection_bigip(base_url, username, password, output_log):
    error = False
    bigip = requests.session()
    bigip.auth = (username, password)
    bigip.verify = False
    bigip.headers.update({'Content-Type': 'application/json'})

    payload = {}
    payload['username'] = username
    payload['password'] = password
    payload['loginProviderName'] = 'tmos'   
    
    bigip_url_base = '{}/mgmt/tm'.format(base_url)
    try:
        bigip_url_base_token = '{}/mgmt/shared/authn/login'.format(base_url)
        token = bigip.post(bigip_url_base_token, json.dumps(payload)).json()['token']['token']
        bigip.auth = ('')
        bigip.headers.update({'X-F5-Auth-Token': token})
        credentials = str(bigip.get('%s/ltm/virtual' % bigip_url_base, timeout=5.0))
        
    except:
        output_log.append({'Errors': 'Unable to communicate with ' + base_url[8:]})
        error = True
        return output_log, error
    
    if credentials.__contains__('200'):
        output_log.append({'NotificationsSuccess': 'Successfully connected to ' + base_url[8:]})
        return output_log, error, bigip_url_base, bigip         
    
    else:
        output_log.append({'Errors': 'Username or password is incorrect.'}) 
        error = True
        return output_log, error        

        
def check_sync(bigip_url_base, bigip, output_log):
    error = False
    sync_on_ltm = bigip.get('%s/cm/sync-status' % bigip_url_base)
    sync_on_ltm = json.loads(sync_on_ltm.content)

    sync_on_ltm_0 = sync_on_ltm['entries'][u'https://localhost/mgmt/tm/cm/sync-status/0']['nestedStats']['entries']['https://localhost/mgmt/tm/cm/syncStatus/0/details']['nestedStats']['entries']['https://localhost/mgmt/tm/cm/syncStatus/0/details/0']['nestedStats']['entries']['details']['description']

    sync_on_ltm_1 = sync_on_ltm['entries'][u'https://localhost/mgmt/tm/cm/sync-status/0']['nestedStats']['entries']['https://localhost/mgmt/tm/cm/syncStatus/0/details']['nestedStats']['entries']['https://localhost/mgmt/tm/cm/syncStatus/0/details/1']['nestedStats']['entries']['details']['description']

    sync_on_ltm_2 = sync_on_ltm['entries'][u'https://localhost/mgmt/tm/cm/sync-status/0']['nestedStats']['entries']['https://localhost/mgmt/tm/cm/syncStatus/0/details']['nestedStats']['entries']['https://localhost/mgmt/tm/cm/syncStatus/0/details/2']['nestedStats']['entries']['details']['description']

    sync_on_ltm_3 = sync_on_ltm['entries'][u'https://localhost/mgmt/tm/cm/sync-status/0']['nestedStats']['entries']['https://localhost/mgmt/tm/cm/syncStatus/0/details']['nestedStats']['entries']['https://localhost/mgmt/tm/cm/syncStatus/0/details/3']['nestedStats']['entries']['details']['description']

    output_log.append({'Notifications': sync_on_ltm_0})
    output_log.append({'Notifications': sync_on_ltm_1})
    output_log.append({'Notifications': sync_on_ltm_2})
    output_log.append({'Notifications': sync_on_ltm_3})
    
    
    if 'Changes Pending' in sync_on_ltm_3:
        output_log.append({'Errors': 'Please SYNC LTM configuration before continuing!'})   
        error = True
        return output_log, error    
    
    else:
        return output_log, error


def check_httpprofile(vs_dict, partition, bigip_url_base, bigip, output_log):
    error = False
    counter = 0
    httpptofiles_on_ltm = bigip.get('%s/ltm/profile/http' % bigip_url_base)
    http_default_profile = vs_dict['vs']['O2']
    http_profile = vs_dict['vs']['K2']

    httpptofiles_on_ltm = json.loads(httpptofiles_on_ltm.content)
    httpptofiles_on_ltm = httpptofiles_on_ltm['items']
    
    # Check if default profile exists.
    for httpprofile_dict in httpptofiles_on_ltm:
        for key, value in httpprofile_dict.items():
            if http_default_profile == value:
                counter = counter + 1
                output_log.append({'Notifications': 'Default HTTP(S) Profile {} present on LTM.'
                                  .format(http_default_profile)})

                for httpprofile_dict in httpptofiles_on_ltm:
                    for key, value in httpprofile_dict.items():
                        # check if http profile name is preset on ltm
                        if http_profile == value:
                            error = True
                            output_log.append({'Errors': 'HTTP(S) profile name {} already present on LTM'
                                              .format(http_profile)})

    if counter == 0:
        error = True
        output_log.append({'Errors': 'Default HTTP(S) Profile {}, not present, please create default profile.'
                          .format(http_default_profile)})
        
    if error:
        return output_log, error
    
    if not error:
        output_log.append({'Notifications': 'HTTP(S) Profile {} will be created.'.format(http_profile)})
        return output_log, error


def check_ssl_profile(vs_dict, partition, bigip_url_base, bigip, output_log):
    error = False
    counter = 0
    marker_c = 0
    marker_s = 0    
    ssl_default_profile = vs_dict['vs']['N2']
    ssl_profile_client = vs_dict['vs']['L2']
    ssl_profile_server = vs_dict['vs']['M2']
    sslprofiles_on_ltm = bigip.get('%s/ltm/profile/client-ssl' % bigip_url_base)
    sslprofiles_on_ltm = json.loads(sslprofiles_on_ltm.content)
    sslprofiles_on_ltm = sslprofiles_on_ltm['items']
    
    # Check default profile exist
    for sslprofile_dict in sslprofiles_on_ltm:
        for key, value in sslprofile_dict.items():
            if ssl_default_profile == value:
                counter = counter + 1
                output_log.append({'Notifications': 'Default SSL Profile {} present on LTM.'
                                  .format(ssl_default_profile)})

                for sslprofile_dict in sslprofiles_on_ltm:
                    for key, value in sslprofile_dict.items():
                        # Check if ssl client profile name is preset on ltm
                        if sslprofiles_on_ltm == value:
                            output_log.append({'Errors': 'SSL Client Profile name {} already present on LTM.'.format(
                                sslprofiles_on_ltm)})
                            marker_c = 1
                            error = True

                        if ssl_profile_server == value:
                            output_log.append({'Errors': 'SSL Server Profile name {} already present on LTM.'.format(
                                ssl_profile_server)})
                            marker_s = 1
                            error = True

    if counter == 0:
        output_log.append({'Errors': 'Default SSL Profile {}, not present, please create default profile.'
                          .format(ssl_default_profile)})
        error = True

    if marker_c == 0:
        output_log.append({'Notifications': 'SSL Client profile {} will be created.'.format(ssl_profile_client)})

    if marker_s == 0:
        if ssl_profile_server:
            output_log.append({'Notifications': 'SSL Server profile {} will be created'.format(ssl_profile_server)})
    else:
        output_log.append({'Notifications': 'No SSL Server profile.'})

    return output_log, error
    
    
def check_cert(vs_dict, partition, bigip_url_base, bigip, output_log):

    error = False
    counter = 0
    cert = 0
    chain = 0
    key_check = 0

    ssl_cert_chain_on_ltm = bigip.get('%s/sys/file/ssl-cert' % bigip_url_base)
    ssl_cert_chain_on_ltm = json.loads(ssl_cert_chain_on_ltm.content)
    ssl_cert_chain_on_ltm = ssl_cert_chain_on_ltm['items']

    ssl_cert_key_on_ltm = bigip.get('%s/sys/file/ssl-key' % bigip_url_base)
    ssl_cert_key_on_ltm = json.loads(ssl_cert_key_on_ltm.content)
    ssl_cert_key_on_ltm = ssl_cert_key_on_ltm['items']

    vs_hostname_crt = str(vs_dict['vs']['Y2']) + '.crt'
    vs_hostname_key = str(vs_dict['vs']['Y2']) + '.key'
    vs_hostname_chain = str(vs_dict['vs']['Z2']) + '.crt'

    for ssl_cert_dict in ssl_cert_chain_on_ltm:
        for key, value in ssl_cert_dict.items():
            if vs_hostname_crt == value:
                cert = 1

    for ssl_cert_dict in ssl_cert_chain_on_ltm:
        for key, value in ssl_cert_dict.items():
            if vs_hostname_chain == value:
                chain = 1

    for ssl_key_dict in ssl_cert_key_on_ltm:
        for key, value in ssl_key_dict.items():
            if vs_hostname_key == value:
                key_check = 1

    if cert == 1:
        output_log.append({'NotificationsSuccess': 'SSL Cert : {} present.'.format(vs_hostname_crt)})
        
    else:
        error = True
        output_log.append({'Errors': 'SSL Cert NOT present on LTM.'})
        counter = counter + 1

    if chain== 1:
        output_log.append({'NotificationsSuccess': 'SSL Chain : {} present.'.format(vs_hostname_chain)})

    else:
        error = True
        output_log.append({'Errors': 'SSL Chain NOT present on LTM.'})      
        counter = counter + 1
    if key_check == 1:
        output_log.append({'NotificationsSuccess': 'SSL Cert Key : {} present.'.format(vs_hostname_key)})

    else:
        error = True
        output_log.append({'Errors': 'SSL Cert Key NOT present on LTM.'})
        counter = counter + 1

    return output_log, error 


def check_http_mon(vs_dict, partition, bigip_url_base, bigip, output_log):
    
    error = False
    marker = 0
    http_mon_name = vs_dict['vs']['Q2']
    http_mon_on_ltm = bigip.get('%s/ltm/monitor/http' % bigip_url_base, )
    http_mon_on_ltm = json.loads(http_mon_on_ltm.content)
    http_mon_on_ltm = http_mon_on_ltm['items']

    https_mon_on_ltm = bigip.get('%s/ltm/monitor/https' % bigip_url_base)
    https_mon_on_ltm = json.loads(https_mon_on_ltm.content)
    https_mon_on_ltm = https_mon_on_ltm['items']

    for http_mon_dict in http_mon_on_ltm:
        for key, value in http_mon_dict.items():
            if http_mon_name == value:
                output_log.append({'Errors': 'HTTP monitor : {} present on LTM'.format(http_mon_name)})         
                marker = 1
                error = True

    for https_mon_dict in https_mon_on_ltm:
        for key, value in https_mon_dict.items():
            if http_mon_name == value:
                output_log.append({'Errors': 'HTTPS monitor : {} present on LTM'.format(http_mon_name)})    
                marker = 1
                error = True

    if marker == 0:
        output_log.append({'Notifications': 'HTTP(S) monitor {} will be created'.format(http_mon_name)})
        
    return output_log, error

    
def compare_snat_on_ltm_excel(vs_dict, partition, bigip_url_base, bigip, output_log):
    error = False
    snat_ip = (vs_dict['vs']['B2'])
    snat_pool_name = vs_dict['vs']['X2']

    snat_on_ltm = bigip.get('%s/ltm/snatpool' % bigip_url_base)
    snat_on_ltm = json.loads(snat_on_ltm.content)

    try:
        snat_on_ltm = snat_on_ltm['items']

    except:
        snat_on_ltm = [{u'kind': 'tm:ltm:snatpool'}]

    for dict_snat in snat_on_ltm:

        key_address_value = str(dict_snat.get('members'))
        key_address_value = key_address_value.strip("[u'/Common/").strip("']")
        key_name_value = str(dict_snat.get('name'))
        print(snat_ip)
        print(key_address_value)

        if snat_ip == key_address_value:

            if snat_pool_name == key_name_value:
                output_log.append({'NotificationsWarning': 'SNAT IP and SNAT Pool name already present on LTM. {}:{}'
                                  .format(snat_pool_name, snat_ip)})
                snat_pool_present = 1
                return output_log, error, snat_pool_present
                    
            else:
                snat_pool_present = 1
                output_log.append({'Errors': 'SNAT IP is already configured on LTM but SNAT Pool name on does '
                                             'not match name on Excel.'})
                output_log.append({'Errors': 'SNAT IP : {}'.format(snat_ip)})   
                output_log.append({'Errors': 'Pool name on LTM : {}'.format(key_name_value)})   
                output_log.append({'Errors': 'SNAT Pool name on Excel : {}'.format(snat_pool_name)})    
                error = True

        if snat_pool_name == key_name_value:
            snat_pool_present = 1
            output_log.append({'Errors': 'SNAT Pool name is already configured on LTM but SNAT IP does '
                                         'not match name on Excel.'})
            output_log.append({'Errors': 'SNAT IP on Excel : {}'.format(snat_ip)})  
            output_log.append({'Errors': 'SNAT IP on LTM : {}'.format(key_address_value)})  
            output_log.append({'Errors': 'SNAT Pool name : {}'.format(snat_pool_name)})         
            error = True

        else:
            snat_pool_present = 0

    if snat_pool_present == 0:
        if error == False:
            output_log.append({'Notifications': 'SNAT pool {} : {} will be created.'.format(snat_pool_name, snat_ip)})

    else:
        output_log.append({'Notifications': ' SNAT pool will not be created.'})

    return  output_log, error, snat_pool_present
    
 
def compare_ltm_nodes(vs_dict, partition, bigip_url_base, bigip, output_log):
    error = False
    node_list = vs_dict['node_list']
    node_list_priority = vs_dict['node_priority']
    node_list_pool = []
    node_port = vs_dict['vs']['V2']
    
    for node_name, node_pg in zip(node_list_priority[0::2], node_list_priority[1::2]):
        node_name_port = str(node_name) + ':' + str(node_port)
        node_list_pool.extend([{'kind': 'ltm:pool:nodes', 'name': '{}'.format(node_name_port),'prioritygroup': '{}'
                               .format(node_pg)}])
        
    
    # check if nodes already exist on ltm
    nodes_on_ltm = bigip.get('%s/ltm/node' % bigip_url_base)
    nodes_on_ltm = json.loads(nodes_on_ltm.content)

    # catch exception if no nodes on ltm
    try:
        nodes_on_ltm_ip_address = nodes_on_ltm['items']
        nodes_on_ltm_name = nodes_on_ltm['items']

    except:
        nodes_on_ltm_ip_address = [{u'kind': 'tm:ltm:node:nodestate'}]
        nodes_on_ltm_name = [{u'kind': 'tm:ltm:node:nodestate'}]

    nodes_on_ltm_dict = dict(enumerate(nodes_on_ltm_ip_address))
    node_list_a = iter(node_list)
    node_list_b = list(node_list)

    for item in node_list_a:

        excel_node_pair = (item, next(node_list_a))
        excel_node_name = excel_node_pair[0]
        excel_node_ip = excel_node_pair[1]


        for new_dict in nodes_on_ltm_dict:
            try:
                node_name = nodes_on_ltm_dict[new_dict]['name']
                node_ip = nodes_on_ltm_dict[new_dict]['address']
            except:
                output_log.append({'Notifications': 'No Nodes configured on LTM'})
                return output_log, error, node_list, 


            if node_name == excel_node_name and node_ip == excel_node_ip:
                output_log.append({'NotificationsWarning': 'Node already present on LTM: {} - {}'
                                  .format(node_name, node_ip)})

                node_list_b.remove(excel_node_name)
                node_list_b.remove(excel_node_ip)

    node_list = node_list_b
    node_list_a = iter(node_list)

    for item in node_list_a:
        excel_node_pair = [item, next(node_list_a)]
        excel_node_name = excel_node_pair[0]
        excel_node_ip = excel_node_pair[1]

        for new_dict in nodes_on_ltm_dict:
            node_name = nodes_on_ltm_dict[new_dict]['name']
            node_ip = nodes_on_ltm_dict[new_dict]['address']

            if node_name == excel_node_name:
                output_log.append({'Errors': 'Node Name/IP mismatch for: {} - {}'.format(node_name, node_ip)})
                error = True

            if node_ip == excel_node_ip:
                output_log.append({'Errors': 'Node IP/Name mismatch for: {} - {}'.format(node_ip, node_name)})
                error = True

    if node_list:
        if not error:
            output_log.append({'Headers2': 'The following nodes will be created.'})
            node_list_c = iter(node_list)
            for x in node_list_c:
                a = (x, next(node_list_c))
                output_log.append({'Notifications': '{} - {}' .format(a[0], a[1])})

    else:
        output_log.append({'Notifications': 'No nodes will be created.'})
        'no nodes will be created.'
            
    return output_log, error, node_list, node_list_pool


def compare_pool(vs_dict, partition, bigip_url_base, bigip, output_log):
    error = False
    pool_name = str(vs_dict['vs']['P2'])

    # Get pool from ltm
    pool_on_ltm = bigip.get('%s/ltm/pool' % bigip_url_base)
    pool_on_ltm = json.loads(pool_on_ltm.content)

    # CATCH EXCEPTION IF NO POOL ON LTM
    try:
        pool_on_ltm = pool_on_ltm['items']

    except:
        pool_on_ltm = [{u'kind': 'tm:ltm:pool:poolstate'}]

    for dict_pool in pool_on_ltm:
        pool_name_value_ltm = str((dict_pool.get('name')))
        pool_description = str((dict_pool.get('description')))

        if pool_name == pool_name_value_ltm:
            output_log.append({'Errors': '{} - Pool name present on LTM.{}\n'.format(pool_name, pool_description)})
            error = True

    if not error:
        output_log.append({'Notifications': 'Pool: {} not present on LTM, POOL will be created.'.format(pool_name)})

    return output_log, error


def compare_vs(vs_dict, partition, bigip_url_base, bigip, output_log):
    error = False
    s = ':'
    vs_ip = str(vs_dict['vs']['B2'])
    vs_port = str(vs_dict['vs']['C2'])
    vs_destination = vs_ip + s + vs_port

    # Get vs from ltm
    vs_on_ltm = bigip.get('%s/ltm/virtual' % bigip_url_base)
    vs_on_ltm = json.loads(vs_on_ltm.content)

    # Catch exception if no vs on ltm
    try:
        vs_on_ltm = vs_on_ltm['items']

    except:
        vs_on_ltm = [{u'kind': 'tm:ltm:virtual:virtualstate'}]

    for dict_vs in vs_on_ltm:
        vs_destination_value = str((dict_vs.get('destination')))
        vs_destination_value = vs_destination_value.strip('/Common/')

        if vs_destination == vs_destination_value:
            output_log.append({'Errors': '{}:Virtual Server name present on LTM.\n'.format(vs_destination)})
            error = True

    if not error:
        output_log.append({'Notifications': 'Virtual Server: {} not present on LTM, It will be created.'
                          .format(vs_destination)})

    return output_log, error


def create_vs_ssl_profiles(vs_dict, partition, bigip_url_base, bigip, output_log):
    error = False
    output_log.append({'Headers': 'Creating SSL Client Profile.'})
    ssl_client_profile = {}
    vs_hostname_crt = vs_dict['vs']['Y2'] + '.crt'
    vs_hostname_key = vs_dict['vs']['Y2'] + '.key'
    vs_hostname_chain = vs_dict['vs']['Z2'] + '.crt'
    ssl_default_profile = (vs_dict['vs']['N2'])

    ssl_client_profile['kind'] = 'tm:ltm:profile:client-ssl:client-sslstate'
    ssl_client_profile['name'] = vs_dict['vs']['L2']
    ssl_client_profile['defaultsFrom'] = ssl_default_profile

    ssl_client_profile['cert'] = vs_hostname_crt
    ssl_client_profile['key'] = vs_hostname_key
    ssl_client_profile['chain'] = vs_hostname_chain
    ssl_client_profile['partition'] = partition

    print('SSL Client Profile:')
    print(ssl_client_profile)
    ssl_client_profile_sent = str(bigip.post('%s/ltm/profile/client-ssl' % bigip_url_base,
                                             data=json.dumps(ssl_client_profile)))

    if ssl_client_profile_sent.__contains__('200'):
        output_log.append({'NotificationsInfo': '{} : SSL Client Profile Created'.format(vs_dict['vs']['L2'])})

    elif ssl_client_profile_sent.__contains__('409'):
        output_log.append({'NotificationsInfo': '{} : *SSL Client Profile Modified*'.format(vs_dict['vs']['L2'])})

    elif ssl_client_profile_sent.__contains__('400'):
        output_log.append({'Errors': '{} - Bad Request, unable to create SSL Client Profile*'
                          .format(vs_dict['vs']['L2'])})
        error = True
        return output_log, error

     # Create SSL Server Profile
    if vs_dict['vs']['M2']:

        ssl_server_profile = {}
        output_log.append({'Headers': 'Creating SSL Server Profile.'})
        ssl_server_profile['kind'] = 'tm:ltm:profile:server-ssl:server-sslstate'
        ssl_server_profile['name'] = vs_dict['vs']['M2']
        ssl_server_profile['defaultsFrom'] = 'serverssl'
        ssl_server_profile['partition'] = partition
        print('SSL Server Profile:')
        print(ssl_server_profile)
        ssl_server_profile_sent = str(bigip.post('%s/ltm/profile/server-ssl' % bigip_url_base,
                                                 data=json.dumps(ssl_server_profile)))

        if ssl_server_profile_sent.__contains__('200'):
            output_log.append({'NotificationsInfo': '{} - SSL Server Profile Created'.format(vs_dict['vs']['K2'])})

        elif ssl_server_profile_sent.__contains__('409'):
            output_log.append({'NotificationsInfo': '{} - SSL Server Profile Modified*'.format(vs_dict['vs']['K2'])})

    return output_log, error


def create_pool_monitor(vs_dict, partition, bigip_url_base, bigip, output_log):
    error = False
    
    pool_mon_info = {}
    try:
        traffic_type = vs_dict['vs']['R2']
        traffic_type = (traffic_type.lower())
    except:
        error = True
        output_log.append({'Errors': 'Unable to validate traffic type, no monitor configuration deployed.'})
        return output_log, error

    if traffic_type in ['http', 'HTTP', 'https', 'HTTPS']:
        output_log.append({'Headers': 'Creating HTTP(S) monitor.'})

        if vs_dict['vs']['S2']:
            pool_mon_cst_str = vs_dict['vs']['S2']
            pool_mon_cst_str_send = pool_mon_cst_str.split('"')[1]
            pool_mon_cst_str_receive = pool_mon_cst_str.split('"')[3]
            pool_mon_info['send'] = pool_mon_cst_str_send
            pool_mon_info['recv'] = pool_mon_cst_str_receive

        pool_mon_info['kind'] = 'tm:ltm:monitor:{}:{}state'.format(traffic_type, traffic_type)
        pool_mon_info['name'] = vs_dict['vs']['Q2']
        pool_mon_info['defaultsFrom'] = traffic_type
        pool_mon_info['destination'] = '*:' + str(vs_dict['vs']['V2'])
        pool_mon_info['partition'] = partition

        print('Monitor:')
        print(pool_mon_info)
        https_mon_sent = str(bigip.post('%s/ltm/monitor/%s' % (bigip_url_base, traffic_type), data=json.dumps(pool_mon_info)))

        if https_mon_sent.__contains__('200'):
            output_log.append({'NotificationsInfo': '{} - Monitor Created'.format(vs_dict['vs']['Q2'])})

        elif https_mon_sent.__contains__('409'):
            output_log.append({'NotificationsInfo': '{} - Monitor Modified'.format(vs_dict['vs']['Q2'])})

    return output_log, error


def create_vs_profiles_http(vs_dict, partition, bigip_url_base, bigip, output_log):
    
    error = False
    http_profile = {}
    traffic_type = vs_dict['vs']['D2']
    traffic_type = (traffic_type.lower())
    http_default_profile = vs_dict['vs']['O2']

    if traffic_type == 'HTTP' or 'HTTPS':

        if vs_dict['vs']['O2']:
            output_log.append({'Headers': 'Creating HTTP Profile.'})

            http_profile['kind'] = 'tm:ltm:profile:http:httpstate'
            http_profile['name'] = vs_dict['vs']['K2']
            http_profile['insertXforwardedFor'] = "enabled"
            http_profile['defaultsFrom'] = http_default_profile
            http_profile['partition'] = partition
            print('http Profile:')
            print(http_profile)
            http_profile_sent = str(bigip.post('%s/ltm/profile/http' % bigip_url_base, data=json.dumps(http_profile)))

            if http_profile_sent.__contains__('200'):
                output_log.append({'NotificationsInfo': '{} - HTTP Profile Created'.format(vs_dict['vs']['K2'])})

            elif http_profile_sent.__contains__('409'):
                output_log.append({'NotificationsInfo': '{} : *HTTP Profile Modified*'.format(vs_dict['vs']['K2'])})

            elif http_profile_sent.__contains__('400'):
                error = True
                output_log.append({'Errors': '{} - HTTP Profile not created, no profile configuration deployed.'
                                  .format(vs_dict['vs']['K2'])})

        else:
            error = True
            output_log.append({'Errors': '{} - HTTP Profile not created, no profile configuration deployed.'
                              .format(vs_dict['vs']['K2'])})


    return output_log, error



def create_snat(vs_dict, partition, bigip_url_base, bigip, output_log):
    error = False
    
    if vs_dict['vs']['B2']:
        output_log.append({'Headers': 'Creating SNAT Pool.'})

        snat_info = {}
        snat_timeout = {}
        snat_ip = []
        snat_ip.append(vs_dict['vs']['B2'])
        snat_pool_name = vs_dict['vs']['X2']

        snat_info['kind'] = 'tm:ltm:snatpool:snatpoolstate'
        snat_info['name'] = snat_pool_name
        snat_info['members'] = snat_ip
        snat_info['partition'] = partition

        snat_timeout['kind'] = 'tm:ltm:snat-translation:snat-translationstate'
        snat_timeout['name'] = vs_dict['vs']['B2']
        snat_timeout['address'] = vs_dict['vs']['B2']
        snat_timeout['ipIdleTimeout'] = '300'
        snat_timeout['tcpIdleTimeout'] = '300'
        snat_timeout['udpIdleTimeout'] = '60'
        snat_timeout['partition'] = partition
        print('Snat Info:')
        print(snat_info)
        print('Snat Timeout:')
        print(snat_timeout)
        snat_timeout_sent = str(bigip.post('%s/ltm/snat-translation' % bigip_url_base, data=json.dumps(snat_timeout)))

        snat_info_sent = str(bigip.post('%s/ltm/snatpool' % bigip_url_base, data=json.dumps(snat_info)))

        if snat_info_sent.__contains__('200'):
            output_log.append({'NotificationsInfo': '{} - SNAT Pool Created'.format(snat_pool_name)})

        elif snat_info_sent.__contains__('409'):
            output_log.append({'NotificationsInfo': '{} - SNAT Pool Modified'.format(snat_pool_name)})

        elif snat_info_sent.__contains__('400'):
            output_log.append({'Errors': 'If SNAT IP is already presnt on LTM, then the pool name on the LTM.'})
            output_log.append({'Errors': 'Did not match the pool name on .xlsx ({}).'.format(snat_pool_name)})
            output_log.append({'Errors': 'Please verfiy the SNAT pool name that should used'})
            error = True

    return  output_log, error



def create_nodes(node_list, partition, bigip_url_base, bigip, output_log):
    
    error = False
    node_info = {}
    output_log.append({'Headers': 'Creating Nodes.'})
    index = 0
    for node_name, node_ip in zip(node_list[0::2], node_list[1::2]):
        index = index + 1
        output_log.append({'Headers2': 'Creating nodes for line {}.'.format(index)})
        node_info['kind'] = 'tm:ltm:pool:poolstate'
        node_info['name'] = node_name
        node_info['address'] = node_ip
        node_info['partition'] = partition
        print('Node Info')
        print(node_info)
        node_sent = str(bigip.post('%s/ltm/node' % bigip_url_base, data=json.dumps(node_info)))

        if node_sent.__contains__('200'):
            output_log.append({'NotificationsInfo': '{} : {} Created.'.format(node_ip, node_name)})

        else:
            error = True
            output_log.append({'Errors': 'Failed to create Node for line {}.'.format(index)})

    return output_log, error



def create_pool(vs_dict, partition, bigip_url_base, bigip, output_log):
    error = False
    
    node_list_pool = vs_dict['node_list_pool']
    pool_info = {}
    output_log.append({'Headers': 'Creating Pool.'})

    pool_info['kind'] = 'tm:ltm:pool:poolstate'
    pool_info['name'] = vs_dict['vs']['P2']
    pool_info['description'] = vs_dict['vs']['AA2']
    pool_info['loadBalancingMode'] = vs_dict['vs']['U2']
    pool_info['monitor'] = vs_dict['vs']['Q2']
    pool_info['members'] = node_list_pool
    pool_info['minActiveMembers'] = str(vs_dict['vs']['AV2'])
    pool_info['partition'] = partition
    print('Pool Info')
    print(pool_info)

    pool_sent = str(bigip.post('%s/ltm/pool' % bigip_url_base, data=json.dumps(pool_info)))

    if pool_sent.__contains__('200'):
        output_log.append({'NotificationsInfo': '{} - Pool Created.'.format(vs_dict['vs']['P2'])})

    elif pool_sent.__contains__('409'):
        output_log.append({'NotificationsInfo': '{} - Pool Modified.'.format(vs_dict['vs']['P2'])})
    else:
        error = True
        output_log.append({'Errors': 'Failed to create Pool'})
        output_log.append({'Errors': pool_sent})


    return output_log, error



def create_vs(vs_dict, partition, bigip_url_base, bigip, output_log):
    
    error = False
    if vs_dict['vs']['A2']:
        output_log.append({'Headers': 'Creating Virtual Server.'})

        vs_info = {}
        vs_ip = str(vs_dict['vs']['B2'])
        vs_port = str(vs_dict['vs']['C2'])
        s = ':'
        snat_pool_name = vs_dict['vs']['X2']
        int_ext = vs_dict['vs']['W2']

        vs_destination = vs_ip + s + vs_port

        vs_info['kind'] = 'tm:ltm:virtual:virtualstate'
        vs_info['name'] = vs_dict['vs']['A2']
        vs_info['description'] = vs_dict['vs']['AA2']
        vs_info['destination'] = vs_destination
        vs_info['mask'] = '255.255.255.255'
        vs_info['ipProtocol'] = 'tcp'
        vs_info['pool'] = vs_dict['vs']['P2']
        vs_info['sourceAddressTranslation'] = {'pool': snat_pool_name, 'type': 'snat'}
        vs_info['partition'] = partition

        if int_ext in ['INT']:
            vs_info['profiles'] = [
                {'kind': 'ltm:virtual:profile', 'name': vs_dict['vs']['I2'], 'context': 'all'}]

            if vs_dict['vs']['K2']:
                vs_info['profiles'].append({'kind': 'ltm:virtual:profile', 'name': vs_dict['vs']['K2']})

            if vs_dict['vs']['M2']:
                vs_info['profiles'].append({'kind': 'ltm:virtual:profile', 'name': vs_dict['vs']['M2']})

            if vs_dict['vs']['L2']:
                vs_info['profiles'].append({'kind': 'ltm:virtual:profile', 'name': vs_dict['vs']['L2']})

        else:
            vs_info['profiles'] = [
                {'kind': 'ltm:virtual:profile', 'name': vs_dict['vs']['I2'], 'context': 'clientside'},
                {'kind': 'ltm:virtual:profile', 'name': vs_dict['vs']['J2'], 'context': 'serverside'},
            ]
            if vs_dict['vs']['K2']:
                vs_info['profiles'].append({'kind': 'ltm:virtual:profile', 'name': vs_dict['vs']['K2']})

            if vs_dict['vs']['M2']:
                vs_info['profiles'].append({'kind': 'ltm:virtual:profile', 'name': vs_dict['vs']['M2']})

            if vs_dict['vs']['L2']:
                vs_info['profiles'].append({'kind': 'ltm:virtual:profile', 'name': vs_dict['vs']['L2']})

        print('VS Info:')
        print(vs_info)

        vs_info_sent = str(bigip.post('%s/ltm/virtual' % bigip_url_base, data=json.dumps(vs_info)))

        if vs_info_sent.__contains__('200'):
            output_log.append({'NotificationsInfo': '{} : Virtual Server Created'.format(vs_dict['vs']['A2'])})

        elif vs_info_sent.__contains__('409'):
            output_log.append({'NotificationsInfo': '{} : *Virtual Server Modified*'.format(vs_dict['vs']['A2'])})

        else:
            error = True
            output_log.append({'Errors': '{} - Ubable to create Virtual Server *'.format(vs_dict['vs']['A2'])})

    return output_log, error

def create_advertise_vip(vs_dict, partition, bigip_url_base, bigip, output_log):

    error = False
    vs_ip = str(vs_dict['vs']['B2'])
    patch_url = '{0}/ltm/virtual-address/~{1}~{2}'.format(bigip_url_base, partition, vs_ip)
    patch_json = {"routeAdvertisement": "enabled"}

    try:
        get_response = bigip.get(patch_url, timeout=5)
        payload_response = json.loads(get_response.text)

        if get_response.status_code == 200:
            if payload_response['routeAdvertisement'] == 'enabled':
                output_log.append({'Notifications': 'Virtual IP already advertised.'})
                return output_log, error

        if get_response.status_code == 404:
            error = True
            output_log.append({'Errors': 'Unable to locate {0} in Virtual IP List.'.format(vs_ip)})
            return output_log, error

    except requests.exceptions.HTTPError as errh:
        error = True
        output_log.append({'Errors': 'Http Error: ' + str(errh)})
        return output_log, error

    except requests.exceptions.ConnectionError as errc:
        error = True
        output_log.append({'Errors': 'Error Connecting: ' + str(errc)})
        return output_log, error

    except requests.exceptions.Timeout as errt:
        error = True
        output_log.append({'Errors': 'Timeout Error: ' + str(errt)})
        return output_log, error

    except requests.exceptions.RequestException as err:
        error = True
        output_log.append({'Errors': 'Error: ' + str(err)})
        return output_log, error

    if not error:
        try:
            patch_response = bigip.patch(patch_url, data=json.dumps(patch_json), timeout=5)
            payload_response = json.loads(patch_response.text)

            if patch_response.status_code == 200:
                output_log.append({'NotificationsInfo': '{} : Virtual Server IP Successfully Advertised'.format(vs_ip)})
                return output_log, error

        except requests.exceptions.HTTPError as errh:
            error = True
            output_log.append({'Errors': 'Http Error: ' + str(errh)})
            return output_log, error

        except requests.exceptions.ConnectionError as errc:
            error = True
            output_log.append({'Errors': 'Error Connecting: ' + str(errc)})
            return output_log, error

        except requests.exceptions.Timeout as errt:
            error = True
            output_log.append({'Errors': 'Timeout Error: ' + str(errt)})
            return output_log, error

        except requests.exceptions.RequestException as err:
            error = True
            output_log.append({'Errors': 'Error: ' + str(err)})
            return output_log, error

