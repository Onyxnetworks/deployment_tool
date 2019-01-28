# Base Functions
import openpyxl
from operator import itemgetter


# Custom Functions
from aci_deployment.scripts.contract_search import *
from aci_deployment.scripts.ipg_search import *
from aci_deployment.scripts.endpoint_search import *
from aci_deployment.scripts.external_epg_deployment import *
from aci_deployment.scripts.contract_deployment import *
from aci_deployment.scripts.baseline import APIC_LOGIN
from index.scripts.baseline import get_base_url
# Celery Functions
from celery import shared_task

@shared_task
def ENDPOINT_SEARCH(base_urls, filter_default, username, password, search_string):
    RESULTS = []

    # Build URL List to search.
    url_list = []
    for url in base_urls['ACI']:
        url_list.append(base_urls['ACI'][url])

    ENDPOINT_LIST = GET_ENDPOINTS(url_list, filter_default, username, password)

    try:
        network = ipaddress.IPv4Network(search_string)
        request_type = 'subnet'
    except:
        request_type = 'epg_name'

    for i in ENDPOINT_LIST:
        if request_type == 'subnet':
            if IPNetwork(search_string) in IPNetwork(i['Subnet']) or IPNetwork(i['Subnet']) in IPNetwork(search_string):
                RESULTS.append({'Subnet': i['Subnet'], 'Locality': i['Locality'], 'Location': i['Location'],
                                'EPG': i['EPG'],'Scope': i['Scope'], 'AppProfile':
                                    i['AppProfile'], 'Tenant': i['Tenant']})
        if request_type == 'epg_name':
            if search_string.upper() in i['EPG'].upper():
                RESULTS.append({'Subnet': i['Subnet'], 'Locality': i['Locality'], 'Location': i['Location'],
                                'EPG': i['EPG'], 'Scope': i['Scope'], 'AppProfile':
                                    i['AppProfile'], 'Tenant': i['Tenant']})

    # Sort the list by subnet before returning it.
    RESULTS = sorted(RESULTS, key=itemgetter('Subnet'), reverse=True)
    return RESULTS


@shared_task
def aci_ipg_search(base_urls, username, password, search_string):
    results = []

    # Build URL List to search.
    url_list = []
    for url in base_urls['ACI']:
        url_list.append(base_urls['ACI'][url])

    ipg_list = get_ipg(url_list, username, password)

    # List all EPG for selected
    # Convert  List into upper case
    ipg_list_upper = [element.upper() for element in ipg_list]
    search_string = search_string.upper()
    if [s for s in ipg_list_upper if search_string in s.upper()]:

        fvpathatt_list = get_fvpathatt(url_list, search_string, username, password)

        # loop through output, print and add EPG's to list
        i = 0
        for ipg_location in fvpathatt_list:
            location = ipg_location['location']
            for epg in ipg_location['response']['imdata']:
                results.append({'location': location, 'ipg':
                    epg['fvRsPathAtt']['attributes']['tDn'].split('/')[-1][8:].strip(']'), 'tenant':
                    epg['fvRsPathAtt']['attributes']['dn'].split('/')[1][3:], 'app_prof':
                    epg['fvRsPathAtt']['attributes']['dn'].split('/')[2][3:], 'epg':
                    epg['fvRsPathAtt']['attributes']['dn'].split('/')[3][4:],'encap':
                    epg['fvRsPathAtt']['attributes']['encap']})
                i += 1

    return results

@shared_task
def aci_contract_search(location, url_dict, username, password, request_type, search_string):
    results = {}
    results['consumed'] = []
    results['provided'] = []
    results['vzconsumed'] = []
    results['vzprovided'] = []

    base_url = url_dict[location]

    apic_cookie = APIC_LOGIN(base_url, username, password)

    # Get results for Internal EPG's
    if request_type == 'Internal EPG':
        endpoint_children = get_internal_epg(base_url, search_string, apic_cookie)

    # Get results for External EPG's
    if request_type == 'External EPG':
        endpoint_children = get_external_epg(base_url, search_string, apic_cookie)

    # Get results for VRF Level Contracts

    # Get results for non VRF level Contracts.


    #Consumed Contracts
    for contracts in endpoint_children['imdata']:
        if 'fvRsCons' in contracts:
            contract_name = contracts['fvRsCons']['attributes']['tnVzBrCPName']
            tenant = contracts['fvRsCons']['attributes']['tDn'].split('/')[1][3:]

            port_list = []
            provider_list = []
            ip_list = []

            get_contract_detail_response = get_contract_details(base_url, tenant, contract_name, apic_cookie)

            for subjects in get_contract_detail_response['imdata']:
                if 'vzSubj' in subjects:
                    subject_name = subjects['vzSubj']['attributes']['name']
                    tenant = subjects['vzSubj']['attributes']['dn'].split('/')[1][3:]

                    get_subject_detail_response = get_subject_details(base_url, tenant, contract_name, subject_name,
                                                                      apic_cookie)


                    for filters in get_subject_detail_response['imdata']:
                        if 'vzRsSubjFiltAtt' in filters:
                            print(filters['vzRsSubjFiltAtt']['attributes']['tnVzFilterName'])
                            port_list.append(filters['vzRsSubjFiltAtt']['attributes']['tnVzFilterName'])

                print(port_list)
                port_string = ', '.join(port_list)
                print('String: ' + port_string)
                # Get internal Providers
                if 'vzRtProv' in subjects:
                    if subjects['vzRtProv']['attributes']['tDn'].split('/')[3][:3] == 'epg':
                        provider_epg_name = subjects['vzRtProv']['attributes']['tDn'].split('/')[3][4:]
                        provider_epg_tenant = subjects['vzRtProv']['attributes']['tDn'].split('/')[1][3:]
                        provider_epg_app_prof = subjects['vzRtProv']['attributes']['tDn'].split('/')[2][3:]

                        # Get Internal Providers IPs
                        get_internal_epg_detail_responmse = get_internal_epg_detail(base_url, provider_epg_tenant,
                                                                  provider_epg_app_prof, provider_epg_name, apic_cookie)

                        # Clear IP List
                        ip_list = []
                        for epgs in get_internal_epg_detail_responmse['imdata']:
                            if 'fvCEp' in epgs:
                                provider_subnet = epgs['fvCEp']['attributes']['ip'] + '/32'


                                results['consumed'].append([contract_name, provider_epg_name, provider_subnet, port_string])



                # Get External Providers
                    elif subjects['vzRtProv']['attributes']['tDn'].split('/')[3][:5] == 'instP':
                        provider_epg_name = subjects['vzRtProv']['attributes']['tDn'].split('/')[3][6:]
                        provider_epg_tenant = subjects['vzRtProv']['attributes']['tDn'].split('/')[1][3:]
                        provider_epg_l3out = subjects['vzRtProv']['attributes']['tDn'].split('/')[2][4:]

                        # Get External Providers IPs
                        get_external_epg_detail_responmse = get_external_epg_detail(base_url, provider_epg_tenant,
                                                                                    provider_epg_l3out,
                                                                                    provider_epg_name, apic_cookie)
                        # Clear IP List
                        ip_list = []
                        for epgs in get_external_epg_detail_responmse['imdata']:
                            if 'l3extSubnet' in epgs:
                                scope_list = epgs['l3extSubnet']['attributes']['scope'].split(',')
                                if 'import-security' in scope_list:
                                    provider_subnet = epgs['l3extSubnet']['attributes']['ip']

                                    results['consumed'].append([contract_name, provider_epg_name, provider_subnet, port_string])


    return results


