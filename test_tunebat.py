import urllib.request
import ssl
ssl._create_default_https_context = ssl._create_unverified_context
try:
    req = urllib.request.Request("https://tunebat.com/", headers={'User-Agent': 'Mozilla/5.0'})
    html = urllib.request.urlopen(req).read().decode('utf-8')
    print("Tunebat is reachable (Length: %d)" % len(html))
except Exception as e:
    print(f"Error: {e}")
