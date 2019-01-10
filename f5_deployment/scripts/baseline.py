import json, requests

# Ignore SSL Errors
requests.packages.urllib3.disable_warnings()


def bigip_login(base_url, username, password):
    headers = {'content-type': 'application/json'}
    auth_url = base_url + '/mgmt/shared/authn/login'
    auth_payload = {"username": username, "password": password, "loginProviderName": "tmos"}

    try:
        # Attempt to authenticate
        post_response = requests.post(auth_url, data=json.dumps(auth_payload), headers=headers, timeout=5, verify=False)
        payload_response = json.loads(post_response.text)
        post_response.raise_for_status()

        if post_response.status_code == 200:
            auth_token = payload_response['token']['token']
            return payload_response

    except requests.exceptions.HTTPError as errh:
        error_code = "Http Error:" + str(errh)
        return error_code
    except requests.exceptions.ConnectionError as errc:
        error_code = "Error Connecting:" + str(errc)
        return error_code
    except requests.exceptions.Timeout as errt:
        error_code = "Timeout Error:" + str(errt)
        return error_code
    except requests.exceptions.RequestException as err:
        error_code = "Error:" + str(err)
        return error_code
