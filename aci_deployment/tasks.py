# Base Functions
import openpyxl

# Custom Functions
from aci_deployment.scripts.endpoint_search import *
from aci_deployment.scripts.external_epg_deployment import *
from aci_deployment.scripts.baseline import APIC_LOGIN
# Celery Functions
from celery import shared_task

@shared_task
def SUBNET_SEARCH(BASE_URL, APIC_USERNAME, APIC_PASSWORD, SUBNET):
    RESULTS = []

    ENDPOINT_LIST = GET_ENDPOINTS(BASE_URL, APIC_USERNAME, APIC_PASSWORD)

    for i in ENDPOINT_LIST:
        if IPNetwork(SUBNET) in IPNetwork(i['Subnet']) or IPNetwork(i['Subnet']) in IPNetwork(SUBNET):
            RESULTS.append(
                {'Subnet': i['Subnet'], 'Locality': i['Locality'], 'Location': i['Location'], 'EPG': i['EPG'],
                 'Scope': i['Scope'], 'AppProfile': i['AppProfile'], 'Tenant': i['Tenant']})

    return RESULTS

@shared_task
def EXTERNAL_EPG_EXCEL_OPEN_WORKBOOK(WORKBOOK, LOCATION):
    WB = openpyxl.load_workbook(WORKBOOK, data_only=True)
    if LOCATION == 'DC1':
        PY_WS = WB['ACI_DC1']
    elif LOCATION == 'DC2':
        PY_WS = WB['ACI_DC2']
    elif LOCATION == 'LAB':
        PY_WS = WB['ACI_LAB']
    elif LOCATION == 'SANDBOX':
        PY_WS = WB['ACI_SANDBOX']

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
def EXTERNAL_EPG_VALIDATION(RULE_LIST, LOCATION, APIC_USERNAME, APIC_PASSWORD):
    OUTPUT_LOG = []
    DISPLAY_LIST = []
    TENANT_LIST = ['RED', 'GREEN', 'BLUE']
    ERROR = False
    TENANT = 'common'

    if LOCATION == 'DC1':
        BASE_URL = 'https://sandboxapicdc.cisco.com/api/'
    elif LOCATION == 'DC2':
        BASE_URL = 'https://sandboxapicdc.cisco.com/api/'
    elif LOCATION == 'LAB':
        BASE_URL = 'https://sandboxapicdc.cisco.com/api/'
    elif LOCATION == 'SANDBOX':
        BASE_URL = 'https://sandboxapicdc.cisco.com/api/'


    OUTPUT_LOG.append({'Notifications': ''})
    OUTPUT_LOG.append({'Notifications': 'Validating EPG names in Workbook.'})
    OUTPUT_LOG.append({'Notifications': '-----------------------------'})

    for rules in RULE_LIST:
        print(rules)
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
                elif rules['CONSUMER_L3OUT'] == 'BLUE-DC1-INET_L3O' or 'BLUE-DC2-INET_L3O':
                    continue
                elif not rules['CONSUMER_EPG'].split('_')[0].startswith(rules['CONSUMER_EPG'].split('_')[0]):
                    DISPLAY_LIST.append(rules['CONSUMER_EPG'])
                    ERROR = True

                else:
                    pass

            except:
                ERROR = True
                OUTPUT_LOG.append({'Errors': 'EPGs dont conform to the naming standard'})

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
                elif rules['PROVIDER_L3OUT'] == 'BLUE-DC1-INET_L3O' or 'BLUE-DC2-INET_L3O':
                    continue
                elif not rules['PROVIDER_EPG'].split('_')[0].startswith(rules['PROVIDER_L3OUT'].split('_')[0]):
                    DISPLAY_LIST.append(rules['PROVIDER_EPG'])
                    ERROR = True

                else:
                    pass

            except:
                ERROR = True
                OUTPUT_LOG.append({'Errors': 'EPGs dont conform to the naming standard'})

        else:
            pass

    DISPLAY_SET = set(DISPLAY_LIST)
    for contracts in DISPLAY_SET:
        OUTPUT_LOG.append({'Errors': 'EPG "' + contracts + '" does not conform to the naming standard'})
    DISPLAY_LIST = []

    if not ERROR:
        OUTPUT_LOG.append({'Notifications': 'EPG formatting validated successfully'})


    OUTPUT_LOG.append({'Notifications': ''})
    OUTPUT_LOG.append({'Notifications': 'Validating IP addresses'})
    OUTPUT_LOG.append({'Notifications': '-----------------------------'})
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
        OUTPUT_LOG.append({'Notifications': 'IP validation successful'})

    # Login to fabric
    APIC_COOKIE = APIC_LOGIN(BASE_URL, APIC_USERNAME, APIC_PASSWORD)
    print(BASE_URL + APIC_PASSWORD + APIC_USERNAME)
    print(APIC_COOKIE)
    if APIC_COOKIE:
        OUTPUT_LOG.append({'Notifications': ''})
        OUTPUT_LOG.append({'Notifications': 'Connecting to APIC'})
        OUTPUT_LOG.append({'Notifications': '-----------------------------'})
        OUTPUT_LOG.append({'Notifications': 'Successfully generated authentication cookie'})
    else:
        OUTPUT_LOG.append({'Errors': 'Unable to connect to APIC. Please check your credentials'})

    # Search for L3out and build URL to add IP's
    OUTPUT_LOG.append({'Notifications': ''})
    OUTPUT_LOG.append({'Notifications': 'Validating L3Out Names'})
    OUTPUT_LOG.append({'Notifications': '-----------------------------'})
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
        OUTPUT_LOG.append({'Notifications': 'L3Out validation successful'})

    # Check if IP already exists in Same L3Out or same VRF
    OUTPUT_LOG.append({'Notifications': ''})
    OUTPUT_LOG.append({'Notifications': 'Checking if IP currently exists within VRF'})
    OUTPUT_LOG.append({'Notifications': '-----------------------------'})

    # Get L3out VRF
    for rules in RULE_LIST:
        OUTPUT_LOG.append({'Notifications': 'Checking subnets for line: ' + str(rules['LINE'])})
        OUTPUT_LOG.append({'Notifications': ''})
        if rules['CONSUMER_L3OUT'] != 'INTERNAL' and rules['CONSUMER_EPG'] != 'BLANK':
            L3OUT_NAME = rules['CONSUMER_L3OUT']
            L3OUT_SEARCH_RESPONSE = L3OUT_SEARCH(BASE_URL, APIC_COOKIE, TENANT, L3OUT_NAME, HEADERS)
            L3OUT_DATA = L3OUT_SEARCH_RESPONSE[1]['imdata']
            L3OUT_SUBNETS = []
            # Loop through the VRF pull out all other L3Outs and add any l3extsubnet to a list
            #for key in L3OUT_DATA:
            #    # For Python 3+
            #    if 'l3extRsEctx' in key:
            #    # For Python 2.7
            #    #if key.keys() == ['l3extRsEctx']:
            #        VRF_DN = key['l3extRsEctx']['attributes']['tDn']
            #        VRF_SEARCH_RESPONSE = VRF_SEARCH(BASE_URL, APIC_COOKIE, VRF_DN, HEADERS)
            #        for vrf_l3o in VRF_SEARCH_RESPONSE['imdata']:
            #            # For Python 3+
            #            if 'fvRtEctx' in vrf_l3o:
            #            # For Python 2.7
            #            #if vrf_l3o.keys() == ['fvRtEctx']:
            #                L3OUT_DN = vrf_l3o['fvRtEctx']['attributes']['tDn']
            #                SUBNET_SEARCH_RESPONSE = SUBNET_SEARCH(BASE_URL, APIC_COOKIE, L3OUT_DN, HEADERS)
            #                for subnets in SUBNET_SEARCH_RESPONSE['imdata']:
            #                    L3OUT_SUBNETS.append(subnets['l3extSubnet']['attributes']['ip'])
            #                    EXISTING_SUBNET = subnets['l3extSubnet']['attributes']['ip']
            #                    EXISTING_L3OUT = subnets['l3extSubnet']['attributes']['dn'].split('/')[2][4:]
            #                    EXISTING_EPG = subnets['l3extSubnet']['attributes']['dn'].split('/')[3][6:]
            #                    SCOPE = subnets['l3extSubnet']['attributes']['scope'].split(',')
            #                    if EXISTING_SUBNET in rules['CONSUMER_IP']:
            #                        if 'import-security' in SCOPE:
            #                            if EXISTING_EPG == rules['CONSUMER_EPG']:
            #                                rules['CONSUMER_IP'].remove(EXISTING_SUBNET)
            #                            else:
            #                                OUTPUT_LOG.append({'Errors': EXISTING_SUBNET + ' already exists within ' + EXISTING_L3OUT + ' under EPG ' + EXISTING_EPG + ' no subnet configuration for this epg will be pushed.'})
            #                                ERROR = True
            #                                rules['CONSUMER_IP'].remove(EXISTING_SUBNET)

            #                    else:
            #                        for rule_subnet in rules['CONSUMER_IP']:
            #                            if IPNetwork(rule_subnet) in IPNetwork(EXISTING_SUBNET):
            #                                if int(EXISTING_SUBNET.split('/')[1]) >= 20 and 'import-security' in SCOPE:
            #                                    OUTPUT_LOG.append({'Errors': rule_subnet + ' already exists within ' + EXISTING_L3OUT + ' under EPG ' + EXISTING_EPG + ' inside ' + EXISTING_SUBNET})
            #                                    ERROR = True
            #                                    rules['CONSUMER_IP'].remove(rule_subnet)


            #if len(rules['CONSUMER_IP']) >= 1:
            #    OUTPUT_LOG.append({'Notifications': 'The Following subnets will be added to the EPG: ' + rules['CONSUMER_EPG']})
            #    OUTPUT_LOG.append({'Notifications': str(rules['CONSUMER_IP'])})

            #else:
            #    OUTPUT_LOG.append({'Notifications': 'No subnets will be added to EPG: ' + rules['CONSUMER_EPG']})

        #if rules['PROVIDER_L3OUT'] != 'INTERNAL' and rules['PROVIDER_EPG'] != 'BLANK':
        #    L3OUT_NAME = rules['PROVIDER_L3OUT']
        #    L3OUT_SEARCH_RESPONSE = L3OUT_SEARCH(BASE_URL, APIC_COOKIE, TENANT, L3OUT_NAME, HEADERS)
        #    L3OUT_DATA = L3OUT_SEARCH_RESPONSE[1]['imdata']
        #    L3OUT_SUBNETS = []
        #    # Loop through the VRF pull out all other L3Outs and add any l3extsubnet to a list
        #    for key in L3OUT_DATA:
        #        # For Python 3+
        #        if 'l3extRsEctx' in key:
        #        # For Python 2.7
        #        #if key.keys() == ['l3extRsEctx']:
        #            VRF_DN = key['l3extRsEctx']['attributes']['tDn']
        #            VRF_SEARCH_RESPONSE = VRF_SEARCH(BASE_URL, APIC_COOKIE, VRF_DN, HEADERS)
        #            for vrf_l3o in VRF_SEARCH_RESPONSE['imdata']:
        #                # For Python 3+
        #                if 'fvRtEctx' in vrf_l3o:
        #                # For Python 2.7
        #                #if vrf_l3o.keys() == ['fvRtEctx']:
        #                    L3OUT_DN = vrf_l3o['fvRtEctx']['attributes']['tDn']
        #                    SUBNET_SEARCH_RESPONSE = SUBNET_SEARCH(BASE_URL, APIC_COOKIE, L3OUT_DN, HEADERS)
        #                    for subnets in SUBNET_SEARCH_RESPONSE['imdata']:
        #                        print(subnets)
        #                        L3OUT_SUBNETS.append(subnets['l3extSubnet']['attributes']['ip'])
        #                        EXISTING_SUBNET = subnets['l3extSubnet']['attributes']['ip']
        #                        EXISTING_L3OUT = subnets['l3extSubnet']['attributes']['dn'].split('/')[2][4:]
        #                        EXISTING_EPG = subnets['l3extSubnet']['attributes']['dn'].split('/')[3][6:]
        #                        SCOPE = subnets['l3extSubnet']['attributes']['scope'].split(',')
        #                        if EXISTING_SUBNET in rules['PROVIDER_IP']:
        #                            if 'import-security' in SCOPE:
        #                                if EXISTING_EPG == rules['PROVIDER_EPG']:
        #                                    rules['PROVIDER_IP'].remove(EXISTING_SUBNET)

        #                                else:
        #                                    OUTPUT_LOG.append({'Errors': EXISTING_SUBNET + ' already exists within ' + EXISTING_L3OUT + ' under EPG ' + EXISTING_EPG + ' no subnet configuration for this epg will be pushed.'})
        #                                    ERROR = True
        #                                    rules['PROVIDER_IP'].remove(EXISTING_SUBNET)

        #                        else:
        #                            for rule_subnet in rules['PROVIDER_IP']:
        #                                if IPNetwork(rule_subnet) in IPNetwork(EXISTING_SUBNET):
        #                                    if int(EXISTING_SUBNET.split('/')[1]) >= 20 and 'import-security' in SCOPE:
        #                                        OUTPUT_LOG.append({'Errors': rule_subnet + ' already exists within ' + EXISTING_L3OUT + ' under EPG ' + EXISTING_EPG + ' inside ' + EXISTING_SUBNET})
        #                                        ERROR = True
        #                                        rules['PROVIDER_IP'].remove(rule_subnet)


        #    if len(rules['PROVIDER_IP']) >= 1:
        #        OUTPUT_LOG.append({'Notifications': 'The Following subnets will be added to the EPG: ' + rules['PROVIDER_EPG']})
        #        OUTPUT_LOG.append({'Notifications': str(rules['PROVIDER_IP'])})

        #    else:
        #        OUTPUT_LOG.append({'Notifications': 'No subnets will be added to EPG: ' + rules['PROVIDER_EPG']})

    # Search for VIPs
    OUTPUT_LOG.append({'Notifications': ''})
    OUTPUT_LOG.append({'Notifications': 'Checking if any EPGs are for VIPS'})
    OUTPUT_LOG.append({'Notifications': '-----------------------------'})
