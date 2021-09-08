import datetime

from werkzeug.sansio.response import Response
from Persistence.DatabaseManager import DatabaseManager
import random


class Time:
    def __init__(self) -> None:
        pass
        
    def getTimeMins(self, dd, hh, mm):
        self.dd = (dd % 8) * 24 * 60 
        
        if (hh >= 24):
            self.dd = self.dd + ((hh // 24) * 24 * 60)
            self.hh = (hh%24) * 60
        else:
            self.hh = hh * 60 
        
        self.mm = mm
        
        self.mins = self.dd + self.hh + self.mm
        return self.mins % 10080 if self.mins >= 11520 else self.mins

    def getTimeDiff(self, a_time, d_time):
        if (a_time < d_time):
            return (d_time - a_time)
        else:
            return -1*(d_time - a_time)  + 1440

    def convertTime(self, mins):
        dd = int(mins/1440)
        rem = mins % 1440

        hh = int(rem/60)
        mm = rem % 60

        return (dd, hh, mm)

    def timeToString(self, t_time):
        dd = 'Monday'
        if t_time[0] == 2:
            dd = 'Tuesday'
        elif t_time[0] == 3:
            dd = 'Wednesday'
        elif t_time[0] == 4:
            dd = 'Thursday'
        elif t_time[0] == 5:
            dd = 'Friday'
        elif t_time[0] == 6:
            dd = 'Saturday'
        else:
            dd = 'Sunday'

        tod = 'PM' if t_time[1] >= 12 else 'AM'
        hh = (t_time[1] - 12) if t_time[1] > 12 else t_time[1]

        mm = '0'+str(t_time[2]) if t_time[2] < 10 else str(t_time[2])
        
        return dd + ', ' + str(hh) + ':' + mm + ' ' + tod


class AirportManager:
    def __init__(self):
        self.db = DatabaseManager("Airport")

    def addAirport(self, code, city, country, name = "--"):
        response = self.db.exist(code)
        
        if not response['status']:
            response['status'] = False
            response['error'] = 'Already Exist'
            return response
        
        airport = Airport(code, city, country, name)

        response = self.db.write(airport.code, airport)

        return response

    def getAirport(self, code):
        response = self.db.read(code)
        
        if (response["status"]):
            airport = Airport()
            airport.toObj(response['data'].to_dict())
            response['data'] = airport
        
        return response 

    def addAirportSchedule(self, code, a_code, flight_id, schedule_id, time, isDepart = True):
        response = self.getAirport(code)
        if response['status']:
            response['data'].addFlightSchedule(flight_id, schedule_id, time, a_code, isDepart)
            response = self.db.update(code, response['data'].__dict__)

        return response


class ScheduleManager:
    def __init__(self):
        self.db = DatabaseManager("Flight-Schedules")
        self.flights = FlightManager()
        self.airports = AirportManager()

    def newFlightSchedule(self, flight_id, dday, aday, dhr, dmin, ahr, amin, dept, arr):
        schedule_id = flight_id + '-' + str(random.randint(10000,999999)) + '-' + str(random.randint(0,9999))
        
        schedule = FlightSchedule(schedule_id, dday, aday, dhr, dmin, ahr, amin, dept, arr)

        response = self.flights.addFlightSchedule(flight_id, schedule_id)
        
        if response['status']:
            response = self.airports.addAirportSchedule(dept, arr, flight_id, schedule_id, schedule.dept_time, True)
            if response['status']:
                response = self.airports.addAirportSchedule(arr, dept, flight_id, schedule_id, schedule.arr_time, False)
                if response['status']:
                    response = self.db.write(schedule_id, schedule)
        

        return response

    def getSchedule(self, schedule_id):
        response = self.db.read(schedule_id)

        if (not response["status"]):
            response['data'] = None
            return response

        flight = FlightSchedule()
        flight.toObj(response['data'].to_dict())

        response['data'] = flight
        return response  

class FlightManager:
    def __init__(self, all = False):
        self.db = DatabaseManager("Flight")
        self.all = all

    def newFlight(self, id, capacity, crew_cap):
        flight = Flight(id, capacity, crew_cap)
        return self.db.write(flight.id, flight)


    def addFlightSchedule(self, flight_id, schedule_id):
        response  = self.getFlight(flight_id)

        if response['status']:
            response['data'].addFlightSchedule(schedule_id)
            response = self.db.update(flight_id, response['data'].__dict__)

        return response


    def updateFlightLocation(self, flight_id):
        pass


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
        print(flight_id)
        response = self.db.read(flight_id)

        if (not response["status"]):
            response['data'] = None
            print('init')
            return response
        
        print(response['data'].to_dict())
        flight = Flight()
        flight.toObj(response['data'].to_dict())

        response['data'] = flight
        return response  

    def removeFlight(self, flight_id):
        return self.db.remove(flight_id)



class Airport:
    def __init__(self, code="", city="", country="", name = "--"):
        self.name = name.upper()
        self.code = code.upper()
        self.city = city.upper()
        self.country = country.upper()
        self.search = [self.name, self.code, self.city, self.country]
        self.arriving_flights = []
        self.departing_flights = []

    def addFlightSchedule(self, flight_id, schedule_id, time, code, isDepart = True):
        if isDepart:
            self.departing_flights.append({'flight-id': flight_id, 'schedule-id': schedule_id, 'time': time, 'airport': code})
        else:
            self.arriving_flights.append({'flight-id': flight_id, 'schedule-id': schedule_id, 'time': time, 'airport': code})

    def toObj(self, obj):
        self.name = obj['name']
        self.code = obj['code']
        self.city = obj['city']
        self.country = obj['country']
        self.arriving_flights = obj['arriving_flights']
        self.departing_flights = obj['departing_flights']


class Flight:
    def __init__(self, id="", capacity=0, crew_cap=0, equip = ""):
        self.id  = id
        self.capacity = capacity
        self.equip = equip
        self.crew_cap = crew_cap
        self.flights = []

    def getScheduleCount(self):
        return len(self.flights)

    def addFlightSchedule(self, schedule_id):
        self.flights.append(schedule_id)

    def toObj(self, obj):
        self.id  = obj['id']
        self.capacity = obj['capacity']
        self.flights = obj['flights']
        self.crew_cap = obj['crew_cap']
        self.equip = obj['equip']


class FlightSchedule:
    def __init__(self, id=0, dday=0, aday=0, dhr=0, dmin=0, ahr=0, amin=0, dept='', arr=''):
        self.id = id
        self.timeStamp = datetime.datetime.now()
        self.dday = dday
        self.aday = aday
        time = Time()

        self.dept_time = time.getTimeMins(dday, dhr, dmin)
        self.arr_time = time.getTimeMins(aday, ahr, amin) 
        self.dept = dept
        self.arr = arr
        self.status = '--'
        self.passenger_count = 0

    def updateStatus(self, status):
        self.status = status
    
    def getTimes(self):
        time = Time()
        departing_time = time.convertTime(self.dept_time)
        arriving_time = time.convertTime(self.arr_time)

        return {
            'arr' : time.timeToString(arriving_time),
            'dept' : time.timeToString(departing_time)
        }

    def toObj(self, obj):
        self.id = obj['id']
        self.timeStamp = obj['timeStamp']
        self.dept_time = obj['dept_time']
        self.arr_time = obj['arr_time']
        self.dept = obj['dept']
        self.arr = obj['arr']
        self.status = obj['status']
        self.passenger_count = obj['passenger_count']

class Queue:
    def __init__(self):
        self.queue = []

    def isEmpty(self):
        return self.queue == []

    def add(self, val):
        self.queue.append(val)

    def dequeue(self):
        return self.queue.pop(0)
    
    def isInQueue(self, val):
        return val in self.queue




class Connection:
    def __init__(self):
        self.airports = AirportManager()
        self.time = Time()
        self.visited = []

    def __checkConnectingFlights(self, a_time, d_time):
        if (a_time < d_time) and (self.time.getTimeDiff(a_time, d_time) < 1440):
            return True
        return False

    def __visited(self, code):
        return not code in self.visited

    def __getConnectingFlights(self, flights, time):
        lst = []
        for flight in flights:
            if self.__checkConnectingFlights(time, flight['time']):
                lst.append(flight)

        return lst


    def getAllConnections(self, d_code, a_code, dd):
        time = self.time.getTimeMins(dd, 0, 0)
        queue = Queue()
        response = {
            'status': False,
            'data': [],
            'error': None
        }
        self.visited = []
        paths = []
        code_index = 0
        index = 0
        paths.append([])
        self.visited.append(d_code)
        prev = ()
        while(True):

            d_airport = self.airports.getAirport(d_code)['data']
            connections = self.__getConnectingFlights(d_airport.departing_flights, time)
            print(d_code)
            for connection in connections:
                print('CONNECTION ====== PATHS')
                print('\n\n=================================')
                print(connection)
                print(paths)
                print('=================================\n\n')
                if (not queue.isInQueue([connection['airport'], code_index])):
                        
                    # self.visited.append(connection['airport'])
                    index = index + 1
                    paths[code_index].append((connection['schedule-id'],d_code,connection['airport']))
                    
                    if (prev == ()):
                        paths.append([(connection['schedule-id'],d_code,connection['airport'])])
                    else:
                        paths.append([prev]+[(connection['schedule-id'],d_code,connection['airport'])])

                    if connection['airport'] == a_code:
                        response['data'].append(paths[index-1])
                        print(index)
                        print('PREV ====== FLIGHTS')
                        print('\n\n=================================')
                        print(prev)
                        print('+++++++++++++++++++++++++++++++++++++')
                        print(response['data'])
                        print('=================================\n\n')
                    else:
                        queue.add([connection['airport'], index])

                    
                    print("QUEUE===============")
                    print(queue.queue)
                    print('\n\n')

                    
                            
            if (queue.isEmpty()):
                response['status'] = True
                break
            d = queue.dequeue()
            code_index = d[1]
            d_code = d[0]
            prev = paths[d[1]]

        return response






        