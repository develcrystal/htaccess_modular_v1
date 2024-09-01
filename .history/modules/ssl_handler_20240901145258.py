import requests
import urllib3

def enable_ssl_verification():
    # Enable SSL verification and suppress InsecureRequestWarnings
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def request_with_ssl(url, timeout=30):
    enable_ssl_verification()
    response = requests.get(url, timeout=timeout, verify=True)
    return response