#
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

    if not ERROR:
        OUTPUT_LOG.append({'Notifications': 'APIC Configuration validated successfully'})

    return OUTPUT_LOG

@shared_task
def EXTERNAL_EPG_DEPLOYMENT(LOCATION, APIC_USERNAME, APIC_PASSWORD, RULE_LIST):
    if LOCATION == 'DC1':
        BASE_URL = 'https://sandboxapicdc.cisco.com/api/'
        DC = LOCATION
    elif LOCATION == 'DC2':
        BASE_URL = 'https://sandboxapicdc.cisco.com/api/'
        DC = LOCATION
    elif LOCATION == 'LAB':
        BASE_URL = 'https://sandboxapicdc.cisco.com/api/'
        DC = LOCATION
    elif LOCATION == 'SANDBOX':
        BASE_URL = 'https://sandboxapicdc.cisco.com/api/'
        DC = LOCATION

    TENANT = 'common'
    OUTPUT_LOG = []
    HEADERS = {'content-type': 'application/json'}
    # --------------------------------------------------------------------------#
    # Begin Configuration
    # --------------------------------------------------------------------------#
    OUTPUT_LOG.append({'Notifications': ''})
    OUTPUT_LOG.append({'Notifications': 'Starting External EPG Deployment.'})
    OUTPUT_LOG.append({'Notifications': '-----------------------------'})
    APIC_COOKIE = APIC_LOGIN(BASE_URL, APIC_USERNAME, APIC_PASSWORD)
    if APIC_COOKIE:
        OUTPUT_LOG.append({'Notifications': 'Successfully generated authentication cookie'})
    else:
        OUTPUT_LOG.append({'Errors': 'Unable to connect to APIC. Please check your credentials'})

    for rules in RULE_LIST:
        L3OUT_CONSUME_EPG_CREATED = False
        L3OUT_PROVIDE_EPG_CREATED = False
        OUTPUT_LOG.append({'Notifications': 'Adding EPGs & Subnets for line: ' + str(rules['LINE'])})
        if rules['CONSUMER_L3OUT'] != 'INTERNAL' and rules['CONSUMER_EPG'] != 'BLANK':
            EPG_NAME = rules['CONSUMER_EPG']
            L3OUT_NAME = rules['CONSUMER_L3OUT']
            EXTERNAL_EPG_SEARCH_RESPONSE = EXTERNAL_EPG_SEARCH(BASE_URL, APIC_COOKIE, TENANT, L3OUT_NAME, EPG_NAME, HEADERS)
            if int(EXTERNAL_EPG_SEARCH_RESPONSE['totalCount']) == 1:
                OUTPUT_LOG.append({'Notifications': 'EPG: ' + EPG_NAME + ' already exists under ' + L3OUT_NAME + ' and wont be created'})
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
                OUTPUT_LOG.append({'Notifications': 'EPG: ' + EPG_NAME + ' already exists under ' + L3OUT_NAME + ' and wont be created'})
                L3OUT_PROVIDE_EPG_CREATED = True
            if not L3OUT_PROVIDE_EPG_CREATED:
                OUTPUT_LOG.append({'Notifications': 'Adding External EPG: ' + EPG_NAME + ' TO L3Out: ' + L3OUT_NAME})
                EXTERNAL_EPG_ADD(BASE_URL, APIC_COOKIE, TENANT, L3OUT_NAME, EPG_NAME, HEADERS, OUTPUT_LOG)
            # Add subnets to external EPG
            if len(rules['PROVIDER_IP']) != 0:
                OUTPUT_LOG.append({'Adding Subnets to External EPG: '})
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

    return OUTPUT_LOG