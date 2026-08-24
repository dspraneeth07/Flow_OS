import os

import requests

url = f"{os.getenv('FLOWOS_URL', '')}/api/v1/monitor/builds?flow_id={os.getenv('FLOW_ID', '')}"

headers = {
    "accept": "*/*",
    "x-api-key": f"{os.getenv('FLOWOS_API_KEY', '')}",
}

response = requests.request("DELETE", url, headers=headers)
response.raise_for_status()

print(response.text)
