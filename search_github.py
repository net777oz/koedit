import urllib.request
import json
url = "https://api.github.com/search/code?q=LS11+extension:py"
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
try:
    response = urllib.request.urlopen(req)
    data = json.loads(response.read().decode('utf-8'))
    for item in data.get('items', [])[:5]:
        print(item['html_url'])
except Exception as e:
    print(e)
