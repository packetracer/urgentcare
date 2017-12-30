import json
import requests

#------DEFINE ERROR CASES-----#
def ERROR(case):
	if case == 0:
		ERR = '{"response": {"outputSpeech": {"type": "SSML","ssml": "<speak> Thank you for using LGH Urgent Care. Goodbye. </speak>"}}}'
		ERROR = json.loads(ERR)
		return ERROR
	
	if case == 1:
		ERR = '{"response": {"outputSpeech": {"type": "SSML","ssml": "<speak> Error, It does not appear that you have allowed this skill access to your devices location.  Please allow this skill to access the device address in the Alexa App by selecting the skill in the Your Skills Menu and pressing the manage permissions button.  Once a check mark is next to device address the skill will be ready for use. </speak>"}}}'
		ERROR = json.loads(ERR)
		return ERROR

	if case == 2:
		ERR = '{"response": {"outputSpeech": {"type": "SSML","ssml": "<speak> Im sorry, you have not configured an address in your alexa App, or it is missing your street address, city, state, or zip code.  Please add this information under your Alexa App settings. </speak>"}}}'
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
sSize = "600x600"
lSize = "1200x1200"
origin_ico = "icon:https://i.imgur.com/BCgMssM.png"
dest_ico = "icon:https://i.imgur.com/GatOmK8.png"
key = "AIzaSyCD71FwYGBlaY3oM2xlvfXBRkpKXENdiCM"
gkey = "AIzaSyCD71FwYGBlaY3oM2xlvfXBRkpKXENdiCM"
apptToken = "tEDPEpUNXgojpl+Km7Wq12ggJnDsm4zOVSRAgb0s8PAsSdcNVwIYq02P+BbovsHp3+Wug03sWwfTj3+bUf5HOw=="

postInfo = 'utf8=%E2%9C%93&authenticity_token=tEDPEpUNXgojpl%2BKm7Wq12ggJnDsm4zOVSRAgb0s8PAsSdcNVwIYq02P%2BBbovsHp3%2BWug03sWwfTj3%2BbUf5HOw%3D%3D&appointment%5Bhospital_id%5D="+clinicID+"&appointment%5Bprovider_id%5D="+providerID+"&appointment%5Bis_urgentcare%5D=true&appointment%5Breason_description%5D=Walk-In+Visit&appointment%5Bfirst_name%5D=Testing&appointment%5Blast_name%5D=Testing&appointment%5Bdays_from_today%5D=0&appointment%5Bapt_time%5D=2017-12-06T17%3A30%3A00.000-06%3A00&appointment%5Bemail%5D=amazonapp%40lgh.org&appointment%5Bphone_number%5D=337+366+4039&extra_fields%5B9364%5D%5Bvalue%5D=11%2F23%2F1984&extra_fields%5B9364%5D%5Bcustom_field_id%5D=9364&extra_fields%5B10074%5D%5Bvalue%5D=No&extra_fields%5B10074%5D%5Bcustom_field_id%5D=10074&extra_fields%5B10555%5D%5Bvalue%5D=No&extra_fields%5B10555%5D%5Bcustom_field_id%5D=10555&appointment%5Bcan_send_alert_sms%5D=0&appointment%5Bcan_send_alert_sms%5D=1&appointment%5Bpager_minutes%5D=20&appointment%5Bis_online%5D=true&appointment%5Btos%5D=0&appointment%5Btos%5D=1&commit=Confirm+me!")'

now = ""

#----If Alexa API returns forbidden- ask for user permission to access location ---# 
def permissionCard():
    response = '{"version": "1.0","response": {"outputSpeech": {"type":"PlainText","text":"Please grant the LGH Urgent Care Skill to access your devices location.  Please check your alexa App now in order to manage your permissions."},"card": {"type": "AskForPermissionsConsent","permissions": ["read::alexa:device:all:address"]}}}'
    return json.loads(response)
    
