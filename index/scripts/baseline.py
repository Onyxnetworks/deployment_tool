def get_base_url(environment):
    if environment == 'Production':
        BASE_URLS = {'ACI': {'UKDC1': 'prod_aci_url1', 'UKDC2': 'prod_aci_url2'}, 'F5': {'UKDC1': 'prod_f5_url1', 'UKDC2': 'prod_f5_url2'}}
        return BASE_URLS

    if environment == 'Pre-Production':
        BASE_URLS = {'ACI': {'UKDC1': 'ppe_aci_url1', 'UKDC2': 'ppe_aci_url2'}, 'F5': {'UKDC1': 'ppe_f5_url1', 'UKDC2': 'ppe_f5_url2'}}
        return BASE_URLS


    if environment == 'Lab':
        BASE_URLS = {'ACI': {'UKDC1': 'lab_aci_url1', 'UKDC2': 'lab_aci_url2'}, 'F5': {'UKDC1': 'lab_f5_url1', 'UKDC2': 'lab_f5_url2'}}
        return BASE_URLS

# Example to get base_url for a DC:
# environment == 'Production'
# url_list = get_base_url(environment)
#
# To get the url for ACI in DC1 Production:
# DC = 'UKDC1'
# base_url = url_list['ACI'][DC]
# To get the url for F5 in DC1 Production:
# base_url = url_list['F5'][DC]

# Example for how to do ACI Endpoint search.
#  for BASE_URL in DC_LIST:
#         if 'DCx' in BASE_URL:
#             LOCATION = 'DCX'
#         elif 'DCy' in BASE_URL:
#             LOCATION = 'DCY'
#         else:
#             LOCATION = 'UNKNOWN'
#
#         run get endpoint scripts.
#
#
#
#
#
#
#
##