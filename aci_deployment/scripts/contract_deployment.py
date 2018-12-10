import json, requests, openpyxl, time, os
from .secrets import *
from .baseline import APIC_LOGIN

# Ignore SSL Errors
requests.packages.urllib3.disable_warnings()
HEADERS = {'content-type': 'application/json'}

# ----------------------------------------------------------------------------------------------------------------------------------------------------
#                                            CONFIGURATION AND POSTS
# ----------------------------------------------------------------------------------------------------------------------------------------------------

def INTERNL_EPG_CONTRACT_CONSUME(BASE_URL, EPG_NAME, CONTRACT_NAME, APIC_COOKIE, HEADERS, OUTPUT_LOG):
    INTERNAL_EPG_SEARCH_RESPONSE = INTERNAL_EPG_SEARCH(BASE_URL, APIC_COOKIE, EPG_NAME, HEADERS)
    TENANT = INTERNAL_EPG_SEARCH_RESPONSE['imdata'][0]['fvAEPg']['attributes']['dn'].split('/')[1][3:]
    APP_PROFILE = INTERNAL_EPG_SEARCH_RESPONSE['imdata'][0]['fvAEPg']['attributes']['dn'].split('/')[2][3:]
    CONTRACT_ATTACH_URL = BASE_URL + 'node/mo/uni/tn-{0}/ap-{1}/epg-{2}.json'.format(TENANT, APP_PROFILE, EPG_NAME)
    CONTRACT_ATTACH_JSON = {
        "fvRsCons": {"attributes": {"tnVzBrCPName": CONTRACT_NAME, "status": "created,modified"}, "children": []}}

    try:
        post_response = requests.post(CONTRACT_ATTACH_URL, cookies=APIC_COOKIE, data=json.dumps(CONTRACT_ATTACH_JSON, sort_keys=True),
                                      headers=HEADERS, verify=False)
        CONTRACT_CONSUME_RESPONSE = json.loads(post_response.text)

        if int(CONTRACT_CONSUME_RESPONSE['totalCount']) == 0:
            OUTPUT_LOG.append({'Notifications': 'Contract:  ' + CONTRACT_NAME + ' consumed on EPG: ' + EPG_NAME})
        else:
            OUTPUT_LOG.append({'Errors': 'Failed to consume Contract: ' + CONTRACT_NAME + 'on EPG: ' + EPG_NAME})
            OUTPUT_LOG.append({'Errors': 'Error: ' + post_response.text})

    except:
        OUTPUT_LOG.append({'Errors': 'Error Posting JSON: ' + json.dumps(CONTRACT_ATTACH_JSON)})
        return OUTPUT_LOG

    return OUTPUT_LOG


def INTERNL_EPG_CONTRACT_PROVIDE(BASE_URL, EPG_NAME, CONTRACT_NAME, APIC_COOKIE, HEADERS, OUTPUT_LOG):
    INTERNAL_EPG_SEARCH_RESPONSE = INTERNAL_EPG_SEARCH(BASE_URL, APIC_COOKIE, EPG_NAME, HEADERS)
    TENANT = INTERNAL_EPG_SEARCH_RESPONSE['imdata'][0]['fvAEPg']['attributes']['dn'].split('/')[1][3:]
    APP_PROFILE = INTERNAL_EPG_SEARCH_RESPONSE['imdata'][0]['fvAEPg']['attributes']['dn'].split('/')[2][3:]
    CONTRACT_ATTACH_URL = BASE_URL + 'node/mo/uni/tn-{0}/ap-{1}/epg-{2}.json'.format(TENANT, APP_PROFILE, EPG_NAME)
    CONTRACT_ATTACH_JSON = {
        "fvRsProv": {"attributes": {"tnVzBrCPName": CONTRACT_NAME, "status": "created,modified"}, "children": []}}

    try:
        post_response = requests.post(CONTRACT_ATTACH_URL, cookies=APIC_COOKIE, data=json.dumps(CONTRACT_ATTACH_JSON, sort_keys=True),
                                      headers=HEADERS, verify=False)
        CONTRACT_PROVIDE_RESPONSE = json.loads(post_response.text)

        if int(CONTRACT_PROVIDE_RESPONSE['totalCount']) == 0:
            OUTPUT_LOG.append({'Notifications': 'Contract:  ' + CONTRACT_NAME + '  provided on EPG: ' + EPG_NAME})

        else:
            OUTPUT_LOG.append({'Errors': 'Failed to provide Contract: ' + CONTRACT_NAME + 'on EPG: ' + EPG_NAME})
            OUTPUT_LOG.append({'Errors': 'Error: ' + post_response.text})

    except:
        OUTPUT_LOG.append({'Errors': 'Error Posting JSON: ' + json.dumps(CONTRACT_ATTACH_JSON)})
        OUTPUT_LOG.append({'Errors': 'URL : ' + CONTRACT_ATTACH_URL})
        return OUTPUT_LOG

    return OUTPUT_LOG