#-----Collects wait time for clinic-----#    
def getWaitTime(clinID, waitID):
    #initialize ClockwiseMD base URL with appropriate clinic ID
    #Read data from API and convert to JSON
    URL = 'https://www.clockwisemd.com/hospitals/{}/list/current_wait_range'.format(clinID)
    r = requests.get(URL)
    estWait =  r.content
    print "Estimated Wait:"
    print estWait
    
    if estWait == 'N/A':
        estWait = "currently unavailable."
    else:
        estWait = estWait + ' minutes. '
    return estWait

#-----Based on device location, return closest clinic and associated distance, travel time, and wait time-----#
def findClosestClinic(origin):
    #initialize distance
    lowDuration = 9999999
    #iterate through list of clinics to pull distance and travel time information from google
    for clinic in clinicList:
        dest = clinic.address.replace(' ','+')

        gURL = "https://maps.googleapis.com/maps/api/distancematrix/json?units=imperial&origins="+origin+"&destinations="+dest+"&key="+gkey
        g = requests.get(gURL)
        c = g.json()
        #collect distance metrics from Google API values
        distance = str(c['rows'][0]['elements'][0]['distance']['text'])+'les'
        duration = c['rows'][0]['elements'][0]['duration']['value']
        intDuration = int(duration/60)
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

#---Check for and return registered device address---
def getEchoAddress(req):
        b = req.json()
        #---Check for full address--#
        if (b["addressLine1"] == None) or (b["city"] == None) or (b["stateOrRegion"] == None) or (b["postalCode"] == None):
            return ERROR(2)
        
        #Define address based on API data
        street = "{}".format(b["addressLine1"].encode("utf-8"))
        city = "{}".format(b["city"].encode("utf-8"))
        state = "{}".format(b["stateOrRegion"].encode("utf-8"))
        zipCode = "{}".format(b["postalCode"].encode("utf-8"))

        print "Device Location: "
        print "Street: " + street
        print "City: " + city
        print "State: " + state
        print "Zip: " + zipCode

        origin = (street+' '+city+' '+state+' '+zipCode).replace(' ','+')
        return origin

#---Return closest clinic available to device---#
def locate(origin, isOpen):
    closestClinic = []
    closestClinic = findClosestClinic(origin)
        
    #Pack speech data, return to Echo
    if isOpen == True:
        print "CLOSEST CLINIC: " + closestClinic[0]
        print "DISTANCE:" + closestClinic[1]
        print "DURATION: "+ closestClinic[2] + " minutes"
        response = '{"version": "1.0","response": {"outputSpeech": {"type":"PlainText","text":"The closest facility is '+closestClinic[0]+' which is '+closestClinic[1]+' away.  Your estimated travel time is '+closestClinic[2]+' minutes.  The estimated wait time is '+closestClinic[3]+'"},"card": {"type": "Standard","title": "LGH Urgent Care", "text": "The closest facility is '+closestClinic[0]+' which is '+ closestClinic[1]+' away.  Your estimated travel time is '+closestClinic[2]+' minutes.  The estimated wait time is '+closestClinic[3]+'","image": {"smallImageUrl": "https://maps.googleapis.com/maps/api/staticmap?size='+sSize+'0&maptype=roadmap&markers='+origin_ico+'%7C'+origin+'&markers='+dest_ico+'%7C'+closestClinic[4]+'&key='+key+'","largeImageUrl": "https://maps.googleapis.com/maps/api/staticmap?size='+lSize+'0&maptype=roadmap&markers='+origin_ico+'%7C'+origin+'&markers='+dest_ico+'%7C'+closestClinic[4]+'&key='+key+'"}}}}'
        speech = json.loads(response)
        return speech
    else:
        #If facility is closed, return warning.  
        print "CLOSEST CLINIC: " + closestClinic[0]
        print "DISTANCE: "+ closestClinic[1]
        print "TRAVEL DURATION: " + closestClinic[2] + " minutes"
        response = '{"version": "1.0","response": {"outputSpeech": {"type":"PlainText","text":"The closest facility is '+closestClinic[0]+' which is '+closestClinic[1]+' away.  Your estimated travel time is '+closestClinic[2]+' minutes.  This facility is currently closed.  The hours are 8 AM until 7 PM Monday through Friday, 8 AM until 6 PM Saturdays and 8 AM until 4 PM Sundays"},"card": {"type": "Standard","title": "LGH Urgent Care", "text": "The closest facility is '+closestClinic[0]+' which is '+ closestClinic[1]+' away.  Your estimated travel time is '+closestClinic[2]+' minutes.  This facility is currently closed.","image": {"smallImageUrl": "https://maps.googleapis.com/maps/api/staticmap?size='+sSize+'0&maptype=roadmap&markers='+origin_ico+'%7C'+origin+'&markers='+dest_ico+'%7C'+closestClinic[4]+'&key='+key+'","largeImageUrl": "https://maps.googleapis.com/maps/api/staticmap?size='+lSize+'0&maptype=roadmap&markers='+origin_ico+'%7C'+origin+'&markers='+dest_ico+'%7C'+closestClinic[4]+'&key='+key+'"}}}}'
        speech = json.loads(response)
        return speech

