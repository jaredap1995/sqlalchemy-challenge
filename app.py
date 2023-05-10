# Import the dependencies.
from flask import Flask, jsonify
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.ext.automap import automap_base
import datetime as dt
import numpy as np
from sqlalchemy import create_engine, func



#################################################
# Database Setup
#################################################

engine = create_engine("sqlite:///Resources/hawaii.sqlite")
Base = automap_base()
Base.prepare(engine, reflect=True)
Measurement = Base.classes.measurement
Station = Base.classes.station
session = Session(engine)


#################################################
# Flask Setup
#################################################

app = Flask(__name__)

@app.route("/")
def home():
    return (
        f"Welcome to the Climate API!<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    recent_date=session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    recent_date=recent_date[0]
    year_ago_date=dt.datetime.strptime(recent_date, "%Y-%m-%d") - dt.timedelta(days=365)
    year_ago_date=year_ago_date.strftime("%Y-%m-%d")
    results=session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= year_ago_date).all()
    precipitation_dict = {date: prcp for date, prcp in results}
    return jsonify(precipitation_dict)


@app.route("/api/v1.0/stations")
def stations():
    results=session.query(Station.station).all()
    stations_list=list(np.ravel(results))
    return jsonify(stations_list)



@app.route("/api/v1.0/tobs")
def tobs():
    recent_date=session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    recent_date=recent_date[0]
    year_ago_date=dt.datetime.strptime(recent_date, "%Y-%m-%d") - dt.timedelta(days=365)
    year_ago_date=year_ago_date.strftime("%Y-%m-%d")

    active_stations = session.query(Measurement.station, func.count(Measurement.station)).\
    group_by(Measurement.station).\
    order_by((func.count(Measurement.station)).desc()).all()
    most_active_station = active_stations[0][0]
    results=session.query(Measurement.tobs).\
        where(Measurement.station==most_active_station).all()
    tobs_list=list(np.ravel(results))
    return jsonify(tobs_list)

@app.route("/api/v1.0/<start>")
def start(start):
    # Use the start date provided by the user
    start_date = dt.datetime.strptime(start, "%Y-%m-%d")

    results=session.query(func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)).\
        filter(Measurement.date >= start_date).all()

    tobs_list=list(np.ravel(results))
    return jsonify(tobs_list)


@app.route("/api/v1.0/<start>/<end>")
def start_end(start, end):
    # Use the start and end dates provided by the user
    start_date = dt.datetime.strptime(start, "%Y-%m-%d")
    end_date = dt.datetime.strptime(end, "%Y-%m-%d")

    results=session.query(func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)).\
        filter(Measurement.date >= start_date).\
        filter(Measurement.date <= end_date).all()

    tobs_list=list(np.ravel(results))
    return jsonify(tobs_list)



if __name__ == "__main__":
    app.run(debug=True)





