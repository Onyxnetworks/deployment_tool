import json, requests, ipaddress, openpyxl, time, os
from netaddr import IPNetwork, IPAddress

from .secrets import *
from .baseline import APIC_LOGIN

# Ignore SSL Errors
requests.packages.urllib3.disable_warnings()
HEADERS = {'content-type': 'application/json'}

def EXTERNAL_EPG_ADD(BASE_URL, APIC_COOKIE, TENANT, L3OUT_NAME, EPG_NAME, HEADERS, OUTPUT_LOG):

    ADD_EPG_L3OUT_URL = BASE_URL + 'node/mo/uni/tn-{0}/out-{1}/instP-{2}.json'.format(TENANT, L3OUT_NAME, EPG_NAME)
    ADD_EPG_L3OUT_JSON = {"l3extInstP":{"attributes":{"name":EPG_NAME,"status":"created"},"children":[]}}

    try:
        post_response = requests.post(ADD_EPG_L3OUT_URL, cookies=APIC_COOKIE, data=json.dumps(ADD_EPG_L3OUT_JSON, sort_keys=True), headers=HEADERS, verify=False)
        EXTERNAL_EPG_RESPONSE = json.loads(post_response.text)

        if int(EXTERNAL_EPG_RESPONSE['totalCount']) == 0:
            OUTPUT_LOG.append({'Notifications': EPG_NAME + ' added to L3OUT: ' + L3OUT_NAME})
        else:
            OUTPUT_LOG.append({'Errors': 'Failed to add ' + EPG_NAME + 'to ' + L3OUT_NAME})
            OUTPUT_LOG.append({'Errors': 'Error: ' + post_response.text})
    except:
        OUTPUT_LOG.append({'Errors': 'Error Posting JSON: ' + str(ADD_EPG_L3OUT_JSON)})
        return OUTPUT_LOG

    return OUTPUT_LOG

def EXTERNAL_EPG_SUBNET_ADD(BASE_URL, APIC_COOKIE, TENANT, L3OUT_NAME, EPG_NAME, HEADERS, IP, SCOPE, OUTPUT_LOG):

    ADD_SUBNET_L3OUT_URL = BASE_URL + 'node/mo/uni/tn-{0}/out-{1}/instP-{2}/extsubnet-[{3}].json'.format(TENANT, L3OUT_NAME, EPG_NAME, IP)
    ADD_SUBNET_L3OUT_JSON = {"l3extSubnet": {"attributes": {"ip": IP, "scope": SCOPE, "aggregate": "", "status": "created"}, "children": []}}

    try:
        post_response = requests.post(ADD_SUBNET_L3OUT_URL, cookies=APIC_COOKIE, data=json.dumps(ADD_SUBNET_L3OUT_JSON, sort_keys=True), headers=HEADERS, verify=False)
        EXTERNAL_EPG_SUBNET_RESPONSE = json.loads(post_response.text)

        if int(EXTERNAL_EPG_SUBNET_RESPONSE['totalCount']) == 0:
            OUTPUT_LOG.append({'Notifications': IP + ' added to ' + EPG_NAME + ' under L3Out ' + L3OUT_NAME})
        else:
            OUTPUT_LOG.append({'Errors': 'Failed to add ' + IP + 'to :' + EPG_NAME + ' under L3Out ' + L3OUT_NAME})
            OUTPUT_LOG.append({'Errors': 'Error: ' + post_response.text})
    except:
        OUTPUT_LOG.append({'Errors': 'Error Posting JSON: ' + str(ADD_SUBNET_L3OUT_JSON)})
        return OUTPUT_LOG

    return OUTPUT_LOG

# ----------------------------------------------------------------------------------------------------------------------------------------------------
#											SEARCHES AND GETS
# ----------------------------------------------------------------------------------------------------------------------------------------------------

def SUBNET_SEARCH_EXACT(BASE_URL, APIC_COOKIE, L3OUT_DN, HEADERS):
    SUBNET_SEARCH_URL = BASE_URL + 'node/class/l3extSubnet.json?query-target-filter=and(eq(l3extSubnet.dn,"{0}"))'.format(L3OUT_DN)

    get_response = requests.get(SUBNET_SEARCH_URL, cookies=APIC_COOKIE, headers=HEADERS, verify=False)
    SUBNET_SEARCH_RESPONSE = json.loads(get_response.text)

    return SUBNET_SEARCH_RESPONSE


def L3OUT_SEARCH(BASE_URL, APIC_COOKIE, TENANT, L3OUT_NAME, HEADERS):
    L3OUT_SEARCH_BASE_URL = BASE_URL + 'node/mo/uni/tn-{0}/out-{1}.json?query-target=self'.format(TENANT, L3OUT_NAME)
    L3OUT_SEARCH_CHILDREN_URL = BASE_URL + 'node/mo/uni/tn-{0}/out-{1}.json?query-target=children'.format(TENANT, L3OUT_NAME)

    get_response = requests.get(L3OUT_SEARCH_BASE_URL, cookies=APIC_COOKIE, headers=HEADERS, verify=False)
    L3OUT_SEARCH_RESPONSE_BASE = json.loads(get_response.text)
    get_response = requests.get(L3OUT_SEARCH_CHILDREN_URL, cookies=APIC_COOKIE, headers=HEADERS, verify=False)
    L3OUT_SEARCH_RESPONSE_CHILDREN = json.loads(get_response.text)

    return L3OUT_SEARCH_RESPONSE_BASE, L3OUT_SEARCH_RESPONSE_CHILDREN



def EXTERNAL_EPG_SEARCH(BASE_URL, APIC_COOKIE, TENANT, L3OUT_NAME, EPG_NAME, HEADERS):
    EPG_SEARCH_URL = BASE_URL + '/node/class/l3extInstP.json?query-target-filter=and(eq(l3extInstP.dn,"uni/tn-{0}/out-{1}/instP-{2}"))'.format(
        TENANT, L3OUT_NAME, EPG_NAME)

    get_response = requests.get(EPG_SEARCH_URL, cookies=APIC_COOKIE, headers=HEADERS, verify=False)
    EXTERNAL_EPG_SEARCH_RESPONSE = json.loads(get_response.text)

    return EXTERNAL_EPG_SEARCH_RESPONSE



def VRF_SEARCH(BASE_URL, APIC_COOKIE, VRF_DN, HEADERS):
    VRF_SEARCH_URL = BASE_URL + 'node/mo/{0}.json?query-target=children'.format(VRF_DN)

    get_response = requests.get(VRF_SEARCH_URL, cookies=APIC_COOKIE, headers=HEADERS, verify=False)
    VRF_SEARCH_RESPONSE = json.loads(get_response.text)

    return VRF_SEARCH_RESPONSE



def SUBNET_SEARCH(BASE_URL, APIC_COOKIE, L3OUT_DN, HEADERS):
    SUBNET_SEARCH_URL = BASE_URL + 'node/class/l3extSubnet.json?query-target-filter=and(wcard(l3extSubnet.dn,"{0}/"))'.format(
        L3OUT_DN)

    get_response = requests.get(SUBNET_SEARCH_URL, cookies=APIC_COOKIE, headers=HEADERS, verify=False)
    SUBNET_SEARCH_RESPONSE = json.loads(get_response.text)
    return SUBNET_SEARCH_RESPONSE