#Peel off Skill Intent from Skill Request
def getIntent(event):
    return event['request']['intent']['name']

#Routine that lists all LGH Urgent Care facilities     
def listFac(origin, isOpen):
    clinicDist = []
    
    if isOpen == True:
        response = "The clinics in your area are; "
        for item in clinicList:
            dest = item.address.replace(' ','+')
            gURL = "https://maps.googleapis.com/maps/api/distancematrix/json?units=imperial&origins="+origin+"&destinations="+dest+"&key="+gkey
            g = requests.get(gURL)
            c = g.json()
            distance = str(c['rows'][0]['elements'][0]['distance']['text'])+'les'
            duration = c['rows'][0]['elements'][0]['duration']['text']
            
            response = response + ' ' + item.name + ' which is ' + distance + ' away and takes ' + duration + ' to get there has a waiting time of: ' + getWaitTime(item.clinID, item.waitID)
            
        speech = '{"version": "1.0","response": {"outputSpeech": {"type":"PlainText","text":"'+response+'.  To schedule an appointment, say, schedule an appointment"},"card": {"type": "Standard","title": "Lafayette General Urgent Care", "text": "Lafayette General Urgent Care Facilities: \\n Urgent Care of Carencro \\n Urgent Care of River Ranch \\n Urgent Care of Sugar Mill Pond ","image": {"smallImageUrl": "https://maps.googleapis.com/maps/api/staticmap?size='+sSize+'&markers='+origin_ico+'%7C'+origin+'&markers='+dest_ico+'%7Clabel:A%7C917+W+Gloria+Switch+Lafayette+LA&markers=icon:https://i.imgur.com/GatOmK8.png%7Clabel:B%7C%7C1216+Camellia+Blvd+Lafayette+LA%7C1216+Camellia+Blvd+Lafayette+LA%7C2810+Bonin+Rd+Youngsville&key='+key+'"}},"shouldEndSession":false}}'
        return json.loads(speech)
    else:
        response = "All Urgent Care Facilities are currently closed at this time: Lafayette General Urgent Care Facilities are:"
        for item in clinicList:
            dest = item.address.replace(' ','+')
            gURL = "https://maps.googleapis.com/maps/api/distancematrix/json?units=imperial&origins="+origin+"&destinations="+dest+"&key="+gkey
            g = requests.get(gURL)
            c = g.json()
            distance = str(c['rows'][0]['elements'][0]['distance']['text'])+'les'
            duration = c['rows'][0]['elements'][0]['duration']['text']

            response = response + ' ' + item.name + ' which is ' + distance + ' away and takes ' + duration + ' to get there. '
        speech = '{"version": "1.0","response": {"outputSpeech": {"type":"PlainText","text":"'+response+'"},"card": {"type": "Standard","title": "Lafayette General Urgent Care", "text": "Lafayette General Urgent Care Facilities: \\n Urgent Care of Carencro \\n Urgent Care of River Ranch \\n Urgent Care of Sugar Mill Pond ","image": {"smallImageUrl": "https://maps.googleapis.com/maps/api/staticmap?size='+sSize+'&markers='+origin_ico+'%7C'+origin+'&markers='+dest_ico+'%7Clabel:A%7C917+W+Gloria+Switch+Lafayette+LA&markers=icon:https://i.imgur.com/GatOmK8.png%7Clabel:B%7C%7C1216+Camellia+Blvd+Lafayette+LA%7C1216+Camellia+Blvd+Lafayette+LA%7C2810+Bonin+Rd+Youngsville&key='+key+'"}}}}'
        return json.loads(speech)
        
