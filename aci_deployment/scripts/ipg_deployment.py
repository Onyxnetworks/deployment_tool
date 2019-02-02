import json, requests, time, os
from .baseline import APIC_LOGIN

def get_fabric_nodes(base_url, apic_cookie, headers, output_log):
    error = False
    try:
        get_url = base_url + 'node/class/fabricNode.json?'
        get_response = requests.get(get_url, cookies=apic_cookie, headers=headers, verify=False)
        get_fabic_nodes_response = json.loads(get_response.text)
        return error, get_fabic_nodes_response

    except:
        error = True
        output_log.append({'Errors': 'Failed to get Node list from Fabric.'})
        return error, output_log


def get_fabric_ipgs(base_url, apic_cookie, headers, output_log):
    error = False
    try:
        get_url = base_url + 'node/class/infraAccBndlGrp.json?'
        get_response = requests.get(get_url, cookies=apic_cookie, headers=headers, verify=False)
        get_fabic_ipg_response = json.loads(get_response.text)
        return error, get_fabic_ipg_response

    except:
        error = True
        output_log.append({'Errors': 'Failed to get IPG list from Fabric.'})
        return error, output_log


def get_vpc_domain(base_url, apic_cookie, headers, output_log):
    error = False
    try:
        get_url = base_url + 'node/mo/uni/fabric/protpol.json?query-target=children'
        get_response = requests.get(get_url, cookies=apic_cookie, headers=headers, verify=False)
        get_fabic_vpc_response = json.loads(get_response.text)
        return error, get_fabic_vpc_response

    except:
        error = True
        output_log.append({'Errors': 'Failed to get VPC Domains from Fabric.'})
        return error, output_log


def get_vpc_domain_detail(base_url, apic_cookie, headers, output_log, vpc_name):
    error = False
    try:
        get_url = base_url + 'node/mo/uni/fabric/protpol/expgep-{0}.json?query-target=children'.format(vpc_name)

        get_response = requests.get(get_url, cookies=apic_cookie, headers=headers, verify=False)
        get_fabic_vpc_response = json.loads(get_response.text)
        return error, get_fabic_vpc_response

    except:
        error = True
        output_log.append({'Errors': 'Failed to get VPC Domains details from Fabric.'})
        return error, output_log


def get_lsp_detail(base_url, apic_cookie, headers, output_log, vpc, node_1, node_2):
    error = False
    try:
        if vpc:
            get_url = base_url + 'node/mo/uni/infra/accportprof-VPC-{1}-{2}_LSP.json?query-target=children'.format(vpc,
                                                                                                              node_1,
                                                                                                              node_2)

        if not vpc:
            get_url = base_url + 'node/mo/uni/infra/accportprof-LFS{0}_LSP.json?query-target=children'.format(node_1)

        get_response = requests.get(get_url, cookies=apic_cookie, headers=headers, verify=False)
        get_fabic_lsp_response = json.loads(get_response.text)
        return error, get_fabic_lsp_response

    except:
        error = True
        output_log.append({'Errors': 'Failed to get LSP details from Fabric.'})
        return error, output_log


def get_port_detail(base_url, apic_cookie, headers, output_log, dn):
    error = False
    try:
        get_url = base_url + 'node/mo/{0}.json?query-target=children'.format(dn)

        get_response = requests.get(get_url, cookies=apic_cookie, headers=headers, verify=False)
        get_fabic_lsp_port_response = json.loads(get_response.text)
        return error, get_fabic_lsp_port_response

    except:
        error = True
        output_log.append({'Errors': 'Failed to get LSP Port details from Fabric.'})
        return error, output_log


def get_all_epgs(base_url, apic_cookie, headers, output_log):
    error = False
    try:
        get_url = base_url + 'node/class/fvAEPg.json'

        get_response = requests.get(get_url, cookies=apic_cookie, headers=headers, verify=False)
        get_fabic_epg_response = json.loads(get_response.text)
        return error, get_fabic_epg_response

    except:
        error = True
        output_log.append({'Errors': 'Failed to get EPG details from Fabric.'})
        return error, output_log
