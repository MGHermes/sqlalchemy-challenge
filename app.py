# import Flask
from flask import Flask, jsonify

# import numpy, pandas, and datetime
import numpy as np
import pandas as pd
import datetime as dt

#import SQLAlchemy and ORM (object relational mapper)
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

# create an instance of Flask
app = Flask(__name__)

# connect to the hawaii sqlite database
# use location (Resources/hawaii.sqlite) to connect to that file
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect the hawaii sqlite database into our new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# create our session in order to query the precompiled DB
session = Session(engine)

# create a basic home route
@app.route("/")
def home():
    return(
        f"<center><h2>Welcome to the Hawaii Climate Analysis Local API!</h2></center>"
        f"<center><h3>Select from one of the available routes: </h3></center>"
        f"<center>/api/v1.0/precipitation</center>"
        f"<center>/api/v1.0/stations</center>"
        f"<center>/api/v1.0/tobs</center>"
        f"<center>/api/v1.0/start/end</center>"
    )

# /api/v1.0/precipitation route
@app.route("/api/v1.0/precipitation")
def precip():
    # GOAL: return the previous year's precipitation as a json
    
    # calculate the date one year from the last date in data set.
    previousYear = dt.date(2017, 8, 23) - dt.timedelta(days = 365)

    # perform a query to retrieve the data and precipitation scores
    results = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= previousYear).all()
    
    # close the session
    session.close()
    
    # dictionary with the date as the key and the precipitation (prcp) as the value
    precipitation = {date: prcp for date, prcp in results}

    # convert the dictionary to a json
    return jsonify(precipitation)

# /api/v1.0/stations route
@app.route("/api/v1.0/stations")
def stations():
    # GOAL: show a list of stations

    # perform a query to retrieve the names of the stations
    results = session.query(Station.station).all()

    # close the session
    session.close()

    # use np.ravel to convert the query results to a 1-D array
    # use list function to convert the 1-D array to a list
    stationList = list(np.ravel(results))

    # convert the list to a json and display the results
    return jsonify(stationList)

# /api/v1.0/tobs route
@app.route("/api/v1.0/tobs")
def temperatures():
    # GOAL: return the previous year's temperatures

    # calculate the date one year from the last date in data set.
    previousYear = dt.date(2017, 8, 23) - dt.timedelta(days = 365)

    # perform a query to retrieve the temperatures from the most active station from the past year
    results = session.query(Measurement.date, Measurement.tobs).\
        filter(Measurement.station == 'USC00519281').\
        filter(Measurement.date >= previousYear).all()

    # close the session
    session.close()

    # use np.ravel to convert the query results to a 1-D array
    # use list function to convert the 1-D array to a list
    temperatureList = list(np.ravel(results))

    # return the list of temperatures
    return jsonify(temperatureList)

# /api/v1.0/start ** and ** /api/v1.0/start/end routes
@app.route("/api/v1.0/<start>") # use <> so that start is a variable, not a hardcoded string
@app.route("/api/v1.0/<start>/<end>") # use <> so that start and end are variables
def dateStats(start=None, end=None):
    # GOAL: return the temperatures between two dates (end date is optional)

    # create a select statement (of things that we will be grabbing)
    selection = [func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)]

    # if we do not have an end date
    if not end:
        
        startDate = dt.datetime.strptime(start, "%m%d%Y")

        results = session.query(*selection).filter(Measurement.date >= startDate).all()

        session.close()

        temperatureList = list(np.ravel(results))

        # return the list of temperatures
        return jsonify(temperatureList)

    # if we have an end date
    else:
        
        startDate = dt.datetime.strptime(start, "%m%d%Y") #strip the time

        endDate = dt.datetime.strptime(end, "%m%d%Y") #strip the time

        results = session.query(*selection).\
            filter(Measurement.date >= startDate).\
            filter(Measurement.date <= endDate).all()

        session.close()

        temperatureList = list(np.ravel(results))

        # return the list of temperatures
        return jsonify(temperatureList)

# create an app launcher for Flask
if __name__ == '__main__':
    app.run(host="localhost", port=4999, debug=True)
