#online json system
import json
import requests

token = "$2b$10$TzTRS11nEhPrR8reMZyw6upPdrkXRTdJndUIeCBR78LZdwVUgb8BW"
bin = "635076a265b57a31e69bee29"

def read():
    url = f"https://api.jsonbin.io/v3/b/{bin}/latest"
    headers = {
        "X-Master-Key": token,
        "X-Access-Key": "$2b$10$sNEiMAVBacY5.PIi6lpD0.ISVM7.PDolUq.Ote3ohGBf0NSj2Bi8m"
    }
    return json.loads(requests.get(url, headers=headers).content)["record"]

def write(data): 
    url = f"https://api.jsonbin.io/v3/b/{bin}" 
    headers = {
        "Content-Type": "application/json",
        "X-Master-Key": token
    }
    requests.put(url, headers=headers, data=json.dumps(data))