def CONTRACT_DEPLOYMENT_EXCEL_OPEN_WORKBOOK(WORKBOOK, LOCATION):
    WB = openpyxl.load_workbook(WORKBOOK, data_only=True)
    if LOCATION == 'UKDC1':
        PY_WS = WB['ACI_DC1']
    elif LOCATION == 'UKDC2':
        PY_WS = WB['ACI_DC2']
    elif LOCATION == 'LAB':
        PY_WS = WB['ACI_LAB']

    SERVICE_LIST = []
    RULE_LIST = []
    INDEX = 1

    # Loops through the rows in the worksheet to build contract information
    for row in PY_WS.iter_rows(min_row=2, max_col=10):
        CONSUMER_IP_LIST = []
        PROVIDER_IP_LIST = []
        CONTRACT_NAME = row[2].value.upper()
        if row[8].value:
            CONSUMER_EPG = row[8].value.upper()
        else:
            CONSUMER_EPG = 'BLANK'
        if row[5].value:
            PROVIDER_EPG = row[5].value.upper()
        else:
            PROVIDER_EPG = 'BLANK'
        if row[9].value:
            CONSUMER_IP_LIST = row[9].value.split()
        else:
            pass
        if row[6].value:
            PROVIDER_IP_LIST = row[6].value.split()
        else:
            pass
        if row[3].value:
            SERVICE_LIST = row[3].value.upper().split()
        if row[7].value:
            CONSUMER_L3OUT = row[7].value.upper()
        else:
            CONSUMER_L3OUT = 'INTERNAL'
        if row[4].value:
            PROVIDER_L3OUT = row[4].value.upper()
        else:
            PROVIDER_L3OUT = 'INTERNAL'

        INDEX += 1
        RULE_LIST.append(
            {'LINE': INDEX, 'PROVIDER_L3OUT': PROVIDER_L3OUT, 'CONSUMER_L3OUT': CONSUMER_L3OUT, 'NAME': CONTRACT_NAME,
             'CONSUMER_EPG': CONSUMER_EPG, 'CONSUMER_IP': CONSUMER_IP_LIST, 'PROVIDER_EPG': PROVIDER_EPG,
             'PROVIDER_IP': PROVIDER_IP_LIST, 'SERVICE': SERVICE_LIST})
        SERVICE_LIST = []

    return RULE_LIST


def EXTERNAL_EPG_EXCEL_OPEN_WORKBOOK(WORKBOOK, LOCATION):
    WB = openpyxl.load_workbook(WORKBOOK, data_only=True)
    if LOCATION == 'UKDC1':
        PY_WS = WB['ACI_DC1']
    elif LOCATION == 'UKDC2':
        PY_WS = WB['ACI_DC2']
    elif LOCATION == 'LAB':
        PY_WS = WB['ACI_LAB']

    RULE_LIST = []
    INDEX = 1

    # Loops through the rows in the worksheet to build contract information
    for row in PY_WS.iter_rows(min_row=2, max_col=10):
        CONSUMER_IP_LIST = []
        PROVIDER_IP_LIST = []
        if row[8].value:
            CONSUMER_EPG = row[8].value.upper()
        else:
            CONSUMER_EPG = 'BLANK'
        if row[5].value:
            PROVIDER_EPG = row[5].value.upper()
        else:
            PROVIDER_EPG = 'BLANK'
        if row[9].value:
            CONSUMER_IP_LIST = row[9].value.split()
            i = 0
            for IP in CONSUMER_IP_LIST:
                if len(IP.split('/')) <= 1:
                    IP_SUBNET = IP + '/32'
                    CONSUMER_IP_LIST[i] = IP_SUBNET
                i = i + 1
        else:
            pass
        if row[6].value:
            PROVIDER_IP_LIST = row[6].value.split()
            i = 0
            for IP in PROVIDER_IP_LIST:
                if len(IP.split('/')) <= 1:
                    IP_SUBNET = IP + '/32'
                    PROVIDER_IP_LIST[i] = IP_SUBNET
                i = i + 1
        else:
            pass
        if row[7].value:
            CONSUMER_L3OUT = row[7].value.upper()
        else:
            CONSUMER_L3OUT = 'INTERNAL'
        if row[4].value:
            PROVIDER_L3OUT = row[4].value.upper()
        else:
            PROVIDER_L3OUT = 'INTERNAL'
        INDEX += 1
        RULE_LIST.append({'LINE': INDEX, 'PROVIDER_L3OUT': PROVIDER_L3OUT, 'CONSUMER_L3OUT': CONSUMER_L3OUT,
                          'CONSUMER_EPG': CONSUMER_EPG, 'CONSUMER_IP': CONSUMER_IP_LIST,
                          'PROVIDER_EPG': PROVIDER_EPG, 'PROVIDER_IP': PROVIDER_IP_LIST})
    return RULE_LIST