def EXTERNAL_EPG_CONTRACT_CONSUME(L3OUT_NAME, EPG_NAME, CONTRACT_NAME, BASE_URL, APIC_COOKIE, HEADERS, OUTPUT_LOG):
    # Search for External EPG to build DN.
    EXTERNAL_EPG_SEARCH_RESPONSE = EXTERNAL_EPG_SEARCH(BASE_URL, APIC_COOKIE, L3OUT_NAME, EPG_NAME, HEADERS)

    if int(EXTERNAL_EPG_SEARCH_RESPONSE['totalCount']) == 1:
        TENANT = EXTERNAL_EPG_SEARCH_RESPONSE['imdata'][0]['l3extInstP']['attributes']['dn'].split('/')[1][3:]
        L3OUT = EXTERNAL_EPG_SEARCH_RESPONSE['imdata'][0]['l3extInstP']['attributes']['dn'].split('/')[2][4:]
        L3OUT_CREATED = True

    else:
        L3OUT_CREATED = False
        OUTPUT_LOG.append({'Errors': 'Error ' + EPG_NAME + ' does not exist'})

    # Attach Contract if EPG created
    if L3OUT_CREATED:

        CONTRACT_ATTACH_URL = BASE_URL + 'node/mo/uni/tn-{0}/out-{1}/instP-{2}.json'.format(TENANT, L3OUT, EPG_NAME)
        CONTRACT_ATTACH_JSON = {
            "fvRsCons": {"attributes": {"tnVzBrCPName": CONTRACT_NAME, "status": "created,modified"}, "children": []}}

        try:
            post_response = requests.post(CONTRACT_ATTACH_URL, cookies=APIC_COOKIE,
                                          data=json.dumps(CONTRACT_ATTACH_JSON, sort_keys=True), headers=HEADERS, verify=False)
            if post_response.text == '{"totalCount":"0","imdata":[]}':
                OUTPUT_LOG.append({
                                      'Notifications': 'Contract:  ' + CONTRACT_NAME + ' consumed on EPG: ' + EPG_NAME + ' Under L3Out ' + L3OUT})
            else:
                OUTPUT_LOG.append({
                                      'Errors': 'Failed to consume contract: ' + CONTRACT_NAME + 'on EPG: ' + EPG_NAME + ' under L3Out ' + L3OUT})
                OUTPUT_LOG.append({'Errors': 'Error: ' + post_response.text})

        except:
            OUTPUT_LOG.append({'Errors': 'Error Posting JSON: ' + json.dumps(CONTRACT_ATTACH_JSON)})
            return OUTPUT_LOG

    return OUTPUT_LOG


def EXTERNAL_EPG_CONTRACT_PROVIDE(L3OUT_NAME, EPG_NAME, CONTRACT_NAME, BASE_URL, APIC_COOKIE, HEADERS, OUTPUT_LOG):
    # Search for External EPG to build DN.
    EXTERNAL_EPG_SEARCH_RESPONSE = EXTERNAL_EPG_SEARCH(BASE_URL, APIC_COOKIE, L3OUT_NAME, EPG_NAME, HEADERS)

    if int(EXTERNAL_EPG_SEARCH_RESPONSE['totalCount']) == 1:
        TENANT = EXTERNAL_EPG_SEARCH_RESPONSE['imdata'][0]['l3extInstP']['attributes']['dn'].split('/')[1][3:]
        L3OUT = EXTERNAL_EPG_SEARCH_RESPONSE['imdata'][0]['l3extInstP']['attributes']['dn'].split('/')[2][4:]
        L3OUT_CREATED = True

    else:
        L3OUT_CREATED = False
        OUTPUT_LOG.append({'Errors': 'Error ' + EPG_NAME + ' does not exist'})

    # Attach Contract if EPG created
    if L3OUT_CREATED:

        CONTRACT_ATTACH_URL = BASE_URL + 'node/mo/uni/tn-{0}/out-{1}/instP-{2}.json'.format(TENANT, L3OUT, EPG_NAME)
        CONTRACT_ATTACH_JSON = {
            "fvRsProv": {"attributes": {"tnVzBrCPName": CONTRACT_NAME, "status": "created,modified"}, "children": []}}

        try:
            post_response = requests.post(CONTRACT_ATTACH_URL, cookies=APIC_COOKIE,
                                          data=json.dumps(CONTRACT_ATTACH_JSON, sort_keys=True), headers=HEADERS, verify=False)
            if post_response.text == '{"totalCount":"0","imdata":[]}':
                OUTPUT_LOG.append({
                                      'Notifications': 'Contract:  ' + CONTRACT_NAME + '  provided on EPG: ' + EPG_NAME + ' Under L3Out ' + L3OUT})
            else:
                OUTPUT_LOG.append({
                                      'Errors': 'Failed to provide contract: ' + CONTRACT_NAME + 'on EPG: ' + EPG_NAME + ' under L3Out ' + L3OUT})
                OUTPUT_LOG.append({'Errors': 'Error: ' + post_response.text})
        except:
            OUTPUT_LOG.append({'Errors': 'Error Posting JSON: ' + json.dumps(CONTRACT_ATTACH_JSON)})
            return OUTPUT_LOG

    return OUTPUT_LOG


