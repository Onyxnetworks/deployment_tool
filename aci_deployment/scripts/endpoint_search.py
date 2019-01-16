import json, requests, ipaddress, openpyxl, time, os
from netaddr import IPNetwork, IPAddress
from .baseline import APIC_LOGIN

# Ignore SSL Errors
requests.packages.urllib3.disable_warnings()
HEADERS = {'content-type': 'application/json'}

def GET_ENDPOINTS(url_list, APIC_USERNAME, APIC_PASSWORD):
    ENDPOINT_LIST = []
    HEADERS = {'content-type': 'application/json'}
    # Loop through URL list and Get Endpoints
    for url in url_list:
        BASE_URL = url
        LOCATION = BASE_URL.split('-')[0][8:]
        # Login to fabric
        APIC_COOKIE = APIC_LOGIN(BASE_URL, APIC_USERNAME, APIC_PASSWORD)
        # Get External Endpoints
        ENDPOINT_EXTERNAL_RESPONSE = GET_ENDPOINT_EXTERNAL(BASE_URL, APIC_COOKIE, HEADERS)
        # Get Internal Endpoint data.
        ENDPOINT_INTERNAL_RESPONSE = GET_ENDPOINT_INTERNAL(BASE_URL, APIC_COOKIE, HEADERS)
        # Loop over endpoints and build endpoint lists.
        for i in ENDPOINT_EXTERNAL_RESPONSE['imdata']:
            Tenant = i['l3extSubnet']['attributes']['dn'].split('/')[1][3:]
            L3O = i['l3extSubnet']['attributes']['dn'].split('/')[2][4:]
            if Tenant.startswith(('PRD', 'PPE', 'DC1-SBS', 'DC2-SBS', 'DC1-STS', 'DC2-STS', 'DC1-REP', 'DC2-REP', 'DC1-OTV', 'DC2-OTV')) and L3O.endswith('L3O'):
                continue
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

            ENDPOINT_LIST.append(
                {'Location': LOCATION, 'Tenant': i['l3extSubnet']['attributes']['dn'].split('/')[1][3:],
                 'AppProfile': i['l3extSubnet']['attributes']['dn'].split('/')[2][4:],
                 'EPG': i['l3extSubnet']['attributes']['dn'].split('/')[3][6:],
                 'Subnet': i['l3extSubnet']['attributes']['ip'], 'Scope': SCOPE, 'Locality': 'External'})

        for i in ENDPOINT_INTERNAL_RESPONSE['imdata']:
            ENDPOINT_LIST.append({'Location': LOCATION, 'Tenant': i['fvCEp']['attributes']['dn'].split('/')[1][3:],
                                           'AppProfile': i['fvCEp']['attributes']['dn'].split('/')[2][3:],
                                           'EPG': i['fvCEp']['attributes']['dn'].split('/')[3][4:],
                                           'Subnet': i['fvCEp']['attributes']['ip'] + '/32', 'Scope': '', 'Locality': 'Internal'})

    return ENDPOINT_LIST

def GET_ENDPOINT_INTERNAL(BASE_URL, APIC_COOKIE, HEADERS):
    try:
        GET_URL = BASE_URL + 'node/class/fvCEp.json'
        GET_RESPONSE = requests.get(GET_URL, cookies=APIC_COOKIE, headers=HEADERS, verify=False)
        ENDPOINT_INTERNAL_RESPONSE = json.loads(GET_RESPONSE.text)
        return ENDPOINT_INTERNAL_RESPONSE
    except:
        print('Failed to get Internal Endpoint Data.')


def GET_ENDPOINT_EXTERNAL(BASE_URL, APIC_COOKIE, HEADERS):
    try:
        GET_URL = BASE_URL + 'node/class/l3extSubnet.json'
        GET_RESPONSE = requests.get(GET_URL, cookies=APIC_COOKIE, headers=HEADERS, verify=False)
        ENDPOINT_EXTERNAL_RESPONSE = json.loads(GET_RESPONSE.text)
        return ENDPOINT_EXTERNAL_RESPONSE
    except:
        print('Failed to get External Endpoint Data.')
