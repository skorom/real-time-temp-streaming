from sense_hat import SenseHat
from time import sleep

import firebase_admin
from firebase_admin import credentials, db


sense = SenseHat()
message = ""


def init_firebase():
    """
    Initialize Firebase Admin SDK.

    Option A (recommended on Raspberry Pi): Service account JSON:
        cred = credentials.Certificate("/path/to/serviceAccountKey.json")
        firebase_admin.initialize_app(cred, {"databaseURL": DB_URL})

    Option B: Application Default Credentials (ADC):
        - GOOGLE_APPLICATION_CREDENTIALS environment variable points to
          a service account JSON
        - or another ADC provider (less common on Raspberry Pi)

    Note:
    Even if your Realtime Database rules are currently open
    (no authentication/authorization required),
    the Admin SDK still expects some form of credential.
    """
    if not firebase_admin._apps:
        # Try to initialize using Application Default Credentials
        cred = credentials.Certificate('/path/to/token.json')
        firebase_admin.initialize_app(cred, {"databaseURL": "https://erts-2025-default-rtdb.europe-west1.firebasedatabase.app/"})


def update_firebase():
    """
    Read temperature and humidity from the Sense HAT
    and push the values to Firebase Realtime Database.
    """
    humidity = sense.get_humidity()
    temperature = sense.get_temperature()

    if humidity is not None and temperature is not None:
        sleep(2)
        print(
            "Temp={0:0.1f}*C  Humidity={1:0.1f}%".format(temperature, humidity)
        )
    else:
        print("Failed to get reading. Try again!")
        sleep(10)

    data = {
        "temp": temperature,
        "humidity": humidity
    }

    # Original code used: firebase.post('/rpi', data)
    # In firebase-admin, push() is the equivalent of POST
    # (it generates an automatic unique key)
    db.reference("rpi").push(data)


def _extract_message(payload):
    """
    Extract the message string from different possible
    Realtime Database structures.

    Original code logic:
        tempMessage.values()[0].values()[0]

    Typical expected structures:
        /message/{pushId}/{someKey}: "text"
        /message/{pushId}: "text"
        /message: "text"
    """
    if payload is None:
        return None

    # If the payload is already a string
    if isinstance(payload, str):
        return payload

    # If the payload is a dictionary, try to extract the first value
    if isinstance(payload, dict) and payload:
        first_val = next(iter(payload.values()))

        if isinstance(first_val, str):
            return first_val

        if isinstance(first_val, dict) and first_val:
            inner_val = next(iter(first_val.values()))
            if isinstance(inner_val, str):
                return inner_val

    return None


def update_message():
    """
    Read incoming message from Firebase and display it
    on the Sense HAT LED matrix if it has changed.
    """
    global message

    # Original code used: firebase.get('/message', None)
    payload = db.reference("message").get()
    incoming = _extract_message(payload)

    if incoming is not None and incoming != message:
        message = incoming
        print("Incoming message:", message)
        sense.show_message(message)


def main():
    """
    Main loop:
    - Send sensor data to Firebase
    - Poll Firebase for incoming messages
    """
    init_firebase()

    while True:
        update_firebase()
        update_message()


if __name__ == "__main__":
    main()