def FILTER_ATTACH(BASE_URL, APIC_COOKIE, CONTRACT_NAME, CONTRACT_SUBJECT, FILTER, HEADERS, OUTPUT_LOG):
    CONTRACT_SUBJECT_URL = BASE_URL + 'node/mo/uni/tn-common/brc-{0}/subj-{1}.json'.format(CONTRACT_NAME,
                                                                                           CONTRACT_SUBJECT)
    CONTRACT_SUBJECT_JSON = {
        "vzRsSubjFiltAtt": {"attributes": {"tnVzFilterName": FILTER, "status": "created,modified"}, "children": []}}
    try:
        post_response = requests.post(CONTRACT_SUBJECT_URL, cookies=APIC_COOKIE, data=json.dumps(CONTRACT_SUBJECT_JSON, sort_keys=True),
                                      headers=HEADERS, verify=False)
        CONTRACT_SUBJECT_RESPONSE = json.loads(post_response.text)
        if int(CONTRACT_SUBJECT_RESPONSE['totalCount']) == 0:
            OUTPUT_LOG.append({'Notifications': 'Attached filter: ' + FILTER + ' to Contract: ' + CONTRACT_NAME})
        else:
            OUTPUT_LOG.append({'Errors': 'Failed to attach filter: ' + FILTER + 'to Contract: ' + CONTRACT_NAME})
            OUTPUT_LOG.append({'Errors': 'Error: ' + post_response.text})


    except:
        OUTPUT_LOG.append({'Errors': 'Failed to attach filter: ' + FILTER + 'to Contract: ' + CONTRACT_NAME})
        return OUTPUT_LOG

    return OUTPUT_LOG


def FILTER_CREATE(FILTER_SET, BASE_URL, APIC_COOKIE, HEADERS, OUTPUT_LOG):
    # Loop through filter set to build filters
    for filters in FILTER_SET:
        FILTER_NAME = filters
        FILTER_PROTOCOL = filters.split('-')[0].lower()
        FILTER_DEST_PORT_FROM = filters.split('-')[1]
        if len(filters.split('-')) == 3:
            FILTER_DEST_PORT_TO = filters.split('-')[2]
        else:
            FILTER_DEST_PORT_TO = filters.split('-')[1]
        FILTER_TEMPLATE_URL = BASE_URL + 'node/mo/uni/tn-common/flt-{0}.json'.format(FILTER_NAME)
        FILTER_TEMPLATE_JSON = {"vzFilter": {"attributes": {"name": FILTER_NAME, "status": "created"}, "children": [{
                                                                                                                        "vzEntry": {
                                                                                                                            "attributes": {
                                                                                                                                "name": FILTER_NAME,
                                                                                                                                "etherT": "ip",
                                                                                                                                "prot": FILTER_PROTOCOL,
                                                                                                                                "dFromPort": FILTER_DEST_PORT_FROM,
                                                                                                                                "dToPort": FILTER_DEST_PORT_TO,
                                                                                                                                "status": "created"},
                                                                                                                            "children": []}}]}}
        try:
            post_response = requests.post(FILTER_TEMPLATE_URL, cookies=APIC_COOKIE,
                                          data=json.dumps(FILTER_TEMPLATE_JSON, sort_keys=True), headers=HEADERS, verify=False)
            FILTER_CREATE_RESPONSE = json.loads(post_response.text)

            if int(FILTER_CREATE_RESPONSE['totalCount']) == 0:
                OUTPUT_LOG.append({'Notifications': 'Created Filter for ' + FILTER_NAME})
            else:
                OUTPUT_LOG.append({'Errors': 'Failed to create Filter for:' + FILTER_NAME})
                OUTPUT_LOG.append({'Errors': 'Error: ' + post_response.text})

        except:
            OUTPUT_LOG.append({'Errors': 'Failed to create Filter for:' + FILTER_NAME})
            return OUTPUT_LOG

    return OUTPUT_LOG


