from dbV2 import database
import time
import requests
import json

db = database()
fires = db.getFires()
for fire in fires:
    lat = fire[0]
    lng = fire[1]
    fireID = fire[2]
    url = "https://api.climacell.co/v3/weather/realtime"
    querystring = {"lat":str(lat),"lon":str(lng),"unit_system":"si","fields":"wind_speed,wind_direction","apikey":"your_api_key"}
    response = requests.request("GET", url, params=querystring)
    out = json.loads(response.text)
    try:
        wind_speed = float(out['wind_speed']['value'])
    except:
        wind_speed = 0
    db.addWindSpeed(fireID, wind_speed)
    time.sleep(5)
