import requests
import json

response = requests.get('http://10.128.202.149:5000/slave/ww')

json1=json.loads(response.text)
print(json1["speed"])