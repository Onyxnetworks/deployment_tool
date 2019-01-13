import json, requests

def node_disable_enable_force(selflink, auth_token, request_json):
    # Build auth token header
    headers = {'content-type': 'application/json', 'X-F5-Auth-Token': auth_token}

    put_url = selflink
    try:
        put_response = requests.put(put_url, headers=headers, data=json.dumps(request_json), timeout=5, verify=False)
        payload_response = json.loads(put_response.text)

        if put_response.status_code == 200:
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



def vs_disable_enable_force(selflink, auth_token, request_json):
    # Build auth token header
    headers = {'content-type': 'application/json', 'X-F5-Auth-Token': auth_token}

    patch_url = selflink
    try:
        patch_response = requests.patch(patch_url, headers=headers, data=json.dumps(request_json), timeout=5, verify=False)
        payload_response = json.loads(patch_response.text)

        if patch_response.status_code == 200:
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