@shared_task
def EXTERNAL_EPG_VALIDATION(RULE_LIST, location, url_dict,  username, password):
    OUTPUT_LOG = []
    DISPLAY_LIST = []
    TENANT_LIST = ['RED', 'GREEN', 'BLUE']
    ERROR = False
    TENANT = 'common'

    BASE_URL = url_dict[location]


    OUTPUT_LOG.append({'Headers': 'Validating EPG names in Workbook.'})

    for rules in RULE_LIST:
        if rules['CONSUMER_EPG'] != 'BLANK' and rules['CONSUMER_L3OUT'] != 'INTERNAL':
            try:
                if len(rules['CONSUMER_EPG'].split('_')) > 2:
                    DISPLAY_LIST.append(rules['CONSUMER_EPG'])
                    ERROR = True

                elif rules['CONSUMER_EPG'].split('_')[1].upper() != 'EPG':
                    DISPLAY_LIST.append(rules['CONSUMER_EPG'])
                    ERROR = True

                elif rules['CONSUMER_EPG'].split('-')[0].upper() not in TENANT_LIST:
                    DISPLAY_LIST.append(rules['CONSUMER_EPG'])
                    ERROR = True

                elif rules['CONSUMER_L3OUT'].split('_')[0].endswith('CLOUD'):
                    continue

                # TEMP FIX FOR BLUE INET UNTIL RENAME
                elif rules['CONSUMER_L3OUT'] == 'BLUE-DC1-INET_L3O':
                    continue
                elif rules['CONSUMER_L3OUT'] == 'BLUE-DC2-INET_L3O':
                    continue
                elif not rules['CONSUMER_EPG'].split('_')[0].startswith(rules['CONSUMER_L3OUT'].split('_')[0]):
                    DISPLAY_LIST.append(rules['CONSUMER_EPG'])
                    ERROR = True

                else:
                    pass

            except:
                ERROR = True
                OUTPUT_LOG.append({'Errors': rules['CONSUMER_EPG'] + ' does not conform to the naming standard'})

        if rules['PROVIDER_EPG'] != 'BLANK' and rules['PROVIDER_L3OUT'] != 'INTERNAL':
            try:
                if len(rules['PROVIDER_EPG'].split('_')) > 2:
                    DISPLAY_LIST.append(rules['PROVIDER_EPG'])
                    ERROR = True

                elif rules['PROVIDER_EPG'].split('_')[1].upper() != 'EPG':
                    DISPLAY_LIST.append(rules['PROVIDER_EPG'])
                    ERROR = True

                elif rules['PROVIDER_EPG'].split('-')[0].upper() not in TENANT_LIST:
                    DISPLAY_LIST.append(rules['PROVIDER_EPG'])
                    ERROR = True

                elif rules['PROVIDER_L3OUT'].split('_')[0].endswith('CLOUD'):
                    continue

                # TEMP FIX FOR BLUE INET UNTIL RENAME
                elif rules['PROVIDER_L3OUT'] == 'BLUE-DC1-INET_L3O':
                    continue
                elif rules['PROVIDER_L3OUT'] == 'BLUE-DC2-INET_L3O':
                    continue
                elif not rules['PROVIDER_EPG'].split('_')[0].startswith(rules['PROVIDER_L3OUT'].split('_')[0]):
                    DISPLAY_LIST.append(rules['PROVIDER_EPG'])
                    ERROR = True

                else:
                    pass

            except:
                ERROR = True
                OUTPUT_LOG.append({'Errors': rules['PROVIDER_EPG'] + ' does not conform to the naming standard'})

        else:
            pass

    DISPLAY_SET = set(DISPLAY_LIST)
    for contracts in DISPLAY_SET:
        OUTPUT_LOG.append({'Errors': 'EPG "' + contracts + '" does not conform to the naming standard'})
    DISPLAY_LIST = []

    if not ERROR:
        OUTPUT_LOG.append({'NotificationsSuccess': 'EPG formatting validated successfully'})


    OUTPUT_LOG.append({'Headers': 'Validating IP addresses'})
    for addresses in RULE_LIST:
        if len(addresses['CONSUMER_IP']) >= 1:
            for subnets in addresses['CONSUMER_IP']:
                try:
                    network = ipaddress.IPv4Network(subnets)
                except ValueError:
                    ERROR = True
                    OUTPUT_LOG.append({'Errors': subnets + ' Is not a valid IPv4 address.'})

        if len(addresses['PROVIDER_IP']) >= 1:
            for subnets in addresses['PROVIDER_IP']:
                try:
                    network = ipaddress.IPv4Network(subnets)
                except ValueError:
                    ERROR = True
                    OUTPUT_LOG.append({'Errors': subnets + ' Is not a valid IPv4 address.'})



    if ERROR:
        OUTPUT_LOG.append({'Errors': 'Errors found in IP validation'})
    else:
        OUTPUT_LOG.append({'NotificationsSuccess': 'IP validation successful'})

        OUTPUT_LOG.append({'Headers': 'Connecting to APIC'})
        # Login to fabric
        APIC_COOKIE = APIC_LOGIN(BASE_URL, username, password)
        if APIC_COOKIE:
            OUTPUT_LOG.append({'Notifications': 'Successfully generated authentication cookie'})

            # Search for L3out and build URL to add IP's
            OUTPUT_LOG.append({'Headers': 'Validating L3Out Names'})
            L3OUT_LIST = []

            for rules in RULE_LIST:
                if rules['CONSUMER_L3OUT'] == 'INTERNAL':
                    pass
                else:
                    L3OUT_NAME = rules['CONSUMER_L3OUT']
                    L3OUT_SEARCH_RESPONSE = L3OUT_SEARCH(BASE_URL, APIC_COOKIE, TENANT, L3OUT_NAME, HEADERS)
                    if int(L3OUT_SEARCH_RESPONSE[0]['totalCount']) == 1:
                        if rules['CONSUMER_L3OUT'] == L3OUT_SEARCH_RESPONSE[0]['imdata'][0]['l3extOut']['attributes']['name']:
                            pass
                        else:
                            ERROR = True

                    else:
                        L3OUT_LIST.append(L3OUT_NAME)
                        ERROR = True


            for rules in RULE_LIST:
                if rules['PROVIDER_L3OUT'] == 'INTERNAL':
                    pass
                else:
                    L3OUT_NAME = rules['PROVIDER_L3OUT']
                    L3OUT_SEARCH_RESPONSE = L3OUT_SEARCH(BASE_URL, APIC_COOKIE, TENANT, L3OUT_NAME, HEADERS)
                    if int(L3OUT_SEARCH_RESPONSE[0]['totalCount']) == 1:
                        if rules['PROVIDER_L3OUT'] == L3OUT_SEARCH_RESPONSE[0]['imdata'][0]['l3extOut']['attributes']['name']:
                            pass
                        else:
                            ERROR = True

                    else:
                        L3OUT_LIST.append(L3OUT_NAME)
                        ERROR = True

            L3OUT_SET = set(L3OUT_LIST)
            for l3out in L3OUT_SET:
                OUTPUT_LOG.append({'Errors': 'L3Out: ' + l3out + ' Does not exist, please check naming.'})
            L3OUT_LIST = []

            if ERROR:
                OUTPUT_LOG.append({'Errors': 'Errors found in L3Out validation'})
            else:
                OUTPUT_LOG.append({'NotificationsSuccess': 'L3Out validation successful'})

                # Check if IP already exists in Same L3Out or same VRF
                OUTPUT_LOG.append({'Headers': 'Checking if IP currently exists within VRF'})

                # Get L3out VRF
                for rules in RULE_LIST:
                    OUTPUT_LOG.append({'Headers2': 'Checking subnets for line: ' + str(rules['LINE'])})
                    if rules['CONSUMER_L3OUT'] != 'INTERNAL' and rules['CONSUMER_EPG'] != 'BLANK':
                        L3OUT_NAME = rules['CONSUMER_L3OUT']
                        L3OUT_SEARCH_RESPONSE = L3OUT_SEARCH(BASE_URL, APIC_COOKIE, TENANT, L3OUT_NAME, HEADERS)
                        L3OUT_DATA = L3OUT_SEARCH_RESPONSE[1]['imdata']
                        L3OUT_SUBNETS = []
                        # Loop through the VRF pull out all other L3Outs and add any l3extsubnet to a list
                        for key in L3OUT_DATA:
                            # For Python 3+
                            if 'l3extRsEctx' in key:
                            # For Python 2.7
                            #if key.keys() == ['l3extRsEctx']:
                                VRF_DN = key['l3extRsEctx']['attributes']['tDn']
                                VRF_SEARCH_RESPONSE = VRF_SEARCH(BASE_URL, APIC_COOKIE, VRF_DN, HEADERS)
                                for vrf_l3o in VRF_SEARCH_RESPONSE['imdata']:
                                    # For Python 3+
                                    if 'fvRtEctx' in vrf_l3o:
                                    # For Python 2.7
                                    #if vrf_l3o.keys() == ['fvRtEctx']:
                                        L3OUT_DN = vrf_l3o['fvRtEctx']['attributes']['tDn']
                                        SUBNET_SEARCH_RESPONSE = SUBNET_SEARCH(BASE_URL, APIC_COOKIE, L3OUT_DN, HEADERS)
                                        for subnets in SUBNET_SEARCH_RESPONSE['imdata']:
                                            L3OUT_SUBNETS.append(subnets['l3extSubnet']['attributes']['ip'])
                                            EXISTING_SUBNET = subnets['l3extSubnet']['attributes']['ip']
                                            EXISTING_L3OUT = subnets['l3extSubnet']['attributes']['dn'].split('/')[2][4:]
                                            EXISTING_EPG = subnets['l3extSubnet']['attributes']['dn'].split('/')[3][6:]
                                            SCOPE = subnets['l3extSubnet']['attributes']['scope'].split(',')
                                            if EXISTING_SUBNET in rules['CONSUMER_IP']:
                                                if 'import-security' in SCOPE:
                                                    if EXISTING_EPG == rules['CONSUMER_EPG']:
                                                        rules['CONSUMER_IP'].remove(EXISTING_SUBNET)
                                                    else:
                                                        OUTPUT_LOG.append({'Errors': EXISTING_SUBNET + ' already exists within ' + EXISTING_L3OUT + ' under EPG ' + EXISTING_EPG + ' no subnet configuration for this epg will be pushed.'})
                                                        ERROR = True
                                                        rules['CONSUMER_IP'].remove(EXISTING_SUBNET)

                                            else:
                                                for rule_subnet in rules['CONSUMER_IP']:
                                                    if IPNetwork(rule_subnet) in IPNetwork(EXISTING_SUBNET):
                                                        if int(EXISTING_SUBNET.split('/')[1]) >= 20 and 'import-security' in SCOPE:
                                                            OUTPUT_LOG.append({'Errors': rule_subnet + ' already exists within ' + EXISTING_L3OUT + ' under EPG ' + EXISTING_EPG + ' inside ' + EXISTING_SUBNET})
                                                            ERROR = True
                                                            rules['CONSUMER_IP'].remove(rule_subnet)


                        if len(rules['CONSUMER_IP']) >= 1:
                            OUTPUT_LOG.append({'Notifications': 'The Following subnets will be added to the EPG: ' + rules['CONSUMER_EPG']})
                            OUTPUT_LOG.append({'Notifications': str(rules['CONSUMER_IP'])})

                        else:
                            OUTPUT_LOG.append({'Notifications': 'No subnets will be added to EPG: ' + rules['CONSUMER_EPG']})

                    if rules['PROVIDER_L3OUT'] != 'INTERNAL' and rules['PROVIDER_EPG'] != 'BLANK':
                        L3OUT_NAME = rules['PROVIDER_L3OUT']
                        L3OUT_SEARCH_RESPONSE = L3OUT_SEARCH(BASE_URL, APIC_COOKIE, TENANT, L3OUT_NAME, HEADERS)
                        L3OUT_DATA = L3OUT_SEARCH_RESPONSE[1]['imdata']
                        L3OUT_SUBNETS = []
                        # Loop through the VRF pull out all other L3Outs and add any l3extsubnet to a list
                        for key in L3OUT_DATA:
                            # For Python 3+
                            if 'l3extRsEctx' in key:
                            # For Python 2.7
                            #if key.keys() == ['l3extRsEctx']:
                                VRF_DN = key['l3extRsEctx']['attributes']['tDn']
                                VRF_SEARCH_RESPONSE = VRF_SEARCH(BASE_URL, APIC_COOKIE, VRF_DN, HEADERS)
                                for vrf_l3o in VRF_SEARCH_RESPONSE['imdata']:
                                    # For Python 3+
                                    if 'fvRtEctx' in vrf_l3o:
                                    # For Python 2.7
                                    #if vrf_l3o.keys() == ['fvRtEctx']:
                                        L3OUT_DN = vrf_l3o['fvRtEctx']['attributes']['tDn']
                                        SUBNET_SEARCH_RESPONSE = SUBNET_SEARCH(BASE_URL, APIC_COOKIE, L3OUT_DN, HEADERS)
                                        for subnets in SUBNET_SEARCH_RESPONSE['imdata']:
                                            L3OUT_SUBNETS.append(subnets['l3extSubnet']['attributes']['ip'])
                                            EXISTING_SUBNET = subnets['l3extSubnet']['attributes']['ip']
                                            EXISTING_L3OUT = subnets['l3extSubnet']['attributes']['dn'].split('/')[2][4:]
                                            EXISTING_EPG = subnets['l3extSubnet']['attributes']['dn'].split('/')[3][6:]
                                            SCOPE = subnets['l3extSubnet']['attributes']['scope'].split(',')
                                            if EXISTING_SUBNET in rules['PROVIDER_IP']:
                                                if 'import-security' in SCOPE:
                                                    if EXISTING_EPG == rules['PROVIDER_EPG']:
                                                        rules['PROVIDER_IP'].remove(EXISTING_SUBNET)

                                                    else:
                                                        OUTPUT_LOG.append({'Errors': EXISTING_SUBNET + ' already exists within ' + EXISTING_L3OUT + ' under EPG ' + EXISTING_EPG + ' no subnet configuration for this epg will be pushed.'})
                                                        ERROR = True
                                                        rules['PROVIDER_IP'].remove(EXISTING_SUBNET)

                                            else:
                                                for rule_subnet in rules['PROVIDER_IP']:
                                                    if IPNetwork(rule_subnet) in IPNetwork(EXISTING_SUBNET):
                                                        if int(EXISTING_SUBNET.split('/')[1]) >= 20 and 'import-security' in SCOPE:
                                                            OUTPUT_LOG.append({'Errors': rule_subnet + ' already exists within ' + EXISTING_L3OUT + ' under EPG ' + EXISTING_EPG + ' inside ' + EXISTING_SUBNET})
                                                            ERROR = True
                                                            rules['PROVIDER_IP'].remove(rule_subnet)


                        if len(rules['PROVIDER_IP']) >= 1:
                            OUTPUT_LOG.append({'Notifications': 'The Following subnets will be added to the EPG: ' + rules['PROVIDER_EPG']})
                            OUTPUT_LOG.append({'Notifications': str(rules['PROVIDER_IP'])})

                        else:
                            OUTPUT_LOG.append({'Notifications': 'No subnets will be added to EPG: ' + rules['PROVIDER_EPG']})

                # Search for VIPs
                OUTPUT_LOG.append({'Headers': 'Checking if any EPGs are for VIPS'})

                for rules in RULE_LIST:
                    if rules['PROVIDER_EPG'].split('_')[0].endswith('VS') and rules['PROVIDER_L3OUT'].endswith('DCI_L3O'):
                        for subnets in rules['PROVIDER_IP']:
                            if len(subnets.split('/')) != 0:
                                subnet = subnets.split('/')[0]
                            else:
                                subnet = subnets
                            if not ipaddress.ip_address(subnet).is_private:
                                OUTPUT_LOG.append({'Notifications': rules['PROVIDER_EPG'] + ' contains a public address.'})
                                OUTPUT_LOG.append({'Notifications': subnets + ' will be imported under the DCI and exported under the INET L3Outs'})


                            elif ipaddress.ip_address(subnet).is_private:
                                OUTPUT_LOG.append({'Notifications': rules['PROVIDER_EPG'] + ' contains a private address.'})
                                OUTPUT_LOG.append({'Notifications': subnets + ' will be imported under the DCI L3Out'})

        else:
            OUTPUT_LOG.append({'Errors': 'Unable to connect to APIC.'})

    if not ERROR:
        OUTPUT_LOG.append({'ValidationSuccess': 'APIC Configuration validated successfully'})

    return OUTPUT_LOG
   
        