def waitTime(event, isOpen):
    response = "The current wait times are: "
    cardText = response
    
    if isOpen == True:
        if "ER_SUCCESS_MATCH" in str(event['request']['intent']['slots']['facility']):
            clinID = event['request']['intent']['slots']['facility']['resolutions']['resolutionsPerAuthority'][0]['values'][0]['value']['id']
            response = "The current wait time at "
            cardText = response
            if clinID == '1952':
                clinName = "Urgent Care of Carencro"
            if clinID == '1953':
                clinName = "Urgent Care of River Ranch"
            if clinID == '1954':
                clinName = "Urgent Care of Sugar Mill Pond"
            
            response = response + clinName + ' is ' + getWaitTime(clinID, "1")

            cardText = response

            speech = '{"version": "1.0","response": {"outputSpeech": {"type":"PlainText","text":"'+response+' You can say schedule an appointment if you would like to schedule an appointment at this time."},"card": {"type": "Simple","title": "Lafayette General Urgent Care", "content": "'+cardText+'"},"shouldEndSession":false}}'
            return json.loads(speech)
            
        for item in clinicList:
            waitTime = getWaitTime(item.clinID, item.waitID)
            response = response + ' ' + item.name + ' ' + waitTime + ', ... '
            cardText = cardText + '\\n' + item.name + ' ' + waitTime
        speech = '{"version": "1.0","response": {"outputSpeech": {"type":"PlainText","text":"'+response+' You can say schedule an appointment if you would like to schedule an appointment at this time."},"card": {"type": "Simple","title": "Lafayette General Urgent Care", "content": "'+cardText+'"},"shouldEndSession":false}}'
        return json.loads(speech)
        
    if isOpen == False:
        response = "I'm sorry, the facilities are currently closed.  Wait times are not available"
        speech = '{"version": "1.0","response": {"outputSpeech": {"type":"PlainText","text":"'+response+'"},"card": {"type": "Simple","title": "Lafayette General Urgent Care", "content": "'+cardText+'"}}}'
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

def welcomePrompt():
    print "Welcome Prompt Initiated"
    response = "Welcome to the Lafayette General Urgent Care Skill.  How may I help you today?  You can say Help for more information."
    speech = '{"version": "1.0","response": {"outputSpeech": {"type":"PlainText","text":"' + response + '"},"shouldEndSession":false}}'
    return json.loads(speech)        
    
def helpIntent():
    print "Help Intent Initiated"
    response = "The LGH Urgent Care Skill can provide you information about our Urgent Care facilities in Acaydiana.  You can schedule an appointment by saying Alexa, ask Urgent Care to schedule an appointment.  You can also ask Urgent Care for current wait times, to list all Urgent Care facilities, hours of operation, or even to locate the closest clinic.  To use the skill, simply say Alexa, ask Urgent Care"
    speech = '{"version": "1.0","response": {"outputSpeech": {"type":"PlainText","text":"' + response + '"},"shouldEndSession":false}}'
    return json.loads(speech)
    
