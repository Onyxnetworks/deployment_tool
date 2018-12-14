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
    
    bigip_url_base = 'https://{}/mgmt/tm'.format(base_url)
    
    try:
        bigip_url_base_token = 'https://{}/mgmt/shared/authn/login'.format(base_url)
        token = bigip.post(bigip_url_base_token, json.dumps(payload)).json()['token']['token']
        bigip.auth = ('')
        bigip.headers.update({'X-F5-Auth-Token': token})
        credentials = str(bigip.get('%s/ltm/virtual' % bigip_url_base, timeout=5.0))
        
    except:
        output_log.append({'Errors': 'Unable to communicate with F5.'})
        error = True
        return output_log, error
    
    if credentials.__contains__('200'):
        output_log.append({'NotificationsSuccess': 'Successfully connected to BigIP.'})
        return output_log, error, bigip_url_base, bigip         
    
    else:
        output_log.append({'Errors': 'Username or password is incorrect.'}) 
        error = True
        return output_log, error        

        
def check_sync(bigip_url_base, bigip, output_log):
    error = False
    sync_on_ltm = bigip.get('%s/cm/sync-status' % bigip_url_base)
    sync_on_ltm = json.loads(sync_on_ltm.content)

    sync_on_ltm_0 = sync_on_ltm['entries'][u'https://localhost/mgmt/tm/cm/sync-status/0']['nestedstats']['entries'][
        'https://localhost/mgmt/tm/cm/syncstatus/0/details']['nestedstats']['entries'][
        'https://localhost/mgmt/tm/cm/syncstatus/0/details/0']['nestedstats']['entries']['details']['description']

    sync_on_ltm_1 = sync_on_ltm['entries'][u'https://localhost/mgmt/tm/cm/sync-status/0']['nestedstats']['entries'][
        'https://localhost/mgmt/tm/cm/syncstatus/0/details']['nestedstats']['entries'][
        'https://localhost/mgmt/tm/cm/syncstatus/0/details/1']['nestedstats']['entries']['details']['description']

    sync_on_ltm_2 = sync_on_ltm['entries'][u'https://localhost/mgmt/tm/cm/sync-status/0']['nestedstats']['entries'][
        'https://localhost/mgmt/tm/cm/syncstatus/0/details']['nestedstats']['entries'][
        'https://localhost/mgmt/tm/cm/syncstatus/0/details/2']['nestedstats']['entries']['details']['description']

    sync_on_ltm_3 = sync_on_ltm['entries'][u'https://localhost/mgmt/tm/cm/sync-status/0']['nestedstats']['entries'][
        'https://localhost/mgmt/tm/cm/syncstatus/0/details']['nestedstats']['entries'][
        'https://localhost/mgmt/tm/cm/syncstatus/0/details/3']['nestedstats']['entries']['details']['description']

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
        
def check_httpprofile(vs_dict, bigip_url_base, bigip, output_log):
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
        output_log.append({'Errors': 'Errors found, please review.'})
        return output_log, error    
    
    if not error:
        output_log.append({'Notifications': 'HTTP(S) Profile {} will be created.'.format(http_profile)})
        return output_log, error

def check_ssl_profile(vs_dict, bigip_url_base, bigip, output_log):
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
    
    
def check_cert(vs_dict, bigip_url_base, bigip, output_log):

    error = False
    counter = 0
    cert = 0
    chain = 0
    key = 0

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
                key = 1

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

    if key == 1:
        output_log.append({'NotificationsSuccess': 'SSL Cert Key : {} present.'.format(vs_hostname_key)})

    else:
        error = True
        output_log.append({'Errors': 'SSL Cert Key NOT present on LTM.'})
        counter = counter + 1

    return output_log, error 
    
def check_http_mon(vs_dict, bigip_url_base, bigip, output_log):
    
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

    
def compare_snat_on_ltm_excel(vs_dict, bigip_url_base, bigip, output_log):
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

        if snat_ip == key_address_value:

            if snat_pool_name == key_name_value:
                output_log.append({'NotificationsWarning': 'SNAT IP and SNAT Pool name already present on LTM. {}:{}'
                                  .format(snat_pool_name, snat_ip)})
                snat_pool_present = 1
                return output_log, error, snat_pool_present
                    
            else:
                output_log.append({'Errors': 'SNAT IP is already configured on LTM but SNAT Pool name on does '
                                             'not match name on Excel.'})
                output_log.append({'Errors': 'SNAT IP : {}'.format(snat_ip)})   
                output_log.append({'Errors': 'Pool name on LTM : {}'.format(key_name_value)})   
                output_log.append({'Errors': 'SNAT Pool name on Excel : {}'.format(snat_pool_name)})    
                error = True

        if snat_pool_name == key_name_value:
            output_log.append({'Errors': 'SNAT Pool name is already configured on LTM but SNAT IP does '
                                         'not match name on Excel.'})
            output_log.append({'Errors': 'SNAT IP on Excel : {}'.format(snat_ip)})  
            output_log.append({'Errors': 'SNAT IP on LTM : {}'.format(key_address_value)})  
            output_log.append({'Errors': 'SNAT Pool name : {}'.format(snat_pool_name)})         
            error = True

        else:
            snat_pool_present = 0

    if snat_pool_present == 0:
        output_log.append({'Notifications': 'SNAT pool {} : {} will be created.'.format(snat_pool_name, snat_ip)})

    else:
        output_log.append({'Notifications': ' SNAT pool will not be created.'})

    return  output_log, error, snat_pool_present
    
 
def compare_ltm_nodes(vs_dict, bigip_url_base, bigip, output_log):
    error = False
    node_list = vs_dict['node_list']
    node_list_priority = vs_dict['node_priority']
    nodes_list_pool = []
    node_port = vs_dict['vs']['V2']
    
    for node_name, node_pg in zip(node_list_priority[0::2], node_list_priority[1::2]):
        node_name_port = str(node_name) + ':' + str(node_port)
        nodes_list_pool.extend([{'kind': 'ltm:pool:nodes', 'name': '{}'.format(node_name_port),'prioritygroup': '{}'
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

    print(nodes_on_ltm_ip_address)
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
                return output_log, error, node_list


            if node_name == excel_node_name and node_ip == excel_node_ip:
                output_log.append({'Notifications': 'Node already present on LTM: {} : {}'.format(node_name, node_ip)})

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
                output_log.append({'Errors': 'Node name/*ip mismatch: {}:{}'.format(node_name, node_ip)})
                error = True

            if node_ip == excel_node_ip:
                output_log.append({'Errors': 'Node ip/*name mismatch: {}:{}'.format(node_ip, node_name)})
                error = True

    if node_list:
        output_log.append({'Headers2': 'The following nodes will be created.'})
        node_list_c = iter(node_list)
        for x in node_list_c:
            a = (x, next(node_list_c))
            output_log.append({'Notifications': '{} : {}' .format(a[0], a[1])})

    else:
        output_log.append({'Notifications': 'No nodes will be created.'})
        'no nodes will be created.'
            
    return output_log, error, node_list


def compare_pool(vs_dict, bigip_url_base, bigip, output_log):
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
            output_log.append({'Errors': '{}:POOL name present on LTM.{}\n'.format(pool_name, pool_description)})
            error = True

    if not error:
        output_log.append({'Notifications': 'Pool: {} not present on LTM, POOL will be created.'.format(pool_name)})

    return output_log, error
