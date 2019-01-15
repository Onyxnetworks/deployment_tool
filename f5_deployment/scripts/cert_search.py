#from datetime import datetime
#
#
#datetime_object = datetime.strptime(item_data, '%b %d %H:%M:%S %Y %Z')
#now = datetime.now()
#result = datetime_object.date() - now.date()
#if result.days <= 90:
#    print('Renew Cert')
#
#if datetime_object.date() > now.date():
#    print('Cert Expired')
#
#
#{$env.protocol}://{$env.f5_base_url}/mgmt/tm/ltm/virtual/?expandSubcollections=true&$select=name,destination,profilesReference
#
#
#{$env.protocol}://{$env.f5_base_url}/mgmt/tm/sys/crypto/cert