def getNextAppt(event):
    print "Getting next avilable appt time"
    print str(event['request']['intent']['slots']['facility'])
    print "Facility confirmed? "
    print str(event['request']['intent']['slots']['facility']['confirmationStatus'])
    if 'ER_SUCCESS_MATCH' not in str(event['request']['intent']['slots']['facility']):
        sched = []
        i = 0
        for item in clinicList:
            URL = "https://www.clockwisemd.com/hospitals/{}/appointments/available_times?page_type=urgent_care_online_time_by_reason&version=v1&reason_description=Walk-In%20Visit".format(item.clinID)
            r = requests.get(URL)
            j = r.json()
            if 'display_time' in str(j):
                nextSlot = j['0'][0]['display_time']
                print j['0'][0]
            else:
                nextSlot =  "No appointment times are currently available."
                i+=1
            sched.append(item.name)
            sched.append(str(nextSlot))
    
        if i == 3:     
            speech = '{"version": "1.0","response": {"outputSpeech": {"type":"PlainText","text":"Sorry, there are no appointments available right now."},"shouldEndSession":true}}'
            print speech
            return json.loads(speech)
        response = ""
        for item in sched:
            response = response + ' ' + item +', '
        print response
        speech = '{"version": "1.0","response": {"outputSpeech": {"type":"PlainText","text":"  The next available appointment times are: ' + response + '.  You can say schedule an appointment in order to get in line"},"shouldEndSession":false}}'
        return json.loads(speech)
    else:
        clinID = event['request']['intent']['slots']['facility']['resolutions']['resolutionsPerAuthority'][0]['values'][0]['value']['id']
        URL = "https://www.clockwisemd.com/hospitals/{}/appointments/available_times?page_type=urgent_care_online_time_by_reason&version=v1&reason_description=Walk-In%20Visit".format(clinID)
        r = requests.get(URL)
        j = r.json()
        if 'display_time' in str(j):
            nextSlot = j['0'][0]['display_time']
            print j['0'][0]
            speech = '{"version": "1.0","response": {"outputSpeech": {"type":"PlainText","text":"The next available appointment time is at: '+nextSlot+'.  You can say schedule an appointment in order to get in line."},"shouldEndSession":false}}'
            return json.loads(speech)
        else:
            nextSlot =  "No appointment times are currently available."
            speech = '{"version": "1.0","response": {"outputSpeech": {"type":"PlainText","text":"'+nextSlot+'"},"shouldEndSession":true}}'
            return json.loads(speech)
        

def getApptTime(clinID):
    print "Getting appointment times..."
    URL = "https://www.clockwisemd.com/hospitals/{}/appointments/available_times?page_type=urgent_care_online_time_by_reason&version=v1&reason_description=Walk-In%20Visit".format(clinID)
    r = requests.get(URL)
    j = r.json()
    appTime = []
    print str(j)
    if 'display_time' in str(j):
        appTime.append(j['0'][0]['time'])
        appTime.append(j['0'][0]['display_time'])
        return appTime
    else:
        appTime.append("No appointments currently available.")
        appTime.append("No appointments currently available.")
        return appTime

def build_PlainSpeech(body):
    speech = {}
    speech['type'] = 'PlainText'
    speech['text'] = body
    return speech

def build_response(message, session_attributes={}):
        response = {}
        response['version'] = '1.0'
        response['response'] = message
        return response

def conversation(title, body, session_attributes):
    speechlet = {}
    speechlet['outputSpeech'] = build_PlainSpeech(body)
    speechlet['shouldEndSession'] = False
    return build_response(speechlet, session_attributes=session_attributes)
    
def statement(title, body):
    speechlet = {}
    speechlet['outputSpeech'] = build_PlainSpeech(body)
    speechlet['card'] = build_SimpleCard(title, body)
    speechlet['shouldEndSession'] = True
    return build_response(speechlet)

def continue_dialog():
        message = {}
        message['shouldEndSession'] = False
        message['directives'] = [{'type': 'Dialog.Delegate'}]
        return build_response(message)
    
