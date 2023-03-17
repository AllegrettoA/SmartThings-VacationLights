# SmartThings-VacationLights
Simulate home lighting by randomly turning on &amp; off lights

### Background
This is a Python3 script which replaces the functionality of Groovy smartapp Vacation Lighting Director ([vacation-lighting-director.groovy](https://github.com/SmartThingsCommunity/SmartThingsPublic/tree/master/smartapps/tslagle13/vacation-lighting-director.src)).

The new SmartThings platform requires smartapps be run outside the SmartThings platform such as AWS or Node.js.  In my opinion, this is exceedingly complex compared to the original groovy-based system.  This Python script needs only a simple platform such as a Raspberry PI, Diskstation, etc.  It runs in a periodic loop and does not create any event subscriptions/handlers.  Hopefully someone can replicate this functionality in a Lua-based driver that runs on the hub.

### Setup
Configuration settings are provided by editing the Python script (VacationLights.py) using a text editor or Python editor such as Thonny.

1. **Personal Access Token**.  Since the script runs external to SmartThings, a Personal Access Token is required.  This access token enables the Python app (or any other app) to have access to your SmartThings devices and eliminates the need for login credentials.  You can generate a Personal Access Token by logging on to your SmartTHings account and navigating to https://account.smartthings.com/tokens.  This access token requires **permissions for devices and location mode.**  Edit the Python script and add your access token to the AccessToken variable.

2. **Hub Location ID**.  Obtain your location ID by logging into [https://my.smartthings.com](https://my.smartthings.com).  You will find your location ID in the url, for example: https://my.smartthings.com/location/ **xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx**.

3. **Vacation Lights Group Name**.  The SmartThings app now allows you to create lighting groups.  In the app, click Devices, click "+" and select "Create lighting group".  Name your new lighting group "**Vacation Lights**" and select light devices to add to the group.  The Python app will run only if it can find a lighing group named "Vacation Lights".

4. **NumLightsOn**.  This setting specifies the number of lights that will be turned on randomly.

5. **IntervalMinutes**.  This setting specifies the number of minutes between switching lights on/off.

6. **Sunset**.  Set the Latitude and Longitude for your location.  These ensure sunset is calculated accurately for your location.  Also set **UseSunset = True** to use sunset time to begin turning on vacation lights.

7. **SunsetHourByMonth**.  If you prefer to specify fixed start times, set **UseSunset = False**.  Lighting start hour will then be selected by a list of start time hours by month in **SunsetHourByMonth[]**.  You can edit this list to use the same start hour for the entire year if desired.  The initial list contains start hours which approximate sunrise for each month of the year.

8. **VacationLightsEndHour**.  THis setting specifies the hour that vacation lights turn off.


