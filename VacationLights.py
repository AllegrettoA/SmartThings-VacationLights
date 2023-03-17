#SmartThings Vacation Lights Simulator.
#Replaces original Groovy Smartapp.
#Requires SmartThings Personal Access Token with access to devices, commands, and location
#Author:    Allen Allegretto
#Version:   1.0 (2023-03-14) Original



#Configuration:
#1. Provide SmartThings Personal Access Token.  Token needs access to device commands and location mode.
#2. Provide hub location ID.
#3. Provide name of lighting group name for vacation light devices.
#4. Provide number of lights to turn on each cycle.
#5. Provide PollIntervalMinutes for cycle time.
#6. Start time is sunset. Provide Latitude and Longitude for your location.
#7. If you prefer fixed start time, set set UseSunset = False and modify SunsetHourByMonth[] as desired.
#8. Provide hour to stop vacation lights.

#SmartThings Personal Access Token (https://account.smartthings.com/tokens)
AccessToken = 'xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx'

#Hub location ID
HubLocationId = 'xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx'

#VacationLightsGroupName
VacationLightsGroupName = 'Vacation Lights'    #Lighting group name
NumLightsOn = 3                                #Number of random lights to turn on each cycle
PollIntervalMinutes = 17                       #Time interval in minutes between cycles

#Configure to use actual sunset time to begin vacation lighting
Latitude =   34.2
Longitude = -77.9
UseSunset = True

#Current hour and estimate of Sunset by month
#- List for simplicity, reliability, and flexibility (use equal values for fixed start time, start earlier than sunset, etc.)
#- Set UseSunset = False to use this list.
SunsetHourByMonth = [17, 18, 19,  20, 20, 20,  20, 20, 19,  18, 17, 17]

#End Hour
VacationLightsEndHour = 22




import requests             # used for http requests
import datetime             # used to get current datetime
import random               # random number to choose lights
import time                 # sleep loop
from math import sin, cos, asin, acos, tan, radians, degrees    #sunset calculations


#HTTP request commands and headers
commandsOn =  { "commands": [{ "component": "main", "capability": "switch",      "command": "on" }]  }
commandsLvl = { "commands": [{ "component": "main", "capability": "switchLevel", "command": "setLevel", "arguments": [100] }]  }
commandsOff = { "commands": [{ "component": "main", "capability": "switch",      "command": "off" }]  }

headers = {
    'Authorization': 'Bearer ' + AccessToken,
    'Accept': 'application/vnd.smartthings+json;v=20170916',
    'cache-control': 'no-cache'
    }


