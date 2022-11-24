#import dependencies
from flask import Flask
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
    latest_date = session.query(measurement.date).order_by(measurement.date.desc()).first()
    year_from = dt.date(2017,8,23) - dt.timedelta(days=365)

    annual_prcp = session.query(measurement.date, measurement.prcp).filter(measurement.date >= year_from, measurement.prcp != None).order_by(measurement.date).all()
    return jsonify(dict(annual_prcp))

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
    results=session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
                filter(Measurement.date >= start).filter(Measurement.date <= end).all()
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
    results=session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
                filter(Measurement.date >= start).all()
    session.close()
    tempobs={}
    tempobs["Min_Temp"]=results[0][0]
    tempobs["avg_Temp"]=results[0][1]
    tempobs["max_Temp"]=results[0][2]
    return jsonify(tempobs)
if __name__ == '__main__':
    app.run(debug=True)