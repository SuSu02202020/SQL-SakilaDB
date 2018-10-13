import numpy as np
import pandas as pd
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func


from flask import Flask, jsonify

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# We can view all of the classes that automap found
Base.classes.keys()

# Save reference to the table
# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################
year_ago = dt.date(2017, 8, 23) - dt.timedelta(days=365)

@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Welcome to Hawaii Climate API App!<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start_temp<br/>"
        f"/api/v1.0/temp_range"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():

    """Return the amount of precipitation from last year"""
    # Query for the dates and temperature observations from the last year.
    prcp_year_ago = session.query(Measurement.date, Measurement.prcp).\
                filter(Measurement.date >= year_ago).\
                group_by(Measurement.date).\
                order_by(Measurement.date).all()
    prcp_last_year = list(np.ravel(prcp_year_ago))

    return jsonify(prcp_last_year)

@app.route("/api/v1.0/stations")
def stations():
    """Return a JSON list of stations from the dataset"""
    # Query all stations from the Station table
    stations = session.query(Station.station, Station.name).all()
    station_list = list(np.ravel(stations))

    return jsonify(station_list)

@app.route("/api/v1.0/tobs")
def tobs():
    """Return a JSON list of Temperature Observations (tobs) for the previous year"""
    tobs_year_ago = session.query(Measurement.date, Measurement.station, Measurement.tobs).\
                filter(Measurement.date >= year_ago).\
                group_by(Measurement.date).\
                order_by(Measurement.date).all()
    tobs_list = list(np.ravel(tobs_year_ago))
    return jsonify(tobs_list)

@app.route("/api/v1.0/<start>")
def start_temp(start):
    """Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start"""
    start = dt.striptime(start, '%Y-%m-$d')
    end = dt.date(2017, 8, 23)
    min_avg_max = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date>=start).\
        group_by(Measurement.date).\
        order_by(Measurement.date).all()
    temp_start = list(np.ravel(min_avg_max))
    return jsonify(temp_start)

@app.route("/api/v1.0/<start>/<end>")
def temp_range(start, end):
    """Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start-end range"""
    start = dt.striptime(start, '%Y-%m-$d')
    end =  dt.striptime(end, '%Y-%m-$d')

    min_avg_max_range = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date>=start).\
        filter(Measurement.date<=end).\
        group_by(Measurement.date).\
        order_by(Measurement.date).all()
    range_temp = list(np.ravel(min_avg_max_range))
    return jsonify(range_temp)


if __name__ == '__main__':
    app.run(debug=True)