@shared_task
def EXTERNAL_EPG_DEPLOYMENT(RULE_LIST, location, url_dict, username, password):

    BASE_URL = url_dict[location]

    if location == 'UKDC1':
        DC = 'DC1'
    elif location == 'UKDC2':
        DC = 'DC2'
    elif location == 'LAB':
        DC = 'DC1'

    TENANT = 'common'
    OUTPUT_LOG = []
    HEADERS = {'content-type': 'application/json'}
    # --------------------------------------------------------------------------#
    # Begin Configuration
    # --------------------------------------------------------------------------#
    OUTPUT_LOG.append({'Headers': 'Starting External EPG Deployment.'})
    OUTPUT_LOG.append({'Headers': 'Connecting to APIC'})
    APIC_COOKIE = APIC_LOGIN(BASE_URL, username, password)
    if APIC_COOKIE:
        OUTPUT_LOG.append({'Notifications': 'Successfully generated authentication cookie'})

        check_i = 0
        for rules in RULE_LIST:
            check_i = check_i + 1
            L3OUT_CONSUME_EPG_CREATED = False
            L3OUT_PROVIDE_EPG_CREATED = False
            OUTPUT_LOG.append({'Headers2': 'Adding EPGs & Subnets for line: ' + str(rules['LINE'])})
            if rules['CONSUMER_L3OUT'] != 'INTERNAL' and rules['CONSUMER_EPG'] != 'BLANK':
                EPG_NAME = rules['CONSUMER_EPG']
                L3OUT_NAME = rules['CONSUMER_L3OUT']
                EXTERNAL_EPG_SEARCH_RESPONSE = EXTERNAL_EPG_SEARCH(BASE_URL, APIC_COOKIE, TENANT, L3OUT_NAME, EPG_NAME, HEADERS)
                if int(EXTERNAL_EPG_SEARCH_RESPONSE['totalCount']) == 1:
                    OUTPUT_LOG.append({'NotificationsWarning': 'EPG: ' + EPG_NAME + ' already exists under ' + L3OUT_NAME + ' and wont be created'})
                    L3OUT_CONSUME_EPG_CREATED = True
                if not L3OUT_CONSUME_EPG_CREATED:
                    OUTPUT_LOG.append({'Notifications': 'Adding External EPG: ' + EPG_NAME + ' TO L3Out: ' + L3OUT_NAME})
                    EXTERNAL_EPG_ADD(BASE_URL, APIC_COOKIE, TENANT, L3OUT_NAME, EPG_NAME, HEADERS, OUTPUT_LOG)
                # Add subnets to external EPG
                if len(rules['CONSUMER_IP']) != 0:
                    OUTPUT_LOG.append({'Notifications': 'Adding Subnets to External EPG: '})
                    for IP in rules['CONSUMER_IP']:
                        # SEARCH TO SEE IF SUBNET ALREADY EXISTS IN EPG:
                        L3OUT_DN = 'uni/tn-common/out-' + L3OUT_NAME + '/instP-' + EPG_NAME + '/extsubnet-[' + IP + ']'
                        SUBNET_SEARCH_RESPONSE = SUBNET_SEARCH_EXACT(BASE_URL, APIC_COOKIE, L3OUT_DN, HEADERS)
                        if int(SUBNET_SEARCH_RESPONSE['totalCount']) == 1:
                            for subnets in SUBNET_SEARCH_RESPONSE['imdata']:
                                EXISTING_SUBNET = subnets['l3extSubnet']['attributes']['ip']
                                SCOPE = subnets['l3extSubnet']['attributes']['scope'].split(',')
                                if EXISTING_SUBNET == IP:
                                    #IP Already Configured under EPG
                                    pass

                        else:
                            SCOPE = 'import-security'
                            EXTERNAL_EPG_SUBNET_ADD(BASE_URL, APIC_COOKIE, TENANT, L3OUT_NAME, EPG_NAME, HEADERS, IP, SCOPE, OUTPUT_LOG)

            if rules['PROVIDER_L3OUT'] != 'INTERNAL' and rules['PROVIDER_EPG'] != 'BLANK':
                EPG_NAME = rules['PROVIDER_EPG']
                L3OUT_NAME = rules['PROVIDER_L3OUT']
                EXTERNAL_EPG_SEARCH_RESPONSE = EXTERNAL_EPG_SEARCH(BASE_URL, APIC_COOKIE, TENANT, L3OUT_NAME, EPG_NAME, HEADERS)
                if int(EXTERNAL_EPG_SEARCH_RESPONSE['totalCount']) == 1:
                    OUTPUT_LOG.append({'NotificationsWarning': 'EPG: ' + EPG_NAME + ' already exists under ' + L3OUT_NAME + ' and wont be created'})
                    L3OUT_PROVIDE_EPG_CREATED = True
                if not L3OUT_PROVIDE_EPG_CREATED:
                    OUTPUT_LOG.append({'Notifications': 'Adding External EPG: ' + EPG_NAME + ' TO L3Out: ' + L3OUT_NAME})
                    EXTERNAL_EPG_ADD(BASE_URL, APIC_COOKIE, TENANT, L3OUT_NAME, EPG_NAME, HEADERS, OUTPUT_LOG)
                # Add subnets to external EPG
                if len(rules['PROVIDER_IP']) != 0:
                    OUTPUT_LOG.append({'Notifications': 'Adding Subnets to External EPG: '})
                    for IP in rules['PROVIDER_IP']:
                        # SEARCH TO SEE IF SUBNET ALREADY EXISTS IN EPG:
                        L3OUT_DN = 'uni/tn-common/out-' + L3OUT_NAME + '/instP-' + EPG_NAME + '/extsubnet-[' + IP + ']'
                        SUBNET_SEARCH_RESPONSE = SUBNET_SEARCH_EXACT(BASE_URL, APIC_COOKIE, L3OUT_DN, HEADERS)
                        if int(SUBNET_SEARCH_RESPONSE['totalCount']) == 1:
                            for subnets in SUBNET_SEARCH_RESPONSE['imdata']:
                                EXISTING_SUBNET = subnets['l3extSubnet']['attributes']['ip']
                                SCOPE = subnets['l3extSubnet']['attributes']['scope'].split(',')
                                if EXISTING_SUBNET == IP:
                                    #IP Already Configured under EPG
                                    pass

                        else:
                            if len(IP.split('/')) != 0:
                                subnet = IP.split('/')[0]
                            else:
                                subnet = IP
                            # Check for VS EPGs
                            if rules['PROVIDER_EPG'].split('_')[0].endswith('VS') and rules['PROVIDER_L3OUT'].endswith('DCI_L3O'):

                                if not ipaddress.ip_address(subnet).is_private:
                                    # Import Under DCI
                                    SCOPE = 'import-rtctrl,import-security'
                                    L3OUT_NAME = rules['PROVIDER_L3OUT']
                                    EPG_NAME = rules['PROVIDER_EPG']
                                    EXTERNAL_EPG_SUBNET_ADD(BASE_URL, APIC_COOKIE, TENANT, L3OUT_NAME, EPG_NAME, HEADERS, IP, SCOPE, OUTPUT_LOG)

                                    # Export Under Inet
                                    SCOPE = 'export-rtctrl'
                                    # Build L3out name for Inet L3Out
                                    # Temp fix for BLUE INET
                                    if rules['PROVIDER_L3OUT'].split('-')[0] == 'BLUE':
                                        L3OUT_NAME = rules['PROVIDER_L3OUT'].split('-')[0] + '-' + DC + '-INET_L3O'
                                    else:
                                        L3OUT_NAME = rules['PROVIDER_L3OUT'].split('-')[0] + '-INET_L3O'

                                    EPG_NAME = rules['PROVIDER_L3OUT'].split('_')[0] + '-ROUTING_EPG'
                                    EXTERNAL_EPG_SUBNET_ADD(BASE_URL, APIC_COOKIE, TENANT, L3OUT_NAME, EPG_NAME, HEADERS, IP, SCOPE, OUTPUT_LOG)

                                if ipaddress.ip_address(subnet).is_private:
                                    # Import Under DCI
                                    L3OUT_NAME = rules['PROVIDER_L3OUT']
                                    EPG_NAME = rules['PROVIDER_EPG']
                                    SCOPE = 'import-rtctrl,import-security'
                                    EXTERNAL_EPG_SUBNET_ADD(BASE_URL, APIC_COOKIE, TENANT, L3OUT_NAME, EPG_NAME, HEADERS, IP, SCOPE, OUTPUT_LOG)

                            else:
                                L3OUT_NAME = rules['PROVIDER_L3OUT']
                                EPG_NAME = rules['PROVIDER_EPG']
                                SCOPE = 'import-security'
                                EXTERNAL_EPG_SUBNET_ADD(BASE_URL, APIC_COOKIE, TENANT, L3OUT_NAME, EPG_NAME, HEADERS, IP, SCOPE, OUTPUT_LOG)

    else:
        OUTPUT_LOG.append({'Errors': 'Unable to connect to APIC.'})

    return OUTPUT_LOG


