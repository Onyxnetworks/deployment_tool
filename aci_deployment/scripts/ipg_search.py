import json, requests, ipaddress, openpyxl, time, os
from .baseline import APIC_LOGIN

# Ignore SSL Errors
requests.packages.urllib3.disable_warnings()

def get_ipg(url_list, username, password):

    headers = {'content-type': 'application/json'}

    ipg_list = []

    # Loop through URL list and Get Endpoints
    for url in url_list:
        base_url = url
        # Login to fabric
        apic_cookie = APIC_LOGIN(base_url, username, password)

        # Get all IPG from Fabtic
        all_ipg_list = get_all_ipg(base_url, apic_cookie, headers)

        # loop through output and add IPG names to list
        i = 0
        for ipg in all_ipg_list['imdata']:
            ipg_list.append(ipg['fabricPathEp']['attributes']['name'])
            i += 1

    return ipg_list


def get_all_ipg(base_url, apic_cookie, headers):

    get_url = base_url + 'node/class/fabricPathEp.json'

    try:
        get_response = requests.get(get_url, cookies=apic_cookie, headers=headers, verify=False)
        all_ipg_response = json.loads(get_response.text)
        return all_ipg_response

    except:
        print('Failed to get IPGs.')
        return


def get_fvpathatt(url_list, search_string, username, password):

    headers = {'content-type': 'application/json'}

    mapped_ipg_list = []
    # Loop through URL list and Get Endpoints
    for url in url_list:
        base_url = url
        location = base_url.split('-')[0][8:]

        # Login to fabric
        apic_cookie = APIC_LOGIN(base_url, username, password)


        mapped_ipg = base_url + 'node/class/fvRsPathAtt.json?query-target-filter=and(wcard(fvRsPathAtt.tDn,"' + search_string + '"))'

        try:
            get_response = requests.get(mapped_ipg, cookies=apic_cookie, verify=False)
            fvpathatt_response = json.loads(get_response.text)
            mapped_ipg_list.append({'location:': location, 'response': fvpathatt_response})


        except:
            print('Failed to get Attached Paths.')
            return

    return mapped_ipg_list