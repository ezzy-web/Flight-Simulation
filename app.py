from flask import Flask, render_template, request, redirect, url_for, flash, make_response, Blueprint
from Objects.Flight_redo import Connection, Time, AirportManager, FlightManager, ScheduleManager


manager = FlightManager(True)
smanager = ScheduleManager()
amanager = AirportManager()
connect = Connection()

app = Flask(__name__)
app.config.update(
    DEBUG=True,
    SECRET_KEY=b"FLIGHTSYSTEST10023"
)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/flight")
def addFlightPage():
    return render_template("add-flight.html")

@app.route("/airport")
def addAirportPage():
    return render_template("add-airport.html")


@app.route("/find-flight")
def searchFlightPage():
    return render_template("search-flights.html")


@app.route("/view-flights")
def viewFlightPage():
    response = manager.getAllFlights()
    print(response)
    if response['status']:
        return render_template("flights.html", flightsExist = len(response['data']) != 0, flights = response['data'])
    flash("Error: Something went wrong.")
    return render_template("index.html")




@app.route("/flight-add", methods=['GET', 'POST'])
def addFlightAction():
    if request.method == "POST" :
        response = manager.newFlight(request.form['flight-number'], request.form['capacity'], request.form['crew-capacity'])

        if response['status']:
            flash("Successfully Added Flight " + request.form['flight-number'])
            return redirect(url_for('home'))
    flash("Error: Something went wrong. Try Again")
    return render_template("add-flight.html")


@app.route("/airport-add", methods=['GET', 'POST'])
def addAirportAction():
    if request.method == "POST" :
        response = amanager.addAirport(request.form['airport-code'], request.form['city'], request.form['country']) if (request.form['name'] == "") else amanager.addAirport(request.form['airport-code'], request.form['city'], request.form['country'], request.form['name'])
        
        if response['status']:
            flash("Successfully Added Airport " + request.form['airport-code'].upper())
            return redirect(url_for('home'))
    flash("Error: Something went wrong. Try Again")
    return render_template("add-airport.html")


@app.route("/flight/detail/<flight>")
def flightDetails(flight):
    response = manager.getFlight(flight)
    if response['status']:
        flight = response['data']
        schedules = []
        
        for schedule in flight.flights:

            response = smanager.getSchedule(schedule)

            if response['status']:
                schedules.append(response['data'])
            else:
                flash("Error: Something went wrong. Try Again")
                return render_template("index.html")

        return render_template('flight-details.html', flight = flight, schedules = schedules, isSchedule = len(schedules) != 0)
    flash("Error: Something went wrong. Try Again")
    return render_template("index.html")


@app.route('/flight/<flight_id>/schedule')
def addSchedule(flight_id):
    return render_template("add-schedule.html", flight_id = flight_id)


@app.route('/flight/<flight_id>/schedule/add', methods = ['GET', 'POST'])
def addScheduleAction(flight_id):
    if request.method == 'POST':
        dhh = int(request.form['hour-dept']) if request.form['m-dept'] == 'am' else int(request.form['hour-dept']) + 12
        ahh = int(request.form['hour-arr']) if request.form['m-arr'] == 'am' else int(request.form['hour-arr']) + 12
        response = smanager.newFlightSchedule(flight_id, int(request.form['d-dd']), int(request.form['a-dd']), dhh, int(request.form['mins-dept']), ahh, int(request.form['mins-arr']), request.form['dept-location'].upper(), request.form['arr-location'].upper())

        if response['status']:
            flash("Schedule Successfully Registered")
            return redirect("/flight/detail/" + flight_id)

    flash("Error: Something went wrong. Try Again")
    return redirect("/flight/"+flight_id+"/schedule")

        
if __name__ == "__main__": 
    app.run()

