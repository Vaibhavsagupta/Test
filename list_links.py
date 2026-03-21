import requests
import urllib3
import re
import sys

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

try:
    url = "https://the-eye.eu/redarcs/files/"
    r = requests.get(url, verify=False, timeout=30)
    links = re.findall(r'href="([^"]+)"', r.text)
    hair_links = [l for l in links if 'hair' in l.lower()]
    print("Found links:", hair_links)
except Exception as e:
    print(f"Error: {e}")
