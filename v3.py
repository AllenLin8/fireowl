####################################################
#
#     FireOwl - HackMIT project - 9/20/2020
#    A Project that shows a live dashboard of all the fires in the United States
#
#    Created by:
#       Allen Lin
#       Ben Carter
#       Krishna Ramani 
#       Sahil Khan
#
#    To run, install the following requirements:
#      bottle
#      mysql.connector
#      urllib3
#      gunicorn
#      
#    Edit the below to adjust the port that is served.
PORT_TO_SERVE = 8012    
#    Edit the below to adjust where the website files are served. These files are included with the problem
webfiles = "your_path_here"
#
#
#    Then, to run, simply type 'python3 v3.py' 
#
#####################################################


from bottle import *
import mysql.connector
import datetime
import math
from dbV2 import database
import random
import json
import urllib3
import base64
import time
import requests
import json






def calcDistance(lat1,lon1,lat2,lon2):
    return math.acos(math.sin(math.pi * lat1/180.0) * math.sin(math.pi * lat2/180.0) + math.cos(math.pi * lat1/180.0) * math.cos(math.pi * lat2/180.0) * math.cos(math.pi * lon1/180.0 - math.pi * lon2 / 180.0)) * 3963

                                                                          #sql ACOS(SIN(PI() * lat1 / 180.0) * SIN(PI() * lat2 / 180.0) + COS(PI() * lat1/180.0) * COS(PI() * lat2 / 180.0) * COS(PI() * long1 / 180.0 - PI() * long2 / 180.0)) * 3963

def mapValue(x, in_min, in_max, out_min, out_max):
    return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min

def constrain(x , low, high):
    if(x > high):
        return high
    if(x < low):
        return low
    return x


def makeSafe(text, ignore=None):
    listOf = [
["\"",""],
["'",""],
["&",""],
["<",""],
[">",""],
[" ",""],
["\n",""],
["-",""],
["*",""],
["`",""],
["~",""],
["@",""],
["#",""],
["%",""],
["^",""],
["=",""],
[";",""],
["|",""],
[".",""],
['\\',""]
]
    if(ignore != None):
        ignoreIndex = []
        for x in ignore:
            listOf.pop(listOf.index([x,""]))
     #   for x in ignore:
     #       counter = 0
     #       for let in listOf:
     #           if(let[0] == x):
     #               ignoreIndex.append(counter)
     #           counter = counter + 1
     #       #easyPrint(ignoreIndex)
     #       subtract = 0
     #       for y in ignoreIndex:
     #           listOf.pop(y - subtract)
     #
     #            subtract = subtract + 1

    for x in listOf:
        if(text.find(x[0]) != -1):
            print("Blocked: '%s'" %(x[0]))
    #    print(text.find(x[0]))
    #    print(x[0])
        text = text.replace(str(x[0]),str(x[1]))
    return text




## send all points to html
## get and add a point




def getIPLocation(ipStr):
    http = urllib3.PoolManager()
    try:
        verif = http.request('GET','http://ip-api.com/json/%s' %(ipStr),timeout=2.0)
    except:
        return None
  #  print(verif)
    if(verif.status == 200):
        out = json.loads(verif.data.decode())
      #  print(out)
        a = [0,0]
        if(out['status'] == "success"):
            a[0] = out['lat']
            a[1] = out['lon']
            return (a[0], a[1])
        else:
            return None
    return None