def scheduleAppt(event, isOpen,now):
    print "Starting appointment scheduling"
    if isOpen == False:
        if now <= 6:
            speech = '{"version": "1.0", "response": {"outputSpeech": {"type":"PlainText","text":" Sorry all facilities are currently closed, please try again tomorrow.  Goodbye"}}}'
            return json.loads(speech) 
        
    dialog_state = event['request']['dialogState']

    if dialog_state in ("STARTED", "IN_PROGRESS"):
        return continue_dialog()

    elif dialog_state == "COMPLETED":
        print "Dialogue check complete, building session attributes"
        
        firstName = event['request']['intent']['slots']['firstName']['value']
        lastName = event['request']['intent']['slots']['lastName']['value']
        phoneNumber =  event['request']['intent']['slots']['phoneNumber']['value']
        facilityID = event['request']['intent']['slots']['facility']['resolutions']['resolutionsPerAuthority'][0]['values'][0]['value']['id']
        
        DOB = event['request']['intent']['slots']['birthday']['value']
        bYear = DOB[:4]
        bMonth = DOB[-2:]
        bDay = DOB[-5:]
        fDOB = bDay+'%2F'+bMonth+'%2F'+bYear
        
        cigna = event['request']['intent']['slots']['cigna']['resolutions']['resolutionsPerAuthority'][0]['values'][0]['value']['id']
        bayou = event['request']['intent']['slots']['bayou']['resolutions']['resolutionsPerAuthority'][0]['values'][0]['value']['id']

        phone_len = len(phoneNumber)
        if phone_len == 7:
            area_code = "337"
            phone = phoneNumber
        else:
            area_code = phoneNumber[:3]
            phone = phoneNumber[-7:]
        phone1 = phone[:3]
        phone2 = phone[-4:]
        formattedPhone = area_code+'+'+phone1+'+'+phone2
        apptTime = getApptTime(facilityID)
    
    if apptTime[1] == "No appointments currently available.":
        speech = '{"version": "1.0", "response": {"outputSpeech": {"type":"PlainText","text":" Sorry there are no appointment times available.  If this is an emergency please go to your closest Emergency Facility.  Otherwise, please try again tomorrow.  Goodbye" }, "shouldEndSession":true},"sessionAttributes": {"firstName" : "'+firstName+'", "lastName": "'+lastName+'", "phoneNumber": "'+formattedPhone+'","facilityID": "'+facilityID+'","displayTime":"'+apptTime[1]+'","nextTime":"'+apptTime[0]+'","cigna":"'+cigna+'","bayou":"'+bayou+'","DOB":"'+fDOB+'"}}'
        return json.loads(speech) 
    else:    
      speech = '{"version": "1.0", "response": {"outputSpeech": {"type":"PlainText","text":" The next appointment time is '+apptTime[1]+'. Would you like to get in line?" }, "shouldEndSession":false},"sessionAttributes": {"firstName" : "'+firstName+'", "lastName": "'+lastName+'", "phoneNumber": "'+formattedPhone+'","facilityID": "'+facilityID+'","displayTime":"'+apptTime[1]+'","nextTime":"'+apptTime[0]+'","cigna":"'+cigna+'","bayou":"'+bayou+'","DOB":"'+fDOB+'"}}'
      return json.loads(speech) 
    
