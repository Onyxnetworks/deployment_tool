import json, requests, time, os
from .baseline import APIC_LOGIN

def get_internal_epg(url_list, search_string, username, password):

    headers = {'content-type': 'application/json'}
    contract_list = []
    # Loop through URL list and Get Endpoints
    for url in url_list:
        base_url = url
        # Login to fabric
        apic_cookie = APIC_LOGIN(base_url, username, password)

        # Get searched EPG from Fabtic
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
            continue

        try:
            get_contracts_url = BASE_URL + 'node/mo/uni/tn-{0}/ap-{1}/epg-{2}.json?query-target=children'.format(tenant, app_prof, epg)
            get_response = requests.get(get_contracts_url, cookies=apic_cookie, headers=headers, verify=False)
            all_contract_response = json.loads(get_response.text)
            contract_list.append({'location': location, 'response': all_contract_response})

        except:
            print('Unable to search for EPG Contracts on: ' + base_url)
            continue

    return contract_list


def get_external_epg(url_list, search_string, username, password):

    headers = {'content-type': 'application/json'}
    contract_list = []
    # Loop through URL list and Get Endpoints
    for url in url_list:
        base_url = url
        # Login to fabric
        apic_cookie = APIC_LOGIN(base_url, username, password)

        # Get searched EPG from Fabtic
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
            continue

        try:
            get_contracts_url = BASE_URL + 'node/mo/uni/tn-{0}/out-{1}/instP-{2}.json?query-target=children'.format(tenant, l3out, epg)
            get_response = requests.get(get_contracts_url, cookies=apic_cookie, headers=headers, verify=False)
            all_contract_response = json.loads(get_response.text)
            contract_list.append({'location': location, 'response': all_contract_response})

        except:
            print('Unable to search for EPG Contracts on: ' + base_url)
            continue

    return contract_list



