import json
import requests

#------DEFINE ERROR CASES-----#
def ERROR(case):
	if case == 0:
		ERR = '{"response": {"outputSpeech": {"type": "SSML","ssml": "<speak> There was an error processing your requests please try again. </speak>"}}}'
		ERROR = json.loads(ERR)
		return ERROR
	
	if case == 1:
		ERR = '{"response": {"outputSpeech": {"type": "SSML","ssml": "<speak> Error, It does not appear that you have allowed this skill access to your devices location.  Please allow this skill to access the device address in the Alexa App by selecting the skill in the Your Skills Menu and pressing the manage permissions button.  Once a check mark is next to device address the skill will be ready for use. </speak>"}}}'
		ERROR = json.loads(ERR)
		return ERROR

	if case == 2:
		ERR = '{"response": {"outputSpeech": {"type": "SSML","ssml": "<speak> Error, improper or incomplete address information.  Please properly register an address on your device in the Alexa App.  </speak>"}}}'
		ERROR = json.loads(ERR)
		return ERROR
#------END DEFINITION CASES-----#

#------Define Clinic Object-----#
class Clinic(object):
        def __init__(self, name, address, clinID, waitID):
                self.name = name
                self.address = address
                self.clinID = clinID
                self.waitID = waitID

#LOAD GLOBAL CLINIC LIST WITH DATA    
clinicList = []
clinicList.append(Clinic("Urgent Care of Carencro", "917 W Gloria Switch Rd, Lafayette, LA 70507", "1952", "4860"))
clinicList.append(Clinic("Urgent Care of River Ranch", "1216 Camellia Blvd, Lafayette, LA 70508", "1953", "4861"))
clinicList.append(Clinic("Urgent Care of Sugar Mill Pond", "2810 Bonin Rd, Youngsville, LA 70592", "1954", "4862"))

#-----End Clinic Definitions-----#
#-----BEGIN GLOBAL VARS-----#
sSize = "600x600"
lSize = "1200x1200"
origin_ico = "icon:https://i.imgur.com/BCgMssM.png"
dest_ico = "icon:https://i.imgur.com/GatOmK8.png"
key = "SANITIZED"
gkey = "SANITIZED"
#-----END GLOBALS-----#
#----If Alexa API returns forbidden- ask for user permission to access location ---# 
def permissionCard():
    response = '{"version": "1.0","response": {"outputSpeech": {"type":"PlainText","text":"Please grant the LGH Urgent Care Skill to access your devices location.  Please check your alexa App now in order to manage your permissions."},"card": {"type": "AskForPermissionsConsent","permissions": ["read::alexa:device:all:address"]}}}'
    return json.loads(response)
    
#-----Collects wait time for clinic-----#    
def getWaitTime(clinID, waitID):
    #initialize ClockwiseMD base URL with appropriate clinic ID
    URL = "https://www.clockwisemd.com/hospitals/{}/list/wait_room".format(clinID)
    #Read data from API and convert to JSON
    r = requests.get(URL)
    j = r.json()
    #init counter variable
    i = 0
    #Count number of people in waiting list
    for item in j['lists'][waitID]['list']:
        i+=1
    #Based on number of people listed, multiply by 15 and return estimated wait time
    estWait = "approximately " + str(i*15) + " minutes."
    #if no one in line, force return to set minimum wait time
    if i == 0:
        estWait = "less than 5 minutes."
    return estWait

#-----Based on device location, return closest clinic and associated distance, travel time, and wait time-----#
def findClosestClinic(origin):
    #initialize distance
    lowDuration = 99999
    #iterate through list of clinics to pull distance and travel time information from google
    for clinic in clinicList:
        dest = clinic.address.replace(' ','+')
        gURL = "https://maps.googleapis.com/maps/api/distancematrix/json?units=imperial&origins="+origin+"&destinations="+dest+"&key="+gkey
        print gURL
        g = requests.get(gURL)
        c = g.json()
        #collect distance metrics from Google API values
        distance = str(c['rows'][0]['elements'][0]['distance']['text'])+'les'
        duration = c['rows'][0]['elements'][0]['duration']['text']
        intDuration = int(duration.split(' ')[0])
        #Sort data, take lowest travel time as "winning" clinic
        if intDuration < lowDuration:
            lowDistance = distance
            lowDuration = intDuration
            lowName = clinic.name
            clinID = clinic.clinID
            waitID = clinic.waitID
            lowDest = dest
            
    #Gather wait time based on closest clinic            
    estWait = getWaitTime(clinID, waitID)
    #init list for returning packed data for closest clinic, return said list
    closestClinic = []
    closestClinic.append(lowName)
    closestClinic.append(lowDistance)
    closestClinic.append(str(lowDuration))
    closestClinic.append(estWait)
    closestClinic.append(lowDest)
    
    return closestClinic
    
