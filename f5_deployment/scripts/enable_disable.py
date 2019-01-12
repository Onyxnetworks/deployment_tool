import json, requests

def disable(selflink, auth_token, disabled_json):
    # Build auth token header
    headers = {'content-type': 'application/json', 'X-F5-Auth-Token': auth_token}

    put_url = selflink
    try:
        put_response = requests.put(put_url, headers=headers, data=json.dumps(disabled_json), timeout=5, verify=False)
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