def CONTRACT_CREATE(CONTRACT_SET, BASE_URL, APIC_COOKIE, HEADERS, OUTPUT_LOG):
    # Loop through contract set and build contracts and subjects
    for contracts in CONTRACT_SET:
        CONTRACT_NAME = contracts
        CONTRACT_DESCRIPTION = ''
        SUBJECT_NAME = CONTRACT_NAME.split('_')[0] + '_SBJ'
        CONTRACT_TAG = 'TEST'
        CONTRACT_TEMPLATE_URL = BASE_URL + 'node/mo/uni/tn-common/brc-{0}.json'.format(CONTRACT_NAME)
        CONTRACT_TEMPLATE_JSON = {"vzBrCP": {
            "attributes": {"name": CONTRACT_NAME, "scope": "global", "descr": CONTRACT_DESCRIPTION,
                           "status": "created"},
            "children": [{"vzSubj": {"attributes": {"name": SUBJECT_NAME, "status": "created"}, "children": []}}]}}

        try:
            post_response = requests.post(CONTRACT_TEMPLATE_URL, cookies=APIC_COOKIE,
                                          data=json.dumps(CONTRACT_TEMPLATE_JSON, sort_keys=True), headers=HEADERS, verify=False)
            CONTRACT_CREATE_RESPONSE = json.loads(post_response.text)

            if int(CONTRACT_CREATE_RESPONSE['totalCount']) == 0:
                OUTPUT_LOG.append({'Notifications': 'Created Contract for ' + CONTRACT_NAME})
            else:
                OUTPUT_LOG.append({'Errors': 'Failed to create Contract for:' + CONTRACT_NAME})
                OUTPUT_LOG.append({'Errors': 'Error: ' + post_response.text})
        except:
            OUTPUT_LOG.append({'Errors': 'Failed to create Contract for:' + CONTRACT_NAME})
            return OUTPUT_LOG

    return OUTPUT_LOG


# ----------------------------------------------------------------------------------------------------------------------------------------------------
#                                            SEARCHES AND GETS
# ----------------------------------------------------------------------------------------------------------------------------------------------------
def LIST_COMPARE(a, b):
    return [[x for x in a if x not in b]]


def CONTRACT_SEARCH(BASE_URL, APIC_COOKIE, CONTRACT_NAME, HEADERS):
    CONTRACT_SEARCH_URL = BASE_URL + 'node/class/vzBrCP.json?query-target-filter=and(eq(vzBrCP.name,"{0}"))'.format(
        CONTRACT_NAME)
    get_response = requests.get(CONTRACT_SEARCH_URL, cookies=APIC_COOKIE, headers=HEADERS, verify=False)
    CONTRACT_SEARCH_RESPONSE = json.loads(get_response.text)
    return CONTRACT_SEARCH_RESPONSE


def SUBNET_SEARCH(ENDPOINT_LIST, SUBNET):
    RESULTS = []

    for i in ENDPOINT_LIST:
        if IPNetwork(SUBNET) in IPNetwork(i['Subnet']) or IPNetwork(i['Subnet']) in IPNetwork(SUBNET):
            RESULTS.append(
                {'Subnet': i['Subnet'], 'Locality': i['Locality'], 'Location': i['Location'], 'EPG': i['EPG'],
                 'Scope': i['Scope'], 'AppProfile': i['AppProfile'], 'Tenant': i['Tenant']})

    return RESULTS


