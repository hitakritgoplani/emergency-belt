from boltiot import Bolt, Sms
from twilio.rest import Client
from firebase import Firebase
import json, time, conf, requests, geocoder

firebase = Firebase(conf.firebaseConfig)
db = firebase.database()

mybolt = Bolt(conf.API_KEY, conf.DEVICE_ID)
sms = Sms(conf.SID, conf.AUTH_TOKEN, conf.TO_NUMBER, conf.FROM_NUMBER)
client = Client(conf.SID, conf.AUTH_TOKEN)

def get_sensor_value_from_pin(pin):
	try:
		response = mybolt.digitalRead(pin)
		data = json.loads(response)
		if data['success'] == 1:
			print("Request not successful")
			return -999
		return data['value']
	except Exception as e:
		print("Error")
		return -1

def send_live_location():
	print("Sending Live Location Via SMS...")
	location = db.child("location").get().val()
	lat = location["lat"]
	long = location["long"]
	loc = geocoder.bing([lat, long], key=conf.LOCATION_API_KEY, method='reverse')
	address = str(loc.address)
	response = sms.send_sms(f"Message from Emergency belt, live location is {address}")
	print("Location sent")

def make_emergency_call():
	print("Calling Emergency Contact...")
	call = client.calls.create(
	                        twiml='<Response><Say>Call from Emergency Belt, There is an emergency</Say></Response>',
	                        to=conf.TO_NUMBER,
	                        from_=conf.FROM_NUMBER
	                    )
	print("Called emergency contact")

while True:
	response = get_sensor_value_from_pin('1')
	if response == 0:
		print("Alerting emergency contact")
		send_live_location()
		make_emergency_call()
	time.sleep(5)