def confirmAppt(event):
    print "Attempting to schedule"
    session_attributes = {}
    session_attributes = event['session']['attributes']
    
    displayTime = session_attributes['displayTime']
    firstName = session_attributes['firstName']
    lastName = session_attributes['lastName']
    phoneNumber = session_attributes['phoneNumber']
    nextTime = session_attributes['nextTime']
    facilityID = session_attributes['facilityID']
    cigna = session_attributes['cigna']
    bayou = session_attributes['bayou']
    
    if facilityID == "1952":
        providerID = "4814"
    if facilityID == "1953":
        providerID = "4815"
    if facilityID == "1954":
        providerID = "4816"
    
    URL = "https://www.clockwisemd.com/hospitals/{}/appointments/create_online".format(facilityID)
    postInfo = 'utf8=%E2%9C%93&authenticity_token=tEDPEpUNXgojpl%2BKm7Wq12ggJnDsm4zOVSRAgb0s8PAsSdcNVwIYq02P%2BBbovsHp3%2BWug03sWwfTj3%2BbUf5HOw%3D%3D&appointment%5Bhospital_id%5D='+facilityID+'&appointment%5Bprovider_id%5D='+providerID+'&appointment%5Bis_urgentcare%5D=true&appointment%5Breason_description%5D=Walk-In+Visit&appointment%5Bfirst_name%5D='+firstName+'&appointment%5Blast_name%5D='+lastName+'&appointment%5Bdays_from_today%5D=0&appointment%5Bapt_time%5D='+nextTime+'&appointment%5Bemail%5D=amazonapp%40lgh.org&appointment%5Bphone_number%5D='+phoneNumber+'&extra_fields%5B9364%5D%5Bvalue%5D=11%2F23%2F1984&extra_fields%5B9364%5D%5Bcustom_field_id%5D=9364&extra_fields%5B10074%5D%5Bvalue%5D='+cigna+'&extra_fields%5B10074%5D%5Bcustom_field_id%5D=10074&extra_fields%5B10555%5D%5Bvalue%5D='+bayou+'&extra_fields%5B10555%5D%5Bcustom_field_id%5D=10555&appointment%5Bcan_send_alert_sms%5D=0&appointment%5Bcan_send_alert_sms%5D=1&appointment%5Bpager_minutes%5D=20&appointment%5Bis_online%5D=true&appointment%5Btos%5D=0&appointment%5Btos%5D=1&commit=Confirm+me!'
    
    print "POST INFO:"
    print postInfo
    
    req = requests.post(URL, data=postInfo)

    print req.status_code
    if req.status_code == 200:
        phoneNumber = phoneNumber.replace('+','')
        speech = '{"response": {"outputSpeech": {"type":"SSML","ssml":"<speak> I have scheduled an appointment at '+displayTime+' for '+firstName+' '+lastName+'.  I have sent a text message to <say-as interpret-as=\'telephone\'>'+phoneNumber+'</say-as>.</speak>"}}}'
        return json.loads(speech) 
    
    if req.status_code == 422:
        response = "I'm sorry, that appointment was just taken.  Please try again."
        speech = '{"version": "1.0","response": {"outputSpeech": {"type":"PlainText","text":"' + response + '"},"shouldEndSession":true}}'
        return speech
        
    if req.status_code == 400:
        response = "I'm sorry, an error occured while scheduling your appointment.  Please try again."
        speech = '{"version": "1.0","response": {"outputSpeech": {"type":"PlainText","text":"' + response + '"},"shouldEndSession":true}}'
        return speech

def getReqTime(event):
    now = event['request']['timestamp']
    now = now[-9:]
    now = now[:2]
    print "Current hour UTC: " + now
    return now
    
def checkIfOpen(now):
    intNow = int(now)
    isOpen = False
    print str(intNow)
    if (intNow >= 13 and intNow <= 24):
        print "Facilities are open"
        isOpen = True
    elif (intNow < 1):
        print "Facilities are open"
        isOpen = True
    else:
        print "Facilities are closed"
    return isOpen
        
def getHours(isOpen):
    print "Getting hours"
    if isOpen == True:
        response = "The Urgent Care facilities are currently open.  "
    if isOpen == False:
        response = "The Urgent Care facilities are currently closed.  "
    response = response + 'The hours are 8 AM until 7 PM Monday through Friday, 8 AM until 6 PM Saturdays and 8 AM until 4 PM Sundays'
    speech = '{"response": {"outputSpeech": {"type":"SSML","ssml":"<speak> '+response+'.</speak>"}}}'
    return json.loads(speech)
    