def CONTRACT_SEARCH(BASE_URL, APIC_COOKIE, CONTRACT_NAME, HEADERS):
    CONTRACT_SEARCH_URL = BASE_URL + 'node/class/vzBrCP.json?query-target-filter=and(eq(vzBrCP.name,"{0}"))'.format(
        CONTRACT_NAME)
    get_response = requests.get(CONTRACT_SEARCH_URL, cookies=APIC_COOKIE, headers=HEADERS, verify=False)
    CONTRACT_SEARCH_RESPONSE = json.loads(get_response.text)

    return CONTRACT_SEARCH_RESPONSE


def FILTER_SEARCH(BASE_URL, APIC_COOKIE, FILTER_NAME, HEADERS):
    FILTER_SEARCH_URL = BASE_URL + 'node/class/vzFilter.json?query-target-filter=and(eq(vzFilter.dn,"uni/tn-common/flt-{0}"))'.format(
        FILTER_NAME)
    get_response = requests.get(FILTER_SEARCH_URL, cookies=APIC_COOKIE, headers=HEADERS, verify=False)
    FILTER_SEARCH_RESPONSE = json.loads(get_response.text)

    return FILTER_SEARCH_RESPONSE


def SUBJECT_SEARCH(BASE_URL, APIC_COOKIE, CONTRACT_NAME, TENANT, CONTRACT_SUBJECT, HEADERS):
    SUBJECT_SEARCH_URL = BASE_URL + 'node/mo/uni/tn-{0}/brc-{1}/subj-{2}.json?query-target=children'.format(TENANT,
                                                                                                            CONTRACT_NAME,
                                                                                                            CONTRACT_SUBJECT)
    get_response = requests.get(SUBJECT_SEARCH_URL, cookies=APIC_COOKIE, headers=HEADERS, verify=False)
    SUBJECT_SEARCH_RESPONSE = json.loads(get_response.text)
    return SUBJECT_SEARCH_RESPONSE


def CONTRACT_L3OUT_SEARCH(BASE_URL, APIC_COOKIE, L3OUT_NAME, HEADERS):
    L3OUT_SEARCH_URL = BASE_URL + 'node/mo/uni/tn-common/out-{0}.json?query-target=self'.format(L3OUT_NAME)
    get_response = requests.get(L3OUT_SEARCH_URL, cookies=APIC_COOKIE, headers=HEADERS, verify=False)
    L3OUT_SEARCH_RESPONSE = json.loads(get_response.text)
    return L3OUT_SEARCH_RESPONSE


def INTERNAL_EPG_SEARCH(BASE_URL, APIC_COOKIE, EPG_NAME, HEADERS):
    EPG_SEARCH_URL = BASE_URL + 'node/class/fvAEPg.json?query-target-filter=and(eq(fvAEPg.name,"{0}"))'.format(EPG_NAME)
    get_response = requests.get(EPG_SEARCH_URL, cookies=APIC_COOKIE, headers=HEADERS, verify=False)
    INTERNAL_EPG_SEARCH_RESPONSE = json.loads(get_response.text)
    return INTERNAL_EPG_SEARCH_RESPONSE


def CONTRACT_EXTERNAL_EPG_SEARCH(BASE_URL, APIC_COOKIE, L3OUT_NAME, EPG_NAME, HEADERS):
    EPG_SEARCH_URL = BASE_URL + 'node/class/l3extInstP.json?query-target-filter=and(wcard(l3extInstP.dn,"/out-{0}/instP-{1}"))'.format(
        L3OUT_NAME, EPG_NAME)
    get_response = requests.get(EPG_SEARCH_URL, cookies=APIC_COOKIE, headers=HEADERS, verify=False)
    EXTERNAL_EPG_SEARCH_RESPONSE = json.loads(get_response.text)
    return EXTERNAL_EPG_SEARCH_RESPONSE


def GET_ENDPOINT_INTERNAL(BASE_URL, APIC_COOKIE, HEADERS):
    try:
        GET_URL = BASE_URL + 'node/class/fvCEp.json'
        GET_RESPONSE = requests.get(GET_URL, cookies=APIC_COOKIE, headers=HEADERS, verify=False)
        ENDPOINT_INTERNAL_RESPONSE = json.loads(GET_RESPONSE.text)
        return ENDPOINT_INTERNAL_RESPONSE
    except:
        exit('Failed to get Internal Endpoint Data.')


def GET_ENDPOINT_EXTERNAL(BASE_URL, APIC_COOKIE, HEADERS):
    try:
        GET_URL = BASE_URL + 'node/class/l3extSubnet.json'
        GET_RESPONSE = requests.get(GET_URL, cookies=APIC_COOKIE, headers=HEADERS, verify=False)
        ENDPOINT_EXTERNAL_RESPONSE = json.loads(GET_RESPONSE.text)
        return ENDPOINT_EXTERNAL_RESPONSE
    except:
        exit('Failed to get External Endpoint Data.')


