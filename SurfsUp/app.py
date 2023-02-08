import numpy as np
import datetime as dt
import sys
import pandas as pd

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from sqlalchemy import func

from flask import Flask, jsonify

# database setup
engine = create_engine("sqlite:///Resources/hawaii.sqlite")
Base = automap_base()

# reflect the tables
Base.prepare(engine, reflect=True)
Measurement= Base.classes.measurement
Station = Base.classes.station
session = Session(engine)

# Flask Setup
app = Flask(__name__)

# Flask Routes
@app.route("/")
def welcome():
    """The available API Routes are:"""
    return (
        f"the available API Routes for the Hawaii stations are:<br/>"
        f"total precipitation by date for all stations for the last year: /api/v1.0/precipitation<br/>"
        f"list the stations in the data set: /api/v1.0/stations<br/>"
        f"the dates and temperature observations of the most-active station: /api/v1.0/most_active<br/>"
        f"the maximum/minimum/average temperature for the period after yyyy-mm-dd: /api/v1.0/yyyy-mm-dd<br/>"
        f"the maximum/minimum/average temperature for the period between start(yyyy-mm-dd) and end (yyyy-mm-dd): /api/v1.0/yyyy-mm-dd/yyyy-mm-dd"
    )

# total precipitation by date for all stations: /api/v1.0/precipitation<br/>
@app.route('/api/v1.0/precipitation')
def precipitation():
    session = Session(engine)
    one_year_from_recent = dt.date(2017, 8, 23) - dt.timedelta(weeks=52)
    results = session.query(Measurement.date,func.sum(Measurement.prcp)).\
        filter(Measurement.date >= one_year_from_recent).\
        group_by(Measurement.date).all()
    session.close()

    precipitation_forjson = []
    for date, prcp in results:
        precipitation_forjson_dict = {}
        precipitation_forjson_dict["Date"] = date
        precipitation_forjson_dict["Precipitation"] = prcp
        precipitation_forjson.append(precipitation_forjson_dict)

    return jsonify(precipitation_forjson)

# list of stations in the data set: /api/v1.0/stations
@app.route('/api/v1.0/stations')
def stations():
    session = Session(engine)
    results = session.query(Station.station,Station.name).all()
    session.close()

    stations_forjson = []
    for station,name in results:
        stations_forjson_dict = {}
        stations_forjson_dict["Station"] = station
        stations_forjson_dict["Name"] = name
        
        stations_forjson.append(stations_forjson_dict)

    return jsonify(stations_forjson)

# the dates and temperature observations of the most-active station for the previous year of data /api/v1.0/tobs
@app.route('/api/v1.0/most_active')
def tobs():
    session = Session(engine)
    one_year_from_recent = dt.date(2017, 8, 18) - dt.timedelta(weeks=52)
    results = session.query(Measurement.date,Measurement.tobs).\
        filter(Measurement.date >= one_year_from_recent).\
        filter(Measurement.station=='USC00519281').all()
    session.close()
 # I have added the station name to the json file to add a little more data and avoid confusiuon
    query_precip_forjson = []
    for date, tobs in results:
        query_precip_forjson_dict = {}
        query_precip_forjson_dict["Station"] = 'USC00519281'
        query_precip_forjson_dict["Date"] = date
        query_precip_forjson_dict["Tobs"] = tobs
        query_precip_forjson.append(query_precip_forjson_dict)

    return jsonify(query_precip_forjson)

# the maximum/minimum/average temperature for the period after yyyy-mm-dd /api/v1.0/yyyy-mm-dd"    
@app.route('/api/v1.0/<start_date>')
def get_t_start(start_date):
    session = Session(engine)
    sel = (func.max(Measurement.tobs), func.min(Measurement.tobs), func.avg(Measurement.tobs))
    results = session.query(*sel).\
        filter(Measurement.date >= start_date).all()
    session.close()

 # I have added start date to the json file to add a little more data and avoid confusiuon
    tobs_stats_startend= []
    tobs_stats_1year = []
    for min,avg,max in results:
        tobs_stats_1year_dict = {}
        tobs_stats_1year_dict["Start Date"] = start_date
        tobs_stats_1year_dict["Min"] = min
        tobs_stats_1year_dict["Max"] = max
        tobs_stats_1year_dict["Average"] = avg
        
        tobs_stats_1year.append(tobs_stats_1year_dict)

    return jsonify(tobs_stats_1year)

# the maximum/minimum/average temperature for the period between start(yyyy-mm-dd) and end (yyyy-mm-dd): /api/v1.0/yyyy-mm-dd/yyyy-mm-dd
@app.route('/api/v1.0/<start_date>/<stop_date>')
def get_t_start_stop(start_date,stop_date):
    session = Session(engine)
    sel = (func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs))
    results = session.query(*sel).\
        filter(Measurement.date >= start_date).\
        filter(Measurement.date <= stop_date).all()
    session.close()

    # I have added start and end dates to the json file to add a little more data and avoid confusiuon
    tobs_stats_startend= []
    for min,avg,max in results:
        tobs_stats_startend_dict = {}
        tobs_stats_startend_dict["Start Date"] = start_date
        tobs_stats_startend_dict["End Date"] = stop_date
        tobs_stats_startend_dict["Min"] = min
        tobs_stats_startend_dict["Max"] = max
        tobs_stats_startend_dict["Average"] = avg
        tobs_stats_startend.append(tobs_stats_startend_dict)
    

    return jsonify(tobs_stats_startend)

if __name__ == '__main__':
    app.run(debug=True)
