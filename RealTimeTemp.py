from sense_hat import SenseHat
from firebase import firebase
from time import sleep

sense = SenseHat()
firebase = firebase.FirebaseApplication('https://erts-2025-default-rtdb.europe-west1.firebasedatabase.app/', None)
message = ""

def update_firebase():
    humidity = sense.get_humidity()
    temperature = sense.get_temperature()

    if humidity is not None and temperature is not None:
        sleep(2)
        str_temp = ' {0:0.2f} *C '.format(temperature)
        str_hum  = ' {0:0.2f} %'.format(humidity)
        print('Temp={0:0.1f}*C  Humidity={1:0.1f}%'.format(temperature, humidity))

    else:
        print('Failed to get reading. Try again!')
        sleep(10)

    data = {"temp": temperature, "humidity": humidity}
    firebase.post('/rpi', data)

def updateMessage():
    global message
    tempMessage = firebase.get('/message', None)
    if tempMessage is not None:
        tempMessage = tempMessage.values()[0].values()[0]
        if tempMessage != message:
            message = tempMessage
            print ("Incoming message: ", message)
            sense.show_message(message)


#updateMessage()
while(True):
    update_firebase()
    updateMessage()
