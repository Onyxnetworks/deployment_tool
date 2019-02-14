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
        get_url = base_url + 'node/class/infraAccPortGrp.json?'
        get_response = requests.get(get_url, cookies=apic_cookie, headers=headers, verify=False)
        get_fabic_ipg_response = json.loads(get_response.text)
        return error, get_fabic_ipg_response

    except:
        error = True
        output_log.append({'Errors': 'Failed to get IPG list from Fabric.'})
        return error, output_log


def get_fabric_vpc_ipgs(base_url, apic_cookie, headers, output_log):
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
            get_url = base_url + 'node/mo/uni/infra/accportprof-VPC-{0}-{1}_LSP.json?query-target=children'.format(node_1,
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


def get_epg_detail(base_url, apic_cookie, headers, epg_name, output_log):
    error = False
    try:
        get_url = base_url + 'node/class/fvAEPg.json?query-target-filter=and(eq(fvAEPg.name,"{0}"))'.format(epg_name)

        get_response = requests.get(get_url, cookies=apic_cookie, headers=headers, verify=False)
        get_fabic_epg_response = json.loads(get_response.text)

        if int(get_fabic_epg_response['totalCount']) != 1:
            raise ValueError

        else:
            return error, get_fabic_epg_response

    except ValueError:
        error = True
        output_log.append({'Errors': 'More than one search result returned when looking for EPG: {0} in the Fabric, '
                                     'static binding skipped.'.format(epg_name, get_fabic_epg_response['totalCount'])})
        return error, output_log

    except:
        error = True
        output_log.append({'Errors': 'Failed to get EPG for {0} from Fabric.'.format(epg_name)})
        return error, output_log


def post_create_ipg(base_url, apic_cookie, headers, output_log, ipg_settings):
    error = False

    # Build JSON for IPG creation.
    infraAccBndlGrp = {}
    infraAccBndlGrp['attributes'] = {
        'lagT': 'node',
        'name': ipg_settings['name'],
        'status': 'created'
    }

    infraRsAttEntP = {}
    infraRsAttEntP['attributes'] = {
        'tDn': ipg_settings['aep'],
        'status': 'created,modified'
    }
    infraRsAttEntP['children'] = []

    infraRsHIfPol = {}
    infraRsHIfPol['attributes'] = {
        'tnFabricHIfPolName': ipg_settings['speed'],
        'status': 'created,modified'
    }
    infraRsHIfPol['children'] = []

    infraRsLacpPol = {}
    infraRsLacpPol['attributes'] = {
        'tnLacpLagPolName': ipg_settings['portChannelPolicy'],
        'status': 'created,modified'
    }
    infraRsLacpPol['children'] = []

    infraRsMonIfInfraPol = {}
    infraRsMonIfInfraPol['attributes'] = {
        'tnMonInfraPolName': 'default',
        'status': 'created,modified'
    }
    infraRsMonIfInfraPol['children'] = []

    infraRsCdpIfPol = {}
    infraRsCdpIfPol['attributes'] = {
        'tnCdpIfPolName': 'CDP-ENABLE_POL',
        'status': 'created,modified'
    }
    infraRsCdpIfPol['children'] = []

    infraRsMcpIfPol = {}
    infraRsMcpIfPol['attributes'] = {
        'tnMcpIfPolName': 'MCP-ENABLED_POL',
        'status': 'created,modified'
    }
    infraRsMcpIfPol['children'] = []

    infraRsLldpIfPol = {}
    infraRsLldpIfPol['attributes'] = {
        'tnLldpIfPolName': 'LLDP-ENABLE_POL',
        'status': 'created,modified'
    }
    infraRsLldpIfPol['children'] = []

    infraRsL2IfPol = {}
    infraRsL2IfPol['attributes'] = {
        'tnL2IfPolName': 'L2-DEFAULT_POL',
        'status': 'created,modified'
    }
    infraRsLldpIfPol['children'] = []

    infraAccBndlGrp['children'] = [{'infraRsAttEntP': infraRsAttEntP},
                                   {'infraRsHIfPol': infraRsHIfPol},
                                   {'infraRsLacpPol': infraRsLacpPol},
                                   {'infraRsMonIfInfraPol': infraRsMonIfInfraPol},
                                   {'infraRsCdpIfPol': infraRsCdpIfPol},
                                   {'infraRsMcpIfPol': infraRsMcpIfPol},
                                   {'infraRsLldpIfPol': infraRsLldpIfPol},
                                   {'infraRsL2IfPol': infraRsL2IfPol}
                                   ]

    try:
        post_url = base_url + 'node/mo/uni/infra/funcprof/accbundle-{0}.json'.format(ipg_settings['name'])
        ipg_json = json.dumps({'infraAccBndlGrp': infraAccBndlGrp})

        post_response = requests.post(post_url, data=ipg_json, cookies=apic_cookie, headers=headers, verify=False)
        post_ipg_create_response = json.loads(post_response.text)

        if post_response.status_code == 200:
            output_log.append({'NotificationsInfo': 'IPG: {0} successfully created.'.format(ipg_settings['name'])})
            return error, output_log

        else:
            error = True
            output_log.append({'Errors': 'Error: {0} - Failed to create IPG {1} to LSP.'.format(post_response.status_code, ipg_settings['name'])})

    except:
        error = True
        output_log.append({'Errors': 'Failed to create IPG {0}'.format(ipg_settings['name'])})
        return error, output_log


def post_create_lsp_port(base_url, apic_cookie, headers, output_log, port_settings):
    error = False
    # Build JSON for LSP Port creation.
    infraHPortS = {}
    infraHPortS['attributes'] = {
        'name': port_settings['lspDescription'],
        'status': 'created,modified'
    }

    infraPortBlk = {}
    infraPortBlk['attributes'] = {
        'fromPort': port_settings['fromPort'],
        'toPort': port_settings['toPort'],
        'name': 'block2',
        'status': 'created,modified'
    }
    infraPortBlk['children'] = []

    infraRsAccBaseGrp = {}
    infraRsAccBaseGrp['attributes'] = {
        'tDn': 'uni/infra/funcprof/{0}-{1}'.format(port_settings['ipgPrefix'], port_settings['ipg']),
        'status': 'created,modified'
    }
    infraRsAccBaseGrp['children'] = []

    infraHPortS['children'] = [
        {'infraPortBlk': infraPortBlk},
        {'infraRsAccBaseGrp': infraRsAccBaseGrp}
    ]

    try:

        post_url = base_url + 'node/mo/uni/infra/accportprof-{0}/hports-{1}-typ-range.json'.format(port_settings['lsp'],
                                                                                                   port_settings[
                                                                                                       'lspDescription'])
        lsp_json = json.dumps({'infraHPortS': infraHPortS})

        post_response = requests.post(post_url, data=lsp_json, cookies=apic_cookie, headers=headers, verify=False)
        post_lsp_map_response = json.loads(post_response.text)

        if post_response.status_code == 200:
            output_log.append({'NotificationsInfo': 'IPG: ' + port_settings['ipg'] + ' successfully mapped to LSP: ' +
                               port_settings['lsp'] + ' on port: ' + port_settings['block']})

            try:

                infraPortBlk = {}
                infraPortBlk['attributes'] = {
                    'descr': port_settings['blockDescription']
                }
                infraPortBlk['children'] = []

                lsp_desc_json = json.dumps({'infraPortBlk': infraPortBlk})

                desc_post_url = base_url + 'node/mo/uni/infra/accportprof-{0}/hports-{1}-typ-range/portblk-block2.json'.format(
                    port_settings['lsp'], port_settings['lspDescription'])

                post_response = requests.post(desc_post_url, data=lsp_desc_json, cookies=apic_cookie, headers=headers,
                                              verify=False)
                post_lsp_desc_response = json.loads(post_response.text)

            except:
                error = True
                output_log.append({'Errors': 'Failed to add description for IPG {0} to LSP.'.format(port_settings['ipg'])})

            return error, output_log

        else:
            error = True
            output_log.append({'Errors': 'Error: {0} - Failed to MAP IPG {1} to LSP.'.format(post_response.status_code, port_settings['ipg'])})

    except:
        error = True
        output_log.append({'Errors': 'Failed to MAP IPG {0} to LSP.'.format(port_settings['ipg'])})
        return error, output_log


def post_create_static_binding(base_url, apic_cookie, headers, output_log, binding_settings):
    error = False

    fvRsPathAtt = {}
    fvRsPathAtt['attributes'] = {
        'encap': 'vlan-{0}'.format(binding_settings['encap']),
        'tDn': binding_settings['lsptDn'],
        'mode': binding_settings['mode'],
        'instrImedcy': 'immediate',
        'status': 'created'
    }
    fvRsPathAtt['children'] = []

    static_binding_json = json.dumps({'fvRsPathAtt': fvRsPathAtt})

    try:
        post_url = base_url + 'node/mo/{0}.json'.format(binding_settings['tDn'])

        post_response = requests.post(post_url, data=static_binding_json, cookies=apic_cookie, headers=headers, verify=False)
        post_static_binding_response = json.loads(post_response.text)

        if post_response.status_code == 200:
            output_log.append({'NotificationsInfo': 'IPG: {0} successfully mapped to EPG {1}'.format(binding_settings['ipg_name'], binding_settings['epg_name'])})

            return error, output_log

        elif post_response.status_code == 400 and int(post_static_binding_response['imdata'][0]['error']['attributes']['code']) == 103:
            output_log.append({'NotificationsWarning': 'IPG: {0} already mapped to EPG {1}'.format(
                binding_settings['ipg_name'], binding_settings['epg_name'])})

            return error, output_log

        else:

            raise Exception

    except:
        error = True
        output_log.append({'Errors': 'Failed to map static binding {0} for {1}.'.format(binding_settings['ipg_name'], binding_settings['epg_name'])})
        return error, output_log


