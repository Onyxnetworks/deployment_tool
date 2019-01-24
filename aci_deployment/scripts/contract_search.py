import json, requests, time, os
from .baseline import APIC_LOGIN

def get_internal_epg(base_url, search_string, apic_cookie):

    headers = {'content-type': 'application/json'}

    # Get searched EPG from Fabric
    get_epg_url = base_url + 'node/class/fvAEPg.json?query-target-filter=and(eq(fvAEPg.name,"{0}"))'.format(search_string)

    try:
        get_response = requests.get(get_epg_url, cookies=apic_cookie, headers=headers, verify=False)
        all_epg_response = json.loads(get_response.text)
        location = base_url.split('-')[0][8:]
        tenant = all_epg_response['imdata'][0]['fvAEPg']['attributes']['dn'].split('/')[1][3:]
        app_prof = all_epg_response['imdata'][0]['fvAEPg']['attributes']['dn'].split('/')[2][3:]
        epg = all_epg_response['imdata'][0]['fvAEPg']['attributes']['dn'].split('/')[3][4:]

    except:
        print('Failed to get Info for: ' + base_url)
        return

    try:
        get_contracts_url = base_url + 'node/mo/uni/tn-{0}/ap-{1}/epg-{2}.json?query-target=children'.format(tenant, app_prof, epg)
        get_response = requests.get(get_contracts_url, cookies=apic_cookie, headers=headers, verify=False)
        all_contract_response = json.loads(get_response.text)

    except:
        print('Unable to search for EPG Contracts on: ' + base_url)
        return

    return all_contract_response


def get_external_epg(base_url, search_string, apic_cookie):

    headers = {'content-type': 'application/json'}

    # Get searched EPG from Fabric
    get_epg_url = base_url + 'node/class/l3extInstP.json?query-target-filter=and(eq(l3extInstP.name,"{0}"))'.format(search_string)
    try:
        get_response = requests.get(get_epg_url, cookies=apic_cookie, headers=headers, verify=False)
        all_epg_response = json.loads(get_response.text)
        location = base_url.split('-')[0][8:]
        tenant = all_epg_response['imdata'][0]['l3extInstP']['attributes']['dn'].split('/')[1][3:]
        l3out = all_epg_response['imdata'][0]['l3extInstP']['attributes']['dn'].split('/')[2][4:]
        epg = all_epg_response['imdata'][0]['l3extInstP']['attributes']['dn'].split('/')[3][6:]

    except:
        print('Failed to get Info for: ' + base_url)
        return
    try:
        get_contracts_url = base_url + 'node/mo/uni/tn-{0}/out-{1}/instP-{2}.json?query-target=children'.format(tenant, l3out, epg)
        get_response = requests.get(get_contracts_url, cookies=apic_cookie, headers=headers, verify=False)
        all_contract_response = json.loads(get_response.text)

    except:
        print('Unable to search for EPG Contracts on: ' + base_url)
        return

    return all_contract_response


def get_contract_details(base_url, tenant, contract_name, apic_cookie):

    headers = {'content-type': 'application/json'}

    get_url = base_url + 'node/mo/uni/tn-{0}/brc-{1}.json?query-target=children'.format(tenant, contract_name)
    get_response = requests.get(get_url, cookies=apic_cookie, headers=headers, verify=False)
    contracts = json.loads(get_response.text)

    return contracts


def get_subject_details(base_url, tenant, contract_name, subject_name, apic_cookie):

    headers = {'content-type': 'application/json'}

    get_url = base_url + 'node/mo/uni/tn-{0}/brc-{1}/subj-{2}.json?query-target=children'.format(tenant, contract_name,
                                                                                                 subject_name)
    get_response = requests.get(get_url, cookies=apic_cookie, headers=headers, verify=False)
    all_subject_response = json.loads(get_response.text)

    return all_subject_response

