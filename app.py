#import dependencies
from flask import Flask
from flask import jsonify
import numpy as np 
import datetime as dt 

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

#set up database
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

#reflect database
Base = automap_base()
#reflect the tables
Base.prepare(engine, reflect=True)

#reference to table
measurement = Base.classes.measurement
station = Base.classes.station

#set up flask 
app = Flask(__name__)

#set up routes
@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start<br/>"
        f"/api/v1.0/start/end"
    )


@app.route("/api/v1.0/precipitation")
def precipitation():
    #link session from python to db
    session = Session(engine)

    """Return a list of all precipitation and date"""
    # Query all precipitation and date
    results = session.query(measurement.date,measurement.prcp).all()

    session.close()

    #Convert list of tuples into dict
    all_prcp=[]
    for date,prcp in results:
        prcp_dict = {}
        prcp_dict[date] = prcp
        all_prcp.append(prcp_dict)

    return jsonify(all_prcp)
@app.route("/api/v1.0/stations")
def stations():
    #link session from python to db
    session = Session(engine)
    session.query(measurement.station).distinct().count()
    active_stations = session.query(measurement.station, func.count(measurement.station)).group_by(measurement.station).order_by(func.count(measurement.station).desc()).all()
    return jsonify(dict(active_stations))

@app.route("/api/v1.0/tobs")
def tempartureobs():
    #link session from python to db 
    session = Session(engine)
    tobss = session.query(measurement.tobs).filter(measurement.station == 'USC00519281').filter(measurement.date >= '2017,8,23').all()
    tobs_list = list(np.ravel(tobss))
    return jsonify(tobs_list)


#return the min, avg, and max temperatures for date range
@app.route("/api/v1.0/<start>/<end>")
def calc_temps(start, end):
    #link session from python to db
    session = Session(engine)
    results=session.query(func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)).\
                filter(measurement.date >= start).filter(measurement.date <= end).all()
    session.close()
    tempobs={}
    tempobs["Min_Temp"]=results[0][0]
    tempobs["avg_Temp"]=results[0][1]
    tempobs["max_Temp"]=results[0][2]
    return jsonify(tempobs)

@app.route("/api/v1.0/<start>")
def calc_temps_sd(start):
    #link session from python to db
    session = Session(engine)
    results=session.query(func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)).\
                filter(measurement.date >= start).all()
    session.close()
    tempobs={}
    tempobs["Min_Temp"]=results[0][0]
    tempobs["avg_Temp"]=results[0][1]
    tempobs["max_Temp"]=results[0][2]
    return jsonify(tempobs)
if __name__ == '__main__':
    app.run(debug=True)