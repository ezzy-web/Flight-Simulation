import firebase_admin
from firebase_admin import credentials, firestore, storage
import pyrebase
from flask import Flask



# Firebase Admin Configuration
cred = credentials.Certificate('./server/src/flight-simulator-7a2ca-firebase-adminsdk-aqo2d-3da95c1f9f.json')
default_app = firebase_admin.initialize_app(cred)



# # Pyrebase Configuration
# config = {
#   "apiKey": "AIzaSyAulMymm6QRQ0cBbXA4ic1qeRs3OBCw9YI",
#   "authDomain": "flight-simulator-7a2ca.firebaseapp.com",
#   "projectId": "flight-simulator-7a2ca",
#   "storageBucket": "flight-simulator-7a2ca.appspot.com",
#   "messagingSenderId": "599772213402",
#   "appId": "1:599772213402:web:5a9717abbb785c62d96f23",
#   "measurementId": "G-12RM5D9TXW"
#   }

# firebase = pyrebase.initialize_app(config)


# Flask Configuration
app = Flask(__name__)
app.config.update(
    DEBUG=True,
    SECRET_KEY=b"FLTHSIMUL000SYS0012"
)