def getRealFires():
#    print("Sending Request")
    apiUrl = "https://services3.arcgis.com/T4QMspbfLg3qTGWY/arcgis/rest/services/Active_Fires/FeatureServer/0/query?where=1%3D1&outFields=OBJECTID,CalculatedAcres,CreatedOnDateTime,FireBehaviorGeneral,FireDiscoveryDateTime,FireOutDateTime,FireStrategyPointZonePercent,InitialLatitude,InitialLongitude,IsValid,InitialResponseAcres,UniqueFireIdentifier&returnGeometry=false&outSR=4326&f=json"
    http = urllib3.PoolManager()
    
    try:
        verif = http.request('GET',apiUrl,timeout=2.0)
    except:
        return None
 #   print("Done")
    if(verif.status == 200):
        out = json.loads(verif.data.decode())
        #print(out)
        a = [0,0]
        allFires = out['features']
 #      print("Listing")
        for fire in allFires:
            options = fire['attributes']
            wantedOptions = {}
            wantedOptions["dateTime"] = options['FireDiscoveryDateTime']
            wantedOptions["dateOut"] = options['FireOutDateTime']
            wantedOptions["startSize"] = options['InitialResponseAcres']
            wantedOptions["lat"] = options['InitialLatitude']
            wantedOptions["lon"] = options['InitialLongitude']
            wantedOptions["sizeNow"] = options['CalculatedAcres']
            wantedOptions["fireDataID"] = options['UniqueFireIdentifier']
            wantedOptions["isValid"] = options['IsValid']
            
            ### check if active fire
            if(wantedOptions['lat'] != None and wantedOptions['lon'] != None and wantedOptions['isValid'] == 1 and wantedOptions['dateTime'] != None and wantedOptions['dateOut'] == None and wantedOptions['sizeNow'] != None and wantedOptions['startSize'] != None):
              #  print("%s,%s,%s,%s,%s,%s,%s,%s" % (wantedOptions['fireDataID'],wantedOptions['lat'],wantedOptions['lon'],wantedOptions['sizeNow'],wantedOptions['isValid'],wantedOptions['dateTime'],wantedOptions['dateOut'],wantedOptions['startSize'])   )
                acres = wantedOptions['sizeNow']
                acrePercent = constrain(mapValue( acres + wantedOptions['startSize'] * 4, 0,500000,0,100),0,150)
                secondSince = time.time() - int(int(wantedOptions['dateTime']) / 1000)

                slope = constrain(mapValue((60 * acres) / secondSince,0,15,0,100),0,200)
                intensity = (acrePercent / 2.0) + (slope / 2.0)



                if(intensity > 100):
                    intensity = 100
                elif(intensity < 0):
                    intensity = 0
                newIntensity = 0
                if(intensity > 70):
                    newIntensity = 3
                elif(intensity > 30):
                    newIntensity = 2
                else:
                    newIntensity = 1 
                
                dateA = datetime.datetime.fromtimestamp(int(str(wantedOptions['dateTime'])[:-3]))
                dat = dateA.strftime("%Y/%m/%d %H:%M:%S")
            #    print(int(intensity),int(acrePercent),int(slope),acres)
                db = database()
                db.addFireGOV(float(wantedOptions['lat']),float(wantedOptions['lon']), dat,"National Interagency Fire Center",newIntensity,intensity > 10,wantedOptions['fireDataID'])
                db.close()
          #  if(dateOut == None)

    #    print("Done")
            

      #  print(allFires)
    verif.close()
   

    return None




def index():
    forward = False
    raw = ''
    try:
        raw = makeSafe(request.query.get("forward"),ignore=['='])
        print(raw)
        q = raw[1]
        forward = True
    except:
        pass
    if(forward):
        print("FORWARDING! - abc")
        f = open(webfiles + "/index.html")
        html = f.read()
        f.close()
        html = html.replace("/*#$--FORWARD--$#*/", "window.location.replace('/main?location=%s');//" %(raw))
        return html


        

    return static_file("index.html",root=webfiles)

def addFire():
    lat = 0
    lon = 0
    msg = ''
    intensity = 0
    smoke = 0
    try:
        lat = float(makeSafe(request.query.get("lat"),ignore=['-','.']))
        lon = float(makeSafe(request.query.get("lng"),ignore=['-','.']))
        msg = makeSafe(request.query.get("addInfo"),ignore=[' ','.','\''])
        intensity = abs(int(makeSafe(request.query.get("alert"))))
        smoke = abs(int(makeSafe(request.query.get("smoke"))))

        if(smoke > 1):
            raise ValueError
        if(intensity > 3):
            raise ValueError
    except:
        return "invalid1"

    finalDate = datetime.datetime.now()
   # try:
   #     finalDate = datetime.strptime(dat[0] + " " + dat[1],"%Y/%m/%d %H:%M:%S")
   # except:
   #     return "invalid"
    fS = finalDate.strftime("%Y/%m/%d %H:%M:%S")

    if(abs(lat) > 180.0 or abs(lon) > 180.0):
        return "invalid2"

    db = database()
    db.addFire(lat,lon,fS,msg,intensity,smoke)
    db.close()

    return "good"


