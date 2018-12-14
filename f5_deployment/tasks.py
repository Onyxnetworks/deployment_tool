# Base Functions
import openpyxl

# Celery Functions
from celery import shared_task

# Custom Functions
from f5_deployment.scripts.vs_deployment import *

def vs_deployment_excel_open_workbook(file):
    wb = openpyxl.load_workbook(file, data_only=True)
    py_ws = wb.get_sheet_by_name('Tab_Python')
    vs_dict = {}
    vs_dict['vs'] = {}
    vs_dict['node_list'] = []
    vs_dict['node_priority'] = []
    for col in py_ws.iter_cols(min_row=2, max_row=2, max_col=27):
        for cell in col:
            vs_dict['vs'][cell.coordinate] = cell.value

    for col in py_ws.iter_cols(min_row=2, max_row=2, min_col=28, max_col=47):
        for cell in col:
            cell = str(cell.value)
            if not cell == 'None':
                vs_dict['node_list'].append(cell)
            
    for col in py_ws.iter_cols(min_row=2, max_row=2, min_col=49, max_col=68):
        for cell in col:
            cell = str(cell.value)
            if not cell == 'None':        
                vs_dict['node_priority'].append(cell)        
    
    print(vs_dict)
    return vs_dict
    
@shared_task
def vs_deployment_validation(vs_dict, location, url_dict, username, password):
    
    output_log = []
    error = False
    output_log.append({'Headers': 'Identifying F5 Device group.'})  
    # Get Virtual Server Name
    vs_name = vs_dict['vs']['A2']
    
    if location == 'UKDC1':
        device_group = vs_name.rsplit('-', 10)[0]
        base_url = url_dict[location][device_group]
        output_log.append({'Notifications': 'Device group ' + device_group + ' DGA selected.'})
        
    elif location == 'UKDC2':
        device_group = vs_name.rsplit('-', 10)[0]
        base_url = url_dict[location][device_group]
        output_log.append({'Notifications': 'Device group ' + device_group + ' DGB selected.'})
    
    elif location == 'LAB':
        device_group = 'LAB'
        base_url = url_dict[location][device_group]
        output_log.append({'Notifications': 'Device group ' + device_group + ' selected.'})
    
    else:
        error = True
        output_log.append({'Errors': 'Unable to identify F5 Device group, please check index/baseline.py configuration.'})
  
   
    if not error:   
        output_log.append({'Headers': 'Creating connection to BigIP.'})
        bigip_connection = create_connection_bigip(base_url, username, password, output_log)
        output_log = bigip_connection[0]
        error = bigip_connection[1]
  
    if not error:
        bigip_url_base = bigip_connection[2]
        bigip = bigip_connection[3]
        
        output_log.append({'Headers': 'Checking Sync status of F5.'})   
        #check_sync_result  = check_sync(bigip_url_base, bigip, output_log)
        #output_log = check_sync_result[0]
        #error = check_sync_result[1]
     
    if not error:
        output_log.append({'Headers': 'Checking for HTTP Profiles.'})   
        check_httpprofile_result = check_httpprofile(vs_dict, bigip_url_base, bigip, output_log)
        
        output_log = check_httpprofile_result[0]
        error = check_httpprofile_result[1]
       
    if not error:
            output_log.append({'NotificationsSuccess': 'HTTP Profiles validated successfully.'})
    if not error:
        ssl = vs_dict['vs']['D2']
        if ssl in ['https', 'HTTPS']:
                output_log.append({'Headers': 'Checking SSL Profiles.'})
                check_ssl_profile_result = check_ssl_profile(vs_dict, bigip_url_base, bigip, output_log)
                output_log = check_ssl_profile_result[0]
                error = check_ssl_profile_result[1]
                if not error:
                    output_log.append({'Headers': 'Checking certificates.'})
                    check_cert_result = check_cert(vs_dict, bigip_url_base, bigip, output_log)
                    output_log = check_cert_result[0]
                    error = check_cert_result[1]
    
    if not error:
        output_log.append({'Headers': 'Checking HTTP/S Monitors.'})
        check_http_mon_result = check_http_mon(vs_dict, bigip_url_base, bigip, output_log)
        output_log = check_http_mon_result[0]
        error = check_http_mon_result[1]
    
    if not error:
        output_log.append({'Headers': 'Checking SNAT Pools.'})
        snat_pool_present = compare_snat_on_ltm_excel(vs_dict, bigip_url_base, bigip, output_log)
        output_log = snat_pool_present[0]
        error = snat_pool_present[1]
        snat_pool_present = snat_pool_present[2]
        
    if not error:
        output_log.append({'Headers': 'Checking Nodes.'})
        node_list_result = compare_ltm_nodes(vs_dict, bigip_url_base, bigip, output_log)
        output_log = node_list_result[0]
        error = node_list_result[1]
        node_list = node_list_result[3]
        
    return output_log