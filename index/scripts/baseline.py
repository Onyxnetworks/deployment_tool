def get_base_url(environment):
    if environment == 'Production':
        base_urls = {'ACI': {'UKDC1': 'prod_aci_url1', 'UKDC2': 'prod_aci_url2'}, 'F5': {'UKDC1': 'prod_f5_url1', 'UKDC2': 'prod_f5_url2'}}
        return base_urls

    if environment == 'Pre-Production':
        base_urls = {'ACI': {'UKDC1': 'ppe_aci_url1', 'UKDC2': 'ppe_aci_url2'}, 'F5': {'UKDC1': 'ppe_f5_url1', 'UKDC2': 'ppe_f5_url2'}}
        return base_urls


    if environment == 'Lab':
        base_urls = {'ACI': {'LAB': 'lab_aci_url1'}, 'F5': {'LAB': 'lab_f5_url1'}}
        return base_urls

# Example to get base_url for a DC:
# environment == 'Production'
# url_list = get_base_url(environment)
#
# To get the url for ACI in DC1 Production:
# DC = 'UKDC1'
# base_url = url_list['ACI'][DC]
# To get the url for F5 in DC1 Production:
# base_url = url_list['F5'][DC]