def receiveLocation():
    
    lat = 0
    lon = 0
    skip = False
    try:
        lat = float(makeSafe(request.query.get("lat"),ignore=['-','.']))
        lon = float(makeSafe(request.query.get("lon"),ignore=['-','.']))
        skip = int(makeSafe(request.query.get("no"))) != 0

    except:
        return "invalid"

    if(abs(lat) > 180.0 or abs(lon) > 180.0):
        return "invalid"

    if(skip):
        try:
            lat, lon = getIPLocation(request.get_header("X-ClientIP")) # this comes from a NGINX proxy server. If not used, replace with IP
        except:
            lat, lon = getIPLocation(request.environ.get('REMOTE_ADDR'))

  

  #  print(lat)
  #  print(lon)

    dump = "%s,%s,%s" %(lat,lon,random.randint(2,500))
    dump = dump.encode('ascii')
    encBy = base64.b64encode(dump)
    enc = encBy.decode('ascii')


  #  print(enc)
    response.set_cookie(name="linkBounce",value="T", secret="a93nfd")
    return "good~%s" %(enc)

def getWindSpeeds():
    db = database()
    fires = db.getFiresWind()
    outputList = []
    outputListWeak = []
    outputListMed = []
    outputListHigh = []
    for fire in fires:
        lat = fire[0]
        lng = fire[1]
        wind_speed = fire[3]
        if (wind_speed > 10):
            wind_mag = 3
            outputListHigh.append([lat, lng, wind_mag])
        elif (wind_speed > 5):
            wind_mag = 2
            outputListMed.append([lat, lng, wind_mag])
        else:
            wind_mag = 1
            outputListWeak.append([lat, lng, wind_mag])
    outputList = [outputListWeak, outputListMed, outputListHigh]
    db.close()
    return outputList

