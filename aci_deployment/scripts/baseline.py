import json, requests
from secrets import *

# Ignore SSL Errors
requests.packages.urllib3.disable_warnings()
HEADERS = {'content-type': 'application/json'}

def APIC_LOGIN(BASE_URL, APIC_USERNAME, APIC_PASSWORD):
    HEADERS = {'content-type': 'application/json'}
    # Log into APIC and generate a cookie for future requests
    login_url = BASE_URL + 'aaaLogin.json'
    auth = {"aaaUser": {"attributes": {"name": APIC_USERNAME, "pwd": APIC_PASSWORD}}}
    auth_payload = json.dumps(auth)
    try:
        post_response = requests.post(login_url, data=auth_payload, headers=HEADERS, verify=False)
        # Take token from response to use for future authentications
        payload_response = json.loads(post_response.text)
        if post_response.status_code == 200:
            token = payload_response['imdata'][0]['aaaLogin']['attributes']['token']
            APIC_COOKIE = {}
            APIC_COOKIE['APIC-Cookie'] = token
        else:
            APIC_COOKIE = ''


    except:
        APIC_COOKIE = ''

    return APIC_COOKIE