def getEchoAddress(req):
        b = req.json()
        if (b["addressLine1"] == None) or (b["city"] == None) or (b["stateOrRegion"] == None) or (b["postalCode"] == None):
            return ERROR(2)
        
        #Define address based on API data
        street = "{}".format(b["addressLine1"].encode("utf-8"))
        city = "{}".format(b["city"].encode("utf-8"))
        state = "{}".format(b["stateOrRegion"].encode("utf-8"))
        zipCode = "{}".format(b["postalCode"].encode("utf-8"))
        
        origin = (street+city+' '+state+' '+zipCode).replace(' ','+')
        return origin

def locate(origin):
    closestClinic = []
    closestClinic = findClosestClinic(origin)
        
    #Pack speech data, return to Echo
    response = '{"version": "1.0","response": {"outputSpeech": {"type":"PlainText","text":"The closest facility is '+closestClinic[0]+' which is '+closestClinic[1]+' away.  Your estimated travel time is '+closestClinic[2]+' minutes.  The estimated wait time is '+closestClinic[3]+'"},"card": {"type": "Standard","title": "LGH Urgent Care", "text": "The closest facility is '+closestClinic[0]+' which is '+ closestClinic[1]+' away.  Your estimated travel time is '+closestClinic[2]+' minutes.  The estimated wait time is '+closestClinic[3]+'","image": {"smallImageUrl": "https://maps.googleapis.com/maps/api/staticmap?size='+sSize+'0&maptype=roadmap&markers='+origin_ico+'%7C'+origin+'&markers='+dest_ico+'%7C'+closestClinic[4]+'&key='+key+'","largeImageUrl": "https://maps.googleapis.com/maps/api/staticmap?size='+lSize+'0&maptype=roadmap&markers='+origin_ico+'%7C'+origin+'&markers='+dest_ico+'%7C'+closestClinic[4]+'&key='+key+'"}}}}'
    speech = json.loads(response)
    return speech

#Peel off Skill Intent from Skill Request
def getIntent(event):
    return event['request']['intent']['name']

#Routine that lists all LGH Urgent Care facilities     
def listFac(origin):
    response = "The clinics in your area are; "
    for item in clinicList:
        response = response + item.name + ', '

    speech = '{"version": "1.0","response": {"outputSpeech": {"type":"PlainText","text":"'+response+'"},"card": {"type": "Standard","title": "Lafayette General Urgent Care", "text": "Lafayette General Urgent Care Facilities: \\n Urgent Care of Carencro \\n Urgent Care of River Ranch \\n Urgent Care of Sugar Mill Pond ","image": {"smallImageUrl": "https://maps.googleapis.com/maps/api/staticmap?size='+sSize+'&markers='+origin_ico+'%7C'+origin+'&markers='+dest_ico+'%7Clabel:A%7C917+W+Gloria+Switch+Lafayette+LA&markers=icon:https://i.imgur.com/GatOmK8.png%7Clabel:B%7C%7C1216+Camellia+Blvd+Lafayette+LA%7C1216+Camellia+Blvd+Lafayette+LA%7C2810+Bonin+Rd+Youngsville&key='+key+'"}}}}'
    return json.loads(speech)

def waitTime():
    response = "The current wait times are: "
    cardText = response

    for item in clinicList:
        response = response + ' ' + item.name + ' ' + getWaitTime(item.clinID, item.waitID) + ', ... '
        cardText = cardText + '\\n' + item.name + ' ' + getWaitTime(item.clinID, item.waitID)

    speech = '{"version": "1.0","response": {"outputSpeech": {"type":"PlainText","text":"'+response+'"},"card": {"type": "Simple","title": "Lafayette General Urgent Care", "content": "'+cardText+'"}}}'
    print speech
    return json.loads(speech)


#Routing for discovering Echo Device information
def getDevice(event):
    #Determine deviceID and API Authorization Token sent from Echo's Skill Request
    deviceID = event['context']['System']['device']['deviceId']
    TOKEN = event['context']['System']['apiAccessToken']
    
    #Pull data from Amazon API for location services
    URL =  "https://api.amazonalexa.com/v1/devices/{}/settings/address".format(deviceID)
    HEADER = {'Accept': 'application/json',
             'Authorization': 'Bearer {}'.format(TOKEN)}
    
    r = requests.get(URL, headers=HEADER)
    return r

#Main driver function for skill
def lambda_handler(event, context):
    #Collect intent
    intent = getIntent(event)
    #Collect device information
    req = getDevice(event)
    
    #Check status code to determine exception handling
    #If Forbidden, ask for permission with Alexa Consent Card
    if (req.status_code == 403):
        return permissionCard()
    
    #If successful, use intent to perform desired skill function
    if (req.status_code == 200):
        #Determine device address
        origin = getEchoAddress(req)
        #Calculate the closest clinic and return speech and card for travel/wait metrics 
        if intent == "locate":
            return locate(origin)
        #List the urgent care facilities and return speech and card of locations
        if intent == "listFac":
            return listFac(origin)
        #Return locations and wait times
        if intent == "waitTime":
            return waitTime()
    #if no function determined, return generic error    
    return ERROR(0)
