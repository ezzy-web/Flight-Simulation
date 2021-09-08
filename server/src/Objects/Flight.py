
import datetime
from system.Persistence.DatabaseManager import DatabaseManager


class Location:
    def __init__(self, name="", code="", city="", country=""):
        self.name = name
        self.code = code
        self.city = city
        self.country = country

class Flight:

    def __init__(self, id = 100, departure_days=None, arrival_days=None, str_dest=None, arr_dest = None, capacity = 100, status = "--"):
        self.timeStamp = datetime.datetime.now()
        self.id = id
        self.capacity = capacity
        self.status = status
        self.departure = departure_days
        self.arrival = arrival_days
        self.str_dest = str_dest
        self.arr_dest = arr_dest

    def setLocation(self, arr_location, dept_location):
        self.str_dest = dept_location
        self.arr_dest = arr_location

    def toDict(self):
        try:
            self.str_dest = self.str_dest.__dict__
            self.arr_dest = self.arr_dest.__dict__
        except:
            return self

        return self

    def toObj(self, obj):
        self.timeStamp = obj['timeStamp']
        self.id = obj['id']
        self.capacity = obj['capacity']
        self.status = obj['status']
        self.departure = obj['departure']
        self.arrival = obj['arrival']
        self.str_dest = obj['str_dest']
        self.arr_dest = obj['arr_dest']

class FlightManager:
    def __init__(self, all = False):
        self.db = DatabaseManager("Flight")
        self.all = all

    def newFlight(self, id, departure_time, arrival_time, departure_location, arrival_location, capacity = 100):
        flight = Flight(id, departure_time, arrival_time, departure_location, arrival_location, capacity)
        return self.db.write(flight.id, flight.toDict())


    def updateFlightLocation(self, flight_id, departure_location, arrival_location):
        response = self.getFlight(flight_id)

        if response['status']:
            response['data'].setLocation(arrival_location,departure_location)

            return self.db.update(flight_id, response['data'].toDict().__dict__)

        return response


    def updateFlightStatus(self, flight_id, status):
        return self.db.update(flight_id,{u'status': u''+status})

    def getAllFlights(self):
        response = self.db.getCollection()

        if (not response["status"]):
            response['data'] = []
            return response
        
        data = []
        for doc in response["data"]:
            flight = Flight()
            flight.toObj(doc.to_dict())
            data.append(flight)

        response['data'] = data
        return response

    def resetQuery(self):
        self.db.resetQuery()
        if not self.all :
            self.db.addQuery('status', '!=', 'Completed')

    def addFilter(self, field, operator, value):
        if (value != ""):
            self.db.addQuery(field, operator, value)

    def getFilteredFlights(self):
        response = self.db.getQuerriedDocs()

        if (not response['status']):
            response['data'] = []
            return response

        data = []
        for doc in response['data']:
            flight = Flight()
            flight.toObj(doc.to_dict())
            data.append(flight)

        response['data'] = data
        self.resetQuery()
        return response

    def getFlight(self, flight_id):
        response = self.db.read(flight_id)

        if (not response["status"]):
            response['data'] = None
            return response

        flight = Flight()
        flight.toObj(response['data'].to_dict())

        response['data'] = flight
        return response  

    def removeFlight(self, flight_id):
        return self.db.remove(flight_id)

