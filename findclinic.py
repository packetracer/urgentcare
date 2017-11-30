#IMPORT MODULES
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


#DEFINE CLINIC OBJECT ATTRIBUTES
class Clinic(object):
        def __init__(self, name, address, clinID, waitID):
                self.name = name
                self.address = address
                self.clinID = clinID
                self.waitID = waitID
    
#INITIALIZE LIST OF URGENT CARE CLINICS
clinicList = []
clinicList.append(Clinic('SANITIZED','1','2','3'))
clinicList.append(Clinic('SANITIZED','1','2','3'))
clinicList.append(Clinic("'SANITIZED','1','2','3'))

#GATHER ESTIMATED WAIT TIME BY REQUESTING WAIT ROOM INFORMATION FROM WEB PORTAL BASED ON CLINIC/WAITING ROOM ID 
def getWaitTime(clinID, waitID):
    #DEFINE URL FOR WAITING ROOM PORTAL AND PULL JSON DATA
    URL = "https://www.SANITIZED.URL/{}/list/wait_room".format(clinID)
    r = requests.get(URL)
    j = r.json()

    #INIT COUNTER
    i = 0
    
    #COUNT NUMBER OF PEOPLE IN LINE                         
    for item in j['lists'][waitID]['list']:
        i+=1
    
    #CALCULATE WAIT TIME BASED ON NUMBER OF PEOPLE IN LINE
    estWait = "approximately " + str(i*15) + " minutes."
    
    #IF NO ONE IN LINE, RETURN DEFAULT WAIT TIME
    if i == 0:
        estWait = "less than 5 minutes"
                         
    return estWait

#USE GOOGLE MAPS API FOR TRAVEL TIME DATA AND RETURN CLOSEST CLINIC TO DEVICE ADDRESS                         
def findClosestClinic(origin):
    #INIT DURATION AT ARBITRARY HIGH VALUE                     
    lowDuration = 9999
    #ITERATE THROUGH LIST OF CLINICS AND SORT THE LOWEST TRAVEL TIME
    for clinic in clinicList:
        #FORMAT DESTINATION ADDRESS FOR GOOGLE API CALL
        dest = clinic.address.replace(' ','+')
        gURL = "https://maps.googleapis.com/maps/api/distancematrix/json?units=imperial&origins="+origin+"&destinations="+dest+"&key=SANITIZEDKEY"
        g = requests.get(gURL)
        c = g.json()
        #STRIP OUT DISTANCE AND DURATION, TYPE TRAVEL TIME DURATION AS INTEGER
        distance = str(c['rows'][0]['elements'][0]['distance']['text'])+'les'
        duration = c['rows'][0]['elements'][0]['duration']['text']
        intDuration = int(duration.split(' ')[0])e

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

    if (deviceID == None) or (TOKEN == None):
        return ERROR(1)

    URL =  "https://api.amazonalexa.com/v1/devices/{}/settings/address".format(deviceID)
    HEADER = {'Accept': 'application/json',
             'Authorization': 'Bearer {}'.format(TOKEN)}
    
    r = requests.get(URL, headers=HEADER)
    statusCode = r.status_code
    print "Status: " + str(statusCode)
    if (statusCode == 403):
        return ERROR(1)
    if (statusCode == 200):
        b = r.json()
        if (b["addressLine1"] == None) or (b["city"] == None) or (b["stateOrRegion"] == None) or (b["postalCode"] == None):
            return ERROR(2)
        street = "{}".format(b["addressLine1"].encode("utf-8"))
        city = "{}".format(b["city"].encode("utf-8"))
        state = "{}".format(b["stateOrRegion"].encode("utf-8"))
        zipCode = "{}".format(b["postalCode"].encode("utf-8"))
        
        origin = (street+city+state+zipCode).replace(' ','+')
        closestClinic = []
        closestClinic = findClosestClinic(origin)
        
        response = '{"response": {"outputSpeech": {"type": "SSML","ssml": "<speak> The closest facility is'+closestClinic[0]+' which is '+closestClinic[1]+'away.  Your estimated travel time is '+closestClinic[2]+' minutes.  The estimated wait time is '+closestClinic[3]+'  </speak>"}}}'
        
        speech = json.loads(response)
        return speech
    return ERROR(0)
	
	
	