def GET_ENDPOINTS(BASE_URL, APIC_USERNAME, APIC_PASSWORD):
    ENDPOINT_INTERNAL_LIST = []
    ENDPOINT_EXTERNAL_LIST = []
    LOCATION = 'LAB'
    HEADERS = {'content-type': 'application/json'}
    # Login to fabric
    APIC_COOKIE = APIC_LOGIN(BASE_URL, APIC_USERNAME, APIC_PASSWORD)
    # Get External Endpoints
    ENDPOINT_EXTERNAL_RESPONSE = GET_ENDPOINT_EXTERNAL(BASE_URL, APIC_COOKIE, HEADERS)
    # Get Internal Endpoint data.
    ENDPOINT_INTERNAL_RESPONSE = GET_ENDPOINT_INTERNAL(BASE_URL, APIC_COOKIE, HEADERS)
    # Loop over endpoints and build endpoint lists.
    for i in ENDPOINT_EXTERNAL_RESPONSE['imdata']:
        IMPORT = ''
        EXPORT = ''
        SECURITY = ''
        if 'import-rtctrl' in i['l3extSubnet']['attributes']['scope']:
            IMPORT = 'I '
        if 'export-rtctrl' in i['l3extSubnet']['attributes']['scope']:
            EXPORT = 'E '
        if 'import-security' in i['l3extSubnet']['attributes']['scope']:
            SECURITY = 'S '

        SCOPE = IMPORT + EXPORT + SECURITY

        ENDPOINT_EXTERNAL_LIST.append(
            {'Location': LOCATION, 'Tenant': i['l3extSubnet']['attributes']['dn'].split('/')[1][3:],
             'AppProfile': i['l3extSubnet']['attributes']['dn'].split('/')[2][4:],
             'EPG': i['l3extSubnet']['attributes']['dn'].split('/')[3][6:],
             'Subnet': i['l3extSubnet']['attributes']['ip'], 'Scope': SCOPE, 'Locality': 'External'})

    for i in ENDPOINT_INTERNAL_RESPONSE['imdata']:
        ENDPOINT_EXTERNAL_LIST.append({'Location': LOCATION, 'Tenant': i['fvCEp']['attributes']['dn'].split('/')[1][3:],
                                       'AppProfile': i['fvCEp']['attributes']['dn'].split('/')[2][3:],
                                       'EPG': i['fvCEp']['attributes']['dn'].split('/')[3][4:],
                                       'Subnet': i['fvCEp']['attributes']['ip'], 'Scope': '', 'Locality': 'Internal'})

    return ENDPOINT_EXTERNAL_LIST


def CONTRACT_DEPLOYMENT_EXCEL_FORMAT_VALIDATION(RULE_LIST):
    OUTPUT_LOG = []
    DISPLAY_LIST = []
    TENANT_LIST = ['RED', 'GREEN', 'BLUE']
    ERROR = False

    # Validate Contract Name formatting
    OUTPUT_LOG.append({'Notifications': ''})
    OUTPUT_LOG.append({'Notifications': 'Validating Contract names in Workbook.'})
    OUTPUT_LOG.append({'Notifications': '-----------------------------'})

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

    if not ERROR:
        OUTPUT_LOG.append({'Notifications': 'Contract formatting validated successfully'})

    OUTPUT_LOG.append({'Notifications': ''})
    OUTPUT_LOG.append({'Notifications': 'Validating EPG names in Workbook.'})
    OUTPUT_LOG.append({'Notifications': '-----------------------------'})

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
        OUTPUT_LOG.append({'Notifications': 'EPG formatting validated successfully'})

    OUTPUT_LOG.append({'Notifications': ''})
    OUTPUT_LOG.append({'Notifications': 'Validating Contract and EPG locality.'})
    OUTPUT_LOG.append({'Notifications': '-----------------------------'})

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
        OUTPUT_LOG.append({'Notifications': 'Contract and EPG locality validated successfully'})

    OUTPUT_LOG.append({'Notifications': ''})
    OUTPUT_LOG.append({'Notifications': 'Validating Services in Workbook.'})
    OUTPUT_LOG.append({'Notifications': '-----------------------------'})

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
        OUTPUT_LOG.append({'Notifications': 'Services validated successfully'})

    return OUTPUT_LOG