def getPhone(event):
    print "Getting phone numbers"
    dialog_state = event['request']['dialogState']

    if dialog_state in ("STARTED", "IN_PROGRESS"):
        return continue_dialog()

    elif dialog_state == "COMPLETED":
        facilityID = event['request']['intent']['slots']['facility']['resolutions']['resolutionsPerAuthority'][0]['values'][0]['value']['id']
        if facilityID == '1952':
            facilityName = "Urgent Care of Carencro"
            phoneNumber = '337-886-6455'
        if facilityID == '1953':
            facilityName = "Urgent Care of River Ranch"
            phoneNumber = '337-769-0069'
        if facilityID == '1954':
            facilityName = "Urgent Care of Sugar Mill Pond"
            phoneNumber = '337-857-5765'
    
        response = 'The phone number for ' + facilityName + ' is '
        speech = '{"response": {"outputSpeech": {"type":"SSML","ssml":"<speak> '+response+' <say-as interpret-as=\'telephone\'>'+phoneNumber+'</say-as>.  I have sent this phone number to your Alexa App under the Home Screen</speak>"},"card": {"type": "Standard","title": "Phone Number", "text": "'+facilityName+'\\n'+phoneNumber+'"}}}'
        return json.loads(speech)

def quitSkill():
    print "Quitting skill..."
    speech = '{"response": {"outputSpeech": {"type":"SSML","ssml":"<speak>Thank you for using Lafayette General Urgent Care, goodbye.</speak>"}}}'
    return json.loads(speech)

#Main driver function for skill
def lambda_handler(event, context):
    print event
    now = getReqTime(event)
    
    isOpen = checkIfOpen(now)
    
    if 'intent' not in str(event):
        return welcomePrompt()

    intent = getIntent(event)
    print "Intent: " + intent
    
    if intent == 'getPhone':
        return getPhone(event)
    
    if intent == 'getHours':
        return getHours(isOpen)
        
    if intent == "denyAppt":
        return welcomePrompt()
    
    if intent == "confirmAppt":
        return confirmAppt(event)
    
    if intent == "getNextAppt":
        return getNextAppt(event)
    
    if intent == "scheduleAppt":
        return scheduleAppt(event, isOpen,now)

    if intent == "AMAZON.HelpIntent":
        return helpIntent()        

    if intent == "AMAZON.StopIntent":
        return quitSkill()        

    if intent == "AMAZON.CancelIntent":
        return quitSkill()        

    #Return locations and wait times
    if intent == "waitTime":
        print "Wait Times Initiated"
        return waitTime(event, isOpen)

    #Collect device information
    req = getDevice(event)
    print "Status Code: " + str(req.status_code)
    if event['session']['user']['userId'] == 'debug' or event['session']['user']['userId'] == 'debugclose':
        req.status_code = 200
        
    #If Forbidden, ask for permission with Alexa Consent Card
    if (req.status_code == 403):
        print "Prompting Permission Card"
        return permissionCard()
    
    #If successful, use intent to perform desired skill function
    if (req.status_code == 200):
        #Determine device address
        if event['session']['user']['userId'] == 'debug':
            origin = '1444+S.+Alameda+Street+Los+Angeles+California+90021'
        elif event['session']['user']['userId'] == 'debugclose':
            origin = '113+KELLOGG+AVE+LAFAYETTE+LA+70506'
        else:
            origin = getEchoAddress(req)
        if origin == ERROR(2):
            return origin
            
        #Calculate the closest clinic and return speech and card for travel/wait metrics 
        if intent == "locate":
            print "Locate Device Initiated"
            return locate(origin, isOpen)
            
        #List the urgent care facilities and return speech and card of locations
        if intent == "listFac":
            print "List Facilities Initiated"
            return listFac(origin, isOpen)
        

            
    #if no function determined, return generic error    
    return ERROR(0)