#Main procedure to quesry each device and log data
def UpdateSmartThingsData():
    
    #Active lighting period
    CurrentHour = datetime.datetime.now().hour
    CurrentMonth = datetime.datetime.now().month
    if IsSunset() and CurrentHour <= VacationLightsEndHour:

        #Get current Home/Away status, exit if not Away
        url = 'https://api.smartthings.com/v1/locations/' + HubLocationId + '/modes/current'
        jsonLoc = requests.get(url, headers=headers, timeout=10).json()
        print(jsonLoc['label'])

        #Device lighting during Away mode
        if jsonLoc['label'] == "Away":

            #Find Vacation Lights device group
            jsonGroups = requests.get('https://api.smartthings.com/v1/devicegroups', headers=headers, timeout=10).json()
            jsonVacLights = None
            for grp in jsonGroups['items']:
                if grp['groupName'] == VacationLightsGroupName:
                    jsonVacLights = grp
                    print("Lights found: ", len(jsonVacLights['devices']))
            if jsonVacLights is None:
                print("VacationLightsGroupName not found")
                return
            
            #During vacation lights active period, turn on & off vacation lights
            if IsSunset() and CurrentHour < VacationLightsEndHour:
                
                # Get Devices and current status
                url = 'https://api.smartthings.com/devices?includeStatus=true&includeHealth=true'
                jsonDevices = requests.get(url, headers=headers, timeout=10).json()

                #Build array of deviceId and on/off status
                vacLightStatus = []
                for lgt in jsonVacLights['devices']:
                    #Find matching deviceId in jsonDevices
                    for dev in jsonDevices['items']:
                        if lgt['deviceId'] == dev['deviceId']:
                            for cap in dev['components'][0]['capabilities']:
                                #On/Off status
                                if cap['id'] == 'switch':
                                    strCap = "switch"
                                    if "switchLevel" in str(dev['components'][0]['capabilities']):
                                        strCap = "switchLevel"
                                    vacLightStatus.append([random.random(),
                                                           lgt['deviceId'],
                                                           cap['status']['switch']['value'],
                                                           dev['label'],
                                                           strCap])
                
                #Sort by random number, then select top NumLightsOn in sorted list to turn on
                vacLightStatus.sort()
                for lgt in vacLightStatus:
                    try:
                        idx = vacLightStatus.index(lgt)
                        url = "https://api.smartthings.com/v1/devices/" + lgt[1] + "/commands"    #Vacation Lights
                        if idx < NumLightsOn:
                            #Ensure top of list devices turned on
                            if lgt[2] == "off":
                                if lgt[4] == "switchLevel":
                                    ret = requests.post(url, headers=headers, json=commandsLvl, timeout=5)
                                else:
                                    ret = requests.post(url, headers=headers, json=commandsOn, timeout=5)
                        else:
                            #Ensure rest of list devices turned off
                            if lgt[2] == "on":
                                ret = requests.post(url, headers=headers, json=commandsOff, timeout=5)
                    except:
                        pass    
            
            #All lights out
            if CurrentHour == VacationLightsEndHour:
                url = "https://api.smartthings.com/v1/devices/" + jsonVacLights['deviceGroupId'] + "/commands"    #Vacation Lights
                ret = requests.post(url, headers=headers, json=commandsOff, timeout=5)

    print ('Completed ', datetime.datetime.now(), 'Waiting...')


#Returns sunset time in local time for given latitude and longitude
def CalcSunsetTime(lat, lng):
    #Ref: https://gml.noaa.gov/grad/solcalc/solareqns.PDF
    today = datetime.datetime.now()
    
    #Number of days since Jan 01
    day_of_year = (today - datetime.datetime(today.year, 1, 1)).days + 1

    #Fractional year (γ) is calculated (radians)
    γ = (2*3.14159/365) * (day_of_year - 1)

    #Equation of time (in minutes)
    eqtime = 229.18*( 0.000075 + 0.001868*cos(γ) - 0.032077*sin(γ) - 0.014615*cos(2*γ) - 0.040849*sin(2*γ) )

    #Solar declination angle (radians)  +/- 23.5 degrees
    decl = 0.006918 - 0.399912*cos(γ) + 0.070257*sin(γ) - 0.006758*cos(2*γ) + 0.000907*sin(2*γ) - 0.002697*cos(3*γ) + 0.00148*sin(3*γ)  #radians

    #solar hour angle  (degrees)
    ha = acos(  cos(radians(90.833)) / (cos(radians(lat)) * cos(decl))  - (tan(radians(lat)) * tan(decl))  )
    ha = degrees(ha)

    #Sunrise/Sunset in UTC hours
    sunriseHour = (720 - 4*(lng + ha) - eqtime)/60
    sunsetHour = (720 - 4*(lng - ha) - eqtime)/60
    
    #UTC offset
    UTCoff = time.localtime().tm_gmtoff/3600
    
    #Sunrise/Sunset in local hours
    sunriseHour += UTCoff
    sunsetHour += UTCoff

    return (datetime.datetime.combine(today, datetime.datetime.min.time()) + datetime.timedelta(hours=sunsetHour))


#Checks if time is past sunset based on UseSunset option
def IsSunset():
    curDateTime = datetime.datetime.now()
    if UseSunset:
        return ( curDateTime >= CalcSunsetTime(Latitude, Longitude) )
    if not UseSunset:
        return ( curDateTime.hour >= SunsetHourByMonth[curDateTime.month-1])




#Main process:  Run vacation lights cycle every PollIntervalMinutes
while True:
    try:
        UpdateSmartThingsData()
    except:
        #print(sys.exc_info()[1])
        pass
    time.sleep(60 * PollIntervalMinutes)

quit()