def main():
    cordStart = [0,0]
    windSpeeds = getWindSpeeds()    
  #  print(windSpeeds)
    raw = ''
    try:
        raw = makeSafe(request.query.get("location"),ignore=['='])
        q = raw[1]
    except:
        redirect("/")

    try:
        if(request.get_cookie("linkBounce",secret="a93nfd") != 'T'):
            raise ValueError      

    except:
        redirect("/?forward=%s" %(raw))
    
    response.set_cookie(name="linkBounce",value="F",secret="anfd")

    by = raw.encode('ascii')
    mbytes = base64.b64decode(by)

    location = makeSafe(mbytes.decode('ascii'),ignore=['-','.'])
  #  print(location)
    a = location.split(",")

    try:
        cordStart[0] = float(a[0])
        cordStart[1] = float(a[1])
    except:
        redirect("/")

  #  print("MAIN: ",cordStart)
    getRealFires()
    fires = []
    db = database()
    fireListL = db.getFiresXYWeight(1)
    fireListM = db.getFiresXYWeight(2)
    fireListH = db.getFiresXYWeight(3)
    db.close()
    dump = " "
    f = open(webfiles + "/main.html")
    html = f.read()
    f.close()

    for fire in fireListL:
        dump = dump + "new google.maps.LatLng(" + str(fire[0]) + ", " + str(fire[1]) + "),"
    dump = dump[:-1]

    html = html.replace("<!--$--POINTSLLL--$-->", dump)

    dump = " "
    for fire in fireListM:
        dump = dump + "new google.maps.LatLng(" + str(fire[0]) + ", " + str(fire[1]) + "),"
    dump = dump[:-1]

    html = html.replace("<!--$--POINTSMMM--$-->", dump)

    dump = " "
    for fire in fireListH:
        dump = dump + "new google.maps.LatLng(" + str(fire[0]) + ", " + str(fire[1]) + "),"
    dump = dump[:-1]
    html = html.replace("<!--$--POINTSHHH--$-->", dump)



    
    windSpeedLight = windSpeeds[0]
    dump = " "
    for fire in windSpeedLight:
     #   print(fire)
        dump = dump + "new google.maps.LatLng(" + str(fire[0]) + ", " + str(fire[1]) + "),"
    dump = dump[:-1]
    html = html.replace("<!--$--POINTSWLW--$-->", dump)

    windSpeedMed = windSpeeds[1]
    dump = " "
    for fire in windSpeedMed:
        dump = dump + "new google.maps.LatLng(" + str(fire[0]) + ", " + str(fire[1]) + "),"
    dump = dump[:-1]
    html = html.replace("<!--$--POINTSWMW--$-->", dump)

    windSpeedHigh = windSpeeds[2]
    dump = " "
    for fire in windSpeedHigh:
        dump = dump + "new google.maps.LatLng(" + str(fire[0]) + ", " + str(fire[1]) + "),"
    dump = dump[:-1]
    html = html.replace("<!--$--POINTSWHW--$-->", dump)

    #dump = "{lat: -31.563910, lng: 147.154312},{lat: -33.718234, lng: 150.363181},{lat: -33.727111, lng: 150.371124}"

    
    jsonData = "{ center: { lat: %s,  lng: %s  },  zoom: 9, styles:  " %(cordStart[0],cordStart[1])
    jsonData = jsonData + """
    
    [
    {
        "featureType": "all",
        "elementType": "all",
        "stylers": [
            {
                "visibility": "on"
            }
        ]
    },
    {
        "featureType": "all",
        "elementType": "labels",
        "stylers": [
            {
                "visibility": "on"
            },
            {
                "color": "#EEEEFF"
            },
            {
                "saturation": "-100"
            }
        ]
    },
    {
        "featureType": "all",
        "elementType": "labels.text.fill",
        "stylers": [
            {
                "saturation": 36
            },
            {
                "color": "#EEEEFF"
            },
            {
                "lightness": 40
            },
            {
                "visibility": "on"
            }
        ]
    },
    {
        "featureType": "all",
        "elementType": "labels.text.stroke",
        "stylers": [
            {
                "visibility": "off"
            },
            {
                "color": "#000000"
            },
            {
                "lightness": 16
            }
        ]
    },
    {
        "featureType": "all",
        "elementType": "labels.icon",
        "stylers": [
            {
                "visibility": "off"
            }
        ]
    },
    {
        "featureType": "administrative",
        "elementType": "geometry.fill",
        "stylers": [
            {
                "color": "#000000"
            },
            {
                "lightness": 20
            }
        ]
    },
    {
        "featureType": "administrative",
        "elementType": "geometry.stroke",
        "stylers": [
            {
                "color": "#000000"
            },
            {
                "lightness": 17
            },
            {
                "weight": 1.2
            }
        ]
    },
    {
        "featureType": "landscape",
        "elementType": "geometry",
        "stylers": [
            {
                "color": "#000000"
            },
            {
                "lightness": 20
            }
        ]
    },
    {
        "featureType": "landscape",
        "elementType": "geometry.fill",
        "stylers": [
            {
                "color": "#4d5960"
            }
        ]
    },
    {
        "featureType": "landscape",
        "elementType": "geometry.stroke",
        "stylers": [
            {
                "color": "#4d5960"
            }
        ]
    },
    {
        "featureType": "landscape.natural",
        "elementType": "geometry.fill",
        "stylers": [
            {
                "color": "#4d5960"
            }
        ]
    },
    {
        "featureType": "poi",
        "elementType": "geometry",
        "stylers": [
            {
                "lightness": 21
            }
        ]
    },
    {
        "featureType": "poi",
        "elementType": "geometry.fill",
        "stylers": [
            {
                "color": "#4d5960"
            }
        ]
    },
    {
        "featureType": "poi",
        "elementType": "geometry.stroke",
        "stylers": [
            {
                "color": "#4d5960"
            }
        ]
    },
    {
        "featureType": "road",
        "elementType": "geometry",
        "stylers": [
            {
                "visibility": "on"
            },
            {
                "color": "#7f898d"
            }
        ]
    },
    {
        "featureType": "road",
        "elementType": "geometry.fill",
        "stylers": [
            {
                "color": "#7f898d"
            }
        ]
    },
    {
        "featureType": "road.highway",
        "elementType": "geometry.fill",
        "stylers": [
            {
                "color": "#7f898d"
            },
            {
                "lightness": 17
            }
        ]
    },
    {
        "featureType": "road.highway",
        "elementType": "geometry.stroke",
        "stylers": [
            {
                "color": "#7f898d"
            },
            {
                "lightness": 29
            },
            {
                "weight": 0.2
            }
        ]
    },
    {
        "featureType": "road.arterial",
        "elementType": "geometry",
        "stylers": [
            {
                "color": "#000000"
            },
            {
                "lightness": 18
            }
        ]
    },
    {
        "featureType": "road.arterial",
        "elementType": "geometry.fill",
        "stylers": [
            {
                "color": "#7f898d"
            }
        ]
    },
    {
        "featureType": "road.arterial",
        "elementType": "geometry.stroke",
        "stylers": [
            {
                "color": "#7f898d"
            }
        ]
    },
    {
        "featureType": "road.local",
        "elementType": "geometry",
        "stylers": [
            {
                "color": "#000000"
            },
            {
                "lightness": 16
            }
        ]
    },
    {
        "featureType": "road.local",
        "elementType": "geometry.fill",
        "stylers": [
            {
                "color": "#7f898d"
            }
        ]
    },
    {
        "featureType": "road.local",
        "elementType": "geometry.stroke",
        "stylers": [
            {
                "color": "#7f898d"
            }
        ]
    },
    {
        "featureType": "transit",
        "elementType": "geometry",
        "stylers": [
            {
                "color": "#000000"
            },
            {
                "lightness": 19
            }
        ]
    },
    {
        "featureType": "water",
        "elementType": "all",
        "stylers": [
            {
                "color": "#2b3836"
            },
            {
                "visibility": "on"
            }
        ]
    },
    {
        "featureType": "water",
        "elementType": "geometry",
        "stylers": [
            {
                "color": "#2b3836"
            },
            {
                "lightness": 17
            }
        ]
    },
    {
        "featureType": "water",
        "elementType": "geometry.fill",
        "stylers": [
            {
                "color": "#242b28"
            }
        ]
    },
    {
        "featureType": "water",
        "elementType": "geometry.stroke",
        "stylers": [
            {
                "color": "#242b28"
            }
        ]
    },
    {
        "featureType": "water",
        "elementType": "labels",
        "stylers": [
            {
                "visibility": "off"
            }
        ]
    },
    {
        "featureType": "water",
        "elementType": "labels.text",
        "stylers": [
            {
                "visibility": "off"
            }
        ]
    },
    {
        "featureType": "water",
        "elementType": "labels.text.fill",
        "stylers": [
            {
                "visibility": "off"
            }
        ]
    },
    {
        "featureType": "water",
        "elementType": "labels.text.stroke",
        "stylers": [
            {
                "visibility": "off"
            }
        ]
    },
    {
        "featureType": "water",
        "elementType": "labels.icon",
        "stylers": [
            {
                "visibility": "off"
            }
        ]
    }
]
    
    """
    
 
    html = html.replace("#$--MAPINFO--$#", jsonData + "}")
    

    #### STUFF GOES HERE

    return html





def staticFilesTesting(filepath):
    staticfiles = webfiles
    return static_file(filepath, root=staticfiles)

if __name__ == "__main__":
    hook = "/"
    app = Bottle()
    app.route(hook,"GET", index)
    app.route("/<filepath:path>","GET",staticFilesTesting)
    app.route(hook + "getLocation","GET",receiveLocation)
    app.route(hook + "main","GET",main)
    app.route(hook + "addPin", "GET",addFire)
    app.run(host="", port=PORT_TO_SERVE, server='gunicorn', workers=6,debug=False)
