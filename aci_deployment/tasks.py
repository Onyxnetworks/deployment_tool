# Base Functions
import openpyxl

# Custom Functions
from aci_deployment.scripts.endpoint_search import *
from aci_deployment.scripts.external_epg_deployment import *

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
def EXTERNAL_EPG_EXCEL_FORMAT_VALIDATION(RULE_LIST):
    OUTPUT_LOG = []
    DISPLAY_LIST = []
    TENANT_LIST = ['RED', 'GREEN', 'BLUE']
    ERROR = False

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

    return OUTPUT_LOG