@shared_task
def CONTRACT_DEPLOYMENT_VALIDATION(RULE_LIST, location, url_dict, username, password):
    CONTRACT_LIST = []
    FILTER_LIST = []
    DISPLAY_LIST = []
    OUTPUT_LOG = []
    ERROR = False
    HEADERS = {'content-type': 'application/json'}
    TENANT_LIST = ['RED', 'GREEN', 'BLUE']

    BASE_URL = url_dict[location]

    # Validate Contract Name formatting
    OUTPUT_LOG.append({'Headers': 'Validating Contract names in Workbook.'})

    try:
        for rules in RULE_LIST:
            if (len(rules['NAME'].split('_'))) > 2:
                DISPLAY_LIST.append(rules['NAME'])
                ERROR = True
            elif rules['NAME'].split('_')[1].upper() != 'GCTR':
                DISPLAY_LIST.append(rules['NAME'])
                ERROR = True
            elif rules['NAME'].split('-')[0].upper() not in TENANT_LIST:
                DISPLAY_LIST.append(rules['NAME'])
                ERROR = True

            else:
                pass

        DISPLAY_SET = set(DISPLAY_LIST)
        for contracts in DISPLAY_SET:
            OUTPUT_LOG.append({'Errors': 'Contract "' + contracts + '" does not conform to the naming standard'})
        DISPLAY_LIST = []

    except:
        OUTPUT_LOG.append({'Errors': 'Errors validating Contract names'})
        ERROR = True

    if not ERROR:
        OUTPUT_LOG.append({'NotificationsSuccess': 'Contract formatting validated successfully'})

    OUTPUT_LOG.append({'Headers': 'Validating EPG names in Workbook.'})

    for rules in RULE_LIST:
        if rules['CONSUMER_EPG'] != 'BLANK':
            try:
                if len(rules['CONSUMER_EPG'].split('_')) > 2:
                    DISPLAY_LIST.append(rules['CONSUMER_EPG'])
                    ERROR = True
                elif rules['CONSUMER_EPG'].split('_')[1].upper() != 'EPG':
                    DISPLAY_LIST.append(rules['CONSUMER_EPG'])
                    ERROR = True
                elif rules['CONSUMER_EPG'].split('-')[0].upper() not in TENANT_LIST:
                    DISPLAY_LIST.append(rules['CONSUMER_EPG'])
                    ERROR = True

                else:
                    pass

            except:
                ERROR = True
                OUTPUT_LOG.append(
                    {'Errors': 'EPG "' + rules['CONSUMER_EPG'] + '" does not conform to the naming standard'})

        if rules['PROVIDER_EPG'] != 'BLANK':
            try:
                if len(rules['PROVIDER_EPG'].split('_')) > 2:
                    DISPLAY_LIST.append(rules['PROVIDER_EPG'])
                    ERROR = True

                elif rules['PROVIDER_EPG'].split('_')[1].upper() != 'EPG':
                    DISPLAY_LIST.append(rules['PROVIDER_EPG'])
                    ERROR = True

                elif rules['PROVIDER_EPG'].split('-')[0].upper() not in TENANT_LIST:
                    DISPLAY_LIST.append(rules['PROVIDER_EPG'])
                    ERROR = True

                else:
                    pass

            except:
                ERROR = True
                OUTPUT_LOG.append(
                    {'Errors': 'EPG "' + rules['PROVIDER_EPG'] + '" does not conform to the naming standard'})

        DISPLAY_SET = set(DISPLAY_LIST)
        for contracts in DISPLAY_SET:
            OUTPUT_LOG.append({'Errors': 'EPG "' + contracts + '" does not conform to the naming standard'})
        DISPLAY_LIST = []

    if not ERROR:
        OUTPUT_LOG.append({'NotificationsSuccess': 'EPG formatting validated successfully'})

    OUTPUT_LOG.append({'Headers': 'Validating Contract and EPG locality.'})

    for rules in RULE_LIST:

        if rules['CONSUMER_EPG'] != 'BLANK':
            if rules['CONSUMER_EPG'].split('-')[0].upper() != rules['NAME'].split('-')[0].upper():
                DISPLAY_LIST.append(rules['CONSUMER_EPG'])
                ERROR = True

        if rules['PROVIDER_EPG'] != 'BLANK':
            if rules['PROVIDER_EPG'].split('-')[0].upper() != rules['NAME'].split('-')[0].upper():
                DISPLAY_LIST.append(rules['PROVIDER_EPG'])
                ERROR = True

        else:
            pass

    DISPLAY_SET = set(DISPLAY_LIST)
    for contracts in DISPLAY_SET:
        OUTPUT_LOG.append({'Errors': contracts + ' and Contract named for different Tenants.'})
    DISPLAY_LIST = []

    if not ERROR:
        OUTPUT_LOG.append({'NotificationsSuccess': 'Contract and EPG locality validated successfully'})

    OUTPUT_LOG.append({'Headers': 'Validating Services in Workbook.'})

    for rules in RULE_LIST:
        for services in rules['SERVICE']:
            PROTOCOLS = ['TCP', 'UDP']
            try:
                value = int(services.split('-')[1])
            except:
                OUTPUT_LOG.append(
                    {'Errors': 'Service port not correct format for ' + services + ' on line ' + str(rules['LINE'])})
            if services.split('-')[0] not in PROTOCOLS:
                OUTPUT_LOG.append({'Errors': 'TCP or UDP not specified for service ' + services})
                ERROR = True

            elif int(services.split('-')[1]) == 0:
                OUTPUT_LOG.append({'Errors': 'Error Port out of range ' + services})
                ERROR = True

            elif int(services.split('-')[1]) not in range(1, 65536):
                OUTPUT_LOG.append({'Errors': 'Error Port out of range ' + services})
                ERROR = True

            elif len(services.split('-')) == 3:
                if int(services.split('-')[2]) not in range(1, 65536):
                    OUTPUT_LOG.append({'Errors': 'Error Port out of range ' + services})
                    ERROR = True

            else:
                pass

    if not ERROR:
        OUTPUT_LOG.append({'NotificationsSuccess': 'Services validated successfully'})

        OUTPUT_LOG.append({'Headers': 'Connecting to APIC'})
        APIC_COOKIE = APIC_LOGIN(BASE_URL, username, password)

        if APIC_COOKIE:
            OUTPUT_LOG.append({'Notifications': 'Successfully generated authentication cookie'})

            # Check if Contracts Exist
            OUTPUT_LOG.append({'Headers': 'Checking if Contracts exist'})
            for rules in RULE_LIST:
                CONTRACT_NAME = rules['NAME']
                CONTRACT_SEARCH_RESPONSE = CONTRACT_SEARCH(BASE_URL, APIC_COOKIE, CONTRACT_NAME, HEADERS)
                if int(CONTRACT_SEARCH_RESPONSE['totalCount']) == 1:
                    pass
                else:
                    CONTRACT_LIST.append(CONTRACT_NAME)

            CONTRACT_SET = set(CONTRACT_LIST)
            for contracts in CONTRACT_SET:
                OUTPUT_LOG.append({'Notifications': 'Contract ' + contracts + ' will be created'})

            # Check if Filters Exist
            OUTPUT_LOG.append({'Headers': 'Checking if Filters exist'})
            for rules in RULE_LIST:
                for services in rules['SERVICE']:
                    FILTER_NAME = services
                    FILTER_SEARCH_RESPONSE = FILTER_SEARCH(BASE_URL, APIC_COOKIE, FILTER_NAME, HEADERS)
                    if int(FILTER_SEARCH_RESPONSE['totalCount']) == 1:
                        pass
                    else:
                        FILTER_LIST.append(FILTER_NAME)

            FILTER_SET = set(FILTER_LIST)
            for filters in FILTER_SET:
                OUTPUT_LOG.append({'Notifications': 'Filter ' + filters + ' will be created'})

            # Check if Filters are applied to contracts
            OUTPUT_LOG.append({'Headers': 'Checking if Filters are applied to contracts'})
            for rules in RULE_LIST:
                # Use the contract search to locate subject
                CONTRACT_NAME = rules['NAME']
                CONTRACT_SEARCH_RESPONSE = CONTRACT_SEARCH(BASE_URL, APIC_COOKIE, CONTRACT_NAME, HEADERS)
                # Validate that a contract can be located
                if int(CONTRACT_SEARCH_RESPONSE['totalCount']) == 1:
                    TENANT = CONTRACT_SEARCH_RESPONSE['imdata'][0]['vzBrCP']['attributes']['dn'].split('/')[1][3:]
                    CONTRACT_SUBJECT = \
                    CONTRACT_SEARCH_RESPONSE['imdata'][0]['vzBrCP']['attributes']['dn'].split('/')[2][4:].split('_')[0] + '_SBJ'
                    SUBJECT_SEARCH_RESPONSE = SUBJECT_SEARCH(BASE_URL, APIC_COOKIE, CONTRACT_NAME, TENANT, CONTRACT_SUBJECT,
                                                             HEADERS)

                    # Add all filters for a subject to a list to be used for comparison.
                    SUBJECT_FILTERS = []
                    for filters in SUBJECT_SEARCH_RESPONSE['imdata']:
                        SUBJECT_FILTERS.append(filters['vzRsSubjFiltAtt']['attributes']['tnVzFilterName'])

                    # compare list of filters to those already in subject

                    FILTER_COMPARE = LIST_COMPARE(rules['SERVICE'], SUBJECT_FILTERS)
                    if len(FILTER_COMPARE[0]) == 0:
                        pass

                    elif len(FILTER_COMPARE[0]) > 0:
                        OUTPUT_LOG.append({'Notifications': 'The below filters will be added to contract ' + CONTRACT_NAME})
                        OUTPUT_LOG.append({'Notifications': FILTER_COMPARE[0]})

                    else:
                        ERROR = True
                else:
                    pass

            # Check if L3Outs Exist
            OUTPUT_LOG.append({'Headers': 'Checking if L3Outs exist'})
            for rules in RULE_LIST:
                if rules['CONSUMER_L3OUT'] == 'INTERNAL':
                    pass
                else:
                    L3OUT_NAME = rules['CONSUMER_L3OUT']
                    L3OUT_SEARCH_RESPONSE = CONTRACT_L3OUT_SEARCH(BASE_URL, APIC_COOKIE, L3OUT_NAME, HEADERS)
                    if int(L3OUT_SEARCH_RESPONSE['totalCount']) == 1:
                        if rules['CONSUMER_L3OUT'] == L3OUT_SEARCH_RESPONSE['imdata'][0]['l3extOut']['attributes']['name']:
                            pass
                        else:
                            ERROR = True

                    else:
                        DISPLAY_LIST.append(L3OUT_NAME)
                        ERROR = True

            for rules in RULE_LIST:
                if rules['PROVIDER_L3OUT'] == 'INTERNAL':
                    pass
                else:
                    L3OUT_NAME = rules['PROVIDER_L3OUT']
                    L3OUT_SEARCH_RESPONSE = CONTRACT_L3OUT_SEARCH(BASE_URL, APIC_COOKIE, L3OUT_NAME, HEADERS)
                    if int(L3OUT_SEARCH_RESPONSE['totalCount']) == 1:
                        if rules['PROVIDER_L3OUT'] == L3OUT_SEARCH_RESPONSE['imdata'][0]['l3extOut']['attributes']['name']:
                            pass
                        else:
                            ERROR = True

                    else:
                        DISPLAY_LIST.append(L3OUT_NAME)
                        ERROR = True

            DISPLAY_SET = set(DISPLAY_LIST)
            for l3out in DISPLAY_SET:
                OUTPUT_LOG.append({'Errors': 'L3Out: ' + l3out + ' Does not exist, please check naming.'})
            DISPLAY_LIST = []

            if not ERROR:
                # Check if External EPGs Exist
                OUTPUT_LOG.append({'Headers': 'Checking if External EPGs are created'})
                for rules in RULE_LIST:
                    if rules['CONSUMER_L3OUT'] == 'INTERNAL':
                        pass
                    else:
                        if rules['CONSUMER_EPG'] != 'BLANK':
                            CONSUMER_L3OUT = rules['CONSUMER_L3OUT']
                            CONSUMER_EPG = rules['CONSUMER_EPG']
                            EXTERNAL_EPG_SEARCH_RESPONSE = CONTRACT_EXTERNAL_EPG_SEARCH(BASE_URL, APIC_COOKIE, CONSUMER_L3OUT, CONSUMER_EPG,
                                                                               HEADERS)
                            if int(EXTERNAL_EPG_SEARCH_RESPONSE['totalCount']) == 1:
                                EPG_NAME = EXTERNAL_EPG_SEARCH_RESPONSE['imdata'][0]['l3extInstP']['attributes']['dn'].split('/')[
                                               3][6:]
                                L3OUT_NAME = EXTERNAL_EPG_SEARCH_RESPONSE['imdata'][0]['l3extInstP']['attributes']['dn'].split('/')[
                                                 2][4:]
                                EXTERNAL_EPG_SEARCH_RESPONSE['imdata'][0]['l3extInstP']['attributes']['dn'].split('/')[1][3:]
                                if L3OUT_NAME == rules['CONSUMER_L3OUT']:
                                    pass
                                else:
                                    OUTPUT_LOG.append({'Errors': 'EPG and L3OUT missmatch with ' + L3OUT_NAME + ' and ' + EPG_NAME + ' dont match value: ' +
                                                                    rules['CONSUMER_L3OUT']})

                            else:
                                DISPLAY_LIST.append(CONSUMER_EPG)
                                ERROR = True

                for rules in RULE_LIST:
                    PROVIDER_EPG = rules['PROVIDER_EPG']
                    if rules['PROVIDER_L3OUT'] == 'INTERNAL':
                        pass
                    else:
                        if rules['PROVIDER_EPG'] != 'BLANK':
                            PROVIDER_EPG = rules['PROVIDER_EPG']
                            PROVIDER_L3OUT = rules['PROVIDER_L3OUT']
                            EXTERNAL_EPG_SEARCH_RESPONSE = CONTRACT_EXTERNAL_EPG_SEARCH(BASE_URL, APIC_COOKIE, PROVIDER_L3OUT, PROVIDER_EPG,
                                                                               HEADERS)
                            if int(EXTERNAL_EPG_SEARCH_RESPONSE['totalCount']) == 1:
                                EPG_NAME = EXTERNAL_EPG_SEARCH_RESPONSE['imdata'][0]['l3extInstP']['attributes']['dn'].split('/')[
                                               3][6:]
                                L3OUT_NAME = EXTERNAL_EPG_SEARCH_RESPONSE['imdata'][0]['l3extInstP']['attributes']['dn'].split('/')[
                                                 2][4:]
                                EXTERNAL_EPG_SEARCH_RESPONSE['imdata'][0]['l3extInstP']['attributes']['dn'].split('/')[1][3:]
                                if L3OUT_NAME == rules['PROVIDER_L3OUT']:
                                    pass
                                else:
                                    OUTPUT_LOG.append({'Errors': 'EPG and L3OUT missmatch with ' + L3OUT_NAME + ' and ' + EPG_NAME + ' dont match value: ' +
                                                                    rules['PROVIDER_L3OUT']})

                            else:
                                DISPLAY_LIST.append(PROVIDER_EPG)
                                ERROR = True

                DISPLAY_SET = set(DISPLAY_LIST)
                for epgs in DISPLAY_SET:
                    OUTPUT_LOG.append({'Errors': 'EPG "' + epgs + '" needs creating.'})

            # Check if Internal EPGs Exist
            OUTPUT_LOG.append({'Headers': 'Checking if Internal EPGs are created'})
            EPG_LIST = []
            DISPLAY_LIST = []
            # Search to validate internal EPG's are created
            for rules in RULE_LIST:
                if rules['CONSUMER_L3OUT'] == 'INTERNAL':
                    if rules['CONSUMER_EPG'] != 'BLANK':
                        CONSUMER_EPG = rules['CONSUMER_EPG']
                        # Search for consumer EPG
                        INTERNAL_EPG_SEARCH_RESPONSE = INTERNAL_EPG_SEARCH(BASE_URL, APIC_COOKIE, CONSUMER_EPG, HEADERS)
                        if int(INTERNAL_EPG_SEARCH_RESPONSE['totalCount']) == 1:
                            pass
                        else:
                            DISPLAY_LIST.append(CONSUMER_EPG)
                            ERROR = True
                else:
                    pass

            for rules in RULE_LIST:
                if rules['PROVIDER_L3OUT'] == 'INTERNAL':
                    if rules['PROVIDER_EPG'] != 'BLANK':
                        PROVIDER_EPG = rules['PROVIDER_EPG']
                        # Search for Provider EPG
                        INTERNAL_EPG_SEARCH_RESPONSE = INTERNAL_EPG_SEARCH(BASE_URL, APIC_COOKIE, PROVIDER_EPG, HEADERS)
                        if int(INTERNAL_EPG_SEARCH_RESPONSE['totalCount']) == 1:
                            pass
                        else:
                            DISPLAY_LIST.append(PROVIDER_EPG)
                            ERROR = True
                else:
                    pass

            DISPLAY_SET = set(DISPLAY_LIST)
            for epgs in DISPLAY_SET:
                OUTPUT_LOG.append({'Errors': 'EPG "' + epgs + '" needs creating.'})
            DISPLAY_LIST = []


        else:
            OUTPUT_LOG.append({'Errors': 'Unable to connect to APIC.'})

    if not ERROR:
        OUTPUT_LOG.append({'ValidationSuccess': 'APIC Configuration validated successfully'})

    return OUTPUT_LOG


