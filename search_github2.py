import urllib.request
import json
import base64

url = "https://api.github.com/search/code?q=LS11+koei+language:python"
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 koedit-agent'})

try:
    response = urllib.request.urlopen(req)
    data = json.loads(response.read().decode('utf-8'))
    for item in data.get('items', [])[:3]:
        print(item['name'], item['html_url'])
        
        # also print content snippet
        raw_url = item['url']
        req2 = urllib.request.Request(raw_url, headers={'User-Agent': 'Mozilla/5.0 koedit-agent'})
        resp2 = urllib.request.urlopen(req2)
        d2 = json.loads(resp2.read().decode('utf-8'))
        content = base64.b64decode(d2['content']).decode('utf-8')
        print(content[:500])
        print("-------------")
        
except Exception as e:
    print("Error:", e)
