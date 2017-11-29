import json
import requests

#-----------#
ERR = '{"response": {"outputSpeech": {"type": "SSML","ssml": "<speak> Error, the address is not properly configured on your device.  Please configure a device address inside your Alexa App.  You cunt. </speak>"}}}'
ERROR = json.loads(ERR)
#-----------#

class Clinic(object):
        def __init__(self, name, address, clinID, waitID):
                self.name = name
                self.address = address
                self.clinID = clinID
                self.waitID = waitID
    
clinicList = []
clinicList.append(Clinic("Clinic 1", "123 North South St., Derpville, LA 70566", "2", "0"))
clinicList.append(Clinic("Clinic 2", "321 South North St., Derpville, LA 70566", "3", "1"))
clinicList.append(Clinic("Clinic 3", "231 East West St., Derpville, LA 70566", "4", "2"))

def getWaitTime(clinID, waitID):
    URL = "https://www.waitingroomwebsite.com/hospitals/{}/list/wait_room".format(clinID)
    r = requests.get(URL)
    j = r.json()
    i = 0
    for item in j['lists'][waitID]['list']:
        i+=1
    estWait = "approximately " + str(i*15) + " minutes."
    if i == 0:
        estWait = "less than 5 minutes"
    return estWait

def findClosestClinic(origin):
    lowDuration = 9999
    for clinic in clinicList:
        dest = clinic.address.replace(' ','+')
        gURL = "https://maps.googleapis.com/maps/api/distancematrix/json?units=imperial&origins="+origin+"&destinations="+dest+"&key=YOURAPIKEY"
        g = requests.get(gURL)
        c = g.json()

        distance = str(c['rows'][0]['elements'][0]['distance']['text'])+'les'
        duration = c['rows'][0]['elements'][0]['duration']['text']
        intDuration = int(duration.split(' ')[0])

        if intDuration < lowDuration:
            lowDistance = distance
            lowDuration = intDuration
            lowName = clinic.name
            clinID = clinic.clinID
            waitID = clinic.waitID

    estWait = getWaitTime(clinID, waitID)
    closestClinic = []
    closestClinic.append(lowName)
    closestClinic.append(lowDistance)
    closestClinic.append(str(lowDuration))
    closestClinic.append(estWait)
    
    return closestClinic
      
def lambda_handler(event, context):
    # TODO implement

    deviceID = event['context']['System']['device']['deviceId']
    TOKEN = event['context']['System']['apiAccessToken']
    print deviceID
    print TOKEN
    URL =  "https://api.amazonalexa.com/v1/devices/{}/settings/address".format(deviceID)
    HEADER = {'Accept': 'application/json',
             'Authorization': 'Bearer {}'.format(TOKEN)}
    
    r = requests.get(URL, headers=HEADER)
    statusCode = r.status_code
    if (statusCode == 200):
        b = r.json()
        print str(b)
        if (b["addressLine1"] == None) or (b["city"] == None) or (b["stateOrRegion"] == None) or (b["postalCode"] == None):
            return ERROR
        street = "{}".format(b["addressLine1"].encode("utf-8"))
        city = "{}".format(b["city"].encode("utf-8"))
        state = "{}".format(b["stateOrRegion"].encode("utf-8"))
        zipCode = "{}".format(b["postalCode"].encode("utf-8"))
        
        #origin = get_coordinates(b)
        origin = (street+city+state+zipCode).replace(' ','+')
        closestClinic = []
        closestClinic = findClosestClinic(origin)
        
        response = '{"response": {"outputSpeech": {"type": "SSML","ssml": "<speak> The closest facility is'+closestClinic[0]+' which is '+closestClinic[1]+'away.  Your estimated travel time is '+closestClinic[2]+' minutes.  The estimated wait time is '+closestClinic[3]+'  </speak>"}}}'
        
        speech = json.loads(response)
        return speech
    return ERROR