@shared_task
def CONTRACT_DEPLOYMENT(RULE_LIST, location, url_dict, username, password):

    BASE_URL = url_dict[location]

    CONTRACT_LIST = []
    FILTER_LIST = []
    DISPLAY_LIST = []
    OUTPUT_LOG = []
    HEADERS = {'content-type': 'application/json'}
    # --------------------------------------------------------------------------#
    # Begin Configuration
    # --------------------------------------------------------------------------#
    OUTPUT_LOG.append({'Headers': 'Starting contract provisioning.'})
    OUTPUT_LOG.append({'Headers': 'Connecting to APIC'})
    APIC_COOKIE = APIC_LOGIN(BASE_URL, username, password)
    if APIC_COOKIE:
        OUTPUT_LOG.append({'Notifications': 'Successfully generated authentication cookie'})

        OUTPUT_LOG.append({'Headers': 'Creating Filters.'})
        # Create Filters in Filter SET
        for rules in RULE_LIST:
            for services in rules['SERVICE']:
                FILTER_NAME = services
                FILTER_SEARCH_RESPONSE = FILTER_SEARCH(BASE_URL, APIC_COOKIE, FILTER_NAME, HEADERS)
                if int(FILTER_SEARCH_RESPONSE['totalCount']) == 1:
                    pass
                else:
                    FILTER_LIST.append(FILTER_NAME)

        FILTER_SET = set(FILTER_LIST)
        if len(FILTER_SET) > 0:
            OUTPUT_LOG = FILTER_CREATE(FILTER_SET, BASE_URL, APIC_COOKIE, HEADERS, OUTPUT_LOG)
        else:
            pass

        OUTPUT_LOG.append({'Headers': 'Creating Contract & Subjects.'})
        # Create Contracts and Subjects in Contract SET
        for rules in RULE_LIST:
            CONTRACT_NAME = rules['NAME']
            CONTRACT_SEARCH_RESPONSE = CONTRACT_SEARCH(BASE_URL, APIC_COOKIE, CONTRACT_NAME, HEADERS)
            if int(CONTRACT_SEARCH_RESPONSE['totalCount']) == 1:
                pass
            else:
                CONTRACT_LIST.append(CONTRACT_NAME)

        CONTRACT_SET = set(CONTRACT_LIST)
        if len(CONTRACT_SET) > 0:
            OUTPUT_LOG = CONTRACT_CREATE(CONTRACT_SET, BASE_URL, APIC_COOKIE, HEADERS, OUTPUT_LOG)
        else:
            pass

        # Add filters to subjects
        for rules in RULE_LIST:
            # Use the contract search to locate subject
            CONTRACT_NAME = rules['NAME']
            CONTRACT_SEARCH_RESPONSE = CONTRACT_SEARCH(BASE_URL, APIC_COOKIE, CONTRACT_NAME, HEADERS)
            # Validate that a contract can be located
            if int(CONTRACT_SEARCH_RESPONSE['totalCount']) == 1:
                TENANT = CONTRACT_SEARCH_RESPONSE['imdata'][0]['vzBrCP']['attributes']['dn'].split('/')[1][3:]
                CONTRACT_SUBJECT = \
                CONTRACT_SEARCH_RESPONSE['imdata'][0]['vzBrCP']['attributes']['dn'].split('/')[2][4:].split('_')[0] + '_SBJ'
                SUBJECT_SEARCH_RESPONSE = SUBJECT_SEARCH(BASE_URL, APIC_COOKIE, CONTRACT_NAME, TENANT, CONTRACT_SUBJECT,
                                                         HEADERS)

                # Add all filters for a subject to a list to be used for comparison.
                SUBJECT_FILTERS = []
                for filters in SUBJECT_SEARCH_RESPONSE['imdata']:
                    SUBJECT_FILTERS.append(filters['vzRsSubjFiltAtt']['attributes']['tnVzFilterName'])

                # compare list of filters to those already in subject
                NEW_FILTERS = rules['SERVICE']
                FILTER_COMPARE = LIST_COMPARE(NEW_FILTERS, SUBJECT_FILTERS)
                if len(FILTER_COMPARE[0]) == 0:
                    pass

                elif len(FILTER_COMPARE[0]) > 0:
                    for FILTERS in FILTER_COMPARE[0]:
                        OUTPUT_LOG = FILTER_ATTACH(BASE_URL, APIC_COOKIE, CONTRACT_NAME, CONTRACT_SUBJECT, FILTERS, HEADERS,
                                                   OUTPUT_LOG)

                else:
                    OUTPUT_LOG.append({'Errors': 'Error adding Filters to subject!'})

                NEW_FILTERS = ''

            else:
                pass

        OUTPUT_LOG.append({'Headers': 'Consuming & Providing Contracts.'})

        for rules in RULE_LIST:
            LINE = rules['LINE']
            CONTRACT_NAME = rules['NAME']
            # Consuming contract
            EPG_NAME = rules['CONSUMER_EPG']
            OUTPUT_LOG.append({'Headers2': 'Deploying Contracts for Line: ' + str(LINE)})

            if EPG_NAME != 'BLANK':
                if rules['CONSUMER_L3OUT'] == 'INTERNAL':
                    INTERNL_EPG_CONTRACT_CONSUME(BASE_URL, EPG_NAME, CONTRACT_NAME, APIC_COOKIE, HEADERS, OUTPUT_LOG)
                else:
                    L3OUT_NAME = rules['CONSUMER_L3OUT']
                    EXTERNAL_EPG_CONTRACT_CONSUME(L3OUT_NAME, EPG_NAME, CONTRACT_NAME, BASE_URL, APIC_COOKIE, HEADERS,
                                                  OUTPUT_LOG)

            # Providing contract
            EPG_NAME = rules['PROVIDER_EPG']
            if EPG_NAME != 'BLANK':
                if rules['PROVIDER_L3OUT'] == 'INTERNAL':
                    INTERNL_EPG_CONTRACT_PROVIDE(BASE_URL, EPG_NAME, CONTRACT_NAME, APIC_COOKIE, HEADERS, OUTPUT_LOG)
                else:
                    L3OUT_NAME = rules['PROVIDER_L3OUT']
                    EXTERNAL_EPG_CONTRACT_PROVIDE(L3OUT_NAME, EPG_NAME, CONTRACT_NAME, BASE_URL, APIC_COOKIE, HEADERS,
                                                  OUTPUT_LOG)

    else:
        OUTPUT_LOG.append({'Errors': 'Unable to connect to APIC.'})

    return OUTPUT_LOG
