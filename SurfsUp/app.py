# Import the dependencies.

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify, request

from datetime import datetime, timedelta

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")
#################################################

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
measurement = Base.classes.measurement
station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################
@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start or /api/v1.0/start/end"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)
    
    # Calculate the date one year from the last date in data set.
    time_delta = timedelta(days=365)
    recent_date = datetime.strptime('2017-08-23', '%Y-%m-%d')
    oneYearBefore_date = recent_date - time_delta

    rec_oneYear_data = session.query(measurement.date, measurement.prcp).\
     filter(measurement.date <= recent_date).\
     filter(measurement.date > oneYearBefore_date).all()

    ret_dict = {}
    for r in rec_oneYear_data:
        ret_dict[r.date] =  r.prcp
    session.close()

    return jsonify(ret_dict)

@app.route("/api/v1.0/stations")
def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)    
    rows = session.query(station).all()    
    ret_dict = {}
    for r in rows:
        ret_dict[r.id] =  r.name
    session.close()

    return jsonify(ret_dict)

@app.route("/api/v1.0/tobs")
def tobs():

    # Create our session (link) from Python to the DB
    session = Session(engine)    

    # Calculate the date one year from the last date in data set.
    time_delta = timedelta(days=365)
    recent_date = datetime.strptime('2017-08-23', '%Y-%m-%d')
    oneYearBefore_date = recent_date - time_delta

    tobs_data = session.query(measurement.date, measurement.tobs).\
    filter(measurement.station == 'USC00519281').\
    filter(measurement.date <= recent_date).\
    filter(measurement.date > oneYearBefore_date).all()

    ret_dict = {}
    for r in tobs_data:
        ret_dict[r.date] =  r.tobs
    session.close()

    return jsonify(ret_dict)

@app.route("/api/v1.0/<start>")
@app.route("/api/v1.0/<start>/<end>")
def filterAfterStartDate(start, end=None):    
    session = Session(engine)    
    if ((start is not None) and (end is not None)):
        rows = session.query(func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)).\
            filter(measurement.date >=start).filter(measurement.date <= end)
    elif(start is not None):
        rows = session.query(func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)).\
            filter(measurement.date >=start)
    session.close()
    return jsonify({"tMin": rows[0][0], "tAvg": rows[0][1], "tMax": rows[0][2]})   

  